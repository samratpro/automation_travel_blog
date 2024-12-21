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

token = base64.standard_b64encode((wordpress_username + ':' + wordpress_app_pass).encode('utf-8'))
headers = {'Authorization': 'Basic ' + token.decode('utf-8')}


title_prompt = '''Schrijf een SEO-titel over dit trefwoord binnen 55 tekens. Het trefwoord moet rechtstreeks in de titel worden opgenomen
trefwoord:  <<keyword>>
'''

outline_prompt = '''Genereer een overzicht voor een artikel dat alle relevante onderwerpen op het trefwoord kan behandelen: <<keyword>>
Het overzicht bestaat uit één H1-kop en meerdere H2's met briefing.
Alleen een overzicht nodig, geef geen antwoorden, onnodige woorden of notities. Geef me geen "Overzicht", "Inleiding" of "Conclusie" enz. anderen
Het overzicht moet de volgende opmaak hebben, tussen 8 en 12, H2-sectie:
<H1></H1>
<h2></h2>
- subonderwerp
- subonderwerp
- subonderwerp
- subonderwerp
<h2></h2>
- subonderwerp
- subonderwerp
- subonderwerp
- subonderwerp
<h2></h2>
- subonderwerp
- subonderwerp
- subonderwerp
- subonderwerp
<h2></h2>
.........
'''
introduction_prompt = '''Schrijf een beste blogpostintroductie over dit trefwoord. Intro start met technische termen, niet zoals """ben jij""" en trefwoorden moeten in de output worden opgenomen. Geef me geen directe oplossing in de introsectie, de laatste zin van de intro moet interessant zijn om het volledige artikel te lezen, trefwoord: <<keyword>>
en lengte ca. 120 woorden
'''
paragraph_prompt = '''
Schrijf deze sectie voor de genoemde paragraafkop binnen 120 woorden, zodat het nuttig is voor de lezer, op een interessante en georganiseerde manier zoals menselijk schrijven. Elke outputzin zal kort, betekenisvol en moedertaal zijn.
Ook op belangrijke punten kunt u indien nodig <em></em> toevoegen.
het artikeltrefwoord van deze paragraaf is <<keyword>> (Het trefwoord informeert u alleen over mijn hoofdpunt, onthoud het gewoon),
paragraafkop is: <<heading>>
Het onderwerp dat u hebt gevolgd <<topic_to_cover>>

You can add bullets or tables in sections if appropriate. Bullets and tables with <ul><li> tags, <em></em> tags, <table></table> tags and paragraphs with <p></p> tags. However, try to avoid the table tag if it is not up to 60% necessary. Do not start the sentence with the exact name of the heading or do not start with the heading and the context of the keyword base.
'''

conclusion_prompt = """Schrijf een conclusie voor dit trefwoord dat u in de uiteindelijke conclusie van de inhoud zult gebruiken, in 100 woorden of minder.
Trefwoord: <<keyword>>
"""

Excerpt = '''Schrijf een korte samenvatting,
Trefwoord: <<keyword>>,
Moet trefwoord in output opnemen
en lengte ca. 20 woorden
'''




# Text Generation *******************************
def para_format(text):
    """Paragraph formatting function."""
    if text:
        if text != "rext-render-error":
            choice_parts = [choice([2, 3]), 5, choice([7, 8]), 10, choice([12, 14]), 16]
            p_format = text.replace('?', '?---').replace('.', '.---').replace('!', '!---').split('---')
            parts = [f"<p>{''.join(p_format[choice_parts[i]:choice_parts[i+1]])}</p>" for i in range(len(choice_parts)-1)]
            text = ''.join(parts).replace('<p></p>', '').replace('  ', ' ').replace('\n', '')
            return text
        else:
            return ''
    return ''

def text_render(prompt,
                temp,
                max_toke,role="Ik ben een SEO-vriendelijke assistent voor het schrijven van artikelen",
                language="Output must be in native quality dutch language"):
    """Text generating function.""",
    try:
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
    except:
      return "text-render-error"


