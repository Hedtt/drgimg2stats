from PIL import Image
from pytesseract import pytesseract

# Define path to tessaract.exe
path_to_tesseract = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Define path to image
path_to_image = 'images/20221124213512_1.jpg'
# Point tessaract_cmd to tessaract.exe
pytesseract.tesseract_cmd = path_to_tesseract
# Open image with PIL
img = Image.open(path_to_image)
# Extract text from image
img_crop = img.crop((480,500,950,680))
text = pytesseract.image_to_string(img_crop)

if __name__ == '__main__':
    print(text)
