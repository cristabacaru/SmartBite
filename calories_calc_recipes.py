import sqlite3, random

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

    unique_recipes = set()
    attempts = 0
    max_attempts = 100  # To prevent infinite loops in case of insufficient unique recipes
    calorie_range_step = 50  # Incremental step to widen the calorie range
    current_range = calorie_range_step

    while len(unique_recipes) < num_recipes * 3 and attempts < max_attempts:
        attempts += 1
        random_nr = random.randint(1, 93)

        query = """
        SELECT r1.recipe_id, r2.recipe_id, r3.recipe_id, 
            (r1.calories + r2.calories + r3.calories) AS total_calories
        FROM recipes r1, recipes r2, recipes r3
        WHERE ? < r1.recipe_id AND r1.recipe_id < r2.recipe_id AND r2.recipe_id < r3.recipe_id
        AND ABS((r1.calories + r2.calories + r3.calories) - ?) <= ?
        ORDER BY ABS(total_calories - ?) ASC
        LIMIT ?;
        """

        cursor.execute(query, (random_nr, target_calories, current_range, target_calories, num_recipes))
        rows = cursor.fetchall()

        for row in rows:
            unique_recipes.add(row[0])
            unique_recipes.add(row[1])
            unique_recipes.add(row[2])

            # Stop early if we've collected enough unique recipes
            if len(unique_recipes) >= num_recipes * 3:
                break

        # Expand the calorie range if not enough recipes are found
        if len(unique_recipes) < num_recipes * 3:
            current_range += calorie_range_step

    # Fallback: Select individual recipes if needed to reach 21 unique recipes
    if len(unique_recipes) < num_recipes * 3:
        query = """
        SELECT recipe_id
        FROM recipes
        WHERE recipe_id NOT IN ({})
        ORDER BY ABS(calories - ?) ASC
        LIMIT ?;
        """.format(",".join(map(str, unique_recipes)))
        
        cursor.execute(query, (target_calories, (num_recipes * 3) - len(unique_recipes)))
        rows = cursor.fetchall()
        for row in rows:
            unique_recipes.add(row[0])

    connection.close()

    # Return exactly 21 unique recipes if possible
    return list(unique_recipes)[:num_recipes * 3]