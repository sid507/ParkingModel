# Utility function to update records

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///silversolitaire.db'
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

# logs = VehicleLog.query.filter_by(vehicle_no='MH01AE2222').all()
# for log in logs:
# 	log.vehicle_no = 'MH03DG0611'
inp = int(input('Enter record id: '))

log = VehicleLog.query.get(inp)

choice = int(input('Press to update\n1. exit time\n2. entry time\n3. exit date\n4. entry date\n5. vehicle no\n6. exit day\n'))
if choice == 1:
	inp = input('Enter exit time: ')
	log.exit_time = inp
elif choice == 2: 
	inp = input('Enter entry time: ')
	log.entry_time = inp
elif choice == 3:
	inp = int(input('Enter days before: '))
	date = (datetime.datetime.today() - datetime.timedelta(days=inp)).date()
	log.exit_date = date
elif choice == 4:
	inp = int(input('Enter days before: '))
	date = (datetime.datetime.today() - datetime.timedelta(days=inp)).date()
	log.entry_date = date
elif choice == 5:
	inp = input('Enter vehicle no: ')
	log.vehicle_no = inp
else:
	inp = input('Enter day: ')
	log.exit_day = inp

db.session.commit()
