from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
from model import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///log.db'
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

	def __repr__(self):
		return f"{self.vehicle_no} {self.exit_date} {self.exit_time} {self.exit_day} {self.entry_date} {self.entry_time} {self.predicted_entry_time}"

@app.route('/')
def hello_world():
	return 'hello_world'

@app.route('/resident-exit', methods=["POST"])
def resident_exit():
	if (request.method == "POST"):
		# Get license plate from query arguments
		license_plate_no = request.args.get('licensePlateNo')
		# Find date 30 days before
		date = (datetime.datetime.today() - datetime.timedelta(days = 30)).date()
		# Get records of last one month
		records = VehicleLog.query.filter_by(exit_date >= date, vehicle_no = license_plate_no).all()

		exit_time = []
		entry_time = []
		day = []
		exit_date=[]

		for record in records:
			exit_date.append(record.exit_date)
			exit_time.append(record.exit_time)
			entry_time.append(record.entry_time)
			day.append(record.exit_day.lower()) 

		# Adding missing data and converting to dataframe
		df = addMissingDay(date,datetime.datetime.today().date(),exit_date,day,entry_time,exit_time)
		print(df)
		
		# Convert the String time into pd.toDatetime
		df['Entry'] = pd.to_datetime(df['Entry'])
		df['Exit'] = pd.to_datetime(df['Exit'])

		# Apply the preprocessing
		prediction = predict(df, pd.to_datetime(getCurrentTime()),weekdays[datetime.datetime.today().weekday()])
		if (prediction == "Irregular Data"):
			prediction = None

		# Store a new record for vehicle exit
		log = VehicleLog(vehicle_no = license_plate_no, exit_date = datetime.datetime.today().date(), exit_time = getCurrentTime(), exit_day = weekdays[datetime.datetime.today().weekday()], predicted_entry_time = prediction)
		db.session.add(log)
		db.session.commit()

		return jsonify({"message":"Log created successfully"})

		
@app.route('/resident-entry', methods=["POST"])
def resident_entry():
	if (request.method == "POST"):
		# Get license plate from query arguments
		license_plate_no = request.args.get('licensePlateNo')
		# Update log
		log = VehicleLog.query.filter_by(vehicle_no = license_plate_no, entry_time = None)[-1]
		log.entry_time = getCurrentTime()
		log.entry_date = datetime.datetime.today().date()
		db.session.commit()

		return jsonify({"message":"Log created successfully"})


@app.route('/allocate')
def allocate():
	stay_time = float(request.args.get('time'))
	stay_time = int(stay_time * 3600)
	time = datetime.datetime.now().time()
	stay_till = stay_time + (time.hour * 3600 + time.minute * 60 + time.second)
	records = VehicleLog.query.filter(VehicleLog.exit_date == datetime.datetime.today().date(), VehicleLog.entry_time == None, VehicleLog.predicted_entry_time != None).all()
	
	minimum = 999999
	parking_space = ''
	for record in records:
		arrival_time = timeToSeconds(record.predicted_entry_time)
		if (arrival_time > stay_till):
			if arrival_time < minimum:
				minimum = arrival_time
				parking_space = record.vehicle_no

	return jsonify({"parking_space":parking_space})

if (__name__ == "__main__"):
	app.debug=True
	app.run(debug = True)