# Images *****************************************
location_path = os.path.join(os.getcwd(), "img")
def get_image_link(prompt, size="1024x1024"):
    """Generates an image using OpenAI's DALL·E API based on a text prompt."""
    print(f'{datetime.now()} - Working in get image link Section...')
    try:
      response = openai.Image.create(
          prompt=prompt,
          n=1,
          size=size
      )
      return response['data'][0]['url']
    except:
      return ''

def feature_image(keyword, headers, website_url):
    """Generates and post a feature image for a given prompt."""

    prompt = "Genereer een blogpost-afbeelding voor dit trefwoord: <<keyword>>"
    prompt = prompt.replace('<<keyword>>', keyword)

    print(f'{datetime.now()} - Working in feature image Section...')

    img_url = get_image_link(prompt, size="1024x1024")
    if len(img_url) == 0:
        return 0

    if not os.path.exists(img_path):
        os.makedirs(img_path)
    try:
      headers_fox = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"}
      response = requests.get(img_url, stream=True, headers=headers_fox)
      local_file = open(f'{img_path}/' + keyword + '.jpg', 'wb')
      response.raw.decode_content = True
      shutil.copyfileobj(response.raw, local_file)
      im = Image.open(f'{img_path}/' + keyword + '.jpg')
      resized_im = im.resize((round(im.size[0] * 0.8), round(im.size[1] * 0.8)))
      resized_im.save(f'{img_path}/' + keyword + '.jpg')
      media = {'file': open(f'{img_path}/' + keyword + '.jpg', 'rb')}
      image = requests.post(website_url + '/wp-json/wp/v2/media', headers=headers, files=media)
      img_id = str(json.loads(image.content.decode('utf-8'))['id'])
      return img_id
    except Exception as ops:
        print(f'error : {str(ops)}\n\n')
        return 0



# Category   ***********************************
def create_categories(cat_list, website_url, headers):
    print(f'{datetime.now()} - Working in Category Section...')
    category_ids = []  # Store IDs for all categories

    parent_category_id = 0  # ID for the first (main) category
    for idx, cat_name in enumerate(cat_list):
        id = 0
        is_child = False  # Flag to check if we need to make this category a child

        if len(cat_name) > 0:
            data = {"name": cat_name}
            try:
                # First, check if the category already exists
                cat_exists = False
                cat = requests.get(website_url + '/wp-json/wp/v2/categories', headers=headers, params={'search': cat_name})
                if cat.status_code == 200:
                    cat_data = json.loads(cat.content.decode('utf-8'))
                    for existing_cat in cat_data:
                        if cat_name.lower() == existing_cat['name'].lower():
                            id = str(existing_cat['id'])
                            print(f"Found existing category '{cat_name}' with ID {id}")
                            cat_exists = True
                            if idx == 0:  # First category exists, set it as the parent
                                parent_category_id = id
                            elif idx != 0:  # Second category exists, and we need to check if it's a child
                                is_child = True
                            break

                if not cat_exists:  # If the category doesn't exist
                    # Attempt to create the category
                    cat = requests.post(website_url + '/wp-json/wp/v2/categories', headers=headers, json=data)
                    if cat.status_code == 201:  # Category successfully created
                        id = str(json.loads(cat.content.decode('utf-8'))['id'])
                        print(f"Created new category: {cat_name} with ID {id}")

                        if idx == 0:  # If it's the first category, treat it as the parent
                            parent_category_id = id
                        else:  # If it's the second category, treat it as a child of the first category
                            is_child = True
                    else:
                        print(f"Failed to create category '{cat_name}': {cat.status_code} - {cat.content.decode('utf-8')}")

            except Exception as e:
                print(f"Error handling category '{cat_name}': {e}")
                continue  # Move to the next category if an error occurs

        if id:
            if is_child and parent_category_id:
                # Set the parent category ID for the second category
                category_data = {"parent": parent_category_id}
                requests.post(website_url + f'/wp-json/wp/v2/categories/{id}', headers=headers, json=category_data)
                print(f"Set category '{cat_name}' as child of parent ID {parent_category_id}")

            category_ids.append(id)  # Append the category ID if found or created
        else:
            print(f"Category not found or created: {cat_name}")

    return category_ids

