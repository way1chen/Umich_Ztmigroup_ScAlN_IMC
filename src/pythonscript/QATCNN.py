import torch 
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
import torch.nn.functional as F

import matplotlib.pyplot as plt

import random
import numpy as np

'''
Simple CNN model for image classification for 12x3 ScAlN Crossbar array
Using Quantization Aware Training

Purpose:
When doing image classification with the real crossbar array, there are two points of
hardware rounding/quantization. 1. Input image greyscale range PWM number 2. Floating point precision
of the NN weights.

The original MNIST has greyscale from 0 to 255. Being able to scale to down to 0-127 or even 0-31 
has the advantage of faster calculation time on the crossbar and shorter time is important since
conductance values tend to drift over time.

Most importantly, floating point precision is lacking when we program the conductance weights
on the crossbar due to many factors, some of which are: adc precision, inherently limited 
conductance range of the material, etc. 

Thus QAT becomes more attractive since it accounts for these quantizations and loss in precisions.
'''

# Max pulse we want to use for 255 aka white pixel
MAX_LEVEL = 32

# two digits I want to classify
CLASS_A = 4
CLASS_B = 9

# Conductance range and how many levels to program
G_MIN = 1  # µS
G_MAX = 8  # µS
WEIGHT_LEVELS = 8  # codes 0-7

# Load MNIST data for training and test
# =========================================================================

SEED=17
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)

torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
torch.use_deterministic_algorithms(True)

# mnist is 28 x 28

transform = transforms.Compose([
    transforms.ToTensor(),
    # transforms.Lambda(lambda x: torch.floor(x * 31) / 31) # mnist greyscale is originally 0 to 255, but this quantizes it down to 0 to 31.
])

training_data = torchvision.datasets.MNIST(
    root = "data",
    train= True,
    download=False, # set to True if first time running
    transform=transform
)

# filtering out just 0's and 1's for now.
zerosandones = [i for i in range(len(training_data)) if training_data.targets[i] in [CLASS_A,CLASS_B]]
filtered_training_data = torch.utils.data.Subset(training_data,zerosandones)

g = torch.Generator()
g.manual_seed(SEED)
trainloader = torch.utils.data.DataLoader(filtered_training_data, batch_size=4, shuffle=True, num_workers=0, generator=g)

test_data = torchvision.datasets.MNIST(
    root = "data",
    train = False,
    download = False,
    transform=transform
)

zerosandones_hat = [i for i in range(len(test_data)) if test_data.targets[i] in [CLASS_A,CLASS_B]]
filtered_test_data = torch.utils.data.Subset(test_data, zerosandones_hat)

testloader = torch.utils.data.DataLoader(filtered_test_data, batch_size=4, shuffle=False, num_workers=0)


# Quantization Logic
# ================================================================================
def quantization(x, max_input, min_input, MAXLEVEL=MAX_LEVEL):
    max_input = torch.as_tensor(max_input, device=x.device, dtype=x.dtype)
    min_input = torch.as_tensor(min_input, device=x.device, dtype=x.dtype)

    scale = torch.clamp((max_input - min_input) / MAXLEVEL, min=1e-8) # maybe MAXLEVEL - 1 if i decide to make MAXLEVEL mean from 0 to MAXLEVEL - 1
    x_clamped = torch.clamp(x,min_input, max_input)
    x_quant = torch.round((x_clamped - min_input) / scale)
    x_dequant = x_quant * scale + min_input
    
    return x + (x_dequant - x).detach() # this is so that during forward pass this function returns x_dequant, but during
                                        # backprop, detach makes (xdequant - x) a constant, so it only differentiates x 
                                        # as 1. This is STE method


# main class for the CNN
# ================================================================================

# 28x28×1
# → Conv2d(1, 8, 3) + ReLU + MaxPool(2)    → 24×24×8 (28x28 -> 26x26 due to 3x3 kernel conv, then 13x13 due to maxpool of stride 2)
# → Conv2d(8, 16, 3) + ReLU + MaxPool(2)   → 5×5×16
# → Flatten                                 → 400
# → FC(400, 9) + ReLU                        → 9     ← these 9 go to crossbar
# → FC(9, 2)                                → 2     ← this IS the crossbar

