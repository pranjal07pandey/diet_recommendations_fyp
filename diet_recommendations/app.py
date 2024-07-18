from flask import Flask, render_template, request, jsonify
from get_food_images import get_images_links
from config import Config
from models import User, db
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
import bcrypt
from food_logic import from_slider, generate_recommendations_on_user_form

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
    data = request.get_json()
    username = data['username']
    password = data['password']

    if not username or not password:
        return jsonify({'message': 'username or password required'}), 400
    
    user = User.query.filter_by(username = username).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password):
        return jsonify({'message': 'Login Successful..'}), 200
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
    # info = [age, height, weight, gender, activity_level, weight_loss_plan]
    
    # user_input = {
#     'age': 30,
#     'weight': 70,  # in kg
#     'height': 175,  # in cm
#     'gender': 'male',
#     'activity_level': 'Super active',
#     'weight_loss_plan': 'Maintain weight'
# }
    print('inside the get_recommendations_form function: ')

    recommendations = generate_recommendations_on_user_form(user_input= {
        'age': age,
        'weight': weight,
        'height': height,
        'gender': gender,
        'activity_level': activity_level,
        'weight_loss_plan': weight_loss_plan
    }, selected_options= selected_options)

    print(type(recommendations))
    print('**********************')
    breakfast = recommendations[0].to_dict(orient = 'records')
    lunch = recommendations[1].to_dict(orient = 'records')
    dinner = recommendations[2].to_dict(orient = 'records')
    
    ingredients_breakfast = [items['RecipeIngredientParts'].strip('c()').replace('"', '').split(', ') for items in breakfast]
    ingredients_lunch = [items['RecipeIngredientParts'].strip('c()').replace('"', '').split(', ') for items in lunch]
    ingredients_dinner = [items['RecipeIngredientParts'].strip('c()').replace('"', '').split(', ') for items in dinner]


    for i in range(len(breakfast)):
        breakfast[i]['RecipeIngredientParts'] = ingredients_breakfast[i]
        lunch[i]['RecipeIngredientParts'] = ingredients_lunch[i]
        dinner[i]['RecipeIngredientParts'] = ingredients_dinner[i]
    # breakfast_items = []
    print(breakfast)

    # for items in breakfast['Name']:
    #     breakfast_items.append(items)
    
    # print(breakfast_items)

    return render_template('output.html', meals = [breakfast, lunch, dinner])




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
    
    recommendations = from_slider(metrics= metrics)
    recommendations = recommendations.to_dict(orient = 'records')

    print(recommendations)
    print(type(recommendations))
    print(len(recommendations))


    return jsonify(recommendations)


# def hash_password(password):
#     """Hash a password using bcrypt."""
#     # Generate a salt and hash the password
#     hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
#     return hashed_password

# def check_password(hashed_password, password):
#     """Check if a provided password matches the hashed password."""
#     return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

 

if __name__ == '__main__':
    with app.app_context():
        # db.drop_all()
        db.create_all()
    app.run(debug=True)
