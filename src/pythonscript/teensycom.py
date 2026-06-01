"""
Crossbar Image Processing
==================================
Sending image patches to the Teensy/crossbar,
collecting outputs, and comparing them to a software baseline.
"""

# raspberry code 220301

import time
import math
import serial
import numpy as np
import matplotlib.pyplot as plt
import torch
import torchvision
import torchvision.transforms as transforms
import scipy.signal

from QATCNN import CNN


# --- CONFIG ---
# ============================================================
SERIAL_PORT = "COM7"
BAUD_RATE = 115200
SERIAL_TIMEOUT_S = 5

IMAGE_SIZE = 20
KERNEL_SIZE = 3

# match this with teensy's encoding
MAX_LEVEL = 128


# --- KERNEL ---
# ============================================================
# handle negatives?

# kernel = np.array([
#     [-1, -1, -1],
#     [0, 0, 0],
#     [1, 1, 1]
# ], dtype=np.float32)

# kernel = np.array([
#     [1, 2],
#     [2, 3]
# ], dtype=np.float32)

kernel = np.array([
    [1, 2, 1],
    [2, 4, 2],
    [1, 2, 1]
], dtype=np.float32)

# this acts like a flag for whether we have negative values in our kernel. 
# If we do, we need to set the offset, if not, we just use kernel as is
# we shift by one more, to avoid 0's in the kernel
KERNEL_OFFSET = max(0.0, -float(kernel.min())+1)

# --- IMAGE LOADING ---
# ============================================================
def load_mnist_image(index=0, image_size=100):
    """
    Load one MNIST image resized to image_size x image_size.
    """
    transformimg = transforms.Compose([
    transforms.Resize((image_size,image_size)),
    transforms.ToTensor() 
    # ------ MNIST is greyscale from 0 to 255. However, ToTensor() scales that down to 0.0 to 1.0. 
    ])
    training_data = torchvision.datasets.MNIST(
        root = "data",
        train= True,
        download=False, # set to True if first time running
        transform = transformimg
    )

    exampleimg, examplelabel= training_data[index]

    exampleimg = exampleimg.squeeze().numpy()

    return exampleimg, examplelabel

# loading the test images for CNN image classification
def load_mnist_test_image(class_a, class_b):
    transformimg = transforms.Compose([
        transforms.ToTensor()
    ])
    test_data = torchvision.datasets.MNIST(
        root = "data",
        train = False,
        download = False,
        transform = transformimg
    )

    zerosandones_hat = [i for i in range(len(test_data)) if test_data.targets[i] in [class_a,class_b]]
    filtered_test_data = torch.utils.data.Subset(test_data, zerosandones_hat)

    return torch.utils.data.DataLoader(filtered_test_data, batch_size=1, shuffle=False, num_workers=0)


# --- SOFTWARE BASELINE ---
# ============================================================
def software_convolution(image_2d, kernel):
    """
    Compute the software reference output using 2D convolution.
    """

    return scipy.signal.correlate2d(image_2d, kernel, mode="valid")


def software_patch_response(patch_2d, kernel):
    """
    Compute the software response for one patch.

    - Multiply patch and kernel elementwise
    - Sum the result

    - Additionally put it back to original MNIST scale
    """
    # MNIST is 0 to 255. ToTensor is 0 to 1. Quantize patch takes it to 0 to MAX_LEVEL
    # thus, I want our software pixels back to MNIST scale using this function (0 to 255)
    
    summed = np.sum(patch_2d * kernel)

    if (KERNEL_OFFSET > 0):
        return summed * 255

    return  summed * 255 / kernel.sum() # normalization

# --- QUANTIZATION ---
# ============================================================
def quantize_patch(patch_2d, max_level=MAX_LEVEL):
    """
    Convert one patch into a flat list of integer levels for the Teensy.

    - Quantize each value using the chosen encoding range
    - Flatten the patch into 1D
    - Return a Python list of integers
    """
    arr = np.round(max_level * np.clip(patch_2d, a_min=0.0, a_max=1.0))
    return arr.astype(int).flatten()


