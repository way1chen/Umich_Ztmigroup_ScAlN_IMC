import torch
import torchvision.transforms as transforms
from PIL import Image
import scipy.signal
import matplotlib.pyplot as plt
import numpy as np

# ============================================================
# Load image
# ============================================================

transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.Resize((100, 100)),
    transforms.ToTensor()
])

img = Image.open(r"data\bell.jpeg")

image_tensor = transform(img)      # shape: [1,100,100]
image = image_tensor.squeeze().numpy()

# ============================================================
# Kernel
# ============================================================

# kernel = 0.7 * np.array([
#     [3.5, 4.5, 3.5],
#     [4.5, 5.5, 4.5],
#     [3.5, 4.5, 3.5]
# ], dtype=np.float32)

# # Optional normalization
# kernel = kernel / np.sum(kernel)

# kernel = np.array([
#     [-0.5, -0.5, -0.5],
#     [-0.5,  4, -0.5],
#     [-0.5, -0.5, -0.5]
# ], dtype=np.float32)
# kernel = np.array([
#     [-1, 0, 1],
#     [-2, 0, 2],
#     [-1, 0, 1]
# ], dtype=np.float32)
#kernel = [[-1,0,1],[-1,0,1]]
kernel = [[-2,-2],[0,0],[2,2]]
#kernel = [[-1,0,1],[-1,0,1]]

#kernel = [[-2,-2,-2],[0,0,0],[2,2,2]]

#kernel =  np.array([[-1, 0 ,1], [-1, 0, 1],[-1, 0 ,1]])



# kernel = [[1,2],[3,3],[2,1]]

# kernel = kernel / np.sum(kernel)



# ============================================================
# Convolution
# ============================================================

filtered = scipy.signal.convolve2d(
    image,
    kernel,
    mode="valid"
)

# ============================================================
# Plot
# ============================================================

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8,4))

ax1.imshow(image, cmap="gray")
ax1.set_title("Original")
ax1.axis("off")

ax2.imshow(filtered, cmap="gray")
ax2.set_title("Filtered")
ax2.axis("off")

plt.tight_layout()
plt.show()

fig2 = plt.figure(frameon=False)
ax = plt.Axes(fig2, [0., 0., 1., 1.])
fig2.add_axes(ax)

ax.imshow(filtered, cmap="gray")
ax.set_axis_off()

fig2.savefig(
    "filtered.svg",
    format="svg",
    bbox_inches="tight",
    pad_inches=0
)

plt.close(fig2)