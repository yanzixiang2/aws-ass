from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'student'


@app.route("/addStudent", methods=['GET', 'POST'])
def home():
    return render_template('AddEmp.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')


@app.route("/addStudent", methods=['POST'])
def AddEmp():
    student_name = request.form['student_name']
    student_email = request.form['email']
    student_ic = request.form['ICNO']
    student_id = request.form['student_id']
    student_phone = request.form['phone_number']
    year_of_study = request.form['Year']
    student_faculty = request.form['Faculty']
    student_image_file = request.files['student_image_file']

    insert_sql = "INSERT INTO student VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if student_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (student_name, student_email, student_ic, student_id,student_phone, year_of_study, student_faculty))
        db_conn.commit()
        
        # Uplaod image file in S3 #
        student_image_file_name_in_s3 = "emp-id-" + str(student_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=student_image_file_name_in_s3, Body=student_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                student_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('home.html', name=student_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