# --- SERIAL TRANSPORT ---
# ============================================================
class CrossbarSerial:
    """
    Serial wrapper for Teensy communication.

    Current protocol idea:
    - Python sends one quantized patch as comma-separated integers
    - Teensy replies with one float output

    Improved protocol to compensate for conductance drifting on real array:
    - Python sends all quantized patches at once 
    - Teensy goes through them one by one while the rest waits in the serial monitor
    """

    def __init__(self, port, baud_rate, timeout_s=5):
        """
        - Initialize the serial handle to None
        """
        self.port = port
        self.baud_rate = baud_rate
        self.timeout_s = timeout_s
        self.ser = None

    def open(self):
        """
        - Open the serial.Serial connection
        """
        self.ser = serial.Serial(self.port, self.baud_rate, timeout=self.timeout_s)
        time.sleep(1)
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        print("Serial connection has been made.")

        

    def close(self):
        """
        - Close the serial port if open
        - Clear the handle
        """
        if (self.is_open()):
            self.ser.close()

        self.ser = None

    def is_open(self):
        return self.ser is not None and self.ser.is_open

    def send_patch(self, patch_values):
        """
        Send one patch to the Teensy and receive one float response.

        Error handling:
        - If the response is empty, return NaN
        - If conversion to float fails, return NaN
        - If serial communication fails, return NaN
        """

        if not self.is_open():
            return float("nan"), float("nan") 

        patchtoMCU = ""
        if (KERNEL_OFFSET == 0.0):
            # make the patch of pixels into a string to send to MCU
            patchtoMCU = "PATCH,"+",".join(str(v) for v in patch_values) + "\n"
        
        # this is for when there are negative values in the kernel, requiring another column
        # for the offset calculation. 
        elif (KERNEL_OFFSET > 0.0):
            patchtoMCU = "PATCHOFFS,"+",".join(str(v) for v in patch_values) + "\n"

        # write to MCU
        self.ser.write(patchtoMCU.encode("utf-8"))

        # receive the convolution scalar result
        convfromMCU = self.ser.readline().decode(errors="replace").strip()

        if (convfromMCU == ""):
            return float("nan"), float("nan")

        # this part parses the teensy serial print of manual_sum , offset_sum
        parts = convfromMCU.split(",")

        if len(parts) != 2:
            print("Bad Teensy response:", convfromMCU)
            return float("nan"), float("nan")

        try:
            state_sum = float(parts[0])
            offset_sum = float(parts[1])
        except ValueError:
            print("Bad numeric Teensy response:", convfromMCU)
            return float("nan"), float("nan")

        return state_sum, offset_sum
    
    def send_patch_batch(self, patch_values_list):
        """
        Similar to send_patch but for testing on real array
        - Receives the entire image patch list, instead of just one 

        What is different:
        - Send all the patches at once and teensy reads patch by patch while they wait in the serial monitor
        """

        if not self.is_open():
            return np.empty((0, 2), dtype=np.float32)

        patchtoMCU = ""
        if (KERNEL_OFFSET == 0.0):
            # make the patch of pixels into a string to send to MCU
            patchtoMCU = "PATCHBATCH," + str(len(patch_values_list)) + "\n"
        
        # this is for when there are negative values in the kernel, requiring another column
        # for the offset calculation. 
        elif (KERNEL_OFFSET > 0.0):
            patchtoMCU = "PATCHBATCHOFFS," + str(len(patch_values_list)) + "\n"

        # write to MCU
        self.ser.write(patchtoMCU.encode("utf-8"))

        # send all patches at once
        for patch_values in patch_values_list:
            line = ",".join(str(v) for v in patch_values) + "\n"
            self.ser.write(line.encode())

        # constantly receive whenever teensy sends in convolved values
        total = len(patch_values_list)
        count = 0
        convresults = []
        while True:
            # receive the convolution scalar result
            convfromMCU = self.ser.readline().decode(errors="replace").strip()

            if (convfromMCU == "BATCH_DONE"):
                break

            if (convfromMCU == ""):
                return np.empty((0, 2), dtype=np.float32)

            # this part parses the teensy serial print of manual_sum , offset_sum
            parts = convfromMCU.split(",")

            if len(parts) != 2:
                print("Bad Teensy response:", convfromMCU)
                return np.empty((0, 2), dtype=np.float32)

            try:
                convresults.append((float(parts[0]), float(parts[1])))
                # to keep track whether program is still running
                count += 1
                if count % 20 == 0 or count == total:
                    print(f"Processed {count}/{total} patches")
            except ValueError:
                print("Bad numeric Teensy response:", convfromMCU)
                return np.empty((0, 2), dtype=np.float32)

        return np.array(convresults, dtype=np.float32)


    # Seperate send patch function for CNN image classification
    # - Logic wise very similar to the other send_patches
    # - patch_values is a 9 element vector that is the output of the previous fcl 1 layer
    # ======================================================
    def send_patch_cnn(self, patch_values):
        if not self.is_open():
            return float("nan"), float("nan") 

        patchtoMCU = "PATCHCNN,"+",".join(str(v) for v in patch_values) + "\n"

        # write to MCU
        self.ser.write(patchtoMCU.encode("utf-8"))

        # receive the dot product result
        dotfromMCU = self.ser.readline().decode(errors="replace").strip()

        if (dotfromMCU == ""):
            return float("nan"), float("nan")

        # this part parses the teensy serial print of col 1 and col 2
        parts = dotfromMCU.split(",")

        if len(parts) != 2:
            print("Bad Teensy response:", dotfromMCU)
            return float("nan"), float("nan")

        try:
            col1_sum = float(parts[0])
            col2_sum = float(parts[1])
        except ValueError:
            print("Bad numeric Teensy response:", dotfromMCU)
            return float("nan"), float("nan")

        return col1_sum, col2_sum
        

