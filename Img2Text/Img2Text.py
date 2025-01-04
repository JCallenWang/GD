import os
from pathlib import Path
import easyocr
from PIL import Image, ImageOps, ImageEnhance
import pytesseract
import cv2
import numpy as np
import ast

# assign if Tesseract isn't assigned automatically
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text(directory, filename):    
    image_path = os.path.join(directory, filename)
    if not os.path.isfile(image_path):
        raise FileNotFoundError("the file was not found in {image_path}.")
    # open image
    img = Image.open(image_path)
    img = ImageOps.grayscale(img)
    img = img.point(lambda x: 0 if x < 128 else 255, '1')
    width, height = img.size
    img = img.resize((width * 2, height * 2), Image.Resampling.LANCZOS)
    text = pytesseract.image_to_string(img, lang="chi_sim")
    return text

def extract_text_cv2(directory, filename):
    image_path = os.path.join(directory, filename)
    if not os.path.isfile(image_path):
        raise FileNotFoundError("the file was not found in {image_path}.")
    
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, img = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)    # >128(white), <= 128(black)    
    (h, w) = img.shape[:2]
    img = cv2.resize(img, (w * 2, h * 2), interpolation=cv2.INTER_LANCZOS4)	
    img = cv2.GaussianBlur(img, (5, 5), 0)                      # use 5*5 to blur(bigger = more blurry)
    img = cv2.bitwise_not(img)                                  # turn black to white

    #coords = cv2.findNonZero(img)
    #angle = cv2.minAreaRect(coords)[-1]
    #angle = -(90 + angle) if angle < -45 else -angle
    #center = (w // 2, h // 2)
    #M = cv2.getRotationMatrix2D(center, angle, 1.0)
    #img = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    #show_image("Final Image", img)
    custom_config = r'--psm 4'
    text = pytesseract.image_to_string(img, lang="chi_sim+chi_tra", config = custom_config)
    return text

def extract_text_easyocr(directory, filename):
    image_path = os.path.join(directory, filename)
    if not os.path.isfile(image_path):
        raise FileNotFoundError("the file was not found in {image_path}.")
    
    img = Image.open(image_path)
    #img = ImageOps.grayscale(img)

    #enhancer = ImageEnhance.Contrast(img)
    #img = enhancer.enhance(2.0)

    #img = img.point(lambda x: 0 if x < 128 else 255, 'L')
    #img = img.resize((img.width * 2, img.height * 2), Image.Resampling.LANCZOS)

    img_np = np.array(img, dtype=np.uint8)
    reader = easyocr.Reader(['en', 'ch_tra'])
    #text = reader.readtext(img_np, detail=0)
    text = reader.readtext(image_path, detail=0)
    return text

def show_image(image_name, image):
    cv2.imshow(image_name, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
def replaced_dic(input):
    replacements = {
        '$':'S',
        '-':'一'
    }

    for key, value in replacements.items():
        input = input.replace(key, value)

    return input


# test
if __name__ == "__main__":
    current_directory = Path(__file__).parent
    directory = current_directory / "images"
    filename = "example.png"

    try:
        extracted_text = extract_text_easyocr(directory, filename)
        formatted_text = repr(extracted_text)

        data = ast.literal_eval(formatted_text)
        number = data[0]
        name = data[1]
        rank = data[2]
        rank_replaced = rank.replace('$', 'S')
        content = ''.join(data[3:])
        content_replaced = replaced_dic(content)

        print("extracted text:")
        print(f"original={extracted_text}")
        print(f"number={number}")
        print(f"name={name}")
        print(f"rank={rank_replaced}")
        print(f"content={content_replaced}")
    except FileNotFoundError as e:
        print(e)
