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
from pathlib import Path
from PIL import Image

from QATCNN import CNN

import threading

# --- CONFIG ---
# ============================================================
SERIAL_PORT = "COM7"
BAUD_RATE = 115200
SERIAL_TIMEOUT_S = 5

IMAGE_SIZE = 20

# match this with teensy's encoding
MAX_LEVEL = 128

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)
CNN_CLASS0_PATH = DATA_DIR / "cnn" / "cnn_class0.npz"
CNN_CLASS1_PATH = DATA_DIR / "cnn" / "cnn_class1.npz"
SHIFTED_PASS_PATH = DATA_DIR / "imgproc" / "shifted_pass.npz"
OFFSET_PASS_PATH = DATA_DIR / "imgproc" / "offset_pass.npz"


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

# kernel = 0.7*np.array([
#     [3.5,4.5,3.5],
#     [4.5, 5.5, 4.5],
#     [3.5, 4.5, 3.5]
# ], dtype=np.float32)

# kernel = 0.7*np.array([
#     [2,3],
#     [4,4],
#     [3,2]
# ], dtype=np.float32)

# kernel = 0.7*np.array([
#     [-1,-1],
#     [0,0],
#     [1,1]
# ], dtype=np.float32)
# kernel = 0.7*np.array([
#     [-1,0,1],
#     [-1,0,1]
# ], dtype=np.float32)

# kernel = np.array([
#     [3.,3.3,3.],
#     [3.3, 4.3, 3.3],
#     [3., 3.3, 3.]
# ], dtype=np.float32)

KH, KW = kernel.shape
KERNEL_SIZE = KH * KW

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

def load_mnist_validation_images(validation_indices):
    transform = transforms.ToTensor()

    dataset = torchvision.datasets.MNIST(
        root="data",
        train=True,
        download=False,
        transform=transform,
    )

    subset = torch.utils.data.Subset(
        dataset,
        np.asarray(validation_indices, dtype=np.int64).tolist(),
    )

    return torch.utils.data.DataLoader(
        subset,
        batch_size=1,
        shuffle=False,
        num_workers=0,
    )

def load_scenery_image(filename="umicheecs.jpg", image_size=100):
    image_path = Path(__file__).resolve().parent / "data" / filename

    transform = transforms.Compose([
        transforms.Grayscale(num_output_channels=1),
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
    ])

    with Image.open(image_path) as image:
        image_tensor = transform(image)

    return image_tensor.squeeze(0).numpy()

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
        self.ser = serial.Serial(self.port, self.baud_rate, timeout=self.timeout_s, write_timeout=10)
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
    
    # def send_patch_batch(self, patch_values_list):
    #     """
    #     Similar to send_patch but for testing on real array
    #     - Receives the entire image patch list, instead of just one 

    #     What is different:
    #     - Send all the patches at once and teensy reads patch by patch while they wait in the serial monitor
    #     """

    #     if not self.is_open():
    #         return np.empty((0, 2), dtype=np.float32)

    #     patchtoMCU = ""
    #     if (KERNEL_OFFSET == 0.0):
    #         # make the patch of pixels into a string to send to MCU
    #         patchtoMCU = "PATCHBATCH," + str(len(patch_values_list)) + "\n"
        
    #     # this is for when there are negative values in the kernel, requiring another column
    #     # for the offset calculation. 
    #     elif (KERNEL_OFFSET > 0.0):
    #         patchtoMCU = "PATCHBATCHOFFS," + str(len(patch_values_list)) + "\n"

    #     # write to MCU
    #     self.ser.write_timeout = 10
    #     total = len(patch_values_list)


    #     try:
    #         self.ser.write(patchtoMCU.encode("utf-8"))
    #     except serial.SerialTimeoutException:
    #         print("WRITE STALLED while sending batch header.")
    #         return np.empty((0, 2), dtype=np.float32)

    #     # send all patches at once
    #     send_start = time.monotonic()
    #     last_report = send_start
    #     for i, patch_values in enumerate(patch_values_list):
    #         line = ",".join(str(v) for v in patch_values) + "\n"

    #         try:
    #             self.ser.write(line.encode("utf-8"))
    #         except serial.SerialTimeoutException:
    #             print(
    #                 f"WRITE STALLED while sending "
    #                 f"patch {i + 1}/{total}."
    #             )
    #             return np.empty((0, 2), dtype=np.float32)

    #         now = time.monotonic()

    #         if now - last_report >= 20.0 or i + 1 == total:
    #             elapsed = now - send_start
    #             print(
    #                 f"Queued {i + 1}/{total} patches "
    #                 f"({elapsed:.1f} seconds elapsed)."
    #             )
    #             last_report = now

    #     print("All patches queued. Now reading Teensy results.")

    #     # constantly receive whenever teensy sends in convolved values
    #     count = 0
    #     convresults = []
    #     receive_start = time.monotonic()

    #     while True:
    #         # receive the convolution scalar result
    #         convfromMCU = self.ser.readline().decode(errors="replace").strip()

    #         if (convfromMCU == "BATCH_DONE"):
    #             break

    #         if (convfromMCU == ""):
    #             print(
    #             f"READ TIMEOUT after receiving "
    #             f"{count}/{total} results."
    #             )
    #             return np.empty((0, 2), dtype=np.float32)

    #         # this part parses the teensy serial print of manual_sum , offset_sum
    #         parts = convfromMCU.split(",")

    #         if len(parts) != 2:
    #             print("Bad Teensy response:", convfromMCU)
    #             return np.empty((0, 2), dtype=np.float32)

    #         try:
    #             convresults.append((float(parts[0]), float(parts[1])))
    #             # to keep track whether program is still running
    #             count += 1

    #         except ValueError:
    #             print("Bad numeric Teensy response:", convfromMCU)
    #             return np.empty((0, 2), dtype=np.float32)
            
    #         if count % 20 == 0 or count == total:
    #             elapsed = time.monotonic() - receive_start
    #             print(
    #                 f"Received {count}/{total} results "
    #                 f"({elapsed:.1f} seconds reading)."
    #             )

    #     return np.array(convresults, dtype=np.float32)


    # multithreaded version of send_patch_batch which not only speeds up the communication
    # process but also prevent usb serial buffer from filling up in the case our patch batch 
    # exceeds the maximum it can hold at a time. 

    # read has its own thread and the main threa is the same as the write thread.
    # ===========================================================================================
    def send_patch_batch(self, patch_values_list, use_offset_col=False):
        """
        Send patches continuously while a reader thread continuously collects
        Teensy results.
        """

        if not self.is_open():
            return np.empty((0, 2), dtype=np.float32)
        
        self.ser.reset_input_buffer()

        total = len(patch_values_list)

        if not use_offset_col:
            command = f"PATCHBATCH,{total}\n"
        else:
            command = f"PATCHBATCHOFFS,{total}\n"

        self.ser.write_timeout = None

        # this is the shared array for read and write. 
        convresults = []
        reader_state = {
            "error": None,
            "batch_done": False,
        }

        # Only this thread reads from serial during the batch.
        def read_results():
            try:
                while True:
                    # readline essentially working as a block for read thread to wait until there
                    # is something to read on the serial sent from the teensy.
                    # So as write (main) thread queues up patches to teensy, teensy will continuously
                    # write to python and read thread will simutaneously read as the write thread writes.
                    response = self.ser.readline().decode(
                        errors="replace"
                    ).strip()

                    if response == "":
                        reader_state["error"] = (
                            f"Read timeout after receiving "
                            f"{len(convresults)}/{total} results."
                        )
                        return

                    if response == "BATCH_DONE":
                        reader_state["batch_done"] = True
                        return

                    parts = response.split(",")

                    if len(parts) != 2:
                        reader_state["error"] = (
                            f"Bad Teensy response: {response}"
                        )
                        return

                    try:
                        state_sum = float(parts[0])
                        offset_sum = float(parts[1])
                    except ValueError:
                        reader_state["error"] = (
                            f"Bad numeric Teensy response: {response}"
                        )
                        return

                    convresults.append((state_sum, offset_sum))

                    count = len(convresults)

                    if count % 50 == 0 or count == total:
                        print(f"Received {count}/{total} results")

            except Exception as exc:
                reader_state["error"] = (
                    f"Reader thread failed: {exc}"
                )

        # Send the batch header first. Teensy then waits for patch lines.
        try:
            self.ser.write(command.encode("utf-8"))
        except serial.SerialTimeoutException:
            print("Timed out sending batch header.")
            return np.empty((0, 2), dtype=np.float32)

        # create the read thread and start it. 
        reader_thread = threading.Thread(
            target=read_results,
            daemon=True,
        )
        reader_thread.start()

        send_start = time.monotonic()
        last_report = send_start

        try:
            # write thread. 
            for i, patch_values in enumerate(patch_values_list):
                if reader_state["error"] is not None:
                    break

                line = ",".join(
                    str(v) for v in patch_values
                ) + "\n"

                self.ser.write(line.encode("utf-8"))

                now = time.monotonic()

                if now - last_report >= 10.0 or i + 1 == total:
                    print(
                        f"Sent {i + 1}/{total} patches "
                        f"({now - send_start:.1f} seconds)"
                    )
                    last_report = now

        except serial.SerialTimeoutException:
            reader_state["error"] = "Serial write timed out."

        except KeyboardInterrupt:
            print("Batch interrupted.")

            # This only works after adding ABORT handling to Arduino.
            try:
                self.ser.write(b"ABORT\n")
            except Exception:
                pass

            raise

        # Reader exits after BATCH_DONE or a read timeout/error.
        # This is here because write thread will usually finish first and read thread must
        # keep going until it finishes. 
        reader_thread.join()

        if reader_state["error"] is not None:
            print(reader_state["error"])
            return np.empty((0, 2), dtype=np.float32)

        if not reader_state["batch_done"]:
            print("Batch ended without BATCH_DONE.")
            return np.empty((0, 2), dtype=np.float32)

        if len(convresults) != total:
            print(
                f"Batch count mismatch: expected {total}, "
                f"received {len(convresults)}."
            )
            return np.empty((0, 2), dtype=np.float32)

        print("Batch completed successfully.")

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
        
