from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from calories_calc_recipes import *
from ingredient_search import *

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        password = request.form.get('password')

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        connection.commit()
        connection.close()
        if user:
            if password == user[4]:
                session['user_id'] = user[0]
                return redirect(url_for('home_logged_in'))
            else:
                return render_template('login.html', error="Invalid email or password")
        else:
           return render_template('login.html', error="Invalid email or password")
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Extract data from the form
        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        age = request.form.get('age')
        gender = request.form.get('gender')
        height = request.form.get('height')
        weight = request.form.get('weight')
        weight_goal = request.form.get('weight_goal')
        goal = request.form.get('goal')
        activity = request.form.get('activity')
        agree = request.form.get('agree')

        recommended_calories = calculate_calories(float(weight), float(height), float(age), gender, goal, activity, abs(float(weight)-float(weight_goal)))
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (name, username, email, password, age, gender, caloric_goal, height, weight, weight_goal, activity, recommended_calories)\
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (name, username, email, password, age, gender, goal, height, weight, weight_goal, activity, recommended_calories))
        connection.commit()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        connection.close()

        # Redirect to a success page or render a response
        session['user_id'] = user[0]
        return redirect(url_for('home_logged_in'))
    return render_template('register.html')  # Render the form template

@app.route('/home')
def home_logged_in():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM recipes")
    rows = cursor.fetchall()

    user_id = session['user_id']

    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user_info = cursor.fetchone()
    connection.commit()
    connection.close()

    # Generate a list of cards
    all_cards = []
    for row in rows:
        card = {
            'id': row[0],
            'title': row[1],
            'description': row[3],
            'image_url': row[5],  # Use modulo for image recycling
            'link': '#'
        }
        all_cards.append(card)

    # Pagination logic
    per_page = 21
    page = int(request.args.get('page', 1))  # Get the current page, default to 1
    start = (page - 1) * per_page
    end = start + per_page
    paginated_cards = all_cards[start:end]
    total_pages = -(-len(all_cards) // per_page)  # Ceiling division for total pages

    return render_template(
        'home_logged_in.html',
        cards=paginated_cards,
        current_page=page,
        total_pages=total_pages,
        user_info=user_info
    )

    
@app.route('/browse_recipes', methods=['GET', 'POST'])
def browse_recipes():
    # Handle `finalTags` from POST or GET
    if request.method == 'POST':
        final_tags = request.form.get('finalTags', '')
    else:
        final_tags = request.args.get('finalTags', '')

    tags_list = final_tags.split(',') if final_tags else []

    # Fetch recipes based on tags
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    recipes = find_recipes_by_ingredients(tags_list)
    rows = []
    for recipe in recipes:
        cursor.execute("SELECT * FROM recipes WHERE recipe_id = ?;", (recipe['recipe_id'],))
        row = cursor.fetchone()
        if row:
            row = list(row)
            row.append(recipe['missing_ingredients'])
            rows.append(row)
    connection.close()

    # Generate card details
    all_cards = []
    for row in rows:
        card = {
            'id': row[0],
            'title': row[1],
            'description': row[3],
            'image_url': row[5],
            'link': '#',
            'missing_ingredients': row[6]
        }
        all_cards.append(card)

    # Pagination logic
    per_page = 21
    page = int(request.args.get('page', 1))
    start = (page - 1) * per_page
    end = start + per_page
    paginated_cards = all_cards[start:end]
    total_pages = -(-len(all_cards) // per_page)  # Ceiling division

    return render_template(
        'browse_recipes.html',
        cards=paginated_cards,
        current_page=page,
        total_pages=total_pages,
        finalTags=final_tags,  # Pass `finalTags` back to the template
    )

@app.route('/meal_plan')
def meal_plan():
    import math

    user_id = session['user_id']
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user_info = cursor.fetchone()
    connection.close()

    recipe_ids = find_recipes_near_calories(user_info[12])

    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    rows = []
    for recipe in recipe_ids:
        cursor.execute(f"SELECT * FROM recipes WHERE recipe_id = ?;", (recipe,))
        rows.append(cursor.fetchone())
    connection.commit()
    connection.close()
    # Define weekday names
    weekdays = [
        "Mindful Monday Meals",
        "Tasty Tuesday Treats",
        "Wellness Wednesday",
        "Thoughtful Thursday Plates",
        "Feel-Good Friday Feasts",
        "Satisfying Saturday Selections",
        "Simple Sunday Suppers"
    ]
    # Group recipes into sets of three for each day
    weekly_meals = {}
    for i, row in enumerate(rows):
        day_index = i // 3  # Determine which day this recipe belongs to
        if day_index < len(weekdays):  # Ensure we don't exceed available days
            if weekdays[day_index] not in weekly_meals:
                weekly_meals[weekdays[day_index]] = []
            meal_card = {
                'id': row[0],
                'title': row[1],  # Use meal type for title
                'description': row[3],
                'image_url': row[5],
                'link': '#'
            }
            weekly_meals[weekdays[day_index]].append(meal_card)
    return render_template(
        'meal_plan.html',
        weekly_meals=weekly_meals,
        user_info=user_info
    )

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session['user_id']
    if request.method == 'POST':
        # Extract data from the form
        username = request.form.get('username')
        age = request.form.get('age')
        height = request.form.get('height')
        weight = request.form.get('weight')
        weight_goal = request.form.get('weight_goal')
        goal = request.form.get('goal')
        activity = request.form.get('activity')

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("UPDATE users\
                        SET username = ?, age = ?, caloric_goal = ?, height = ?, weight = ?, weight_goal = ?, activity = ?\
                        WHERE user_id = ?;", (username, age, goal, height, weight, weight_goal, activity, user_id))
        connection.commit()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user_info = cursor.fetchone()
        recommended_calories = calculate_calories(float(user_info[9]), float(user_info[8]), float(user_info[5]), user_info[6], user_info[7], user_info[11], abs(float(user_info[9])-float(user_info[10])))
        cursor.execute("UPDATE users\
                        SET recommended_calories = ?\
                        WHERE user_id = ?;", (recommended_calories, user_id))
        connection.commit()
        connection.close()

    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user_info = cursor.fetchone()
    connection.commit()
    connection.close()
    return render_template('profile.html', user_info=user_info)

@app.route('/recipe')
def recipe():
    recipe_id = request.args.get('id')  # Get the recipe ID from the query parameters
    if not recipe_id:
        return redirect(url_for('home_logged_in'))  # Redirect if no ID is provided

    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM recipes WHERE recipe_id = ?", (recipe_id,))
    recipe_data = cursor.fetchone()
    connection.commit()

    cursor.execute("SELECT i.name AS recipe_ingredient\
                    FROM recipes r\
                    JOIN recipe_ingredients ri ON r.recipe_id = ri.recipe_id\
                    JOIN ingredients i ON ri.ingredient_id = i.ingredient_id\
                    WHERE r.recipe_id = ?;", (recipe_id,))
    recipe_ingredients = cursor.fetchall()
    ingredients = [item[0] for item in recipe_ingredients]
    connection.close()

    if not recipe_data:
        return render_template('404.html'), 404  # Show a 404 page if recipe not found

    return render_template('recipe.html', recipe=recipe_data, ingredients=ingredients)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)