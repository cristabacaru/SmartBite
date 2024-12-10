import sqlite3

# connection to the database
connection = sqlite3.connect("database.db")

cursor = connection.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS recipes (\
                recipe_id INTEGER PRIMARY KEY,\
                name TEXT NOT NULL,\
                calories INTEGER,\
                description TEXT,\
                instructions TEXT);")
cursor.execute("CREATE TABLE IF NOT EXISTS ingredients(\
                ingredient_id INTEGER PRIMARY KEY,\
                name TEXT NOT NULL,\
                calories_per_unit REAL,\
                unit TEXT);")
cursor.execute("CREATE TABLE IF NOT EXISTS recipe_ingredients (\
                id INTEGER PRIMARY KEY,\
                recipe_id INTEGER NOT NULL,\
                ingredient_id INTEGER NOT NULL,\
                quantity REAL NOT NULL,\
                unit TEXT,\
                FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id),\
                FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id));")
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
                weight REAL NOT NULL);")
# commit the creation of tables
connection.commit()

#cursor.execute("INSERT INTO users (user_id, name, email, password)\
             #      VALUES (?, ?, ?, ?)", (2, "Ana", "ana@gail.com", "anaaa"))
#cursor.execute("DELETE FROM users WHERE name = ?", ("Ana",))
connection.commit()

connection.close()

