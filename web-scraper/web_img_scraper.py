import requests
from bs4 import BeautifulSoup
import os
import time
import glob

# base URL 
base_url = '{}' 

# Creating download folder
download_folder = 'downloaded_images'
os.makedirs(download_folder, exist_ok=True)

def download_image(image_url, filename):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {filename}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {image_url}: {e}")

filename_pattern = 'filename*.jpg' #Given filename when saving images to disk.

files = glob.glob(os.path.join(download_folder, filename_pattern))

max_sequence = 0

for file in files:
    filename = os.path.basename(file)

    try:
        seq_part = filename.split('_')[1].split('.')[0].split('-')[0]
        sequence = int(seq_part)
    except (IndexError, ValueError):
        continue

    if sequence > max_sequence:
        max_sequence = sequence

next_sequence = max_sequence + 1
start_page    = next_sequence
end_page      = 0 #FİNAL Image Index!

rate_limit = 0.6 #(second)

for page_num in range(start_page, end_page + 1):
    page_url = base_url.format(page_num)
    print(f"Fetching page {page_url}...")

    try:
        response = requests.get(page_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Try to find the 'image-row' div. If fails skip to the next index.
        try:
            image_tags = soup.find('a', class_='next_img').find_all('img', src=True) # ADJUST THIS ACCORDİNG TO THE WEBSİTE YOU ARE SCRAPİNG
        except AttributeError:
            # Error handling 
            print(f"Skipping page {page_num} (not found or redirected).")
            continue

        # Iterate over the <img> tags
        for image_tag in image_tags:
            full_image_url = image_tag['src']
            
            # Image name generate
            image_name = full_image_url.split('/')[-1]
            image_path = os.path.join(download_folder, image_name)

            download_image(full_image_url, image_path)
        
        # Rate limiting
        time.sleep(rate_limit)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching page {page_num}: {e}")
