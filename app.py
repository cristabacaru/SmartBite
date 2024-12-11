from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

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

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (name, username, email, password, age, gender, caloric_goal, height, weight, weight_goal, activity)\
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (name, username, email, password, age, gender, goal, height, weight, weight_goal, activity))
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
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
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
            'image_url': row[5],
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

    
@app.route('/browse_recipes')
def browse_recipes():
    return render_template('browse_recipes.html')

@app.route('/meal_plan')
def meal_plan():
    import math
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM recipes LIMIT 21")  # Fetch exactly 21 recipes
    rows = cursor.fetchall()

    user_id = session['user_id']

    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user_info = cursor.fetchone()
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
        meal_type = ["Breakfast", "Lunch", "Dinner"][i % 3]  # Cycle through meal types
        if day_index < len(weekdays):  # Ensure we don't exceed available days
            if weekdays[day_index] not in weekly_meals:
                weekly_meals[weekdays[day_index]] = []

            meal_card = {
                'id': row[0],
                'title': f"{meal_type}",  # Use meal type for title
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
        connection.close()

    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user_info = cursor.fetchone()
    connection.commit()
    connection.close()
    return render_template('profile.html', user_info=user_info)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