# cnn patch batch for one col only
def send_patch_cnn_onecol(self, patch_values):
    if len(patch_values) != 6:
        raise ValueError("CNN FC2 input must contain 6 values.")

    command = (
        "PATCHCNNONE,"
        + ",".join(str(int(value)) for value in patch_values)
        + "\n"
    )

    self.ser.write(command.encode("utf-8"))

    response = self.ser.readline().decode(
        errors="replace"
    ).strip()

    if response == "":
        raise RuntimeError("Timed out waiting for CNN score.")

    try:
        return float(response)
    except ValueError as exc:
        raise RuntimeError(
            f"Bad CNN Teensy response: {response}"
        ) from exc

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
    patches.append(np.zeros(kernel.shape, dtype=np.float32))
    patches.append(np.ones(kernel.shape, dtype=np.float32))

    # structured signed-edge anchors
    patches.append(np.array([
        [1, 1, 1],
        [0, 0, 0],
        [0, 0, 0],
    ], dtype=np.float32))
    # patches.append(np.array([
    #     [1, 1],
    #     [0, 0],
    #     [0, 0],
    # ], dtype=np.float32))
    patches.append(np.array([
        [0, 0, 0],
        [0, 0, 0],
        [1, 1, 1],
    ], dtype=np.float32))
    # patches.append(np.array([
    #     [0, 0],
    #     [0, 0],
    #     [1, 1],
    # ], dtype=np.float32))

    patches.append(np.array([
        [1, 0, 0],
        [1, 0, 0],
        [1, 0, 0],
    ], dtype=np.float32))
    # patches.append(np.array([
    #     [1, 0],
    #     [1, 0],
    #     [1, 0],
    # ], dtype=np.float32))

    patches.append(np.array([
        [0, 0, 1],
        [0, 0, 1],
        [0, 0, 1],
    ], dtype=np.float32))
    # patches.append(np.array([
    #     [0, 1],
    #     [0, 1],
    #     [0, 1],
    # ], dtype=np.float32))
    # One active corner
    patches.append(np.array([
        [1, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
    ], dtype=np.float32))
    # patches.append(np.array([
    #     [1, 0],
    #     [0, 0],
    #     [0, 0],
    # ], dtype=np.float32))

    # One active center
    patches.append(np.array([
        [0, 0, 0],
        [0, 1, 0],
        [0, 0, 0],
    ], dtype=np.float32))
    # patches.append(np.array([
    #     [0, 0],
    #     [0, 1],
    #     [0, 0],
    # ], dtype=np.float32))


    # Two active pixels
    patches.append(np.array([
        [1, 0, 0],
        [0, 0, 0],
        [0, 0, 1],
    ], dtype=np.float32))
    # patches.append(np.array([
    #     [1, 0],
    #     [0, 0],
    #     [0, 1],
    # ], dtype=np.float32))

    # Four active corners
    patches.append(np.array([
        [1, 0, 1],
        [0, 0, 0],
        [1, 0, 1],
    ], dtype=np.float32))
    # patches.append(np.array([
    #     [1, 1],
    #     [0, 0],
    #     [1, 1],
    # ], dtype=np.float32))

    # Cross pattern
    patches.append(np.array([
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0],
    ], dtype=np.float32))
    # patches.append(np.array([
    #     [1, 1],
    #     [1, 0],
    #     [1, 1],
    # ], dtype=np.float32))

    # Checkerboard pattern
    patches.append(np.array([
        [1, 0, 1],
        [0, 1, 0],
        [1, 0, 1],
    ], dtype=np.float32))

    if (kernel.shape == (2,3)):
        patches = [
        patch.T if patch.shape == (3,2)  else patch
        for patch in patches
        ]

    # random grayscale patches
    for _ in range(n):
        patches.append(rng.random(kernel.shape, dtype=np.float32))

    rng = np.random.default_rng(17)

    # One-hot patches at two intensities
    for level in [0.5, 1.0]:
        for position in range(KERNEL_SIZE):
            patch = np.zeros(KERNEL_SIZE, dtype=np.float32)
            patch[position] = level
            patches.append(patch.reshape(kernel.shape))

    # Four examples for every active-pixel count
    levels = np.array([0.25, 0.5, 0.75, 1.0], dtype=np.float32)

    for active_count in range(2, KERNEL_SIZE):
        for _ in range(4):
            patch = np.zeros(KERNEL_SIZE, dtype=np.float32)
            positions = rng.choice(KERNEL_SIZE, active_count, replace=False)
            patch[positions] = rng.choice(levels, active_count)
            patches.append(patch.reshape(kernel.shape))

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
        # fixed from 
        # software_vals[i] = software_patch_response(examplepatch[i], kernel)
        # quantize_patch_batch.append(quantize_patch(examplepatch[i], MAX_LEVEL)) 
        # because we want apples to apples comparison

        q_flat = quantize_patch(examplepatch[i], MAX_LEVEL)
        q_patch = np.array(q_flat).reshape(kernel.shape) / MAX_LEVEL

        software_vals[i] = software_patch_response(q_patch, kernel)
        quantize_patch_batch.append(q_flat)
        time.sleep(0.1)
    hardware_vals_list = device.send_patch_batch(quantize_patch_batch)

    # print("software calibration values:")
    # print(software_vals)

    # print("hardware calibration values:")
    # print(hardware_vals_list[:, 0])

    # print("zero sample:")
    # print("software =", software_vals[0])
    # print("hardware =", hardware_vals_list[0, 0])

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


    # this is regress through zero (forced zero line of fit.)
    hardware_main = hardware_vals_list[:, 0]

    # denom = np.dot(hardware_main, hardware_main)
    # if denom == 0:
    #     a_zero = 0.0
    # else:
    #     a_zero = np.dot(hardware_main, software_vals) / denom

    # print("forced-zero slope:", a_zero)



    # seeing which calibration patches are bad.
    # pred_zero = a * hardware_main + c
    # #pred_zero = a_zero * hardware_main

    # residual_zero = software_vals - pred_zero

    # bad_idx = np.argsort(np.abs(residual_zero))[-5:]

    # print("Worst forced-zero calibration residuals:")
    # for idx in bad_idx:
    #     print("idx:", idx)
    #     print("software:", software_vals[idx])
    #     print("hardware:", hardware_main[idx])
    #     print("pred_zero:", pred_zero[idx])
    #     print("residual:", residual_zero[idx])
    #     print("patch:")
    #     print(examplepatch[idx])

    # calibration line fit plot

    x_line = np.linspace(np.min(hardware_main), np.max(hardware_main), 200)

    y_free = a * x_line + c
    #y_zero = a_zero * x_line

    # plt.plot(
    #     x_line,
    #     y_zero,
    #     color="green",
    #     linewidth=2,
    #     linestyle="--",
    #     label=f"Forced-zero: y={a_zero:.3e}x"
    # )


    # plt.xlabel("Hardware raw value")
    # plt.ylabel("Software pixel value")
    # plt.title("Hardware vs Software Calibration")
    # plt.legend()
    # plt.grid(True, alpha=0.3)
    # plt.tight_layout()
    # plt.show()

    active_counts = np.array([
        np.count_nonzero(np.asarray(q_flat))
        for q_flat in quantize_patch_batch
    ])

    plt.figure(figsize=(8, 6))

    scatter = plt.scatter(
        hardware_main,
        software_vals,
        c=active_counts,
        cmap="viridis",
        s=60
    )

    plt.plot(x_line, y_free, color="red", label="Linear fit")

    plt.colorbar(scatter, label="Number of active pixels", shrink=0.5, fraction=0.1, pad=0.04)
    plt.xlabel("Hardware raw value")
    plt.ylabel("Software pixel value")
    plt.title("Calibration Colored by Active-Pixel Count")
    plt.legend()
    plt.grid(True)
    plt.show()
    #return a_zero,0.0,0.0
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

