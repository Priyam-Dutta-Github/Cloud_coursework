from flask import Flask,render_template,flash, redirect,url_for,session,logging,request, jsonify
import json
import requests
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from cassandra.cluster import Cluster
from flask_table import Table, Col, LinkCol
cluster = Cluster(contact_points=['172.17.0.2'],port=9042)
session1 = cluster.connect()
app = Flask(__name__)
app.secret_key = "PriyamD"

#code for index page
@app.route("/")
def index():
        return render_template("index.html")


#code for login page
@app.route("/login",methods=["GET", "POST"])
def login():
        error = None
        if request.method == "POST":
                uname = request.form["uname"]
                passw_candidate = request.form["passw"]
                error = 'Invalid username or password. Please try again !'
                login = session1.execute( "Select username,password From userlogin.stats where username ='"+uname+"'") #pulls user details from cassandra
                for usrs in login:
                        pwd=usrs.password
                        c = pwd.encode('utf-8')
                        if sha256_crypt.verify(passw_candidate, c): #verifies the encrypted password
                                session['usr'] = uname
                                flash('You were successfully logged in')
                                return redirect(url_for("home"))
                        else:
                                flash('Incorrect login details. Please try again')
                                return render_template("login.html", error = error)
        return render_template("login.html")

#function to logout
@app.route('/logout')
def logout():
        session.pop('usr')
        flash('You are now logged out')
        return redirect(url_for('login'))


# Register Form Class
class RegisterForm(Form):
        uname = StringField('Username', [validators.Length(min=4, max=25)])
        mail = StringField('Email', [validators.Length(min=6, max=50)])
        passw = PasswordField('Password', [validators.DataRequired()])


#code for register page
@app.route("/register", methods=["GET", "POST"])
def register():
        form = RegisterForm(request.form)
        if request.method == "POST" and form.validate():
                uname = form.uname.data
                mail = form.mail.data
                passwd = sha256_crypt.encrypt(str(form.passw.data)) #encrypts the password before storing in database
                register = session1.execute( "insert into userlogin.stats(username, email, password) values('"+uname+"', '"+mail+"', '"+passwd+"')")
                return redirect(url_for("login"))
        return render_template("register.html")

#function to call home page
@app.route("/home", methods=["GET", "POST"])
def home():
        if 'usr' in session:
                return render_template("home.html")

#function to call page to enter specific date
@app.route("/entermonth", methods=["GET", "POST"])
def entermonth():
        error = None
        if 'usr' in session:
                return render_template("entermonth.html")
        else:
                error = 'Please login to access site'
                return render_template("login.html", error = error)


#function to load data from police api for specific month if not already present
crime_url_template = 'https://data.police.uk/api/crimes-street/all-crime?lat={lat}&lng={lng}&date={data}'
@app.route('/crimemonth', methods=["POST"])
def crimemonth():
        error = None
        if 'usr' in session:
                my_date = request.form['month_yr'] #date entered by user
                chk = session1.execute("Select * From crimestat.stats where month='"+my_date+"' ALLOW FILTERING")
                if not chk: #to check if any crime for that month and year combination is present
                        my_latitude = request.args.get('lat','51.52369')
                        my_longitude = request.args.get('lng','-0.0395857')
                        crime_url = crime_url_template.format(lat = my_latitude, lng = my_longitude, data = my_date)
                        resp2 = requests.get(crime_url)
                        if resp2.ok:
                                result=resp2.json()
                                for r in result: #insert data into cassandra if not present
                                    session1.execute("insert into crimestat.stats(category, id, latitude, longitude, street_id, street_name, location_type, month) values('{}', '{}', '{}', '{}','{}',$$'{}'$$,'{}','{}')".format(r['category'],r['id'],r['location']['latitude'],r['location']['longitude'], r['location']['street']['id'], r['location']['street']['name'],r['location_type'],r['month']))
                                        #call function to show all data
                                return redirect(url_for ("allcrime"))
                        else:
                                flash ("Invalid Date")
                #call function to show all data
                return render_template("allcrime.html", output_data = chk)

        else:
                error = 'Please login to access site'
                return render_template("login.html", error = error)


#function to show all data
@app.route('/allcrime', methods=["GET"])
def allcrime():
        error = None
        if 'usr' in session:
                all = session1.execute ("Select * From crimestat.stats ALLOW FILTERING")
                return render_template("allcrime.html", output_data = all)

        else:
                error = 'Please login to access site'
                return render_template("login.html", error = error)

#function to edit data
@app.route('/editcrime/<string:id>', methods=["GET", "POST"])
def editcrime(id):
        error = None
        if 'usr' in session:
                edt = session1.execute( "Select * From crimestat.stats where id='"+id+"'")
                return render_template("updatecrime.html", output= edt)
        else:
                error = 'Please login to access site'
                return render_template("login.html", error = error)

#function to update data
@app.route('/update', methods=["GET", "POST"])
def update():
        error = None
        if 'usr' in session:
                id = request.form['id']
                category_new = request.form['category']
                session1.execute( "update crimestat.stats set category='"+category_new+"' where id='"+id+"'") #updates the new category and saves in database
                return redirect(url_for ("allcrime"))
        else:
                error = 'Please login to access site'
                return render_template("login.html", error = error)

#updating data using put function to be called externally
@app.route('/update/<string:id>/<string:category>', methods=["PUT"])
def upd(id,category):
        session1.execute( "update crimestat.stats set category='"+category+"' where id='"+id+"'")
        return "crime {} updated".format(id)

#function to delete data
@app.route('/deletecrime/<string:id>', methods=["POST", "DELETE"])
def deletecrime(id):
        if request.method == "POST":
                error = None
                if 'usr' in session:
                        session1.execute ("delete From crimestat.stats where id='"+id+"'") #deletes the specific record from the database
                        return redirect(url_for ("allcrime"))
                else:
                        error = 'Please login to access site'
                        return render_template("login.html", error = error)
        if request.method == "DELETE": #to delete data from database when called externally
                session1.execute ("delete From crimestat.stats where id='"+id+"'")
                return "Crime {} deleted".format(id)

if __name__ == "__main__":
        app.run(host='0.0.0.0', port=80)
