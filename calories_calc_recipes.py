import sqlite3

def calculate_bmi(weight, height):
    return weight / (height ** 2)

def calculate_bmr(weight, height, age, gender):
    if gender.lower() == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    elif gender.lower() == 'female':
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    else:
        raise ValueError("Gender must be 'male' or 'female'.")
    
    return bmr

def calculate_tdee(bmr, activity_level):
    if activity_level == 'Sedentary':
        return bmr * 1.2
    elif activity_level == 'Lightly Active':
        return bmr * 1.375
    elif activity_level == 'Moderately Active':
        return bmr * 1.55
    elif activity_level == 'Very Active':
        return bmr * 1.725
    else:
        return bmr * 1

def calculate_calories(weight, height, age, gender, goal, activity_level, weight_loss_kilos):
    bmr = calculate_bmr(weight, height, age, gender)
    tdee = calculate_tdee(bmr, activity_level)

    if goal == 'Maintain Weight':
        return tdee
    elif goal == 'Lose Weight':
        calorie_deficit = 500  # Default deficit
        return tdee - calorie_deficit
    elif goal == 'Gain Weight':
        calorie_surplus = 500  # Default surplus
        return tdee + calorie_surplus
    else:
        raise ValueError("Goal must be 'maintain', 'weight_loss', or 'weight_gain'.")

def find_recipes_near_calories(target_calories, num_recipes=7):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    import random

    for _ in range(num_recipes):
        random_nr = random.randint(1, 93)
        results = []
        query = """
        SELECT r1.recipe_id, r2.recipe_id, r3.recipe_id, 
            (r1.calories + r2.calories + r3.calories) AS total_calories
        FROM recipes r1, recipes r2, recipes r3
        WHERE ? < r1.recipe_id AND r1.recipe_id < r2.recipe_id AND r2.recipe_id < r3.recipe_id
        ORDER BY ABS(total_calories - ?) ASC
        LIMIT ?;
        """

        cursor.execute(query, (random_nr, target_calories, num_recipes))
        rows = cursor.fetchall()
        for row in rows:
            results.append(row[0])
            results.append(row[1])
            results.append(row[2])

    connection.close()

    return results
