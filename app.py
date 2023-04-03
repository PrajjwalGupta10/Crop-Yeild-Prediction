from flask import Flask, render_template, request, redirect, url_for, session
import numpy as np
import pandas as pd
import joblib
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

app.secret_key = 'xyzsdfg'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'user-system'
  
mysql = MySQL(app)


model = joblib.load('Optimizing Agricultural Production.save')

#login
@app.route('/login', methods =['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s AND password = % s', (email, password, ))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['name'] = user['name']
            session['email'] = user['email']
            mesage = 'Logged in successfully !'
            return render_template('Home.html', mesage = mesage)
        else:
            mesage = 'Please enter correct email / password !'
    return render_template('login.html', mesage = mesage)
#logout  
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))
#register  
@app.route('/register', methods =['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form :
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            mesage = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif not userName or not password or not email:
            mesage = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO user VALUES ( % s, % s, % s)', (userName, email, password, ))
            mysql.connection.commit()
            mesage = 'You have successfully registered !'
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('register.html', mesage = mesage)
# Home
@app.route('/')
def home():
    return render_template('login.html')

# Analysis
@app.route('/analysis', methods=['GET'])
def analysis():
    return render_template('Analysis.html')


# About me
@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

# predict
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        Ratio_of_Nitrogen_content_in_soil = request.form['Ratio_of_Nitrogen_content_in_soil']
        Ratio_of_Phosphorous_content_in_soil = request.form['Ratio_of_Phosphorous_content_in_soil']
        Ration_of_Potassium_content_in_soil = request.form['Ration_of_Potassium_content_in_soil']
        Temperature_in_degree_Celsius = request.form['Temperature_in_degree_Celsius']
        Relative_humidity = request.form['Relative_humidity']
        ph_value_of_the_soil = request.form['ph_value_of_the_soil']
        Rainfall_in_mm = request.form['Rainfall_in_mm']

        List = [Ratio_of_Nitrogen_content_in_soil,
                Ratio_of_Phosphorous_content_in_soil,
                Ration_of_Potassium_content_in_soil,
                Temperature_in_degree_Celsius,
                Relative_humidity,
                ph_value_of_the_soil,
                Rainfall_in_mm]
        inp_data = [(float(x)) for x in List]

        prediction = model.predict([inp_data])
        prediction = (prediction[0])
        return render_template('Predict.html', pred_val=prediction)
    else:
        return render_template('Predict.html')



# The Function called when the scipt is run
if __name__ == '__main__':
    app.run(debug=True)