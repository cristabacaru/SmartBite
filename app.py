from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

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
        cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
        db_password = cursor.fetchone()
        connection.commit()
        connection.close()
        if db_password:
            if password == db_password[0]:
                return redirect(url_for('success'))
            else:
                print("incorrect password")
                return redirect(url_for('login'))
        else:
            print("incorrect mail")
            return redirect(url_for('login'))
            
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
        goal = request.form.get('goal')
        agree = request.form.get('agree')

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO users (name, username, email, password, age, gender, caloric_goal, height, weight)\
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (name, username, email, password, age, gender, goal, height, weight))
        connection.commit()
        connection.close()

        # Redirect to a success page or render a response
        return redirect(url_for('success'))
    return render_template('register.html')  # Render the form template

# asta nush daca e necesara
@app.route('/success')
def success():
    return "Registration Successful!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

