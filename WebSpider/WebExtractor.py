from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup   # web spider
import time
import re
import os       # open file
import opencc   # sim-Chi to tra-Chi

# Set up Selenium with Chrome WebDriver
def setup_driver():
    options = Options()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    service = Service("/Users/jcwang/Desktop/Project/GD/chromedriver-mac-arm64/chromedriver")  # Replace with your driver path
    driver = webdriver.Chrome(service=service, options=options)
    return driver
# Extract text and images from a webpage
def extract_text_and_images(url):
    driver = setup_driver()
    try:
        driver.get(url)
        time.sleep(5)  # Wait for dynamic content to load
        
        # Get page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Extract all text
        text = soup.get_text(separator="\n").strip()
        
        # Extract all image URLs
        images = []
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                full_src = driver.current_url + src if src.startswith("/") else src
                images.append(full_src)
        
        return {"text": text, "images": images}
    finally:
        driver.quit()
# Remove empty lines from a file_path
def remove_empty_lines(file_path):
    try:
        # Open the file and read all lines
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Filter out lines that are empty or contain only whitespace
        non_empty_lines = [line for line in lines if line.strip()]
        
        # Write the non-empty lines back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(non_empty_lines)
        
        print("Empty lines removed successfully.")
    except Exception as e:
        print(f"Error: {e}")
def GD_get_all_text_and_images(write_dir_path):
    for i in range(1, 23, 1):
        url = f"https://www.meoogo.com/GI/index.html#page/{i}"  # Replace with your URL
        data = extract_text_and_images(url)

        # Loop body
        if data and data['text'].strip():
            text_file_path = os.path.join(write_dir_path, f"extracted_text_{i}.txt")
            # Save text to a file
            with open(text_file_path, "w", encoding="utf-8") as text_file:
                text_file.write(data['text'])

            img_file_path = os.path.join(write_dir_path, f"image_urls_{i}.txt")
            # Save image URLs to a file
            with open(img_file_path, "w", encoding="utf-8") as img_file:
                for img_url in data['images']:
                    img_file.write(img_url + "\n")

            print(f"Extraction complete. Files_{i} saved.")

        remove_empty_lines(f"extracted_text_{i}.txt")

# parse text into groups with regular expression
def parse_groups(text):
    pattern = r'(-?\d+)\n(.*?)\1'
    matches = re.findall(pattern, text,re.DOTALL)
    #groups = [match[0] + '\n' + match[1] + match[0] for match in matches]
    groups = []
    for match in matches:
        start_end_number = match[0]
        content = match[1]
        group = f"{start_end_number}\n{content}{start_end_number}"
        groups.append(group)
    return groups
# OpenCC
def convert_simplified_Chinese_to_traditional_Chinese(input):
    converter = opencc.OpenCC('s2tw')
    return converter.convert(input)
# read file from <dir_path>, parsed with regular expression, convert to ZhCN and save it
def read_parse_convert(dir_path, fixed_dir_path):
    for filename in os.listdir(dir_path):
        parsed_content = []
        if filename.endswith(".txt"):
            file_path = os.path.join(dir_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()

                groups = parse_groups(file_content)
                for group in groups:
                    contents = convert_simplified_Chinese_to_traditional_Chinese(group)
                    splitlines = str(contents).splitlines()
                    #print(f"{file_path}==>read, file_content==>{contents}")
                    #for item in splitlines:
                    #    print(f"item==>{item}")
                    number = splitlines[0]
                    name = splitlines[1]
                    rank = splitlines[2]
                    discription = splitlines[3]
                    print(f"{number}\t{name}\t{rank}\t{discription}\n")
                    parsed_content.append(f"{number}\t{name}\t{rank}\t{discription}\n")
        
        converted_file_path = os.path.join(fixed_dir_path, filename)
        with open(converted_file_path, 'w', encoding='utf-8') as file:
            file.writelines(parsed_content)



        

