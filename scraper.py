import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import json


service = Service(executable_path="./chromedriver")
driver = webdriver.Chrome(service=service)
k = 0
v = 0


base_url = "https://www.bbcgoodfood.com/recipes/collection/quick-and-easy-family-recipes?page="


all_recipe_links = []


for page_number in range(1, 5):
    url = base_url + str(page_number)
    driver.get(url)
    

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'link')))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    

    link_tags = soup.find_all('a', class_='link d-block')
    
    for link_tag in link_tags:
        link = link_tag['href']
        if link.startswith('/recipes/'):
            full_link = 'https://www.bbcgoodfood.com' + link
            all_recipe_links.append(full_link)


# print(f"Total recipes found: {len(all_recipe_links)}")

def sanitize_title_for_url(title):
    
    return title.lower().replace(' ', '-')


def to_camel_case(title):
    
    words = title.split(' ')
    return words[0].lower() + ''.join(word.capitalize() for word in words[1:])


def matches_title_in_img_url(img_url, sanitized_title):

    img_url_normalized = img_url.lower()

    if sanitized_title in img_url_normalized:
        return True
    camel_case_title = to_camel_case(sanitized_title)
    if camel_case_title in img_url_normalized:
        return True
    return False

def matches_image_by_title(img_title, recipe_title):

    img_title_normalized = re.sub(r'\s+', ' ', img_title.lower()).strip()
    recipe_title_normalized = re.sub(r'\s+', ' ', recipe_title.lower()).strip()

    return recipe_title_normalized in img_title_normalized


all_recipe_data = []


for recipe_link in all_recipe_links:
    # print(f"\nInspecting recipe: {recipe_link}")
    
    driver.get(recipe_link)
    

    recipe_html = driver.page_source
    soup = BeautifulSoup(recipe_html, 'html.parser')
    

    title_tag = soup.find('h1', class_='heading-1')
    title = title_tag.text.strip() if title_tag else "No title found"

    img_tags = soup.find_all('img')


    for img_tag in img_tags:
        img_title = img_tag.get('title', '').strip()
    

        if matches_image_by_title(img_title, title):
            img_url = img_tag.get('src', '')  
            v += 1
            # print(f"Found image URL: {img_url}")
            break

    ingredients_section = soup.find('ul', class_='ingredients-list list')
    if ingredients_section:
        ingredients = [item.get_text(strip=True) for item in ingredients_section.find_all('li')]
    else:
        ingredients = ["No ingredients found"]
    

    method_section = driver.find_elements(By.XPATH, "//h2[text()='Method']")
    if not method_section:
        # print("No method steps found, skipping this recipe.")
        continue 


    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'method-steps__heading')))
    

    method_section = driver.find_element(By.XPATH, "//h2[text()='Method']/following-sibling::ul")
    

    soup3 = BeautifulSoup(driver.page_source, 'html.parser')


    steps_list = soup3.find_all('li', class_='method-steps__list-item')

    steps = []
    for step in steps_list:
        step_heading = step.find('h3', class_='method-steps__item-heading')
        step_text = step.find('div', class_='editor-content')
    
        step_number = step_heading.text.strip() if step_heading else "No step number found"
        instructions = step_text.text.strip() if step_text else "No instructions found"
        steps.append(f"{step_number}: {instructions}")


    nutrition_data = {}
    try:
        nutrition_button = driver.find_element(By.XPATH, """/html/body/div[1]/div[4]/main/div[2]/div/div[3]/div[1]/div[1]/div[2]/div/div/div[1]/div[1]/h2[2]/button""")
        driver.execute_script("arguments[0].scrollIntoView();", nutrition_button)

        html_content2 = driver.page_source
        soup2 = BeautifulSoup(html_content2, 'html.parser')

        nutrition_list = soup2.find('ul', class_='nutrition-list')
        if nutrition_list:
            nutrition_items = nutrition_list.find_all('li', class_='nutrition-list__item')
            for item in nutrition_items:
                label = item.find('span', class_='fw-600 mr-1').text.strip()
                value = item.get_text(strip=True).replace(label, '').strip()
                nutrition_data[label] = value
        
            # print("Nutritional Values:")
            for key, value in nutrition_data.items():
                # print(f"{key}: {value}")
    except Exception:
        # print("Nutrition button not found. Skipping...")


    recipe_data = {
        "recipe_name": title,
        "recipe_image_link": img_url,
        "recipe_ingredients": ingredients,
        "recipe_steps": steps,
        "nutrition_data": nutrition_data
    }
    all_recipe_data.append(recipe_data)
    k += 1


with open('recipe_data.json', 'w') as json_file:
    json.dump(all_recipe_data, json_file, indent=4)


# print(f"Processed {k} recipes.")
# print(v)
driver.quit()