# Outline *********************************

def formated_outline(keyword):
    """Generates an outline for a given keyword."""
    print(f'{datetime.now()} - Working in Outline Section...')

    i = 1
    while True:
        outline_raw = text_render(outline_prompt.replace('<<keyword>>', keyword),
                                  0.9,
                                  5000,
                                  """Zeker! Ik ben een assistent die helpt bij het schrijven van artikelen.
                                     Ik help je om een ​​beste artikelschets te maken.
                                     Ik ben te intelligent, ik speel een rol als een deskundige mens.
                                     Ik zal voldoen aan elke vereiste die je wilt
                                     """)
        i += 1
        if any(keyword in outline_raw.lower() for keyword in ['<h2>', 'rext-render-error']):
            break
    outlines = ""
    for line in outline_raw.replace('<h2>', '---<h2>').replace('<H2>', '---<H2>').split('---'):
        if 'h2' in line.lower() and not any(keyword in line.lower() for keyword in ['introduction', 'objective', 'conclusion', 'overview']):
            outlines += ' '.join(l if '</' in l else l.replace('-', '').strip() + '. ' for l in line.splitlines() if len(l) > 2)
    return outlines


# Content Body ***********************************
def content_body(keyword):
    print(f'{datetime.now()} - Working in content body Section...')
    outline = formated_outline(keyword)
    content_body_data = ''
    for heading in outline.replace('<h2>','---<h2>').split('---'):
        if len(heading) > 1:
            pattern = r"\b\d+\.\d+\b|[.?#@%$&()\[\]=\\/-]"
            heading_html_format = re.sub(pattern, "", heading.replace('</h2>','<h2>---').split('---')[0])
            heading_text_format = heading_html_format.replace('<h2>','').replace('</h2>','').strip().capitalize()
            try:
              topic_to_cover = heading.replace('</h2>','<h2>---').split('---')[1].replace(' -','').strip()
            except:
              topic_to_cover = ''

            # body_img_src = body_img(clean_heading.strip() + ' '+keyword.strip(), bulkmodel, new_directory_path, json_url, headers, img_status)
            para_prompt = paragraph_prompt.replace('<<keyword>>', keyword).replace('<<heading>>', heading_text_format).replace('<<topic_to_cover>>',topic_to_cover)
            section = para_format(text_render(para_prompt,
                                              0.9,
                                              5000,
                                              """Zeker! Ik ben een assistent die artikelen schrijft. Ik help je om artikelparagrafen per deel te maken. Ik ben te intelligent, ik speel de rol van een deskundige menselijke schrijver."""
                                              ))
            content_body_data += heading + section
    print(f'{datetime.now()} - Content body done...')
    return content_body_data


def youtubevid(self,youtube_api):
    print(f'{datetime.now()} - Working in Youtube Section...')
    if len(youtube_api) > 0:
        youtube = build('youtube', 'v3', developerKey=youtube_api.strip())
        try:
            request = youtube.search().list(q=self, part='snippet', type='video', maxResults=1)
            res = request.execute()
            id = res['items'][0]['id']['videoId']
            youtube_url = '<!-- wp:html --><figure  style="text-align: center"><iframe width="640" height="360" src="https://www.youtube.com/embed/' + id + '?rel=0&amp;enablejsapi=1"></iframe></figure><!-- /wp:html --><!-- wp:separator {"align":"center"} --><hr class="wp-block-separator aligncenter"/><!-- /wp:separator -->'
        except Exception as oops:
            youtube_url = ''
            print(f'{datetime.now()} - Youtube api finished...')
        return youtube_url
    else:
        return ''


