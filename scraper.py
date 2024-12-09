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
    
    # Wait for the Ingredients tab to be clickable and click it
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[text()="Ingredients"]'))).click()
    
    # Wait for the page to load the ingredients content
    time.sleep(1)  # Adjust if needed
    
    # Get the page source after switching tabs
    recipe_html = driver.page_source
    soup = BeautifulSoup(recipe_html, 'html.parser')
    
    # Extract the recipe title
    title_tag = soup.find('h1', class_='heading-1')
    title = title_tag.text.strip() if title_tag else "No title found"
    
    # Print the recipe title
    print(f"Title: {title}")

# Close the browser after finishing
driver.quit()