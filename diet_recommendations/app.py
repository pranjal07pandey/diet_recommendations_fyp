from flask import Flask, render_template
from get_food_images import get_images_links

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/food-images')
def get_food():
    return get_images_links("virgin pina colada")

    

if __name__ == '__main__':
    app.run(debug=True)
