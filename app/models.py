from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

from datetime import datetime

db = SQLAlchemy()

# Association table for many-to-many relationship between User and Group
user_group_association = db.Table('user_group_association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)

# Association table for many-to-many relationship between Group and Bridge
group_bridge_association = db.Table('group_bridge_association',
    db.Column('group_id', db.Integer, db.ForeignKey('group.id')),
    db.Column('bridge_id', db.Integer, db.ForeignKey('bridge.id'))
)

# Association table for many-to-many relationship between Product and Item
product_item_association = db.Table('product_item_association',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
    db.Column('item_id', db.Integer, db.ForeignKey('item.id'))
)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    designation = db.Column(db.String(255), nullable=True)
    supplier = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    parameters = db.Column(db.String(255), nullable=True)
    system = db.Column(db.String(255), nullable=True)
    photo = db.Column(db.String(255), nullable=True)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(255), nullable=False)
    condition = db.Column(db.String(50), nullable=False)
    unit = db.Column(db.String(50), nullable=False)
    measurement = db.Column(db.Integer)
    products = db.relationship('Product', secondary=product_item_association, backref='items')

class Tools(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description=db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    groups = db.relationship('Group', secondary=user_group_association, backref='users')


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    bridges = db.relationship('Bridge', secondary=group_bridge_association, backref='groups')


class Bridge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100))
    facility = db.Column(db.String(100))
    crossing = db.Column(db.String(100))
    location = db.Column(db.String(200))
    photo_url = db.Column(db.String(500))
    sensors = db.relationship('Sensor', backref='bridge', lazy=True)


class Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sensor_type = db.Column(db.String(50), nullable=False)  # e.g. temperature, tilt, strain
    current_value = db.Column(db.Float, nullable=True)
    bridge_id = db.Column(db.Integer, db.ForeignKey('bridge.id'), nullable=False)
    sensor_data = db.relationship('SensorData', backref='sensor', lazy=True)
    

class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Float, nullable=False)  # Decimal field for sensor data
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp for when the data was captured
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.id'), nullable=False)  # Foreign key to the Sensor model
