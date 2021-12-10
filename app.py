from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import datetime
from model import *

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
		exit_date=[]

		for record in records:
			exit_date.append(record.exit_date)
			exit_time.append(record.exit_time)
			entry_time.append(record.entry_time)
			day.append(record.exit_day) 
		print(exit_time)
		print(entry_time)
		print(day)
		# Using this record we will predict when user will arrive


		
@app.route('/entry', methods=["POST"])
def entry():
	if (request.method == "POST"):
		# Code to make an entry in database
		pass


@app.route('/test',methods=["GET"])
def test():
	licence_plate_no = "MH01AE1111" #request.data.licensePlateNo
		# Find date 30 days before
	date = (datetime.datetime.today() - datetime.timedelta(days = 30)).date()
	# Get records of last one month
	records = VehicleLog.query.filter(VehicleLog.exit_date >= date, VehicleLog.vehicle_no == "MH01AE4444" ).all()

	exit_time = []
	entry_time = []
	day = []
	exit_date=[]

	for record in records:
		exit_date.append(record.exit_date)
		exit_time.append(record.exit_time)
		entry_time.append(record.entry_time)
		day.append(record.exit_day.lower()) 
	# print(exit_time)
	# print(entry_time)
	# print(day)
	# print(exit_date)

	# Adding missing data and converting to dataframe
	df = addMissingDay(date,datetime.datetime.today().date(),exit_date,day,entry_time,exit_time)
	print(df)
	
	# Convert the String time into pd.toDatetime

	df['Entry'] = pd.to_datetime(df['Entry'])
	df['Exit'] = pd.to_datetime(df['Exit'])


	# Apply the preprocessing
	return predict(df,pd.to_datetime('10:25:20'),'friday')

	# return "Success"
	

if (__name__ == "__main__"):
	app.debug=True
	app.run(debug = True)