class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(1,8,3) # conv2d(in channel, out channel, kernel size)
        self.pool = nn.MaxPool2d(2,2)
        self.conv2 = nn.Conv2d(8,16,3)
        self.fc1 = nn.Linear(5*5*16, 9) 
        self.fc2 = nn.Linear(9,2, bias=False) 
        self.register_buffer("act_max", torch.tensor(0.0))

    def get_fcl1_output(self, x):
        x = self.pool(F.relu(self.conv1(x))) # 1 -> greyscale, 8 channels, 3x3 kernel 
        x = self.pool(F.relu(self.conv2(x))) # 8 channels, 16 channels, 3x3 kernel
        x = torch.flatten(x, 1) # flattens the matrix into vector for fcl
        x = F.relu(self.fc1(x)) # ReLU allows us to only input positive inputs to our array
        return x

    def forward(self, x):
        x = self.get_fcl1_output(x)
        
        # We have to find the typical max value right before the fc2 layer so we can quantize
        w_min = self.fc2.weight.detach().min()
        if self.training:
            batch_max = x.detach().amax()
            if self.act_max.item() == 0.0:
                self.act_max.copy_(batch_max)
            else:
                self.act_max.mul_(0.99).add_(0.01 * batch_max)

        w_shifted = self.fc2.weight - w_min
        w_shifted_max = w_shifted.detach().max()

        w_shifted_quant = quantization(w_shifted, w_shifted_max, 0, WEIGHT_LEVELS - 1)
        offset_w = quantization(-w_min, w_shifted_max, 0, WEIGHT_LEVELS - 1)

        x = quantization(x, self.act_max, 0, MAX_LEVEL)  
        x = F.linear(x, w_shifted_quant) - offset_w * x.sum(dim=1, keepdim=True)
        return x

if __name__ == '__main__':  # things inside this are ignored when this module is called from another file  
    net = CNN()

    lossfx = nn.CrossEntropyLoss()
    optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

    for epoch in range(2):
        running_loss = 0.0
        for i, data in enumerate(trainloader, 0):
            inputs, labels = data
            labels = (labels == CLASS_B).long()

            optimizer.zero_grad()

            outputs = net(inputs)
            loss = lossfx(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            if i % 2000 == 1999:
                print('[%d, %5d] loss: %.3f' %
                    (epoch + 1, i + 1, running_loss / 2000))
                running_loss = 0.0

    print('Finished Training')

    # save the model states
    torch.save({
    "state_dict": net.state_dict(),
    "class_a": CLASS_A,
    "class_b": CLASS_B,
    "max_level": MAX_LEVEL,
    "weight_levels": WEIGHT_LEVELS,
    "g_min": G_MIN,
    "g_max": G_MAX,
    }, "qatcnn_checkpoint.pt")


    #print(net.fc2.weight.detach().cpu().numpy())
    #print(net.fc2.bias.detach().cpu().numpy())

    # start inference, this sets training to false
    net.eval()

    # accuracy checker 
    correct = 0
    total = 0
    misclassified = []
    with torch.no_grad():
        # loop through batches of test data 
        for data in testloader: 
            # image and label pair for each mnist digit
            images, labels = data 
            labels = (labels == CLASS_B).long()
            # push the test images through cnn with no grad
            outputs = net(images) 
            # max takes the parameters (value, index). we find max across axis 1 which 
            # gives us the index of whichever class (0 or 1) it has a higher number of 
            _, predicted = torch.max(outputs, 1) 
            # add to everytime the image in the batch has the same 
            # predicted label as the true label
            correct += (predicted == labels).sum().item()

            wronglyclass = predicted != labels
            if (wronglyclass.any()):
                misclassified.append((images[wronglyclass], predicted[wronglyclass], labels[wronglyclass]))

            # total number of all data.
            total += labels.size(0)

    print(f'Accuracy: {100 * correct / total:.2f}%')


    # Hardware Extract Conductance Targets
    # ============================================

    print("Activation max:", float(net.act_max.cpu()))
    print("Activation scale per pulse:", float(net.act_max.cpu()) / MAX_LEVEL)

    with torch.no_grad():
        w = net.fc2.weight.detach()
        w_min = w.min()
        w_shifted = w - w_min
        w_max = w_shifted.max()
        scale = w_max / (WEIGHT_LEVELS - 1)
        
        weight_codes = torch.round(w_shifted / scale).clamp(0, WEIGHT_LEVELS - 1)
        offset_code = torch.round((-w_min) / scale).clamp(0, WEIGHT_LEVELS - 1)
        
        conductance_targets = G_MIN + weight_codes * (G_MAX - G_MIN) / (WEIGHT_LEVELS - 1)
        offset_conductance = G_MIN + offset_code * (G_MAX - G_MIN) / (WEIGHT_LEVELS - 1)
        
        print("Weight codes:")
        print(weight_codes.cpu().numpy().astype(int))
        print("Offset code:", int(offset_code.item()))
        print("Conductance targets (µS):")
        print(conductance_targets.cpu().numpy() * 0.000001)
        print("Offset conductance (µS):", float(offset_conductance) * 0.000001)

    # visualizing the misclassified images
    for imgs, preds, labs in misclassified:
        for k in range(imgs.size(0)):
            plt.imshow(imgs[k].squeeze(), cmap='gray')
            pred_label = CLASS_A if preds[k].item() == 0 else CLASS_B
            actual_label = CLASS_A if labs[k].item() == 0 else CLASS_B
            plt.title(f'Predicted: {pred_label}, Actual: {actual_label}')
            plt.show()

    
    