def process_image_real(device, image_2d):
    """
    Similar to process_image() above

    What is different:
    - 
    
    """

    # one_hot_patches = []

    # for i in range(9):
    #     patch = np.zeros((3, 3), dtype=np.float32)
    #     patch.flat[i] = 1.0
    #     one_hot_patches.append(quantize_patch(patch, MAX_LEVEL))

    # results = device.send_patch_batch(one_hot_patches)

    # print("=== One-hot row responses ===")
    # for i, result in enumerate(results[:, 0]):
    #     physical_row = i + 3 if i < 4 else i + 4
    #     print(f"Patch position {i}, physical row {physical_row}: {result}")

    # patterns = [
    #     np.array([[1,1,1],[0,0,0],[0,0,0]], dtype=np.float32),
    #     np.array([[0,0,0],[0,0,0],[1,1,1]], dtype=np.float32),
    #     np.ones((3,3), dtype=np.float32),
    # ]

    # batch = []

    # for pattern in patterns:
    #     for _ in range(10):
    #         batch.append(quantize_patch(pattern, MAX_LEVEL))

    # results = device.send_patch_batch(batch)

    # for i, name in enumerate(["top", "bottom", "all"]):
    #     values = results[i * 10:(i + 1) * 10, 0]
    #     print(name, values)
    #     print("mean:", np.mean(values))

    height = image_2d.shape[0] - KH + 1
    width = image_2d.shape[1] - KW + 1

    a,b,c = calibrate_data_real_array(device, kernel)

    
    patch_batch_list = []
    for row in range(height):
        for col in range(width):
            patch_batch_list.append(quantize_patch(image_2d[row:row+KH, col:col+KW], MAX_LEVEL))


    hardware_col_list = device.send_patch_batch(patch_batch_list)
    hardware_pixel_image = apply_linear_calibration(hardware_col_list[:,0],hardware_col_list[:,1],a,b,c).reshape(height, width)

    return hardware_pixel_image

