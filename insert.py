# Utility function for inserting dummy data

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///silversolitaire.db'
db = SQLAlchemy(app)

weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

class VehicleLog(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	vehicle_no = db.Column(db.String(20))
	exit_date = db.Column(db.Date)
	exit_time = db.Column(db.String(20))
	exit_day = db.Column(db.String(20))
	entry_date = db.Column(db.Date)
	entry_time = db.Column(db.String(20))
	predicted_entry_time = db.Column(db.String(20))

exit_time = input('Enter exit time: ')
entry_time = input('Enter entry time: ')
vehicle_no = input('Enter vehicle no: ')
days_before = int(input('Days before: '))
date = (datetime.datetime.today() - datetime.timedelta(days=days_before)).date()
day = weekdays[date.weekday()]

log = VehicleLog(vehicle_no = vehicle_no, exit_date = date, exit_time = exit_time, exit_day = day, entry_time = entry_time, entry_date = date)
db.session.add(log)
db.session.commit()