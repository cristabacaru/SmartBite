import sqlite3
import re

def extract_core_ingredient(ingredient):
    """
    Extract the core name of an ingredient by removing quantities, units, and descriptors.
    """
    # Remove quantities and units
    ingredient = re.sub(r'\b(\d+(\.\d+)?(g|ml|oz|kg|l|tsp|tbsp|cup|slice|packet|can|jar|tub)s?)\b', '', ingredient, flags=re.IGNORECASE)
    # Remove descriptors
    ingredient = re.sub(r'\b(chopped|drained|fresh|dried|finely|grated|plus|extra|for|dusting|optional|large|small|medium)\b', '', ingredient, flags=re.IGNORECASE)
    # Remove non-alphabetic characters
    ingredient = re.sub(r'[^a-zA-Z\s]', '', ingredient)
    # Return lowercase stripped string
    return ingredient.strip().lower()

def find_recipes_by_ingredients(ingredient_list):
    """
    Search for recipes with the most matching ingredients.
    """
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    # Preprocess the ingredient list
    processed_ingredients = [extract_core_ingredient(ing) for ing in ingredient_list]

    # Prepare the results container
    results = []

    # Query to fetch recipes and their ingredients
    query = """
    SELECT r.recipe_id, r.name, GROUP_CONCAT(i.name) AS recipe_ingredients
    FROM recipes r
    JOIN recipe_ingredients ri ON r.recipe_id = ri.recipe_id
    JOIN ingredients i ON ri.ingredient_id = i.ingredient_id
    GROUP BY r.recipe_id;
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    for row in rows:
        recipe_id = row[0]
        recipe_name = row[1]
        recipe_ingredients = row[2].split(',') if row[2] else []

        # Preprocess the recipe ingredients for comparison
        processed_recipe_ingredients = [extract_core_ingredient(ri) for ri in recipe_ingredients]

        # Find matched ingredients
        matched = [
            ing for ing in processed_ingredients
            if any(re.search(rf'\b{re.escape(ing)}\b', ri) for ri in processed_recipe_ingredients)
        ]

        # Determine missing ingredients
        missing = [ing for ing in processed_ingredients if ing not in matched]

        results.append({
            "recipe_id": recipe_id,
            "recipe_name": recipe_name,
            "matched_ingredients": matched,
            "missing_ingredients": missing,
            "matched_count": len(matched)
        })

    # Sort results by the number of matched ingredients in descending order
    results = sorted(results, key=lambda x: x['matched_count'], reverse=True)[:10]

    connection.close()

    return results

# Example usage:
ingredient_list = [
    "chicken",
    "oil",
    "peas"
]

top_recipes = find_recipes_by_ingredients(ingredient_list)

print("Top Recipes:")
for recipe in top_recipes:
    print(f"ID: {recipe['recipe_id']}, Name: {recipe['recipe_name']}")
    print(f"Matched Ingredients: {', '.join(recipe['matched_ingredients'])}")
    print(f"Missing Ingredients: {', '.join(recipe['missing_ingredients'])}")
    print()

