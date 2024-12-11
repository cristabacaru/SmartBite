import sqlite3, json

# connection to the database
connection = sqlite3.connect("database.db")

cursor = connection.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS recipes (\
                recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,\
                name TEXT NOT NULL,\
                calories INTEGER,\
                description TEXT,\
                instructions TEXT,\
                picture TEXT UNIQUE);")
cursor.execute("CREATE TABLE IF NOT EXISTS ingredients(\
                ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,\
                name TEXT NOT NULL UNIQUE);")
cursor.execute("CREATE TABLE IF NOT EXISTS recipe_ingredients (\
                id INTEGER PRIMARY KEY AUTOINCREMENT,\
                recipe_id INTEGER NOT NULL,\
                ingredient_id INTEGER NOT NULL,\
                FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id),\
                FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id),\
                UNIQUE(recipe_id, ingredient_id));")
cursor.execute("CREATE TABLE IF NOT EXISTS users (\
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,\
                name TEXT NOT NULL,\
                username TEXT,\
                email TEXT NOT NULL UNIQUE,\
                password TEXT NOT NULL,\
                age INTEGER NOT NULL,\
                gender TEXT NOT NULL,\
                caloric_goal INTEGER NOT NULL,\
                height REAL NOT NULL,\
                weight REAL NOT NULL,\
                weight_goal REAL NOT NULL,\
                activity TEXT NOT NULL);")
# commit the creation of tables
connection.commit()

with open('recipe_data.json', 'r') as file:
    recipe_data = json.load(file)

for recipe in recipe_data:
    if 'kcal' not in recipe['nutrition_data']:
        continue
    instructions = ""
    for step in recipe['recipe_steps']:
        instructions = instructions + step + '\n'
    description = ""
    for info in recipe['nutrition_data']:
        description = description + info + ': ' + recipe['nutrition_data'][info] + '\n'
    cursor.execute("INSERT OR IGNORE INTO recipes (name, calories, description, instructions, picture)\
                 VALUES (?, ?, ?, ?, ?)", (recipe['recipe_name'], recipe['nutrition_data']['kcal'], description, instructions, recipe['recipe_image_link']))
    connection.commit()
    recipe_id = cursor.lastrowid

    for ingredient in recipe['recipe_ingredients']:
        cursor.execute("INSERT OR IGNORE INTO ingredients (name) VALUES (?)", (ingredient,))
        connection.commit()

        cursor.execute("SELECT ingredient_id FROM ingredients WHERE name = ?", (ingredient,))
        ingredient_id = cursor.fetchone()[0]

        cursor.execute("INSERT OR IGNORE INTO recipe_ingredients (recipe_id, ingredient_id) VALUES (?, ?)", (recipe_id, ingredient_id))
        connection.commit()





# recipe_name = "Spaghetti Carbonara"
# calories = 600
# description = "A classic Italian pasta dish with eggs, cheese, pancetta, and pepper."
# instructions = "Boil pasta, fry pancetta, combine with egg mixture, and serve with cheese and pepper."
# picture = "carbonara.jpg"

# # Insert Recipe
# cursor.execute("INSERT OR IGNORE INTO recipes (name, calories, description, instructions, picture)\
#                 VALUES (?, ?, ?, ?, ?)", (recipe_name, calories, description, instructions, picture))
# connection.commit()
# recipe_id = cursor.lastrowid

# # Ingredients for the Recipe
# ingredients_name = [
#     ("Pasta",),               # 1
#     ("Pancetta",),            # 2
#     ("Eggs",),                # 3
#     ("Parmesan Cheese",),     # 4
#     ("Black Pepper",),        # 5
#     ("Salt",)                 # 6
# ]

# # Insert Ingredients
# cursor.executemany("INSERT OR IGNORE INTO ingredients (name) VALUES (?)", ingredients_name)
# connection.commit()

# # Add Recipe Ingredients
# recipe_ingredients = [
#     (recipe_id, 1, 400, "grams"),  # Pasta
#     (recipe_id, 2, 100, "grams"),  # Pancetta
#     (recipe_id, 3, 4, "units"),    # Eggs
#     (recipe_id, 4, 100, "grams"),  # Parmesan Cheese
#     (recipe_id, 5, 1, "teaspoon"), # Black Pepper
#     (recipe_id, 6, 1, "teaspoon")  # Salt
# ]

# # Insert Recipe Ingredients
# cursor.executemany("INSERT OR IGNORE INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit)\
#                     VALUES (?, ?, ?, ?)", recipe_ingredients)
# connection.commit()

connection.close()

