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
'''

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
# but we are using 100x100 images, so we much resize it
transformto100x100 = transforms.Compose([
    transforms.Resize((100,100)),
    transforms.ToTensor()
])


training_data = torchvision.datasets.MNIST(
    root = "data",
    train= True,
    download=False, # set to True if first time running
    transform = transformto100x100
)

# filtering out just 0's and 1's for now.
zerosandones = [i for i in range(len(training_data)) if training_data.targets[i] in [0,1]]
filtered_training_data = torch.utils.data.Subset(training_data,zerosandones)

g = torch.Generator()
g.manual_seed(SEED)
trainloader = torch.utils.data.DataLoader(filtered_training_data, batch_size=4, shuffle=True, num_workers=0, generator=g)

test_data = torchvision.datasets.MNIST(
    root = "data",
    train = False,
    download = False,
    transform = transformto100x100
)

zerosandoneshat = [i for i in range(len(test_data)) if test_data.targets[i] in [0,1]]
filtered_test_data = torch.utils.data.Subset(test_data, zerosandoneshat)

testloader = torch.utils.data.DataLoader(filtered_test_data, batch_size=4, shuffle=False, num_workers=0)


# main class for the CNN
# ================================================================================

# 100×100×1
# → Conv2d(1, 8, 3) + ReLU + MaxPool(2)    → 49×49×8
# → Conv2d(8, 16, 3) + ReLU + MaxPool(2)   → 23×23×16
# → Flatten                                 → 8464
# → FC(8464, 32) + ReLU                     → 32
# → FC(32, 9) + ReLU                        → 9     ← these 9 go to crossbar
# → FC(9, 2)                                → 2     ← this IS the crossbar

if __name__ == '__main__':
    class CNN(nn.Module):
        def __init__(self):
            super(CNN, self).__init__()
            self.conv1 = nn.Conv2d(1,8,3) # conv2d(in channel, out channel, kernel size)
            self.pool = nn.MaxPool2d(2,2)
            self.conv2 = nn.Conv2d(8,16,3)
            self.fc1 = nn.Linear(23*23*16, 32) 
            self.fc2 = nn.Linear(32, 9)
            self.fc3 = nn.Linear(9,2)

        def forward(self, x):
            x = self.pool(F.relu(self.conv1(x))) # 1 -> greyscale, 8 channels, 3x3 kernel --> 98x98x8 -> 49x49x8
            x = self.pool(F.relu(self.conv2(x))) # 8 channels, 16 channels, 3x3 kernel --> 47x47x16 -> 23x23x16
            x = torch.flatten(x, 1) # flattens the matrix into vector for fcl
            x = F.relu(self.fc1(x)) 
            x = F.relu(self.fc2(x))
            x = self.fc3(x)
            return x
        
    net = CNN()

    lossfx = nn.CrossEntropyLoss()
    optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

    for epoch in range(2):
        running_loss = 0.0
        for i, data in enumerate(trainloader, 0):
            inputs, labels = data

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


    print(net.fc3.weight.detach().cpu().numpy())
    print(net.fc3.bias.detach().cpu().numpy())



    # accuracy checker 
    correct = 0
    total = 0
    misclassified = []
    with torch.no_grad():
        # loop through batches of test data 
        for data in testloader: 
            # image and label pair for each mnist digit
            images, labels = data 
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

    # visualizing the misclassified images
    for imgs, preds, labs in misclassified:
        for k in range(imgs.size(0)):
            plt.imshow(imgs[k].squeeze(), cmap='gray')
            plt.title(f'Predicted: {preds[k].item()}, Actual: {labs[k].item()}')
            plt.show()

    
    

