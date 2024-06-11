import img2pdf
import natsort
import os

IMG_EXTENSIONS = [".jpg", ".png"]

def isImage(file):
    return os.path.splitext(file)[1].lower() in IMG_EXTENSIONS

def GetImagesInFolder(dirs):
    images = []
    for dir in dirs:
        files = natsort.os_sorted(os.listdir(dir))
        images += [os.path.join(dir, f) for f in files if isImage(f) ]
    return images

def Convert(images, output_name):
    with open(output_name, "wb") as f:
        f.write(img2pdf.convert(images))

def ParseBytes(bytes):
    
    size = bytes

    if size > 1000:
        size = size / 1024
        factor = "KB"

    if size > 1000:
        size = size / 1024
        factor = "MB"

    return f"{size:.2f} {factor}"