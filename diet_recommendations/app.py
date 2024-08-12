from flask import Flask, render_template, request, jsonify
from get_food_images import get_images_links
from config import Config
from models import User, db
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
import bcrypt
from food_logic import from_slider, generate_recommendations_on_user_form
from get_food_images import get_images_links

# Convert the string representation to a list
import ast 


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
# Initialize Flask-Migrate
migrate = Migrate(app, db)

@app.route('/')
def index():
    return render_template('login_register.html')

@app.route('/add_user', methods = ['POST'])
def add_user():
    data = request.get_json()
    username = data['username']
    password = data['password']

    if not username or not password:
        return jsonify({'message': 'Username or password required..'}), 400
    
    hashed_pwd = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # check if user already exists:
    existing_user = User.query.filter_by(username = username).first()

    if existing_user:
        return jsonify({'message': 'user already exists..'}), 400
    
    new_user = User(username = data['username'], password = hashed_pwd)

    try: 
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': f'User {username} added successfully!'})
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'error': 'Database error!', 'details': str(e)}), 500
    

@app.route('/get_users', methods = ['GET'])
def get_user():
    users = User.query.all()
    print(users)
    return jsonify([user.to_dict() for user in users])


@app.route('/login', methods = ['POST'])
def user_login():
    data = request.form
    username = data['username']
    password = data['password']

    if not username or not password:
        return jsonify({'message': 'username or password required'}), 400
    
    user = User.query.filter_by(username = username).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password):
        print('username and password matched....')
        return render_template('user_info.html')
    else:
        return jsonify({'message': 'username or password incorrect..'}), 401



@app.route('/food-images')
def get_food():
    return get_images_links("virgin pina colada")


@app.route('/get_custom_values')
def get_values():
    return render_template('slider.html')

@app.route('/user_info')
def user_info_form():
    return render_template('user_info.html')


