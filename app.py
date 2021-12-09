from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import datetime

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

	def __repr__(self):
		return f"{self.vehicle_no} {self.exit_date} {self.exit_time} {self.exit_day} {self.entry_date} {self.entry_time} {self.predicted_entry_time}"

@app.route('/')
def hello_world():
	return 'hello_world'

@app.route('/exit', methods=["POST"])
def exit():
	if (request.method == "POST"):
		licence_plate_no = request.data.licensePlateNo
		# Find date 30 days before
		date = (datetime.datetime.today() - datetime.timedelta(days = 30)).date()
		# Get records of last one month
		records = VehicleLog.query.filter(VehicleLog.exit_date >= date, VehicleLog.vehicle_no == license_plate_no ).all()

		exit_time = []
		entry_time = []
		day = []

		for record in records:
			exit_time.append(record.exit_time)
			entry_time.append(record.entry_time)
			day.append(record.exit_day) 

		# Using this record we will predict when user will arrive


		
@app.route('/entry', methods=["POST"])
def entry():
	if (request.method == "POST"):
		# Code to make an entry in database
		pass


if (__name__ == "__main__"):
  app.run(debug = True)