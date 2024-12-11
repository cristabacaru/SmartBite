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

def find_recipes_near_calories(target_calories, num_recipes=3, attempts=7):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    results = []
    query = """
    SELECT r1.recipe_id, r1.name, r2.recipe_id, r2.name, r3.recipe_id, r3.name, 
           (r1.calories + r2.calories + r3.calories) AS total_calories
    FROM recipes r1, recipes r2, recipes r3
    WHERE r1.recipe_id < r2.recipe_id AND r2.recipe_id < r3.recipe_id
    ORDER BY ABS(total_calories - ?) ASC
    LIMIT ?;
    """

    for _ in range(attempts):
        cursor.execute(query, (target_calories, num_recipes))
        rows = cursor.fetchall()
        for row in rows:
            recipe_ids = (row[0], row[2], row[4])
            recipe_names = (row[1], row[3], row[5])
            total_calories = row[6]
            results.append((recipe_ids, recipe_names, total_calories))

    connection.close()

    return results

# # Example usage:
# weight = 70  # in kg
# height = 1.75  # in meters
# age = 30  # in years
# gender = 'female'
# goal = 'weight_gain'
# activity_level = 1.375  # Lightly active
# weight_loss_kilos = 5  # weight to lose in kilograms

# # Calculate BMI
# bmi = calculate_bmi(weight, height)
# print(f"BMI: {bmi:.2f}")

# # Calculate recommended calorie intake
# recommended_calories = calculate_calories(weight, height * 100, age, gender, goal, activity_level, weight_loss_kilos)
# print(f"Recommended Calories for {goal}: {recommended_calories:.0f} kcal/day")

# # Find recipes close to recommended calories
# recipe_combinations = find_recipes_near_calories(recommended_calories)
# if recipe_combinations:
#     print("Recommended Recipes:")
#     for i, (ids, names, total_calories) in enumerate(recipe_combinations, 1):
#         print(f"Combination {i}:")
#         for recipe_id, recipe_name in zip(ids, names):
#             print(f"  - ID: {recipe_id}, Name: {recipe_name}")
#         print(f"  Total Calories: {total_calories:.0f} kcal\n")
# else:
#     print("No recipes found.")
