from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy


society_name = input('Enter society name: ')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{society_name}.db'
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

db.create_all()
db.session.commit()