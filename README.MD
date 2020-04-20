The code pulls data from UK Police API "https://data.police.uk/" to show crimes for all/selected date for latitude = '51.52369' and longitude = '-0.0395857'

The URL template is as follows:
https://data.police.uk/api/crimes-street/all-crime?lat={lat}&lng={lng}&date={data}
(where lat= latitude and lng=longitude)

All html templates required to run this code are stored under the 'templates' folder.

The file "cassandra.txt" stores the commands used to setup the table structures in casssandra.

*************************************************
The code is written as such that the app route is the same as the function name. For example: to access the login page enter "http://ec2-18-204-218-107.compute-1.amazonaws.com/login" where 'http://ec2-18-204-218-107.compute-1.amazonaws.com' is the dns name.

However, to access the other routes of the application, user has to login first and continue to be logged in to the session.

*************************************************

The functions are explained below. 

1. index():
The page for the user to login or register. "index.html" is used to provide options to the user.

2. register(): 
The function for the user to register their details. "register.html" is used for the user to enter username, email and password. 
The passwords entered is encrypted using 'sha256_crypt' and stored in the DB.
Upon sucessful registration user is redirected to the login page.

3. login():
The function for the user to login. The user enters username and password previously registered.
"login.html" is used for the user to provide credentials.
Upon sucessful login, user is directed to the home() function. 

4. home():
The function uses "home.html" template to provide 2 options to the user. 
i) Has a link to see all existing crimes already available in cassandra. Redirectes to allcrime() function.
ii) Has a link to select a particular month to see those crimes. Redirects to entermonth() function

5. entermonth():
The function uses "entermonth.html" for the user to enter the year and month.
Upon entering the value, the user is directed to see the crimes for the that month using crimemonth() function.

6. crimemonth():
The function takes the input month from the user and checks in cassandra if any data for that month is already present. 
i) If already present, it redirectes to "allcrime.html" to show the data available
ii) If not present, it pulls data from the api for that month and stores in cassandra. Then it redirects to allcrime() function.

7. allcrime():
The function checks all available data present in cassandra and dispalys them using "allcrime.html".
"allcrime.html" has options for the user to update or delete a crime record.
i) if the user selects to delete the record, the function deletecrime() is called
ii) if the user selects to edit the record, the function editcrime is called

8. editcrime():
The function selects the record from the database for the given record id and calls "updatecrime.html".
"updatecrime.html" is used to enable editing the crime category for the selected crime id. Once the user submits the change the update() function is called.

9. update():
The function takes the crime id as input and updates the crime category in the database. It then redirects to the allcrime() function to show the updated record along with all other records.

10. deletecrime():
The function tales the crime id as input and deletes the selected record from the database.
Upon sucessful deletion, redirects the page to show all available crimes using the allcrime() function.

11. upd():
This function is created to demonstrate the put function and update the crime category when called externally example from Postman.

12. logout():
This function helps the user to logout of the session.

*******************************************************
Setup steps:

>> Launch AWS EC2 instance.
>> Login to ubuntu
>> create Dockerfile
>> create requirements.txt 
>> create app.py with the python code functions as mentioned above
>> create a directory "templates" and store all the html files inside it
>> deploy cassandra via docker
>> pull the Cassandra Docker Image using: - sudo docker pull cassandra:latest
>> run a Cassandra instance within docker using: - sudo docker run --name cassandra-test -p 9042:9042 -d cassandra:latest
>> run cassandra: - docker run -p 127.0.0.1:32779:9042 --name cassandra -d cassandra:latest
>> to interact with our Cassandra via its native command line shell client
called ‘cqlsh’ run: - sudo docker exec -it cassandra-test cqlsh
>> execute the queries as given in "cassandra.txt" and exit cqlsh
>> to build the image run: - sudo docker build . --tag=cassandrarest:v1
>> run it as a service, exposing the deploment to get an external IP: - sudo docker run -p 80:80 cassandrarest:v1
>> login to your web browser using the dns of the aws instance.

*********************************************************
