import torchvision
import torchvision.transforms as transforms
import numpy as np

IMAGE_SIZE = 20
MAX_LEVEL = 128
INDEX = 0

transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
])

dataset = torchvision.datasets.MNIST(
    root="data",
    train=True,
    download=False,
    transform=transform,
)

image, label = dataset[INDEX]
image_2d = image.squeeze().numpy()
image_q = np.round(np.clip(image_2d, 0.0, 1.0) * MAX_LEVEL).astype(int)

print(f"// Label: {label}")
print(f"const uint8_t mnist_image[{IMAGE_SIZE}][{IMAGE_SIZE}] = {{")
for row in image_q:
    print("  {" + ", ".join(str(v) for v in row) + "},")
print("};")
