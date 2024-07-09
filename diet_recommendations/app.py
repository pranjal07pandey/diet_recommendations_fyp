from flask import Flask, render_template, request, jsonify
from get_food_images import get_images_links
from config import Config
from models import User, db
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
import bcrypt

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
