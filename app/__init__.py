from flask import Flask, request, jsonify
from flask_migrate import Migrate
import os

#Imports for the Live chart example
import json
import logging
import random
import sys
import time
from datetime import datetime
from flask import Response, render_template, request, stream_with_context
from typing import Iterator

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

#from dotenv import load_dotenv
uri = os.getenv("SQLALCHEMY_DATABASE_URI")  # or however you get your database URL
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

from .models import db

# Explicitly set the path to the static folder
static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static')

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates'), static_folder=static_path, static_url_path='/static')

# Only load .env file if not on Heroku
if os.environ.get('HEROKU') is None:
    from dotenv import load_dotenv
    load_dotenv()

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['STATIC_FOLDER'] = 'static'

db.init_app(app)

migrate = Migrate(app, db)

"""
API Section
def get_sensor_data():
    api_url = "RESENSYS_API_URL"
    params = {
        'api_key': 'RESENSYS_API_KEY',
        
    }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

@app.route('/')
def index():
    sensor_data = get_sensor_data()
    return render_template('index.html', data=sensor_data)        
"""

# Import views after the app instance is created
from . import views, models

#This part defines a route for the root URL ("/"). When a user accesses the root URL, Flask triggers this function
@app.route("/")
def index() -> str:
    return render_template("base.html")

"""This function is a generator (Iterator[str]) that continuously produces random data.
The data includes a timestamp and a random value between 0 and 100, simulating sensor data or live measurements.
The data is encoded in JSON format and sent as a server-sent event"""
def generate_random_data() -> Iterator[str]:
    """
    Generates random value between 0 and 100

    :return: String containing current timestamp (YYYY-mm-dd HH:MM:SS) and randomly generated data.
    """
    if request.headers.getlist("X-Forwarded-For"):
        client_ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        client_ip = request.remote_addr or ""

    try:
        logger.info("Client %s connected", client_ip)
        while True:
            json_data = json.dumps(
                {
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "value": random.random() * 100,
                }
            )
            yield f"data:{json_data}\n\n"
            time.sleep(1)
    except GeneratorExit:
        logger.info("Client %s disconnected", client_ip)

"""This route ("/chart-data") streams the generated data to the client's web browser.
It uses generate_random_data to create a stream of data.
The Response object is created with a MIME type of text/event-stream, which is used for server-sent events. 
This allows the server to push updates to the client in real-time."""
@app.route("/chart-data")
def chart_data() -> Response:
    response = Response(stream_with_context(generate_random_data()), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response

"""This block checks if the script is being run directly (not imported as a module).
If so, it starts the Flask application. host="0.0.0.0" allows the server to be accessible externally. threaded=True enables handling multiple requests at the same time."""
#if __name__ == "__main__":
    #app.run(host="0.0.0.0", threaded=True)

"""
@app.route('/get_bridge_info/', methods=['GET'])
def get_bridge_info():
    # Get the bridge ID from the request parameters
    bridge_id = request.args.get('bridge')

    # Query the database to retrieve bridge information for the requested bridge_id
    bridge = Bridge.query.filter_by(id=bridge_id).first()

    # Check if the bridge with the specified ID exists in the database
    if bridge:
        # Convert the bridge object to a dictionary
        bridge_info = {
            'name': bridge.name,
            'number': bridge.number,
            'location': bridge.location
        }
        return jsonify(bridge_info)
    else:
        # Return an error response if the bridge_id is not found in the database
        return jsonify({'error': 'Bridge not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
"""
