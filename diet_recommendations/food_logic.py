'''1. Collect and Integrate User Inputs

# First, create a way to collect the necessary inputs from users. These inputs will be used to calculate the daily caloric needs and tailor meal recommendations accordingly.
# 2. Calculate Daily Caloric Needs

# Use the inputs to calculate the Basal Metabolic Rate (BMR) and then adjust it according to the weight loss plan.
# Calculating BMR:

#     Mifflin-St Jeor Equation:
#         For men: BMR = 10 * weight (kg) + 6.25 * height (cm) - 5 * age (years) + 5
#         For women: BMR = 10 * weight (kg) + 6.25 * height (cm) - 5 * age (years) - 161

# Adjusting BMR for Activity Level:

#     Sedentary (little or no exercise): Caloric Needs = BMR * 1.2
#     Lightly active (light exercise/sports 1-3 days/week): Caloric Needs = BMR * 1.375
#     Moderately active (moderate exercise/sports 3-5 days/week): Caloric Needs = BMR * 1.55
#     Very active (hard exercise/sports 6-7 days a week): Caloric Needs = BMR * 1.725
#     Super active (very hard exercise/sports & physical job or 2x training): Caloric Needs = BMR * 1.9

# Adjusting for Weight Loss Plan:

#     Mild weight loss (0.25 kg/week): Subtract 250 calories from daily caloric needs.
#     Moderate weight loss (0.5 kg/week): Subtract 500 calories from daily caloric needs.
#     Extreme weight loss (1 kg/week): Subtract 1000 calories from daily caloric needs.

'''
import pandas as pd
from ml_pipeline import ml_model

dataframe = pd.read_csv('../data/dataset_filterd.csv', compression='gzip', header=0)
food_df = dataframe.copy()

def calculate_bmr(weight, height, age, gender):
    if gender == 'male':
        return 10 * weight + 6.25*height - 5*age + 5
    else:
        return 10 * weight + 6.35*height - 5*age - 161
    
def calculate_bmi(height, weight):
    return round(weight / height **2, 2)


def calculate_daily_caloric_need(bmr, activity_level):
    activity_multipliers = {
        'Sedentary': 1.2,
        'Lightly active': 1.375,
        'Moderately active': 1.55,
        'Very active': 1.725,
        'Super active': 1.9
    }

    return bmr * activity_multipliers[activity_level]

def adjust_for_weight_loss(daily_caloric_need, weight_loss_plan):
    adjustment = {
        'Maintain weight': 0,
        'Mild weight loss': -200,
        'Moderate weight loss': -400,
        'Extreme weight loss': -800
    }

    return daily_caloric_need + adjustment[weight_loss_plan]

# Example user inputs
user_input = {
    'age': 30,
    'weight': 70,  # in kg
    'height': 175,  # in cm
    'gender': 'male',
    'activity_level': 'Super active',
    'weight_loss_plan': 'Maintain weight'
}

# calculate bmr
bmr = calculate_bmr(user_input['weight'], user_input['height'], user_input['age'], user_input['gender'])


# Calculate daily caloric needs based on activity level
daily_caloric_needs = calculate_daily_caloric_need(bmr, user_input['activity_level'])

# Adjust for weight loss plan
adjusted_caloric_needs = adjust_for_weight_loss(daily_caloric_needs, user_input['weight_loss_plan'])

print(f"Daily Caloric Needs: {adjusted_caloric_needs}")

max_daily_ingredients = {
    'max_daily_fat': 100,
    'max_daily_Saturatedfat': 13,
    'max_daily_Cholesterol': 300,
    'max_daily_Sodium': 2300,
    'max_daily_Carbohydrate': 325,
    'max_daily_Fiber': 40,
    'max_daily_Sugar': 40,
    'max_daily_Protein': 200
}

LOW_FACTOR = 0.4
HIGH_FACTOR = 0.8

options = {
    'low_fats': max_daily_ingredients['max_daily_fat'] * LOW_FACTOR,
    'low_saturates': max_daily_ingredients['max_daily_Saturatedfat'] * LOW_FACTOR,
    'low_cholestrol': max_daily_ingredients['max_daily_Cholesterol'] * LOW_FACTOR,
    'low_sodium': max_daily_ingredients['max_daily_Sodium'] * LOW_FACTOR,
    'low_carbs': max_daily_ingredients['max_daily_Carbohydrate'] * LOW_FACTOR,
    'high_fiber': max_daily_ingredients['max_daily_Fiber'] * HIGH_FACTOR,
    'low_sugar': max_daily_ingredients['max_daily_Sugar'] * LOW_FACTOR,
    'high_protein': max_daily_ingredients['max_daily_Protein'] * HIGH_FACTOR,
}

print('low carbs....')

print(options['high_protein'])

def meal_calories_percentage(number_of_meals):
    if number_of_meals == 3:
        percentage_calories = {'breakfast': 0.4, 'lunch': 0.35, 'dinner': 0.25}
    elif number_of_meals == 4:
        percentage_calories = {'breakfast':0.40,'morning snack':0.05,'lunch':0.30,'dinner':0.25}
    elif number_of_meals == 5:
        percentage_calories = {'breakfast':0.40,'morning snack':0.05,'lunch':0.30,'afternoon snack':0.05,'dinner':0.20}
    
    return percentage_calories


def generate_recommendations(caloric_need, options, food_df):
    
    recommendations = []

    calories_breakdown = meal_calories_percentage(number_of_meals=3)
    print(calories_breakdown)
    
    values = []
    for _, v in options.items():
        values.append(round(v))
    
    for meal in calories_breakdown:
        meal_calories = caloric_need * calories_breakdown[meal]
        meal_values = [round(x* calories_breakdown[meal]) for x in values]
    
        if meal == 'breakfast':
            recommend_metrics = [round(meal_calories)]
            recommend_metrics.extend(meal_values)

        elif meal == 'lunch':
            recommend_metrics = [round(meal_calories)]
            recommend_metrics.extend(meal_values)
        
        elif meal == 'dinner':
            recommend_metrics = [round(meal_calories)]
            recommend_metrics.extend(meal_values)
        
        
        generator=ml_model(food_df=food_df, nutrients_metrics=recommend_metrics)
        # recommended_recipes=generator.generate().json()['output']
        recommendations.append(generator)
    
    print(recommendations[0])
    print([recipe for recipe in recommendations[0]['Name']])

generate_recommendations(adjusted_caloric_needs, options=options, food_df=food_df)