# --- PATCH SANITY TESTS ---
# ============================================================
def run_patch_sanity_suite(device, kernel):
    """
    Run a few simple patch tests before attempting a full image sweep.

    """

    examplepatch = np.array([[[1,1,1],[1,1,1],[1,1,1]],
                             [[0,0.5,0],[1,1,1],[0,0.5,0]],
                             [[0,0.5,0],[0,0.5,0],[0,0.5,0]],
                             [[1,0,1],[0,1,0],[1,0,1]],
                             [[0,0,0],[0,0,0],[0,0,0]]
                             ])
    
    for i in range(examplepatch.shape[0]):
        # ignore offset column for now
        results, _ = device.send_patch(quantize_patch(examplepatch[i], MAX_LEVEL))
        # the hardware result is vread*(sum of 1/weights) -> which gives us current
        # * 5100 -> which is the feedback gain
        # * pixel input value (0 to 255) * pulse width (4652)
        print("hardware:", results)
        print("software: ", software_patch_response(examplepatch[i], kernel))
        time.sleep(0.1)  

# --- CALIBRATION ---
# ============================================================

def randomize_calibration_patches(n=20, seed=0):
    """
    Few patches of my own + randomize patches for calibration with hardware pixel to software pixels

    Returns a list of patches to use for calibration
    """
    rng = np.random.default_rng(seed)

    patches = []

    # important anchors
    patches.append(np.zeros((3, 3), dtype=np.float32))
    patches.append(np.ones((3, 3), dtype=np.float32))

    # structured signed-edge anchors
    patches.append(np.array([
        [1, 1, 1],
        [0, 0, 0],
        [0, 0, 0],
    ], dtype=np.float32))

    patches.append(np.array([
        [0, 0, 0],
        [0, 0, 0],
        [1, 1, 1],
    ], dtype=np.float32))

    patches.append(np.array([
        [1, 0, 0],
        [1, 0, 0],
        [1, 0, 0],
    ], dtype=np.float32))

    patches.append(np.array([
        [0, 0, 1],
        [0, 0, 1],
        [0, 0, 1],
    ], dtype=np.float32))

    # random grayscale patches
    for _ in range(n):
        patches.append(rng.random((3, 3), dtype=np.float32))

    return np.array(patches)


