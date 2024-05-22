import img2pdf
import natsort
import os

def GetImagesInFolder(dirs):
    images = []
    for dir in dirs:
        files = natsort.os_sorted(os.listdir(dir))
        images += [os.path.join(dir, f) for f in files if os.path.splitext(f)[1] in [".jpg", ".png"]]
    return images

def Convert(images, output_name):
    with open(output_name, "wb") as f:
        f.write(img2pdf.convert(images))

def ParseBytes(bytes):
    size = bytes / 1024
    return f"{size:.2f} KB"