def img_proc_metrics(img, final_pixel_list, software_result):
    diff = final_pixel_list - software_result

    mae = np.mean(np.abs(diff))
    mse = np.mean(diff ** 2)
    rmse = np.sqrt(mse)

    print("Mean Absolute Error:", mae)
    print("Mean Squared Error:", mse)
    print("Root MSE:", rmse)

    # Measures whether hardware preserves the overall spatial pattern.
    overall_corr = np.corrcoef(
        software_result.ravel(),
        final_pixel_list.ravel()
    )[0, 1]

    # Separate meaningful software signal from background.
    signal_threshold = 5.0
    signal_mask = software_result > signal_threshold
    background_mask = ~signal_mask

    if np.count_nonzero(signal_mask) > 1:
        signal_corr = np.corrcoef(
            software_result[signal_mask],
            final_pixel_list[signal_mask]
        )[0, 1]

        signal_mae = np.mean(
            np.abs(final_pixel_list[signal_mask] - software_result[signal_mask])
        )
    else:
        signal_corr = float("nan")
        signal_mae = float("nan")

    if np.any(background_mask):
        background_mae = np.mean(
            np.abs(final_pixel_list[background_mask] - software_result[background_mask])
        )
    else:
        background_mae = float("nan")

    print("Overall Correlation:", overall_corr)
    print("Signal Correlation:", signal_corr)
    print("Signal MAE:", signal_mae)
    print("Background MAE:", background_mae)

    # --- plotting ---
    if KERNEL_OFFSET > 0:
        software_display = software_result
        hardware_display = final_pixel_list

        limit = max(
            np.max(np.abs(software_display)),
            np.max(np.abs(hardware_display)),
        )

        cmap = "gray"
        vmin = -limit
        vmax = limit
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

    plt.figure(figsize=(10, 5))

    plt.subplot(1, 2, 1)
    d1 = plt.imshow(diff, cmap="coolwarm", vmin=-np.max(np.abs(diff)), vmax=np.max(np.abs(diff)))
    plt.title("Signed Difference")
    plt.colorbar(d1, shrink=0.5, fraction=0.1, pad=0.04)
    plt.axis("off")

    plt.subplot(1, 2, 2)
    d2 = plt.imshow(np.abs(diff), cmap="viridis")
    plt.title("Absolute Difference")
    plt.colorbar(d2, shrink=0.5, fraction=0.1, pad=0.04)
    plt.axis("off")

    plt.tight_layout()
    plt.show()

