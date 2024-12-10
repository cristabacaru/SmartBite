import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re

# Setup ChromeDriver
service = Service(executable_path="./chromedriver")
driver = webdriver.Chrome(service=service)
k = 0
v = 0

# Base URL for the recipe collection
base_url = "https://www.bbcgoodfood.com/recipes/collection/quick-and-easy-family-recipes?page="

# List to store all recipe links
all_recipe_links = []

# Iterate through pages
for page_number in range(1, 5):  # Change range as per your need
    url = base_url + str(page_number)
    driver.get(url)
    
    # Wait for page to load and find all recipe links
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'link')))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Find all <a> tags with class 'link d-block'
    link_tags = soup.find_all('a', class_='link d-block')
    
    for link_tag in link_tags:
        link = link_tag['href']
        if link.startswith('/recipes/'):
            full_link = 'https://www.bbcgoodfood.com' + link  # Complete relative link
            all_recipe_links.append(full_link)

# Print the total number of recipe links found
print(f"Total recipes found: {len(all_recipe_links)}")

def sanitize_title_for_url(title):
    # Convert to lowercase and replace spaces with hyphens for URL compatibility
    return title.lower().replace(' ', '-')

# Function to convert a string to camel case
def to_camel_case(title):
    # Remove spaces and capitalize each word (except the first one)
    words = title.split(' ')
    return words[0].lower() + ''.join(word.capitalize() for word in words[1:])

# Function to check if a sanitized title exists in an image URL, considering case insensitivity and camel case
def matches_title_in_img_url(img_url, sanitized_title):
    # Normalize the image URL by making it lowercase
    img_url_normalized = img_url.lower()

    # Check for case-insensitive match, sanitized title, and camel case variations
    if sanitized_title in img_url_normalized:
        return True
    camel_case_title = to_camel_case(sanitized_title)
    if camel_case_title in img_url_normalized:
        return True
    return False

def matches_image_by_title(img_title, recipe_title):
    # Normalize both titles by converting to lowercase and removing extra spaces
    img_title_normalized = re.sub(r'\s+', ' ', img_title.lower()).strip()
    recipe_title_normalized = re.sub(r'\s+', ' ', recipe_title.lower()).strip()
    # Check if the sanitized recipe title is part of the image title
    return recipe_title_normalized in img_title_normalized


# Now let's inspect each recipe page
for recipe_link in all_recipe_links:
    print(f"\nInspecting recipe: {recipe_link}")
    
    driver.get(recipe_link)
    
    # Get the page source after switching tabs
    recipe_html = driver.page_source
    soup = BeautifulSoup(recipe_html, 'html.parser')
    
    # Extract the recipe title
    title_tag = soup.find('h1', class_='heading-1')
    title = title_tag.text.strip() if title_tag else "No title found"

    img_tags = soup.find_all('img')

# Loop through all image tags to find the one that matches the title
    for img_tag in img_tags:
        img_title = img_tag.get('title', '').strip()  # Extract title attribute
    
    # If the image title matches the recipe title
        if matches_image_by_title(img_title, title):
            img_url = img_tag.get('src', '')  # Extract image URL
            v += 1
            print(f"Found image URL: {img_url}")
            break
            
    
    # Extract the ingredients
    ingredients_section = soup.find('ul', class_='ingredients-list list')
    if ingredients_section:
        # Extract all list items (<li>) inside the ingredients list
        ingredients = [item.get_text(strip=True) for item in ingredients_section.find_all('li')]
    else:
        ingredients = ["No ingredients found"]
    
    # Print the recipe title and ingredients
    print(f"Title: {title}")
    print("Ingredients:")
    for ingredient in ingredients:
        print(f"- {ingredient}")
    
    # Check for the presence of the Method section
    method_section = driver.find_elements(By.XPATH, "//h2[text()='Method']")
    if not method_section:
        print("No method steps found, skipping this recipe.")
        continue  # Skip to the next recipe if "Method" is not found

    # Wait for the "Method" section to be present
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'method-steps__heading')))
    
    # Find the entire "Method" section starting from the heading
    method_section = driver.find_element(By.XPATH, "//h2[text()='Method']/following-sibling::ul")
    
    # Get the page source and parse it with BeautifulSoup
    soup3 = BeautifulSoup(driver.page_source, 'html.parser')

    # Find all list items (steps) under the "Method" section
    steps_list = soup3.find_all('li', class_='method-steps__list-item')

    # Extract and print each step
    print("Recipe Steps:")
    for step in steps_list:
        step_heading = step.find('h3', class_='method-steps__item-heading')
        step_text = step.find('div', class_='editor-content')
    
        # Extract step number (step 1, step 2, etc.)
        step_number = step_heading.text.strip() if step_heading else "No step number found"
    
        # Extract step instructions (if available)
        instructions = step_text.text.strip() if step_text else "No instructions found"
    
        # Print the step number and instructions
        print(f"{step_number}: {instructions}")

    try:
        # Check if Nutrition section exists
        nutrition_button = driver.find_element(By.XPATH, """/html/body/div[1]/div[4]/main/div[2]/div/div[3]/div[1]/div[1]/div[2]/div/div/div[1]/div[1]/h2[2]/button""")
        # Scroll to the Nutrition button
        driver.execute_script("arguments[0].scrollIntoView();", nutrition_button)

        html_content2 = driver.page_source  # Fetch the current page's source

        # Parse with BeautifulSoup
        soup2 = BeautifulSoup(html_content2, 'html.parser')

        # Find the Nutrition section
        nutrition_list = soup2.find('ul', class_='nutrition-list')
        if nutrition_list:
            # Extract all nutritional items
            nutrition_items = nutrition_list.find_all('li', class_='nutrition-list__item')
            nutrition_data = {}
            for item in nutrition_items:
                # Extract the label and value
                label = item.find('span', class_='fw-600 mr-1').text.strip()
                value = item.get_text(strip=True).replace(label, '').strip()
                nutrition_data[label] = value
        
            # Print the extracted nutrition data
            print("Nutritional Values:")
            for key, value in nutrition_data.items():
                print(f"{key}: {value}")
        k += 1
    except Exception:
        print("Nutrition button not found. Skipping...")
        continue  # Skip to the next recipe

# Close the browser after finishing
print(f"Processed {k} recipes.")
print(v)
driver.quit()
