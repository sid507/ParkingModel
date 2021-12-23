# Utility function to update records

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///log.db'
db = SQLAlchemy(app)

class VehicleLog(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	vehicle_no = db.Column(db.String(20))
	exit_date = db.Column(db.Date)
	exit_time = db.Column(db.String(20))
	exit_day = db.Column(db.String(20))
	entry_date = db.Column(db.Date)
	entry_time = db.Column(db.String(20))
	predicted_entry_time = db.Column(db.String(20))

inp = int(input('Enter record id: '))

log = VehicleLog.query.get(inp)

choice = int(input('Press 1 to update exit time and 2 to update entry time: '))
if choice == 1:
	inp = input('Enter exit time: ')
	log.exit_time = inp
else: 
	inp = input('Enter entry time: ')
	log.entry_time = inp

db.session.commit()