#def calibrate_data(device, image_2d, kernel, num_samples=100):
def calibrate_data(device, kernel):
    """
    Collect patch-level software/hardware pairs for calibration.

    Returns 

    """
    # --- we might need a random sampler for calibration --- 
    # examplepatch = np.array([[[1,1,1],[1,1,1],[1,1,1]],
    #                          [[0,0.5,0],[1,1,1],[0,0.5,0]],
    #                          [[0,0.5,0],[0,0.5,0],[0,0.5,0]],
    #                          [[1,0,1],[0,1,0],[1,0,1]],
    #                          [[0,0,0],[0,1,0],[0,0,0]],
    #                          [[0,0,0],[0,0,0],[1,1,1]],
    #                          [[1,1,1],[0,0,0],[0,0,0]],
    #                          [[0,0,0],[0,0,0],[0,0,0]]
    #                          ])

    examplepatch = randomize_calibration_patches()
    software_vals = np.zeros(examplepatch.shape[0])
    hardware_vals = np.zeros(examplepatch.shape[0])
    hardware_offset_vals = np.zeros(examplepatch.shape[0])
    
    for i in range(examplepatch.shape[0]):
        software_vals[i] = software_patch_response(examplepatch[i], kernel)
        hardware_vals[i], hardware_offset_vals[i] = device.send_patch(quantize_patch(examplepatch[i], MAX_LEVEL))
        # print("software_vals:", software_vals)
        # print("hardware_vals:", hardware_vals)

        time.sleep(0.1)

    # m, b = np.polyfit(hardware_vals, software_vals, 1)
    # print(f"slope: {m}")
    # print(f"intercept: {b}")
    
    # this is fitting a * regular col + b * offset col + c
    X = np.column_stack([
    hardware_vals,
    hardware_offset_vals,
    np.ones_like(hardware_vals)
    ])

    a, b, c = np.linalg.lstsq(X, software_vals, rcond=None)[0]

    print(f"slope a: {a}")
    print(f"slope b: {b}")
    print(f"intercept: {c}")

    return a,b,c

def calibrate_data_real_array(device, kernel):
    """
    Collect patch-level software/hardware pairs for calibration.

    TODO:
    - Extract patches from the image
    - Choose a subset of patches (random or first num_samples)
    - For each patch:
      - compute software response
      - quantize patch
      - send patch to hardware
      - store software and hardware outputs
    - Return two numpy arrays:
      software_vals, hardware_vals
    """

    examplepatch = randomize_calibration_patches()
    software_vals = np.zeros(examplepatch.shape[0])
    
    quantize_patch_batch = []
    for i in range(examplepatch.shape[0]):
        software_vals[i] = software_patch_response(examplepatch[i], kernel)
        quantize_patch_batch.append(quantize_patch(examplepatch[i], MAX_LEVEL))
        time.sleep(0.1)
    hardware_vals_list = device.send_patch_batch(quantize_patch_batch)

    # this is fitting a * regular col + b * offset col + c
    X = np.column_stack([
    hardware_vals_list[:,0], # actual column
    hardware_vals_list[:,1], # offset column
    np.ones_like(hardware_vals_list[:,0])
    ])

    a, b, c = np.linalg.lstsq(X, software_vals, rcond=None)[0]

    print(f"slope a: {a}")
    print(f"slope b: {b}")
    print(f"intercept: {c}")

    return a,b,c



def apply_linear_calibration(hardware_pixel, hardware_offset_pixel, a, b, c):
    """
    Apply the fitted linear calibration to a hardware pixel.
    """
    return a * hardware_pixel + b * hardware_offset_pixel + c

# --- CALIBRATION TEST ---
# ============================================================
def run_calibration_test(device, kernel):

    patch_list = np.array([[[1,0.9,1],[0.1,1,1],[1,1,1]],
                             [[0.2,0.5,0],[0,1,1],[0,0.6,0]],
                             [[0,0.5,0.7],[0,0.5,0.2],[0.3,0.5,0]],
                             [[1,0.1,1],[0,1,0],[0,0,1]],
                             [[0.1,0,0.1],[0,0.4,0],[0,0,0]]
                             ])

    a,b,c = calibrate_data(device, kernel)
    # test passes if the two print values are close to each other
    for i in range(5):
        expected_software = software_patch_response(patch_list[i], kernel)
        thecol, offsetcol = device.send_patch(quantize_patch(patch_list[i], MAX_LEVEL))
        calibrated_hardware = apply_linear_calibration(thecol,offsetcol,a,b,c)
        print("software pixel: ", expected_software)
        print("hardware pixel: ", calibrated_hardware)
        print("error: ", np.abs(expected_software - calibrated_hardware))
        time.sleep(0.1)


# ============================================================
# --- IMAGE SWEEP ---
# ============================================================
def process_image(device, image_2d, window_size=3):
    """
    Slide the kernel over the image and send each patch to the hardware.

    - Compute the valid output shape
    - Initialize an output array
    - Loop through every patch position
    - Extract patch
    - Quantize patch
    - Send patch to hardware
    - Store returned value in output[row, col]
    - Print progress every N patches
    - Return the raw hardware output image
    """
    height = image_2d.shape[0] - window_size + 1
    width = image_2d.shape[1] - window_size + 1
    hardware_pixel_image = np.zeros((height, width))

    a,b,c = calibrate_data(device, kernel)

    total = height * width
    count = 0
    for row in range(height):
        for col in range(width):
            patch = image_2d[row:row+window_size, col:col+window_size]
            thecol, offsetcol = device.send_patch(quantize_patch(patch, MAX_LEVEL))
            hardware_pixel_image[row,col] = apply_linear_calibration(thecol,offsetcol,a,b,c)

            # to keep track whether program is still running
            count += 1
            if count % 20 == 0 or count == total:
                print(f"Processed {count}/{total} patches")

    return hardware_pixel_image

