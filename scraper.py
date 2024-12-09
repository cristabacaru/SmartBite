import requests
from bs4 import BeautifulSoup

# URL-ul de bază al paginii
base_url = "https://www.bbcgoodfood.com/recipes/collection/quick-and-easy-family-recipes?page="

# Lista pentru a stoca toate linkurile rețetelor
all_recipe_links = []

# Iterăm prin mai multe pagini
for page_number in range(1, 5):  # În acest caz, vom prelua primele 3 pagini
    url = base_url + str(page_number)
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Găsim toate elementele <a> cu clasa "link d-block"
        link_tags = soup.find_all('a', class_='link d-block')

        for link_tag in link_tags:
            link = link_tag['href']  # Extragem link-ul din atributul href
            if link.startswith('/recipes/'):
                full_link = 'https://www.bbcgoodfood.com' + link  # Link relativ - completăm cu domeniul
                all_recipe_links.append(full_link)

# Afișăm numărul total de rețete găsite și toate link-urile
print(f"Numărul total de rețete găsite: {len(all_recipe_links)}")
for recipe_link in all_recipe_links:
    print(recipe_link)
