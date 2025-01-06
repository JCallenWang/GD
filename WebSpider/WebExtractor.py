from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup   # web spider
from collections import OrderedDict # maintain the order of lines
import time
import re
import os       # open file
import opencc   # sim-Chi to tra-Chi
import requests # web request

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

#dir_path = "web_data_remove_emptylines/extracted_img/"
#output_filename = "all_cards_img.txt"
def merge_to_singlefile_ignore_duplicated_lines(dir_path, output_filename):
    # Use OrderedDict to store unique lines while maintaining order
    unique_lines = OrderedDict()

    # Collect all .txt files with the specific suffix pattern
    txt_files = [f for f in os.listdir(dir_path) if f.endswith(".txt") and "_" in f]
    # Sort the files by their numeric suffix
    sorted_files = sorted(txt_files, key=lambda x: int(x.split("_")[-1].split(".")[0]))

    # Read all .txt files in the directory
    for file in sorted_files:
        file_path = os.path.join(dir_path, file)
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                unique_lines[line.strip()] = None  # Add to OrderedDict
    # Write the unique lines to the output file
    with open(output_filename, "w", encoding="utf-8") as output:
        output.write("\n".join(unique_lines.keys()) + "\n")
    print(f"Merged and cleaned file saved as '{output_filename}'")
#input_file = "all_cards_img.txt"
#save_dir = "images"
def get_images(input_file, save_dir):
    with open(input_file, "r", encoding="utf-8") as file:
        url_list = file.readlines()

    os.makedirs(save_dir, exist_ok=True)  # Create directory if it doesn't exist

    # Download images
    for i, url in enumerate(url_list, start=1):
        try:
            clean_url = url.strip()
            response = requests.get(clean_url, stream=True)
            response.raise_for_status()  # Raise an error for HTTP issues
            # Extract file extension from the URL, fallback to ".jpg" if no extension is found
            ext = os.path.splitext(url)[-1] if os.path.splitext(url)[-1] else ".jpg"
            # Create file name with proper extension
            file_name = os.path.join(save_dir, f"image_{i}{ext}")
            # Save the image
            with open(file_name, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Downloaded: {file_name}")
        except Exception as e:
            print(f"Failed to download {url}: {e}")

    print("All downloads completed!")