def run_mnist_test(device, kernel, mode):


    if mode == "resistor":
        img, _ = load_mnist_image(4, 20)
        final_pixel_list = process_image(device, img, 3)
    elif mode == "real":
        img, _ = load_mnist_image(4, 20)
        final_pixel_list = process_image_real(device, img)
    elif mode == "scenery":
        img = load_scenery_image(filename="bell.jpeg", image_size=100)
        final_pixel_list = process_image_real(device, img)

    software_input = (
        np.round(np.clip(img, 0.0, 1.0) * MAX_LEVEL)
        / MAX_LEVEL
    )
    software_raw = software_convolution(software_input, kernel)

    if KERNEL_OFFSET > 0:
        software_result = software_raw * 255
    else:
        software_result = software_raw * 255 / kernel.sum()

        # --- Save final mnistreal arrays, metrics, and SVG panels ---
    diff = final_pixel_list - software_result

    mae = np.mean(np.abs(diff))
    mse = np.mean(diff ** 2)
    rmse = np.sqrt(mse)

    signal_threshold = 5.0
    signal_mask = np.abs(software_result) > signal_threshold
    background_mask = ~signal_mask

    overall_corr = np.corrcoef(
        software_result.ravel(),
        final_pixel_list.ravel(),
    )[0, 1]

    signal_corr = np.corrcoef(
        software_result[signal_mask],
        final_pixel_list[signal_mask],
    )[0, 1]

    signal_mae = np.mean(
        np.abs(final_pixel_list[signal_mask] - software_result[signal_mask])
    )

    background_mae = np.mean(
        np.abs(final_pixel_list[background_mask] - software_result[background_mask])
    )

    # Use signed scale for signed kernels; standard 0..255 for blur kernels.
    if KERNEL_OFFSET > 0:
        response_limit = max(
            float(np.max(np.abs(software_result))),
            float(np.max(np.abs(final_pixel_list))),
            1e-12,
        )
        response_vmin = -response_limit
        response_vmax = response_limit
    else:
        response_vmin = 0
        response_vmax = 255

    diff_limit = max(float(np.max(np.abs(diff))), 1e-12)

    def save_svg_panel(data, title, filename, cmap, vmin, vmax, colorbar_label=None):
        fig, ax = plt.subplots(figsize=(5, 5))

        im = ax.imshow(
            data,
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
            interpolation="nearest",
        )

        ax.set_title(title)
        ax.axis("off")

        if colorbar_label is not None:
            cbar = fig.colorbar(im, ax=ax, shrink=0.8)
            cbar.set_label(colorbar_label)

        fig.savefig(
            DATA_DIR / filename,
            format="svg",
            bbox_inches="tight",
        )
        plt.close(fig)

    # Keep filenames separate for MNIST and scenery runs.
    result_name = "mnistreal" if mode == "real" else f"{mode}_real"

    save_svg_panel(
        img,
        "Original Input",
        f"{result_name}_original.svg",
        "gray",
        0,
        1,
    )

    save_svg_panel(
        software_result,
        "Software Convolution",
        f"{result_name}_software.svg",
        "gray",
        response_vmin,
        response_vmax,
        "Response",
    )

    save_svg_panel(
        final_pixel_list,
        "Crossbar Output",
        f"{result_name}_hardware.svg",
        "gray",
        response_vmin,
        response_vmax,
        "Response",
    )

    save_svg_panel(
        diff,
        "Signed Difference: Hardware - Software",
        f"{result_name}_signed_difference.svg",
        "coolwarm",
        -diff_limit,
        diff_limit,
        "Difference",
    )

    save_svg_panel(
        np.abs(diff),
        "Absolute Difference",
        f"{result_name}_absolute_difference.svg",
        "viridis",
        0,
        diff_limit,
        "Absolute error",
    )

    np.savez(
        DATA_DIR / f"{result_name}_results.npz",

        image=img.astype(np.float32),
        kernel=kernel.astype(np.float32),
        max_level=np.array(MAX_LEVEL, dtype=np.int32),

        software_result=software_result.astype(np.float32),
        hardware_result=final_pixel_list.astype(np.float32),
        signed_difference=diff.astype(np.float32),
        absolute_difference=np.abs(diff).astype(np.float32),

        mae=np.array(mae, dtype=np.float64),
        mse=np.array(mse, dtype=np.float64),
        rmse=np.array(rmse, dtype=np.float64),
        overall_correlation=np.array(overall_corr, dtype=np.float64),
        signal_correlation=np.array(signal_corr, dtype=np.float64),
        signal_mae=np.array(signal_mae, dtype=np.float64),
        background_mae=np.array(background_mae, dtype=np.float64),
    )

    print(f"Saved {result_name} SVG panels and NPZ data to:")
    print(DATA_DIR)

    img_proc_metrics(img, final_pixel_list, software_result)


def run_mnist_one_col(device, shift_or_off, mode):

    if mode == "mnist":
        img, _ = load_mnist_image(4,20)
    elif mode == "scenery":
        img = load_scenery_image(filename="bell.jpeg", image_size=100)
        
    
    height = img.shape[0] - KH + 1
    width = img.shape[1] - KW + 1

    # in regular mnistreal, we did calibrate real array here
    # but not here because we need to fit a * shifted + b * offset + c seperately
    # so we do it later at the end when we input the calibration patches for shifted
    # and offset weights
    # after that we use those a,b,c values for real mnist inputs calibration

    image_inputs = []
    for row in range(height):
        for col in range(width):
            image_inputs.append(quantize_patch(img[row:row+KH, col:col+KW], MAX_LEVEL))
    
    image_inputs = np.asarray(image_inputs, dtype=np.uint8)

    if shift_or_off == "shift":
        calibration_patches = randomize_calibration_patches()

        calibration_inputs= []

        for patch in calibration_patches:
            calibration_inputs.append(quantize_patch(patch, MAX_LEVEL))

        calibration_inputs = np.asarray(calibration_inputs, dtype=np.uint8)

        save_path = SHIFTED_PASS_PATH

    else:
        if not SHIFTED_PASS_PATH.exists():
            raise FileNotFoundError(
                "Run mnistshift first. shifted_pass.npz is missing."
            )
        
        shift = np.load(SHIFTED_PASS_PATH, allow_pickle=False)

        calibration_inputs = shift["calibration_inputs"]
        image_inputs = shift["image_inputs"]

        save_path = OFFSET_PASS_PATH
    
    print("Sending calibration patches")
    calibration_results = device.send_patch_batch(calibration_inputs, use_offset_col=False)
    
    print("Sending image patches")
    image_results = device.send_patch_batch(image_inputs, use_offset_col=False)

    np.savez(
        save_path,
        image=img.astype(np.float32),
        image_shape=np.array([height, width], dtype=np.int32),
        calibration_inputs=calibration_inputs,
        calibration_raw=calibration_results[:, 0],
        image_inputs=image_inputs,
        image_raw=image_results[:, 0],
        max_level=np.array(MAX_LEVEL, dtype=np.int32),
    )

    print(f"Saved data to:")
    print(save_path)

