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
    return bmr * activity_level


def calculate_calories(weight, height, age, gender, goal, activity_level, weight_loss_kilos):
    bmr = calculate_bmr(weight, height, age, gender)
    tdee = calculate_tdee(bmr, activity_level)

    if goal.lower() == 'maintain':
        return tdee
    elif goal.lower() == 'weight_loss':
        # Caloric deficit for weight loss (500 calories/day is a common recommendation)
        if weight_loss_kilos > 0:
            # Weight loss: generally aim for a 500-1000 kcal/day deficit
            calorie_deficit = 500  # Adjust this based on weight loss goals
            return tdee - calorie_deficit
        else:
            # Default for weight loss without specifying kilos
            calorie_deficit = 500
            return tdee - calorie_deficit
    elif goal.lower() == 'weight_gain':
        # Caloric surplus for weight gain (500 calories/day is common for gaining weight)
        calorie_surplus = 500
        return tdee + calorie_surplus
    else:
        raise ValueError("Goal must be 'maintain', 'weight_loss', or 'weight_gain'.")




# Example usage:
weight = 70  # in kg
height = 1.75  # in meters
age = 30  # in years
gender = 'female'
goal = 'weight_gain'
activity_level = 1.375  # Lightly active
weight_loss_kilos = 5  # weight to lose in kilograms

# Calculate BMI
bmi = calculate_bmi(weight, height)
print(f"BMI: {bmi:.2f}")

# Calculate recommended calorie intake
recommended_calories = calculate_calories(weight, height * 100, age, gender, goal, activity_level, weight_loss_kilos)
print(f"Recommended Calories for {goal}: {recommended_calories:.0f} kcal/day")
