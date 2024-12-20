from random import choice
from time import sleep
import openai, os, json, shutil, base64, requests
from datetime import datetime
from PIL import Image
import re
from random import choice
from googleapiclient.discovery import build
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

info_path = os.path.join(os.getcwd(), "data/info.txt")

with open(info_path) as info_file:
    info = info_file.readlines()
    info = [x.strip() for x in info if len(x) > 0]
    openai.api_key = info[0].split("=")[1].strip()
    model = info[1].split("=")[1].strip()
    website_url = info[2].split("=")[1].strip()
    post_status = info[3].split("=")[1].strip()
    wordpress_username = info[4].split("=")[1].strip()
    wordpress_app_pass = info[5].split("=")[1].strip()
    youtube_api = info[6].split("=")[1].strip()

token = base64.standard_b64encode((wordpress_username + ':' + wordpress_app_pass).encode('utf-8'))
headers = {'Authorization': 'Basic ' + token.decode('utf-8')}


location_path = os.path.join(os.getcwd(), "img")
print(location_path)
if not os.path.exists(location_path):
    os.makedirs(location_path)




def create_categories(cat_list, website_url, headers):
    print(f'{datetime.now()} - Working in Category Section...')
    category_ids = []  # Store IDs for all categories

    for cat_name in cat_list:
        id = 0
        if len(cat_name) > 0:
            data = {"name": cat_name}
            try:
                # Attempt to create the category
                cat = requests.post(website_url + '/wp-json/wp/v2/categories', headers=headers, json=data)
                if cat.status_code == 201:  # Category successfully created
                    id = str(json.loads(cat.content.decode('utf-8'))['id'])
                elif cat.status_code == 400:  # Category exists
                    response = json.loads(cat.content.decode('utf-8'))
                    if "term_id" in response["data"]:
                        id = str(response["data"]["term_id"])  # Use the existing ID
                    else:
                        print(f"Failed to extract existing category ID for '{cat_name}': {response}")
                else:
                    print(f"Failed to create category '{cat_name}': {cat.status_code} - {cat.content.decode('utf-8')}")
            except Exception as e:
                print(f"Error creating category '{cat_name}': {e}")
                try:
                    # If creation fails, check if it already exists
                    cat = requests.get(website_url + '/wp-json/wp/v2/categories', headers=headers)
                    if cat.status_code == 200:
                        cat_id = json.loads(cat.content.decode('utf-8'))
                        for existing_cat in cat_id:
                            if cat_name.lower() == existing_cat['name'].lower():
                                id = str(existing_cat['id'])
                    else:
                        print(f"Failed to fetch categories: {cat.status_code} - {cat.content.decode('utf-8')}")
                except Exception as e:
                    print(f"Error fetching categories: {e}")

        if id:
            category_ids.append(id)  # Append the category ID if found or created
        else:
            print(f"Category not found or created: {cat_name}")

    return category_ids





ids = create_categories(['dubai','accommodaties dubai'], website_url, headers)

print(ids)
