import torchvision
import torchvision.transforms as transforms
import scipy
import matplotlib.pyplot as plt
import numpy as np

'''
Simple Image Processing model for the 12x3 ScAlN Crossbar array
---------------------------------------------------------------

We will be using 100x100 grayscale images and pass it through different kernels (sharpen, blur, edge detection)

3x3 kernel slides through the image 3x3 pixels at a time

'''

# Load MNIST data for training and test
# =========================================================================

# mnist is 28 x 28
# but we are using 100x100 images, so we much resize it
transformto100x100 = transforms.Compose([
    transforms.Resize((20,20)),
    transforms.ToTensor()
])
training_data = torchvision.datasets.MNIST(
    root = "data",
    train= True,
    download=False, # set to True if first time running
    transform = transformto100x100
)

#kernel = [[0,-1,0],[-1,5,-1],[0,-1,0]]
#kernel = [[-1,-1,-1],[0,0,0],[1,1,1]]
#kernel = [[1/9,1/9,1/9],[1/9,1/9,1/9],[1/9,1/9,1/9]]
#kernel = (1/16)*np.array([[1,2,1],[2,4,2],[1,2,1]])
#kernel =  np.array([[-1, 0 ,1], [-1, 0, 1],[-1, 0 ,1]])

# kernel = [[0,0,0],[1,1,1],[2,2,2]]

# offset = [[1,1,1],[1,1,1],[1,1,1]]

# kernel = [[1,3],[3,1]]

# kernel = [[1,2,1],[2,3,2],[1,2,1]]

kernel = [[1,2],[2,3]]

filtered = []

for i in range(10): 
    images,_ = training_data[i]
    images = images.squeeze().numpy()
    filtered = scipy.signal.convolve2d(images, kernel, mode="valid")
    #print(filtered)

    # offsetconvolve = scipy.signal.convolve2d(images,offset, mode="valid")

    # filtered = filtered - offsetconvolve

    fig, (ax1, ax2) = plt.subplots(1, 2)
    ax1.imshow(images, cmap='gray')
    ax1.set_title('Original')
    ax2.imshow(filtered, cmap='gray')
    ax2.set_title('Sharpened')
    plt.show()