@app.route('/get_recommendations_form', methods = ['POST'])
def get_recommendations_form():
    data = request.form
    # print(data)
    print('age and height.................')
    age = int(data['age'])
    height = int(data['height'])
    weight = int(data['weight'])
    gender = data['gender']
    activity_level = data['activity_level']
    weight_loss_plan = data['weight_loss_plan']

    selected_options = []
    
    low_carbs = data.get('low_carbs', 'not_selected')
    low_saturates = data.get('low_saturates', 'not_selected')
    low_cholesterol = data.get('low_cholesterol', 'not_selected')
    low_sodium = data.get('low_sodium', 'not_selected')
    low_fats = data.get('low_fats', 'not_selected')
    high_fiber = data.get('high_fiber', 'not_selected')
    low_sugar = data.get('low_sugar', 'not_selected')
    high_protein = data.get('high_protein', 'not_selected')
    
    checkbox_lists = [low_fats, low_saturates, low_cholesterol, low_sodium, low_carbs, high_fiber, high_protein, low_sugar]

    for items in checkbox_lists:
        if items != 'not_selected':
            selected_options.append(items)
    
    print(selected_options)
    
    print('inside the get_recommendations_form function: ')

    # calculate BMI
    height_in_m = height / 100
    bmi = round(weight / height_in_m **2, 2)
    print('The BMI is: ',  bmi)

    if bmi<18.5:
        category='Underweight'
        color='red'
    elif 18.5<=bmi<25:
        category='Normal'
        color='green'
    elif 25<=bmi<30:
        category='Overweight'
        color='yellow'
    else:
        category='Obesity'    
        color='red'
    
    bmi_result = [{'bmi': bmi,'category': category, 'color': color} ]

    print('Bmi result: ', bmi_result)

    # Now For BMR
    if gender == 'male':
        bmr = 10 * weight + 6.25*height - 5*age + 5
    else:
        bmr = 10 * weight + 6.35*height - 5*age - 161
    
    activity_multipliers = {
        'Sedentary': 1.2,
        'Lightly active': 1.375,
        'Moderately active': 1.55,
        'Very active': 1.725,
        'Super active': 1.9
    }

    daily_caloric_need = bmr * activity_multipliers[activity_level]
    
    adjustment = {
        'Maintain weight': 0,
        'Mild weight loss': -200,
        'Moderate weight loss': -400,
        'Extreme weight loss': -800
    }

    adjust_according_to_plan = daily_caloric_need + adjustment[weight_loss_plan]

    print('Your Daily Caloric need is: ', daily_caloric_need)

    print('Your Daily Caloric need according to your plan is: ', adjust_according_to_plan)

    caloric_info = [{'daily_caloric_need': round(daily_caloric_need,0), 'bmr': round(bmr,0), 'adjust_according_to_plan': round(adjust_according_to_plan,0), 'weight_loss_plan': weight_loss_plan}]

    recommendations = generate_recommendations_on_user_form(user_input= {
        'age': age,
        'weight': weight,
        'height': height,
        'gender': gender,
        'activity_level': activity_level,
        'weight_loss_plan': weight_loss_plan
    }, selected_options= selected_options)

    # print(type(recommendations))
    # print('**********************')
    breakfast = recommendations[0].to_dict(orient = 'records')
    lunch = recommendations[1].to_dict(orient = 'records')
    dinner = recommendations[2].to_dict(orient = 'records')
    
    # ingredients_breakfast = [items['RecipeIngredientParts'].strip('c()').replace('"', '').split(', ') for items in breakfast]
    # ingredients_lunch = [items['RecipeIngredientParts'].strip('c()').replace('"', '').split(', ') for items in lunch]
    # ingredients_dinner = [items['RecipeIngredientParts'].strip('c()').replace('"', '').split(', ') for items in dinner]


    # for i in range(len(breakfast)):
    #     breakfast[i]['RecipeIngredientParts'] = ingredients_breakfast[i]
    #     lunch[i]['RecipeIngredientParts'] = ingredients_lunch[i]
    #     dinner[i]['RecipeIngredientParts'] = ingredients_dinner[i]
    # breakfast_items = []
    

    for i in range(len(breakfast)):
        breakfast[i]['Images'] = ast.literal_eval(breakfast[i]['Images'])
        lunch[i]['Images'] = ast.literal_eval(lunch[i]['Images'])
        dinner[i]['Images'] = ast.literal_eval(dinner[i]['Images'])

        breakfast[i]['RecipeIngredientParts'] = ast.literal_eval(breakfast[i]['RecipeIngredientParts'])
        lunch[i]['RecipeIngredientParts'] = ast.literal_eval(lunch[i]['RecipeIngredientParts'])
        dinner[i]['RecipeIngredientParts'] = ast.literal_eval(dinner[i]['RecipeIngredientParts'])

        breakfast[i]['RecipeInstructions'] = ast.literal_eval(breakfast[i]['RecipeInstructions'])
        lunch[i]['RecipeInstructions'] = ast.literal_eval(lunch[i]['RecipeInstructions'])
        dinner[i]['RecipeInstructions'] = ast.literal_eval(dinner[i]['RecipeInstructions'])

    # for i in range(len(breakfast)):
    #     breakfast[i]['RecipeIngredientParts'] = ast.literal_eval(breakfast[i]['RecipeIngredientParts'])
    #     lunch[i]['RecipeIngredientParts'] = ast.literal_eval(lunch[i]['RecipeIngredientParts'])
    #     dinner[i]['RecipeIngredientParts'] = ast.literal_eval(dinner[i]['RecipeIngredientParts'])

    # for i in range(len(breakfast)):
    #     breakfast[i]['RecipeInstructions'] = ast.literal_eval(breakfast[i]['RecipeInstructions'])
    #     lunch[i]['RecipeInstructions'] = ast.literal_eval(lunch[i]['RecipeInstructions'])
    #     dinner[i]['RecipeInstructions'] = ast.literal_eval(dinner[i]['RecipeInstructions'])

    for meals in breakfast:
        
        if meals['Images'][0] == 'https://static.vecteezy.com/system/resources/previews/005/337/799/original/icon-image-not-found-free-vector.jpg':
            meals['Images'][0] = get_images_links(meals['Name'])
            
    
    for meals in lunch:
        
        if meals['Images'][0] == 'https://static.vecteezy.com/system/resources/previews/005/337/799/original/icon-image-not-found-free-vector.jpg':
            meals['Images'][0] = get_images_links(meals['Name'])
            
    
    for meals in dinner:
        
        if meals['Images'][0] == 'https://static.vecteezy.com/system/resources/previews/005/337/799/original/icon-image-not-found-free-vector.jpg':
            meals['Images'][0] = get_images_links(meals['Name'])
            


    return render_template('output.html', meals = [breakfast, lunch, dinner, bmi_result, caloric_info])



@app.route('/get_recommendations', methods = ['POST'])
def get_recommendations():
    data = request.get_json()
    print('Data from the slider are: -------------> ')
    calories = int(data['calories'])
    fat = int(data['fat'])
    saturatedFats = int(data['saturatedFats'])
    protein = int(data['protein'])
    fiber = int(data['fiber'])
    cholesterol = int(data['cholesterol'])
    sugar = int(data['sugar'])
    carbs = int(data['carbohydrate'])
    sodium = int(data['sodium'])

    metrics = [calories, fat, saturatedFats, cholesterol, sodium, carbs, fiber, sugar, protein]
    
    print('values from slider...>')
    print(metrics)

    recommendations = from_slider(metrics= metrics)
    recommendations = recommendations.to_dict(orient = 'records')

    for i in range(len(recommendations)):
        recommendations[i]['RecipeIngredientParts'] = ast.literal_eval(recommendations[i]['RecipeIngredientParts'])
        recommendations[i]['Images'] = ast.literal_eval(recommendations[i]['Images'])
        recommendations[i]['RecipeInstructions'] = ast.literal_eval(recommendations[i]['RecipeInstructions'])

    print('recommendations...>')
    
    for recommendation in recommendations:
        if recommendation['Images'][0] == 'https://static.vecteezy.com/system/resources/previews/005/337/799/original/icon-image-not-found-free-vector.jpg':
            print(f'{recommendation['Name']} not found..')
            recommendation['Images'][0] = get_images_links(recommendation['Name'])

        print(type(recommendation['Images']))

    return jsonify(recommendations)


if __name__ == '__main__':
    with app.app_context():
        # db.drop_all()
        db.create_all()
    app.run(debug=True)
