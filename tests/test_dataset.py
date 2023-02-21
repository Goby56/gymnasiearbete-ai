from PIL import Image, ImageFilter
import numpy as np
import random

import os, sys
sys.path.append(os.getcwd())
import sample


dataset = sample.CompiledDataset(
    filename="emnist-digits.mat",
    image_size=(28, 28)
)

# test_data = dataset.get_test_data()

# image1, label1 = dataset.get(1, convert=True)
# pil_image1 = Image.fromarray(image1)
# # pil_image1 = pil_image1.convert("RGB")
# # pil_image1.save("test.png")
# # quit()

# image2, label2 = next(test_data)
# image2 = dataset.convert_image(image2)
# label2 = dataset.convert_label(label2)
# pil_image2 = Image.fromarray(image2)

# pil_image1.show()
# print(label1)

# pil_image2.show()
# print(label2)

def load_img():
    return Image.open("test.png")

def to_array(image):
    return np.asarray(image.convert("L")) / 255

def to_image(array):
    return Image.fromarray((array * 255).astype(int))

def augment_data(arr, options):
    new_img = to_image(arr)
    if options["rotate"]:
        new_img = new_img.rotate(random.randint(-30, 30), resample=Image.BICUBIC)
    if options["blur"]:
        new_img = new_img.filter(ImageFilter.GaussianBlur(random.random() * 1.2))
    if options["noise"]:
        array = to_array(new_img)
        array += np.random.random(array.shape) * 0.5
        return np.clip(array, 0, 1)

    return to_array(new_img)

options = {
    "noise": True,
    "shift": False, # no
    "rotate": True,
    "scale": False, # no
    "blur": False # no
}

# img = load_img()
# arr = augment_data(img, options)
# new_img = to_image(arr)
# new_img.show()

for bad in dataset.next_batch(random.randint(1, 10000)):
    pass

img = dataset.get(1, convert=True)
to_image(augment_data(img[0], options)).show()
to_image(img[0]).show()
print(img[1])