def combine_mnist():

    shifted = np.load(SHIFTED_PASS_PATH, allow_pickle=False)
    offset = np.load(OFFSET_PASS_PATH, allow_pickle=False)

    calibration_inputs = shifted["calibration_inputs"]

    software_cal = []

    for q_flat in calibration_inputs:
        q_patch = (q_flat.astype(np.float32).reshape(kernel.shape)/MAX_LEVEL)

        software_cal.append(software_patch_response(q_patch, kernel))
    
    software_cal = np.asarray(software_cal, dtype=np.float64)

    h_shift_cal = shifted["calibration_raw"].astype(np.float64)
    h_offset_cal = offset["calibration_raw"].astype(np.float64)

    # One joint linear fit:
    # software_signed = a * shifted_hardware
    #                 + b * offset_hardware
    #                 + c
    X = np.column_stack([
        h_shift_cal,
        h_offset_cal,
        np.ones_like(h_shift_cal),
    ])

    a, b, c = np.linalg.lstsq(
        X,
        software_cal,
        rcond=None,
    )[0]

    print("shifted coefficient a:", a)
    print("offset coefficient b:", b)
    print("intercept c:", c)

    hardware_flat = (
        a * shifted["image_raw"].astype(np.float64)
        + b * offset["image_raw"].astype(np.float64)
        + c
    )

    height, width = shifted["image_shape"]
    hardware_result = hardware_flat.reshape(
        int(height),
        int(width),
    )

    img = shifted["image"]

    # Signed reference result.
    software_input = (
    np.round(np.clip(img, 0.0, 1.0) * MAX_LEVEL)
    / MAX_LEVEL
    )
    software_result = software_convolution(
        software_input,
        kernel
    ) * 255.0

        # --- Save final signed-edge results and individual SVG panels ---
    diff = hardware_result - software_result

    signed_limit = max(
        float(np.max(np.abs(software_result))),
        float(np.max(np.abs(hardware_result))),
        1e-12,
    )
    diff_limit = max(float(np.max(np.abs(diff))), 1e-12)

    def save_panel(data, title, filename, cmap, vmin, vmax, colorbar_label=None):
        fig, ax = plt.subplots(figsize=(5, 5))
        im = ax.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
        ax.set_title(title)
        ax.axis("off")

        if colorbar_label is not None:
            cbar = fig.colorbar(im, ax=ax, shrink=0.8)
            cbar.set_label(colorbar_label)

        fig.savefig(
            DATA_DIR / filename,
            format="svg",
            bbox_inches="tight",
        )
        plt.close(fig)

    # Original input and signed software/hardware outputs.
    save_panel(
        img,
        "Original Input",
        "edge_original.svg",
        "gray",
        0,
        1,
    )

    save_panel(
        software_result,
        "Software Signed Edge Response",
        "edge_software_signed.svg",
        "gray",
        -signed_limit,
        signed_limit,
        "Signed response",
    )

    save_panel(
        hardware_result,
        "Crossbar Signed Edge Response",
        "edge_hardware_signed.svg",
        "gray",
        -signed_limit,
        signed_limit,
        "Signed response",
    )

    save_panel(
        diff,
        "Signed Difference: Hardware - Software",
        "edge_signed_difference.svg",
        "coolwarm",
        -diff_limit,
        diff_limit,
        "Difference",
    )

    save_panel(
        np.abs(diff),
        "Absolute Difference",
        "edge_absolute_difference.svg",
        "viridis",
        0,
        diff_limit,
        "Absolute error",
    )

    # Save every numerical quantity needed to reproduce metrics and figures.
    mae = np.mean(np.abs(diff))
    mse = np.mean(diff ** 2)
    rmse = np.sqrt(mse)

    signal_threshold = 5.0
    signal_mask = np.abs(software_result) > signal_threshold
    background_mask = ~signal_mask

    overall_corr = np.corrcoef(
        software_result.ravel(),
        hardware_result.ravel(),
    )[0, 1]

    signal_corr = np.corrcoef(
        software_result[signal_mask],
        hardware_result[signal_mask],
    )[0, 1]

    signal_mae = np.mean(
        np.abs(hardware_result[signal_mask] - software_result[signal_mask])
    )

    background_mae = np.mean(
        np.abs(hardware_result[background_mask] - software_result[background_mask])
    )

    np.savez(
        DATA_DIR / "negative_kernel_combined_results.npz",

        # Inputs and kernel
        image=img.astype(np.float32),
        kernel=kernel.astype(np.float32),
        max_level=np.array(MAX_LEVEL, dtype=np.int32),

        # Raw hardware outputs from both physical passes
        shifted_calibration_raw=h_shift_cal.astype(np.float32),
        offset_calibration_raw=h_offset_cal.astype(np.float32),
        shifted_image_raw=shifted["image_raw"].astype(np.float32),
        offset_image_raw=offset["image_raw"].astype(np.float32),

        # Joint calibration
        coefficient_a=np.array(a, dtype=np.float64),
        coefficient_b=np.array(b, dtype=np.float64),
        intercept_c=np.array(c, dtype=np.float64),

        # Final reconstructed arrays
        software_result=software_result.astype(np.float32),
        hardware_result=hardware_result.astype(np.float32),
        signed_difference=diff.astype(np.float32),
        absolute_difference=np.abs(diff).astype(np.float32),

        # Metrics
        mae=np.array(mae, dtype=np.float64),
        mse=np.array(mse, dtype=np.float64),
        rmse=np.array(rmse, dtype=np.float64),
        overall_correlation=np.array(overall_corr, dtype=np.float64),
        signal_correlation=np.array(signal_corr, dtype=np.float64),
        signal_mae=np.array(signal_mae, dtype=np.float64),
        background_mae=np.array(background_mae, dtype=np.float64),
    )

    print("Saved SVG panels and final NPZ data to:")
    print(DATA_DIR)

    img_proc_metrics(img, hardware_result, software_result)


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
    ckpt = torch.load(path, map_location="cpu", weights_only=False)
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

    start_time = time.perf_counter()

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

    end_time = time.perf_counter()

    print("Finished CNN resistor-array test")
    print("Total images:", total)
    print("Correct:", correct)
    print("Incorrect:", incorrect)
    print("Time elapsed:", end_time - start_time)

    if total > 0:
        print(f"Final accuracy: {100 * correct / total:.2f}%")

# CNN image classification on the real array
def run_cnn_real_array(device):
    model,ckpt = load_qat_save()

    class_a = ckpt["class_a"]
    class_b = ckpt["class_b"]
    total = 0
    correct = 0
    incorrect = 0

    testdigits = load_mnist_test_image(class_a, class_b)

    # send the weights from QATCNN to teensy for it to set the conductance
    weights = ckpt["conductance_targets"].flatten()
    cmd = "WEIGHTS," + ",".join(f"{w:.12g}" for w in weights) + "\n"
    device.ser.write(cmd.encode("utf-8"))
    while True:
        line = device.ser.readline().decode(errors="replace").strip()
        print("Teensy:", line)
        if line == "ACK":
            break

    start_time = time.perf_counter()
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

    end_time = time.perf_counter()

    print("Finished CNN resistor-array test")
    print("Total images:", total)
    print("Correct:", correct)
    print("Incorrect:", incorrect)
    print("Time elapsed:", end_time - start_time)

    if total > 0:
        print(f"Final accuracy: {100 * correct / total:.2f}%")


