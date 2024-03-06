from flask import Flask, jsonify
from app.weather import weather_blueprint
from app.place import place_bp

app = Flask(__name__)

# blueprints
app.register_blueprint(weather_blueprint, url_prefix='/weather')
app.register_blueprint(place_bp, url_prefix='/place')

@app.route('/')
def init():
    return 'Hi', 200

@app.route("/hello-world")
def hello_world():
    data = {
        "v": "hello",
    }
    return jsonify(data), 200

@app.route('/privacy')
def privacy():
    return "The APP does not collect any user data", 200