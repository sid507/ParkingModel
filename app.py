from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import datetime
from model import *

app = Flask(__name__)
db = SQLAlchemy(app)

weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

# Schema
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

class Vehicles(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	vehicle_no = db.Column(db.String(20))
	flat = db.Column(db.String(30))
	occupied = db.Column(db.Boolean, default=False)

# Routes

@app.route('/logs')
def logs():
	society_name = request.args.get('society')
	app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{society_name}.db'
	
	vno = request.args.get('vno')
	if vno == None:
		logs = VehicleLog.query.all()
	else:
		logs = VehicleLog.query.filter_by(vehicle_no = vno)
	return render_template('log.html', logs=logs)

@app.route('/exit', methods=["POST"])
def resident_exit():
	society_name = request.args.get('society')
	app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{society_name}.db'
	
	if (request.method == "POST"):
		try:
			# Get query arguments
			license_plate_no = request.args.get('licensePlateNo')
			hour = request.args.get('hour')
			mins = request.args.get('min')
			sec = request.args.get('sec')
			time = f"{hour}:{mins}:{sec}"
			# Find date 30 days before
			date = (datetime.datetime.today() - datetime.timedelta(days = 30)).date()
			# Get records of last one month
			records = VehicleLog.query.filter(VehicleLog.exit_date >= date, VehicleLog.vehicle_no == license_plate_no).all()

			exit_time = []
			entry_time = []
			day = []
			exit_date =[]

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
			prediction = predict(df, pd.to_datetime(time),weekdays[datetime.datetime.today().weekday()])

			if (prediction == "Irregular Data"):
				prediction = None
			# Store a new record for vehicle exit
			log = VehicleLog(vehicle_no = license_plate_no, exit_date = datetime.datetime.today().date(), exit_time = time, exit_day = weekdays[datetime.datetime.today().weekday()], predicted_entry_time = prediction)
			db.session.add(log)
			db.session.commit()

			return jsonify({"message":"Log created successfully"}), 201
		except:
			return jsonify({"message":"Something went wrong"}), 400
		
@app.route('/entry', methods=["POST"])
def resident_entry():
	society_name = request.args.get('society')
	app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{society_name}.db'
	
	if (request.method == "POST"):
		try:
			# Get query arguments
			license_plate_no = request.args.get('licensePlateNo')
			hour = request.args.get('hour')
			mins = request.args.get('min')
			sec = request.args.get('sec')
			time = f"{hour}:{mins}:{sec}"
			# Update log
			log = VehicleLog.query.filter_by(vehicle_no = license_plate_no, entry_time = None)[-1]
			log.entry_time = time
			log.entry_date = datetime.datetime.today().date()
			db.session.commit()

			return jsonify({"message":"Log updated successfully"}), 200
		except:
			return jsonify({"message":"Something went wrong"}), 400

@app.route('/allocate')
def allocate():
	society_name = request.args.get('society')
	app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{society_name}.db'
	
	try:
		stay_time = float(request.args.get('time'))
		stay_time = int(stay_time * 3600)
		time = datetime.datetime.now().time()
		stay_till = stay_time + (time.hour * 3600 + time.minute * 60 + time.second)
		records = VehicleLog.query.filter(VehicleLog.exit_date == datetime.datetime.today().date(), VehicleLog.entry_time == None, VehicleLog.predicted_entry_time != None).all()
		
		minimum = 999999
		parking_space = ''
		for record in records:
			vehicle_status = Vehicles.query.filter_by(vehicle_no = record.vehicle_no).first()
			if vehicle_status != None and vehicle_status.occupied == False:
				arrival_time = timeToSeconds(record.predicted_entry_time)
				if arrival_time > stay_till:
					if arrival_time < minimum:
						minimum = arrival_time
						parking_space = record.vehicle_no
		
		if parking_space != '':
			vehicle_status = Vehicles.query.filter_by(vehicle_no = parking_space).first()
			parking_space = vehicle_status.flat
			vehicle_status.occupied = True
			db.session.commit()

		return jsonify({"parking_space": parking_space}), 200
	except:
		return jsonify({"message": "Something went wrong"}), 400

@app.route('/dis-allocate')
def dis_allocate():
	try:
		society_name = request.args.get('society')
		app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{society_name}.db'

		parking = request.args.get('parking')
		vehicle_status = Vehicles.query.filter_by(flat = parking).first()
		vehicle_status.occupied = False
		db.session.commit()

		return jsonify({"message": "Data updated"}), 200
	except:
		return jsonify({"message": "Something went wrong"}), 400

@app.route('/usage')
def usage():
	society_name = request.args.get('society')
	app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{society_name}.db'
	
	# Get license plate from query arguments
	license_plate_no = request.args.get('licensePlateNo')
	# Find date 28 days before
	date = (datetime.datetime.today() - datetime.timedelta(days = 28)).date()
	# Get records of last one month
	records = VehicleLog.query.filter(VehicleLog.exit_date >= date, VehicleLog.vehicle_no == license_plate_no).all()
	usage = len(records)
	exit_time = []
	entry_time = []
	day = []
	exit_date =[]

	# Check if vehicle is currently in use or not
	in_use = False
	if(usage>0 and records[-1].entry_date == None):
		in_use = True

	for record in records:
		exit_date.append(record.exit_date)
		exit_time.append(record.exit_time)
		entry_time.append(record.entry_time)
		day.append(record.exit_day.lower()) 

	# Adding missing data and converting to dataframe
	df = addMissingDay(date, (datetime.datetime.today() - datetime.timedelta(days = 1)).date(),exit_date,day,entry_time,exit_time)
	exit_time = list(map(timeToSeconds,df['Exit'].tolist()))
	entry_time = list(map(timeToSeconds,df['Entry'].tolist()))
	day = list(map(lambda x: x[0].upper(), df['Day'].tolist()))
	return jsonify({"usage":usage, "exit_time":exit_time, "entry_time":entry_time, "day":day, "in_use":in_use}), 201

@app.route('/add-vehicle', methods=["POST"])
def add_vehicle():
	society_name = request.args.get('society')
	app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{society_name}.db'

	if (request.method == "POST"):
		vno = request.form.get('licensePlateNo')
		parking = request.form.get('parking')
		try:
			vehicle = Vehicles(vehicle_no = vno, flat = parking, occupied = False)
			db.session.add(vehicle)
			db.session.commit()

			return jsonify({"message": "Vehicle added successfully"}), 200
		except:
			return jsonify({"message": "Something went wrong"}), 400

if (__name__ == "__main__"):
	app.run(host='192.168.0.112', debug = True)