def run_cnn_one_col(device, class_index):
    """
    class_index = 0 for cnn0 (first classification)
    class_index = 1 for cnn1 (second classification)
    """

    def encode(loader):
        encoded, labels = [], []
        with torch.no_grad():
            for img, label in loader:
                fc1 = model.get_fcl1_output(img)
                codes = quantize_fcl1_ouput(
                    fc1, model.act_max, ckpt["max_level"]
                )
                encoded.append(codes.squeeze(0).cpu().numpy())
                labels.append(label.item())

        return (
            np.asarray(encoded, dtype=np.uint8),
            np.asarray(labels, dtype=np.int64),
        )

    model, ckpt = load_qat_save()

    class_a = int(ckpt["class_a"])
    class_b = int(ckpt["class_b"])

    all_weights = np.asarray(ckpt["conductance_targets"], dtype=np.float64)
    class_weights = all_weights[class_index]

    if class_index == 0:
        validation_loader = load_mnist_validation_images(
            ckpt["validation_indices"].cpu().numpy()
        )
        test_loader = load_mnist_test_image(class_a, class_b)

        validation_inputs, validation_labels = encode(validation_loader)
        test_inputs, test_labels = encode(test_loader)
        output_path = CNN_CLASS0_PATH
    else:
        class0 = np.load(CNN_CLASS0_PATH, allow_pickle=False)
        validation_inputs = class0["validation_inputs"]
        validation_labels = class0["validation_labels"]
        test_inputs = class0["test_inputs"]
        test_labels = class0["test_labels"]
        output_path = CNN_CLASS1_PATH

    # Program first.
    device.ser.reset_input_buffer()
    command = "CNNWEIGHTS," + ",".join(
        f"{weight:.12g}" for weight in class_weights
    ) + "\n"
    device.ser.write(command.encode("utf-8"))

    while True:
        line = device.ser.readline().decode(errors="replace").strip()
        if line == "ACK":
            break
        if line.startswith("ERROR:"):
            raise RuntimeError(line)
        if line:
            print("Teensy:", line)

    # Measure only after programming.
    all_inputs = np.concatenate([validation_inputs, test_inputs], axis=0)
    all_scores = []

    for index, codes in enumerate(all_inputs):
        all_scores.append(send_patch_cnn_onecol(device, codes))

        if (index + 1) % 100 == 0:
            print(f"Processed {index + 1}/{len(all_inputs)}")

    all_scores = np.asarray(all_scores, dtype=np.float64)
    n_validation = len(validation_inputs)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        output_path,
        class_a=class_a,
        class_b=class_b,
        class_index=class_index,
        validation_inputs=validation_inputs,
        validation_labels=validation_labels,
        validation_scores=all_scores[:n_validation],
        test_inputs=test_inputs,
        test_labels=test_labels,
        test_scores=all_scores[n_validation:],
    )

    print("Saved:", output_path)

def combine_cnn():
    class0 = np.load(CNN_CLASS0_PATH, allow_pickle=False)
    class1 = np.load(CNN_CLASS1_PATH, allow_pickle=False)

    class_a = int(class0["class_a"])
    class_b = int(class0["class_b"])

    # Ensure both passes used exactly the same images in the same order.
    if not np.array_equal(
        class0["validation_inputs"],
        class1["validation_inputs"],
    ):
        raise RuntimeError("Validation inputs differ between cnn0 and cnn1.")

    if not np.array_equal(
        class0["test_inputs"],
        class1["test_inputs"],
    ):
        raise RuntimeError("Test inputs differ between cnn0 and cnn1.")

    validation_labels = class0["validation_labels"]
    test_labels = class0["test_labels"]

    validation_margin = (
        class1["validation_scores"]
        - class0["validation_scores"]
    )

    # Candidate thresholds are placed between measured margins.
    unique_margins = np.sort(np.unique(validation_margin))

    if len(unique_margins) == 1:
        candidate_thresholds = unique_margins
    else:
        middle_thresholds = (
            unique_margins[:-1] + unique_margins[1:]
        ) / 2.0

        epsilon = max(
            1.0,
            np.max(np.abs(unique_margins)) * 1e-9,
        )

        candidate_thresholds = np.concatenate([
            [unique_margins[0] - epsilon],
            middle_thresholds,
            [unique_margins[-1] + epsilon],
        ])

    best_threshold = 0.0
    best_balanced_accuracy = -1.0

    # Select the threshold using validation labels only.
    for threshold in candidate_thresholds:
        predictions = np.where(
            validation_margin > threshold,
            class_b,
            class_a,
        )

        recall_a = np.mean(
            predictions[validation_labels == class_a] == class_a
        )
        recall_b = np.mean(
            predictions[validation_labels == class_b] == class_b
        )

        balanced_accuracy = 0.5 * (recall_a + recall_b)

        if (
            balanced_accuracy > best_balanced_accuracy
            or (
                np.isclose(
                    balanced_accuracy,
                    best_balanced_accuracy,
                )
                and abs(threshold) < abs(best_threshold)
            )
        ):
            best_balanced_accuracy = balanced_accuracy
            best_threshold = float(threshold)

    # Apply the frozen threshold to the untouched test set.
    test_margin = (
        class1["test_scores"]
        - class0["test_scores"]
    )

    raw_predictions = np.where(
        test_margin > 0.0,
        class_b,
        class_a,
    )

    calibrated_predictions = np.where(
        test_margin > best_threshold,
        class_b,
        class_a,
    )

    raw_accuracy = 100.0 * np.mean(
        raw_predictions == test_labels
    )
    calibrated_accuracy = 100.0 * np.mean(
        calibrated_predictions == test_labels
    )

    print("Validation images:", len(validation_labels))
    print("Selected threshold:", best_threshold)
    print(
        "Validation balanced accuracy:",
        f"{100.0 * best_balanced_accuracy:.2f}%",
    )
    print("Final test images:", len(test_labels))
    print(f"Raw argmax test accuracy: {raw_accuracy:.2f}%")
    print(
        f"Calibrated test accuracy: "
        f"{calibrated_accuracy:.2f}%"
    )

    print(
        f"Class {class_a} predicted as {class_a}:",
        int(np.sum(
            (test_labels == class_a)
            & (calibrated_predictions == class_a)
        )),
    )
    print(
        f"Class {class_a} predicted as {class_b}:",
        int(np.sum(
            (test_labels == class_a)
            & (calibrated_predictions == class_b)
        )),
    )
    print(
        f"Class {class_b} predicted as {class_a}:",
        int(np.sum(
            (test_labels == class_b)
            & (calibrated_predictions == class_a)
        )),
    )
    print(
        f"Class {class_b} predicted as {class_b}:",
        int(np.sum(
            (test_labels == class_b)
            & (calibrated_predictions == class_b)
        )),
    )

    combined_path = (
        CNN_CLASS0_PATH.parent / "cnn_combined.npz"
    )

    np.savez(
        combined_path,
        class_a=class_a,
        class_b=class_b,
        threshold=best_threshold,
        validation_margin=validation_margin,
        validation_labels=validation_labels,
        test_margin=test_margin,
        test_labels=test_labels,
        raw_predictions=raw_predictions,
        calibrated_predictions=calibrated_predictions,
        raw_accuracy=raw_accuracy,
        calibrated_accuracy=calibrated_accuracy,
    )

    print("Saved combined CNN results to:")
    print(combined_path)


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