def generate_keyword(topic):
    prompt = f"""
    Stel één specifiek en relevant long-tail zoekwoord van 4-5 woorden voor op basis van het onderwerp: {topic}. 
    Het zoekwoord moet:
    - In het Nederlands zijn.
    - Gericht zijn op een niche of specifieke doelgroep.
    - Minder competitief en geschikt voor nieuwe of kleinere websites.
    - Direct gerelateerd aan het onderwerp en gebruikersintentie weerspiegelen.

    Geef alleen het zoekwoord terug zonder extra uitleg of interpunctie.
    """
    keyword = text_render(prompt, 1, 100, '', '')
    return keyword.strip()


infinity = 1
post_run = 1
print(f'\n{datetime.now()} - Task started. It will work infinity time without manual closing or Windows crush...\n')
while True:
    topic_path = os.path.join(os.getcwd(), "data/topics.txt")
    with open(topic_path) as location_file:
        topic_info = location_file.readlines()
    topic_list = [x.strip() for x in topic_info if len(x) > 0]

    for topic in topic_list:
        try:
            location_path = os.path.join(os.getcwd(), "data/location.txt")
            with open(location_path) as location_file:
                location_info = location_file.readlines()
            location_list = [x.strip() for x in location_info if len(x) > 0]

            sub_cat_path = os.path.join(os.getcwd(), "data/sub_category.txt")
            with open(sub_cat_path) as cat_file:
                cat_info = cat_file.readlines()
            sub_cat_list = [x.strip() for x in cat_info if len(x) > 0]

            for location in location_list:
                for sub_cat in sub_cat_list:
                    keyword = generate_keyword(f"{topic} {sub_cat} {location} ")
                    print(keyword)
                    if keyword != "text-render-error":
                        print(f'{datetime.now()} - Topic : `{topic}`, location : `{location}`, sub category : `{sub_cat}`')
                        print(f'{datetime.now()} - Keyword ({str(post_run)}) : {keyword}\n')
                        title = text_render(title_prompt.replace('<<keyword>>', keyword), 0.9, 500).replace('"', '')


                        introduction = para_format(text_render(introduction_prompt.replace('<<keyword>>', keyword), 0.9, 1000))
                        conclusion_part = "<h2>Conclusie</h2>" + para_format(text_render(conclusion_prompt.replace('<<keyword>>', keyword), 0.9, 500))


                        post_body = introduction + content_body(keyword) + conclusion_part + youtubevid(keyword, youtube_api)

                        excerpt = text_render(Excerpt.replace('<<keyword>>', keyword), 0.9, 250)

                        image_id = feature_image(keyword, headers, website_url)

                        category_ids = create_categories([location,f"{sub_cat} {location}"], website_url, headers)
                        slug = keyword.replace(' ', '-')

                        # Post Data
                        if not category_ids:  # Check if the list is empty
                            post = {
                                'title': title,
                                'slug': slug,
                                'status': post_status,
                                'content': post_body,
                                'format': 'standard',
                                'excerpt': excerpt,
                                'featured_media': int(image_id)
                            }
                        else:
                            post = {
                                'title': title,
                                'slug': slug,
                                'status': post_status,
                                'content': post_body,
                                'categories': category_ids,  # Use the list of category IDs
                                'format': 'standard',
                                'excerpt': excerpt,
                                'featured_media': int(image_id)
                            }

                        # Posting Request
                        r = requests.post(website_url + '/wp-json/wp/v2/posts', headers=headers, json=post)
                        if r.status_code == 201:
                            print(f'\n{datetime.now()}')
                            print('>>>>> ', f'({post_run})', '.', keyword,
                                  website_url + '/' + slug + '.....  Published **** \n>>>>>  ...\n>>>>>  ...')
                        else:
                            print(f'\n{datetime.now()}')
                            print('>>>>> ', f'({post_run})', '.', keyword, r.status_code, '.....   error **** \n>>>>>  ...\n>>>>>  ...')

                        post_run += 1
                        shutil.rmtree(img_path)
                    else:
                        print(f'{datetime.now()} - OpenAI API-KEY ERROR ..........')
        except:
            pass

    print(f'\n{datetime.now()} - Complete all keyword {infinity} time going to next loop.\nIt will work infinity time without manual closing or Windows crush...\n')
    infinity += 1
