# Parking Space Allocation API

This API is a part of Final Year Project https://github.com/Yash4900/EaseIt

The main purpose of this Flask API is assign a parking space when a visitor arrives in society. Assignment is done based on the visitor's stay time in society and the predicted arrival time of the resident vehicles. The arrival time of residents is predicted using the XGBoost Model which takes past vehicle logs of residents as features. The vehicle logs are maintained in an SQLite Database and data is stored via API calls.
