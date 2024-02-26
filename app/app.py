from flask import Flask, jsonify
from app.weather import weather_blueprint

app = Flask(__name__)

# blueprints
app.register_blueprint(weather_blueprint, url_prefix='/weather')

@app.route('/')
def init():
    return 'Hi', 200

@app.route("/hello-world")
def hello_world():
    data = {
        "v": "hello",
    }
    return jsonify(data), 200