def process_image_real(device, image_2d, window_size=3):
    """
    Similar to process_image() above

    What is different:
    - 
    
    """
    height = image_2d.shape[0] - window_size + 1
    width = image_2d.shape[1] - window_size + 1

    a,b,c = calibrate_data_real_array(device, kernel)

    
    patch_batch_list = []
    for row in range(height):
        for col in range(width):
            patch_batch_list.append(quantize_patch(image_2d[row:row+window_size, col:col+window_size], MAX_LEVEL))


    hardware_col_list = device.send_patch_batch(patch_batch_list)
    hardware_pixel_image = apply_linear_calibration(hardware_col_list[:,0],hardware_col_list[:,1],a,b,c).reshape(height, width)

    return hardware_pixel_image

def run_mnist_test(device, kernel, real):

    img, _ = load_mnist_image(1, 20)

    if not real:
        final_pixel_list = process_image(device, img, 3)
    else:
        final_pixel_list = process_image_real(device, img, 3)

    software_raw = software_convolution(img, kernel)

    if KERNEL_OFFSET > 0:
        software_result = software_raw * 255
    else:
        software_result = software_raw * 255 / kernel.sum()

    diff = final_pixel_list - software_result

    mae = np.mean(np.abs(diff))
    mse = np.mean(diff ** 2)
    rmse = np.sqrt(mse)

    print("Mean Absolute Error:", mae)
    print("Mean Squared Error:", mse)
    print("Root MSE:", rmse)

    # --- plotting ---
    if KERNEL_OFFSET > 0:
        software_display = np.abs(software_result)
        hardware_display = np.abs(final_pixel_list)

        cmap = "gray"
        vmin = 0
        vmax = max(np.max(software_display), np.max(hardware_display))
    else:
        software_display = software_result
        hardware_display = final_pixel_list

        cmap = "gray"
        vmin = 0
        vmax = 255

    plt.figure(figsize=(15, 5))

    plt.subplot(1, 3, 1)
    plt.imshow(img, cmap="gray")
    plt.title("Original MNIST")
    plt.axis("off")

    plt.subplot(1, 3, 2)
    plt.imshow(software_display, cmap=cmap, vmin=vmin, vmax=vmax)
    plt.title("Software Convolution")
    plt.axis("off")

    plt.subplot(1, 3, 3)
    plt.imshow(hardware_display, cmap=cmap, vmin=vmin, vmax=vmax)
    plt.title("Crossbar Output")
    plt.axis("off")

    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(5, 5))
    plt.imshow(np.abs(diff), cmap="viridis")
    plt.title("Absolute Difference (0..255 units)")
    plt.colorbar()
    plt.axis("off")
    plt.show()

# Image Classification Tests
# ===========================================================

# The output of fc1 is what goes inside the crossbar array as inputs
# Here we quantize the fc1 ouput based on the act_max we found and froze
# during training. We then scale it to fit the max_level we set, where max
# level here is the max number of PWM per input
def quantize_fcl1_ouput(x, act_max, max_level):
    scale = max(float(act_max) / max_level, 1e-8)
    codes = torch.round(torch.clamp(x,0,float(act_max))/scale)
    return codes.clamp(0, max_level).to(torch.int64)

# This loads the saved QATCNN model from QATCNN.py
def load_qat_save(path="qatcnn_checkpoint.pt"):
    ckpt = torch.load(path, map_location="cpu")
    model = CNN()
    model.load_state_dict(ckpt["state_dict"])
    model.eval()
    return model, ckpt

