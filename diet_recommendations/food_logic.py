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
from random import uniform as rnd

def read_food_data():
    dataframe = pd.read_csv('../data/dataset_filtered.csv', compression='gzip', header=0)
    food_df = dataframe.copy()
    return food_df

# Example user inputs
# user_input = {
#     'age': 30,
#     'weight': 70,  # in kg
#     'height': 175,  # in cm
#     'gender': 'male',
#     'activity_level': 'Super active',
#     'weight_loss_plan': 'Maintain weight'
# }


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


# print(f"Daily Caloric Needs: {adjusted_caloric_needs}")

def custom_calories(selected_options):

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

    LOW_FACTOR = 0.5
    HIGH_FACTOR = 1.0

    options = {
        'low_fats': max_daily_ingredients['max_daily_fat'] * LOW_FACTOR if 'low_fats' in selected_options else 100,
        'low_saturates': max_daily_ingredients['max_daily_Saturatedfat'] * LOW_FACTOR if 'low_saturates' in selected_options else 13,
        'low_cholesterol': max_daily_ingredients['max_daily_Cholesterol'] * LOW_FACTOR if 'low_cholesterol' in selected_options else 300,
        'low_sodium': max_daily_ingredients['max_daily_Sodium'] * LOW_FACTOR if 'low_sodium' in selected_options else 2300,
        'low_carbs': max_daily_ingredients['max_daily_Carbohydrate'] * LOW_FACTOR if 'low_carbs' in selected_options else 325,
        'high_fiber': max_daily_ingredients['max_daily_Fiber'] * HIGH_FACTOR if 'high_fiber' in selected_options else 30,
        'low_sugar': max_daily_ingredients['max_daily_Sugar'] * LOW_FACTOR if 'low_sugar' in selected_options else 40,
        'high_protein': max_daily_ingredients['max_daily_Protein'] * HIGH_FACTOR if 'high_protein' in selected_options else 150,
    }

    return options

def meal_calories_percentage(number_of_meals):
    if number_of_meals == 3:
        percentage_calories = {'breakfast': 0.5, 'lunch': 0.3, 'dinner': 0.2}
    elif number_of_meals == 4:
        percentage_calories = {'breakfast':0.40,'morning snack':0.05,'lunch':0.30,'dinner':0.25}
    elif number_of_meals == 5:
        percentage_calories = {'breakfast':0.40,'morning snack':0.05,'lunch':0.30,'afternoon snack':0.05,'dinner':0.20}
    
    return percentage_calories


def generate_recommendations(caloric_need, options):

    print('inside the generate_recommendations functions.....')
    
    recommendations = []

    calories_breakdown = meal_calories_percentage(number_of_meals=3)
    print(calories_breakdown)
    
    values = []
    food_df = read_food_data()

    for _, v in options.items():
        values.append(round(v))
    
    print(values)
    
    for meal in calories_breakdown:
        meal_calories = caloric_need * calories_breakdown[meal]
        meal_values = [round(x* calories_breakdown[meal]) for x in values]

        
        if meal == 'breakfast':
            recommend_metrics = [round(meal_calories)]
            recommend_metrics.extend(meal_values)

        elif meal == 'lunch':
            recommend_metrics = [round(meal_calories), round(rnd(20,30)), round(rnd(1,4)), round(rnd(70,90)), round(rnd(400,690)), round(rnd(80,97)), round(rnd(7,12)), round(rnd(7,12)), round(rnd(40,60))]
            # recommend_metrics.extend(meal_values)
        
        elif meal == 'dinner':
            recommend_metrics = [round(meal_calories), round(rnd(10,20)), round(rnd(1,3)), round(rnd(40,60)), round(rnd(300,460)), round(rnd(50,65)), round(rnd(5,8)), round(rnd(5,8)), round(rnd(30,40))]
            # recommend_metrics.extend(meal_values)
        
        
        generator=ml_model(food_df=food_df, nutrients_metrics=recommend_metrics)
        # recommended_recipes=generator.generate().json()['output']
        recommendations.append(generator)
    
    # print(recommendations[0])
    # print([recipe for recipe in recommendations[0]['Name']])
    return recommendations

# generate_recommendations(caloric_need = 1000, options = options)


def generate_recommendations_on_user_form(user_input, selected_options):

    print('inside the generate_recommendations_on_user_form function.....')
    # calculate bmr
    bmr = calculate_bmr(user_input['weight'], user_input['height'], user_input['age'], user_input['gender'])
    print('the Bmr of this person is: ', bmr)
    # Calculate daily caloric needs based on activity level
    daily_caloric_needs = calculate_daily_caloric_need(bmr, user_input['activity_level'])

    print('daily caloric need for this person is: ', daily_caloric_needs)


    # Adjust for weight loss plan
    caloric_need = adjust_for_weight_loss(daily_caloric_needs, user_input['weight_loss_plan'])

    print('adjusted caloric need according to the weight loss plan is: ', caloric_need)

    options = custom_calories(selected_options)

    output_from_model = generate_recommendations(caloric_need, options)

    return output_from_model


def from_slider(metrics):
    print('inside the from_slider function...........')
    food_df = read_food_data()
    foods = ml_model(food_df,nutrients_metrics=metrics)
    return foods

# generate_recommendations(adjusted_caloric_needs, options=options, food_df=food_df)
