from werkzeug.security import generate_password_hash
import random
from datetime import timedelta, date, datetime

from app import db, app
from app.models import Bridge, User, Group, Sensor, SensorData

def create_sensors_for_bridges():
    bridges = Bridge.query.all()
    for bridge in bridges:
        # Create four tilt sensors
        for _ in range(4):
            tilt_sensor = Sensor(sensor_type="tilt", bridge_id=bridge.id)
            db.session.add(tilt_sensor)
        
        # Create one temperature sensor
        temp_sensor = Sensor(sensor_type="temperature", bridge_id=bridge.id)
        db.session.add(temp_sensor)
    db.session.commit()

def generate_sensor_data():
    sensors = Sensor.query.all()
    
    # Define base values for tilt sensors
    tilt_sensors = [sensor for sensor in sensors if sensor.sensor_type == "tilt"]
    # Generate 28 random base values within a desired range (e.g., -0.9 to 0.9)
    all_base_values = [random.uniform(-0.9, 0.9) for _ in range(28)]
    # Shuffle the base values
    random.shuffle(all_base_values)
    # Assign these shuffled base values to the tilt sensors
    sensor_base_values = {tilt_sensor.id: base_value for tilt_sensor, base_value in zip(tilt_sensors, all_base_values)}

    # Generate hourly data for the past 30 days
    current_datetime = datetime.utcnow().replace(minute=0, second=0, microsecond=0) - timedelta(days=730)
    end_datetime = datetime.utcnow()
    while current_datetime <= end_datetime:
        _generate_data_for_datetime(sensors, current_datetime, sensor_base_values)
        current_datetime += timedelta(hours=1)

    db.session.commit()

def _generate_data_for_datetime(sensors, current_datetime, sensor_base_values):
    for sensor in sensors:
        if sensor.sensor_type == "tilt":
            # Get the base value for the sensor
            base_value = sensor_base_values.get(sensor.id, 0)  # Default to 0 if sensor ID not found

            # Generate tilt data with a small fluctuation around the base value
            fluctuation = random.uniform(-0.05, 0.05)  # Adjust this range for larger/smaller fluctuations
            data_value = base_value + fluctuation

            # Occasionally introduce a spike
            if random.random() < 0.001:  # 0.1% chance
                data_value = random.uniform(-2, 2)
        elif sensor.sensor_type == "temperature":
            # Generate temperature data based on month
            if current_datetime.month in [12, 1]:
                data_value = random.uniform(45, 55)
            elif current_datetime.month in [7, 8]:
                data_value = random.uniform(85, 95)
            else:
                data_value = random.uniform(55, 85)
        
        sensor_data = SensorData(data=data_value, timestamp=current_datetime, sensor_id=sensor.id)
        db.session.add(sensor_data)

with app.app_context():
    # Create bridges
    bridge_numbers = [2753, 6174, 600012, 600225, 5379, 2893, 3434]
    for number in bridge_numbers:
        bridge = Bridge.query.filter_by(number=str(number)).first()
        if not bridge:
            bridge = Bridge(number=str(number))
            db.session.add(bridge)
    db.session.commit()

    # Create test users
    users_data = [
        {"email": "user1@example.com", "password": "password1","groups": 1},
        {"email": "user2@example.com", "password": "password2","groups": 2},
        {"email": "user3@example.com", "password": "password3","groups": 1},
    ]
    for user_data in users_data:
        user = User.query.filter_by(email=user_data["email"]).first()
        if not user:
            hashed_password = generate_password_hash(user_data["password"], method='scrypt')
            user = User(email=user_data["email"], password=hashed_password)
            db.session.add(user)
    db.session.commit()

    # Create groups
    group_names = ["Group 1", "Group 2"]
    for name in group_names:
        group = Group.query.filter_by(name=name).first()
        if not group:
            group = Group(name=name)
            db.session.add(group)
    db.session.commit()

    # Assign bridges to groups using the recommended method
    group1 = Group.query.filter_by(name="Group 1").first()
    group2 = Group.query.filter_by(name="Group 2").first()
    group1.bridges.extend([db.session.get(Bridge, 1), db.session.get(Bridge, 2), db.session.get(Bridge, 5), db.session.get(Bridge, 6), db.session.get(Bridge, 7),])
    group2.bridges.extend([db.session.get(Bridge, 3), db.session.get(Bridge, 4)])
    db.session.commit()

    # Assign users to groups
    user1 = User.query.filter_by(email="user1@example.com").first()
    user2 = User.query.filter_by(email="mohsacko@gmail.com").first()
    if group1 not in user1.groups:
        user1.groups.append(group1)
    if group2 not in user2.groups:
        user2.groups.append(group2)
    db.session.commit()

    # After creating bridges, groups, and users
    create_sensors_for_bridges()
    generate_sensor_data()
