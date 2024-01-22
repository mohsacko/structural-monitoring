from flask import render_template, redirect, url_for, flash, request, jsonify

from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

import json
from datetime import datetime, timedelta

from . import app
from .models import db, User, Bridge, SensorData
from .utils import DateTimeEncoder

login_manager = LoginManager()
login_manager.login_view = 'login'  # specify the name of the login view
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def dashboard():
    user = User.query.get(current_user.id)
    user_bridges = set()  # To avoid duplicate bridges
    for group in user.groups:
        for bridge in group.bridges:
            user_bridges.add(bridge)
    return render_template('dashboard.html', bridges=user_bridges)

@app.route("/bridges", methods=['GET'])
@login_required
def bridges():
    bridge_id = request.args.get('bridge')
    view = request.args.get('view', 'hourly')  # Default to hourly view
    bridge = Bridge.query.get(bridge_id)
    print(request.args)
    
    # Fetch sensor data for the bridge
    sensors = bridge.sensors
    tilt_data = []
    now = datetime(year=2023, month=9, day=14, hour=23, minute=59)

    if view == 'hourly':
        start_time = now - timedelta(hours=23, minutes=59)
    elif view == 'weekly':
        interval = timedelta(hours=8)
        start_time = now - timedelta(days=6, hours=23, minutes=59)
    elif view == 'monthly':
        interval = timedelta(hours=24)
        start_time = now - timedelta(days=29, hours=23, minutes=59)
    elif view == 'annual':
        interval = timedelta(weeks=1)
        start_time = now - timedelta(days=364, hours=23, minutes=59)

    # Fetch all tilt sensor data for the bridge in a single query
    tilt_sensors = [sensor for sensor in bridge.sensors if sensor.sensor_type == 'tilt']
    sensor_ids = [sensor.id for sensor in tilt_sensors]
    all_data = SensorData.query.filter(
        SensorData.sensor_id.in_(sensor_ids),
        SensorData.timestamp.between(start_time, now)
    ).order_by(SensorData.timestamp.asc()).all()

    # Process the data to structure it as needed
    tilt_data = []
    for sensor_id in sensor_ids:
        sensor_data = [{"date": data.timestamp, "value": data.data, "sensor_id": data.sensor_id} for data in all_data if data.sensor_id == sensor_id]
        tilt_data.append(sensor_data)

    tilt_data = json.dumps(tilt_data, cls=DateTimeEncoder)

    if 'view' in request.args:
        return render_template('partials/bridge_data_content.html', sensors=tilt_sensors, tilt_data=tilt_data)
    else:
        return render_template('partials/bridge_data.html', sensors=tilt_sensors, bridge=bridge, tilt_data=tilt_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('dashboard'))

@app.route("/live", methods=['GET', 'POST'])
def live():
    return render_template('live.html')