def run_cnn_resistor(device):
    model,ckpt = load_qat_save()

    class_a = ckpt["class_a"]
    class_b = ckpt["class_b"]
    total = 0
    correct = 0
    incorrect = 0

    testdigits = load_mnist_test_image(class_a, class_b)

    with torch.no_grad():
        for img,labels in testdigits: 
            fcl1_output = model.get_fcl1_output(img) 
            fcl2_input = quantize_fcl1_ouput(fcl1_output, model.act_max, ckpt["max_level"])

            col1_sum, col2_sum = device.send_patch_cnn(fcl2_input.squeeze(0).tolist())

            predicted = class_a if col1_sum > col2_sum else class_b

            if (predicted == labels.item()):
                correct += 1
            else: 
                incorrect += 1

            total += 1

            if total % 100 == 0:
                print(
                    f"Processed {total} images | "
                    f"Accuracy: {100 * correct / total:.2f}% | "
                    f"Incorrect: {incorrect}"
                )

    print("Finished CNN resistor-array test")
    print("Total images:", total)
    print("Correct:", correct)
    print("Incorrect:", incorrect)

    if total > 0:
        print(f"Final accuracy: {100 * correct / total:.2f}%")




# ============================================================
# --- Teensy <-> Python Communication ---
# ============================================================

def read_all_available_lines(device, pause_s=0.1):
    """
    Read and print all currently available Teensy serial output.
    """
    time.sleep(pause_s)

    while device.ser.in_waiting > 0:
        line = device.ser.readline().decode("utf-8", errors="replace").strip()
        if line != "":
            print("Teensy:", line)

def send_command(device, cmd, pause_s=0.2, echo=True):
    """
    Send one text command to Teensy exactly like Serial Monitor would.
    """
    if not device.is_open():
        print("ERROR: serial port is not open")
        return

    device.ser.write((cmd + "\n").encode("utf-8"))
    read_all_available_lines(device, pause_s=pause_s)

def print_pymenu():
    print("=== PYTHON COMMANDS ===")
    print("pymenu   - Show Python commands")
    print("testmenu - Shows the Arduino side test menu")
    print("drain  - Read buffered Teensy output (you can keep pressing)")
    print("sanity - Run Python patch sanity suite")
    print("calibtest - Run Python calibration sanity suite")
    print("mnist - Run full mnist image processing test with pyserial")
    print("mnistreal - Run full mnist image processing test with row10 as baseline subtraction")
    print("cnnres - Run the FC2 layer of the CNN image classification on the resistor array")
    print("quit   - Exit Python script (BUT MAKE SURE TO SWITCH OFF AND TYPE OFF)")
    print()
    print("Anything else is sent directly to Teensy.")

# --- MAIN ---
# ============================================================
def main():
    """
    Suggested experiment order:

    1. Load image
    2. Compute software baseline
    3. Open serial connection
    4. Run patch sanity tests
    5. Collect calibration dataset
    6. Fit linear calibration
    7. Process full image through hardware
    8. Apply calibration
    9. Compute MAE / MSE against software baseline
    10. Display results
    11. Close serial connection

    """

    device = CrossbarSerial(SERIAL_PORT, BAUD_RATE, SERIAL_TIMEOUT_S)

    try:
        device.open()

        # Teensy often resets when serial opens
        time.sleep(2.0)
        read_all_available_lines(device, pause_s=0.5)

        print("Type on to turn on pin pu")
        print("Type quit to exit.\n")

        while True:
            cmd = input("> ").strip()

            if cmd.lower() == "quit":
                break

            if cmd == "":
                continue

            if cmd.lower() == "drain":
                read_all_available_lines(device, pause_s=0.1)
                continue

            if cmd.lower() == "pymenu":
                print_pymenu()
                continue

            if cmd.lower() == "sanity":
                print("Running patch sanity test")
                run_patch_sanity_suite(device, kernel)
                print_pymenu()
                continue

            if cmd.lower() == "calibtest":
                print("Running hardware pixel to software pixel calibration test")
                run_calibration_test(device, kernel)
                print_pymenu()
                continue

            if cmd.lower() == "mnist":
                print("Running full mnist image processing test")
                run_mnist_test(device, kernel, False)
                print_pymenu()
                continue
            if cmd.lower() == "mnistreal":
                print("Running full mnist image processing test with row10 baseline subtraction")
                run_mnist_test(device, kernel, True)
                print_pymenu()
                continue

            if cmd.lower() == "cnnres":
                print("Running FC2 layer of the CNN image classification")
                run_cnn_resistor(device)
                print_pymenu()
                continue

            send_command(device, cmd)
        

    finally:
        device.close()
        print("Serial connection closed.")



if __name__ == "__main__":
    main()