def listen_for_teensy(device, idle_timeout_s=3.0, max_time_s=None, log_path="teensy_log.txt"):
    """
    Keep reading Teensy output until no new line arrives for idle_timeout_s.
    Also write every printed Teensy line to a text file.
    """
    start = time.monotonic()
    last_line = time.monotonic()

    with open(log_path, "w", encoding="utf-8") as f:
        while True:
            if max_time_s is not None and time.monotonic() - start > max_time_s:
                print("Stopped listening: max_time_s reached.")
                f.write("Stopped listening: max_time_s reached.\n")
                break

            line = device.ser.readline().decode("utf-8", errors="replace").strip()

            if line:
                print("Teensy:", line)
                f.write(line + "\n")
                f.flush()
                last_line = time.monotonic()
                continue

            if time.monotonic() - last_line > idle_timeout_s:
                print("Stopped listening: idle timeout.")
                f.write("Stopped listening: idle timeout.\n")
                break

def print_pymenu():
    print("=== PYTHON COMMANDS ===")
    print("pymenu   - Show Python commands")
    print("testmenu - Shows the Arduino side test menu")
    print("drain  - Read buffered Teensy output (you can keep pressing)")
    print("sanity - Run Python patch sanity suite")
    print("calibtest - Run Python calibration sanity suite")
    print("mnist - Run full mnist image processing test with pyserial")
    print("mnistreal - Run full mnist image processing test with row10 as baseline subtraction")
    print("========================================================================================")
    print("mnistshift - Run shifted part of negative kernel image processing MNIST")
    print("mnistoff - Run offset part of negative kernel image processing MNIST")
    print("mnistcomb - Combines the above two") 
    print("========================================================================================")
    print("sc - Run full image processing on our eecs building with row 10 as baseline subtraction")
    print("cnnres - Run the FC2 layer of the CNN image classification on the resistor array")
    print("========================================================================================")
    print("cnn0 - Program class-0 FC2 weights and save hardware scores")
    print("cnn1 - Program class-1 FC2 weights and save hardware scores")
    print("cnncomb - Compare both saved score arrays and report accuracy")
    print("========================================================================================")
    print("quit   - Exit Python script (BUT MAKE SURE TO SWITCH OFF AND TYPE OFF)")
    print()
    print("Anything else is sent directly to Teensy.")

# --- MAIN ---
# ============================================================
def main():

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

            # for quick loading of serial monitor
            if cmd.lower() == "drain":
                read_all_available_lines(device, pause_s=0.1)
                continue
            # continuous reading of the serial monitor. Usually better for long tests.
            if cmd.lower() == "listen":
                listen_for_teensy(device, idle_timeout_s=7.0, log_path="conductance.txt")
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
                run_mnist_test(device, kernel, "resistor")
                print_pymenu()
                continue
            if cmd.lower() == "mnistreal":
                print("Running full mnist image processing test with row10 baseline subtraction")
                run_mnist_test(device, kernel, "real")
                print_pymenu()
                continue

            if cmd.lower() == "sc":
                print("Running full scenery image processing of our eecs building test with row10 baseline subtraction")
                run_mnist_test(device, kernel, "scenery")
                print_pymenu()
                continue

            # these are the mnist image processing commands for negative kernels but using only one col
            if cmd.lower() == "mnistshift":
                print("Running the shifted part of the mnist image processing for negative kernels")
                run_mnist_one_col(device, "shift", mode="mnist")
                print_pymenu()
                continue
            if cmd.lower() == "mnistoff":
                print("Running the offset part of the mnist image processing for negative kernels")
                run_mnist_one_col(device, "offset", mode="mnist")
                print_pymenu()
                continue
            if cmd.lower() == "mnistcomb":
                print("Combining the mnistshift and mnistoff results for the full negative kernel img proc")
                combine_mnist()
                print_pymenu()
                continue
            if cmd.lower() == "scshift":
                print("Running the shifted part of the scenery image processing for negative kernels")
                run_mnist_one_col(device, "shift", mode="scenery")
                print_pymenu()
                continue
            if cmd.lower() == "scoff":
                print("Running the offset part of the scenery image processing for negative kernels")
                run_mnist_one_col(device, "offset", mode="scenery")
                print_pymenu()
                continue
            if cmd.lower() == "sccomb":
                print("Combining the scshift and scoff results for the full negative kernel img proc")
                combine_mnist()
                print_pymenu()
                continue

            if cmd.lower() == "cnnres":
                print("Running FC2 layer of the CNN image classification")
                run_cnn_resistor(device)
                print_pymenu()
                continue
            if cmd.lower() == "cnnreal":
                print("Running CNN image classification on real array")
                run_cnn_real_array(device)
                print_pymenu()
                continue

            if cmd.lower() == "cnn0":
                print("Running CNN image classification on real array and doing one of the classification")
                run_cnn_one_col(device, class_index = 0)
                print_pymenu()
                continue
            if cmd.lower() == "cnn1":
                print("Running CNN image classification on real array and doing the other classification")
                run_cnn_one_col(device, class_index = 1)
                print_pymenu()
                continue
            if cmd.lower() == "cnncomb":
                print("Running CNN image classification argmax comparison")
                combine_cnn()
                print_pymenu()
                continue

            send_command(device, cmd)
        

    finally:
        device.close()
        print("Serial connection closed.")



if __name__ == "__main__":
    main()
