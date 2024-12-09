import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Setup ChromeDriver
service = Service(executable_path="./chromedriver")
driver = webdriver.Chrome(service=service)
k = 0
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

# Now let's inspect each recipe page
for recipe_link in all_recipe_links:
    print(f"\nInspecting recipe: {recipe_link}")
    
    driver.get(recipe_link)
    
    # # Get the page source after switching tabs
    recipe_html = driver.page_source
    soup = BeautifulSoup(recipe_html, 'html.parser')
    
    # Extract the recipe title
    title_tag = soup.find('h1', class_='heading-1')
    title = title_tag.text.strip() if title_tag else "No title found"
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
    html_content = """
            <picture class="image__picture" width="440" height="399.52000000000004">
            <source type="image/webp" sizes="(min-width: 768px) 300px,(min-width: 544px) 556px,calc(100vw - 20px)" srcset="https://images.immediate.co.uk/production/volatile/sites/30/2020/08/butter-bean-chorizo-stew-c630c75.jpg?quality=90&amp;webp=true&amp;resize=300,272 300w,https://images.immediate.co.uk/production/volatile/sites/30/2020/08/butter-bean-chorizo-stew-c630c75.jpg?quality=90&amp;webp=true&amp;resize=375,341 375w,https://images.immediate.co.uk/production/volatile/sites/30/2020/08/butter-bean-chorizo-stew-c630c75.jpg?quality=90&amp;webp=true&amp;resize=440,400 440w">
            <source sizes="(min-width: 768px) 300px,(min-width: 544px) 556px,calc(100vw - 20px)" srcset="https://images.immediate.co.uk/production/volatile/sites/30/2020/08/butter-bean-chorizo-stew-c630c75.jpg?quality=90&amp;resize=300,272 300w,https://images.immediate.co.uk/production/volatile/sites/30/2020/08/butter-bean-chorizo-stew-c630c75.jpg?quality=90&amp;resize=375,341 375w,https://images.immediate.co.uk/production/volatile/sites/30/2020/08/butter-bean-chorizo-stew-c630c75.jpg?quality=90&amp;resize=440,400 440w">
            <img class="image__img" src="https://images.immediate.co.uk/production/volatile/sites/30/2020/08/butter-bean-chorizo-stew-c630c75.jpg?quality=90&amp;resize=440,400" alt="Butter bean &amp; chorizo stew" data-item-name="Butter bean &amp; chorizo stew" title="Butter bean &amp; chorizo stew" style="aspect-ratio:1 / 0.908;object-fit:cover" loading="eager" width="440" height="399.52000000000004">
            </picture>
            """



    # Find the <img> tag with the 'class' attribute containing 'image__img'
    img_tag = soup.find('img', class_='image__img')

# Extract the 'src' attribute
    if img_tag:
        image_url = img_tag['src']
        print(f"Image URL: {image_url}")
    else:
        print("No image URL found.")
    try:
        nutrition_button = driver.find_element(By.XPATH, """/html/body/div[1]/div[4]/main/div[2]/div/div[3]/div[1]/div[1]/div[2]/div/div/div[1]/div[1]/h2[2]/button""")
        # Scroll to the Nutrition button
        # Scroll to the button
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
print(k)
driver.quit()