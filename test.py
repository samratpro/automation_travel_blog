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
img_path = os.path.join(os.getcwd(), "img")

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
    banner = info[7].split("=")[1].strip()




def text_render(prompt,
                temp,
                max_toke,role="Ik ben een SEO-vriendelijke assistent voor het schrijven van artikelen",
                language="Output must be in native quality dutch language"):

      """Text generating function.""",
      response = openai.ChatCompletion.create(
          model=model,
          messages=[{"role": "system", "content": role},
                    {"role": "user", "content": prompt + "\n" + language}],
          temperature=temp,
          max_tokens=max_toke,
          top_p=1,
          frequency_penalty=0,
          presence_penalty=0
      )

      result = ''
      for choice in response.choices:
         result += choice.message['content']

      return result



data = text_render("hi", 0.9, 100)
print(data)