from datetime import datetime
from datetime import date
from flask import Flask, render_template,flash,session,redirect,url_for
import json
from flask import request,jsonify
from flask_session import Session
from flask import send_file
from flask_mail import *  
from random import *
import mysql.connector
from mysql.connector import errorcode
import subprocess,os
from subprocess import PIPE
import base64
import random
from copyleaks.copyleaks import Copyleaks
from copyleaks.exceptions.command_error import CommandError
from copyleaks.models.submit.document import FileDocument, UrlDocument, OcrFileDocument
from copyleaks.models.submit.properties.scan_properties import ScanProperties
from copyleaks.models.export import *
# Register on https://api.copyleaks.com and grab your secret key (from the dashboard page).
EMAIL_ADDRESS = 'nileshgupta2001@gmail.com'
KEY = '3506c579-ea1a-427d-8fc1-6594748cde48'


app=Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
Session(app)
mail = Mail(app) 
app.config["MAIL_SERVER"]='smtp.gmail.com'  
app.config["MAIL_PORT"] = 465      
app.config["MAIL_USERNAME"] = 'nileshgupta2001@gmail.com'  
app.config['MAIL_PASSWORD'] = 'idvbrbrwsndlowft'  
app.config['MAIL_USE_TLS'] = False  
app.config['MAIL_USE_SSL'] = True 
mail = Mail(app)  
otp = randint(000000,999999)

@app.route('/')
def index():
  return render_template('index.html')
  
@app.route('/blogg')
def blog2():
  return render_template('blogg.html') 
  
@app.route('/plagcheck')
def plagcheck():
  checkplag()
  return render_template('plagcheck.html',output=a)   
  
@app.route('/teacherlogin')
def teacherlogin():
  return render_template('teacherlogin.html')  
  
@app.route('/viewresult')
def viewresult():
  return render_template('viewresult.html')    
  
@app.route('/exam')
def exam():
	check=''
	return render_template('exam.html',check=check) 
    
@app.route('/createtest')
def createtest():
  return render_template('createtest.html')  
  
@app.route('/markresult')
def markresult():
  return render_template('markresult.html')   

def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData
    
@app.route('/submit',methods=['GET','POST'])
def submit():
	if request.method=='POST':

		#Getting input(code and input for program) and checkbox value from the form.
		code=request.form['code']
		inp=request.form['input']
		chk=request.form.get('check')
    
        #Checking if the checkbox is checked or not.
		if  not chk=='1':
			#If checkbox was not ckecked then the input field will be empty and checkbox will be unchecked. 
			inp=""
			check=''
		else:
			##If checkbox was ckecked then the input field will stay the same and checkbox will be checked.
			check='checked'
    
        #calling the function to compile and execute the c program.	
		output=complier_output(code,inp,chk)
	#return render_tempelate to 	
	return render_template('exam.html',code=code,input=inp,output=output,check=check)
    
def complier_output(code,inp,chk):
  #checking if a file already exists or not in no the create one.
  x=datetime.now().strftime("%Y_%m_%d_%H_%M_%S")  
  x=str(x)
  username = session['name']
  filename = username + "_" + x +".c"
  if not os.path.exists(filename):
    os.open(filename,os.O_CREAT)
  #creating a file descriptor to write in to the file.	
  fd=os.open(filename,os.O_WRONLY)	
  #truncate the content of the file to 0 bytes so that there is no overwriting in any way using the write operation.
  os.truncate(fd,0)
  #encode the string into bytes.
  fileadd=str.encode(code)
  #write to the file.
  os.write(fd,fileadd)
  #close the file descriptor.
  os.close(fd)
  #Compiling the c program file and retrieving the error if any. 
  s=subprocess.run(['gcc','-o','new',filename],stderr=PIPE,shell=True)
  #storing the value returned by return code.
  check=s.returncode
  #checking whether program compiled succesfully or not.
  if check==0:
	#cheking whether input for program is enabled or not.
	  if chk=='1':
		#executing the program with input.
		  r=subprocess.run(["new.exe"],input=inp.encode(),stdout=PIPE,shell=True)
	  else:
		  #executing the program without input.
		  r=subprocess.run(["new.exe"],stdout=PIPE,shell=True)
	  #return the output of the program.	
	  return r.stdout.decode("utf-8")
  else:
	#return the error if the program did not compile successfully
	  return s.stderr.decode("utf-8")
    
def checkplag():
    try:
        auth_token = Copyleaks.login(EMAIL_ADDRESS, KEY)
    except CommandError as ce:
        response = ce.get_response()
        print(f"An error occurred (HTTP status code {response.status_code}):")
        print(response.content)
        exit(1)
    print("Logged successfully!\nToken:")
    print(auth_token)
    #data = open(filename, "r").read()
    fn='nillin1234_2022_11_05_22_30_52.c'
    data = open(fn, "r").read()
    print(data)
    data_bytes = base64.b64encode(bytes(data, 'utf-8')) # bytes
    encoded=data_bytes.decode('utf-8') # convert bytes to string
    print(encoded)
    #encoded = base64.b64encode(data)
    SCAN_ID = random.randint(100, 100000)  # generate a random scan id
    file_submission = FileDocument(encoded, fn)
    scan_properties = ScanProperties('http://127.0.0.1:5000/plagcheck/{status}/SCAN_ID')
    scan_properties.set_sandbox(True)  # Turn on sandbox mode. Turn off on production.
    file_submission.set_properties(scan_properties)
    Copyleaks.submit_file(auth_token, SCAN_ID, file_submission)  # sending the submission to scanning
    print("Send to scanning")
    a="You will notify, using your webhook, once the scan was completed."
    print("You will notify, using your webhook, once the scan was completed.")
    return a
    
    
    
@app.route('/dashboard')  
def dashboard():

    #if not session.get("name"):
        # if not there in the session then redirect to the login page
        #return redirect("/login")
    return render_template('dashboard.html')

@app.route('/dashboardteacher')  
def dashboardteacher():

    #if not session.get("name"):
        # if not there in the session then redirect to the login page
        #return redirect("/login")
    return render_template('dashboardteacher.html')
    
@app.route('/viewtests')  
def viewtests():
    return render_template('viewtests.html')
    
@app.route("/searchtestall",methods=["POST","GET"])
def searchtestall():
    print("Content-Type: text/html")
    print()
    candidate=" "
    htmlresponse=[]
    try:
        con = mysql.connector.connect(user="nilesh@registerdbnew1", password="uAeSy9@1", host="registerdbnew1.mysql.database.azure.com", port=3306, database="bu_code",  ssl_ca=r"C:\Users\dell\Downloads\BaltimoreCyberTrustRoot.crt.pem",ssl_disabled=False)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cur=con.cursor()
        print("Connection established")
        if request.method == 'POST':
            query = "SELECT * from `questions` ORDER BY `questionid`"
            cur.execute(query)
            numrows = int(cur.rowcount)
            candidate = cur.fetchall()
            for result in candidate:
                    t = result[6]
                    t=t.strftime('%Y-%m-%d %H:%M:%S') 
                    content = {'testID': result[0], 'testName': result[1], 'input': result[3], 'output': result[4], 'skill': result[5], 'topic': result[2], 'deadline': t}
                    htmlresponse.append(content)
                    content = {}
    print(htmlresponse)
    return jsonify(htmlresponse) 

def write_file(data, filename):
    # Convert binary data to proper format and write it on Hard Disk    
    if (os.path.exists(filename) == False):
        with open(filename, 'wb') as file:
            file.write(data)
        
@app.route('/return-files/')
def return_files_tut():
	try:
		return send_file(fileobj, attachment_filename=fileobj)
	except Exception as e:
		return str(e)        
    
@app.route("/searchresultall",methods=["POST","GET"])
def searchresultall():
    print("Content-Type: text/html")
    print()
    candidate=" "
    htmlresponse=[]
    try:
        con = mysql.connector.connect(user="nilesh@registerdbnew1", password="uAeSy9@1", host="registerdbnew1.mysql.database.azure.com", port=3306, database="bu_code",  ssl_ca=r"C:\Users\dell\Downloads\BaltimoreCyberTrustRoot.crt.pem",ssl_disabled=False)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cur=con.cursor()
        print("Connection established")
        if request.method == 'POST':
            query = "SELECT * from `result` ORDER BY `submit_time`"
            cur.execute(query)
            numrows = int(cur.rowcount)
            username = session['name']
            global fileobj
            candidate = cur.fetchall()
            for arr in candidate:
                    t = arr[6]
                    t=t.strftime('%Y-%m-%d %H:%M:%S') 
                    file = arr[5]
                    fileobj = username + "_" + str(arr[3])+".c"
                    write_file(file, fileobj)
                    content = {'stud_enroll': arr[0], 'stud_name': arr[1], 'stud_batch': arr[2], 'questionid': arr[3], 'question': arr[4], 'submit_time': t, 'plag_score': arr[7],'score' : arr[8]}
                    htmlresponse.append(content)
                    content = {}
    print(htmlresponse)
    return jsonify(htmlresponse)
    
@app.route("/studsearchresultall",methods=["POST","GET"])
def studsearchresultall():
    print("Content-Type: text/html")
    print()
    candidate=" "
    htmlresponse=[]
    try:
        con = mysql.connector.connect(user="nilesh@registerdbnew1", password="uAeSy9@1", host="registerdbnew1.mysql.database.azure.com", port=3306, database="bu_code",  ssl_ca=r"C:\Users\dell\Downloads\BaltimoreCyberTrustRoot.crt.pem",ssl_disabled=False)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cur=con.cursor()
        print("Connection established")
        if request.method == 'POST':
            username = session['name']
            '''
            query = ("SELECT * from `student_login` WHERE `stud_name` = %s",(username,))
            cur.execute(*query)
            candidate = cur.fetchall()
            for arr in candidate:
                stud_id= arr[0]
            print(stud_id)
            '''
            #query = "SELECT * from `result` WHERE `stud_name`= %s and `questionid` LIKE %s ORDER BY submit_time DESC LIMIT 20"
            query2 = ("SELECT * from `result` WHERE `stud_name`= %s ORDER BY submit_time DESC LIMIT 20",(username,))
            #cur.execute(query)
            #cur.execute(query, val)
            cur.execute(*query2)
            numrows = int(cur.rowcount)
            candidate2 = cur.fetchall()
            for arr in candidate2:
                    file = arr[5]
                    fileobj = username + "_" + str(arr[3])+".c"
                    write_file(file, fileobj)
                    content = {'questionid': arr[3], 'question': arr[4], 'plag_score': arr[7],'score' : arr[8]}
                    htmlresponse.append(content)
                    content = {}
    print(htmlresponse)
    return jsonify(htmlresponse)    
    
@app.route("/studsearchresultbyqid",methods=["POST","GET"])
def studsearchresultbyqid():
    print("Content-Type: text/html")
    print()
    candidate=" "
    htmlresponse=[]
    try:
        con = mysql.connector.connect(user="nilesh@registerdbnew1", password="uAeSy9@1", host="registerdbnew1.mysql.database.azure.com", port=3306, database="bu_code",  ssl_ca=r"C:\Users\dell\Downloads\BaltimoreCyberTrustRoot.crt.pem",ssl_disabled=False)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cur=con.cursor()
        print("Connection established")
        if request.method == 'POST':
            username = session['name']
            search_word = request.form.get("query", False)
            print(search_word)
            search_word= f"%{search_word}%"
            query = "SELECT * from `result` WHERE `stud_name`= %s ORDER BY submit_time DESC LIMIT 20"
            #cur.execute(query)
            cur.execute(query, (username,search_word))
            numrows = int(cur.rowcount)
            global fileobj
            candidate = cur.fetchall()
            for arr in candidate:
                    file = arr[5]
                    fileobj = username + "_" + str(arr[3])+".c"
                    write_file(file, fileobj)
                    content = {'questionid': arr[3], 'question': arr[4], 'plag_score': arr[7],'score' : arr[8]}
                    htmlresponse.append(content)
                    content = {}
    print(htmlresponse)
    return jsonify(htmlresponse)      
    
@app.route("/searchresultbybatch",methods=["POST","GET"])
def searchresultbybatch():
    print("Content-Type: text/html")
    print()
    candidate=" "
    htmlresponse=[]
    try:
        con = mysql.connector.connect(user="nilesh@registerdbnew1", password="uAeSy9@1", host="registerdbnew1.mysql.database.azure.com", port=3306, database="bu_code",  ssl_ca=r"C:\Users\dell\Downloads\BaltimoreCyberTrustRoot.crt.pem",ssl_disabled=False)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cur=con.cursor()
        print("Connection established")
        if request.method == 'POST':
            search_word = request.form.get("query", False)
            print(search_word)
            search_word= f"%{search_word}%"
            query = ("SELECT * from `result` WHERE `stud_batch` LIKE %s ORDER BY submit_time DESC LIMIT 20",(search_word,))
            cur.execute(*query)
            candidate = cur.fetchall()
            numrows = int(cur.rowcount)
            username = session['name']
            global fileobj
            candidate = cur.fetchall()
            for arr in candidate:
                    t = arr[6]
                    t=t.strftime('%Y-%m-%d %H:%M:%S') 
                    file = arr[5]
                    fileobj = username + "_" + str(arr[3])+".c"
                    write_file(file, fileobj)
                    content = {'stud_enroll': arr[0], 'stud_name': arr[1], 'stud_batch': arr[2], 'questionid': arr[3], 'question': arr[4], 'submit_time': t, 'plag_score': arr[7],'score' : arr[8]}
                    htmlresponse.append(content)
                    content = {}
    print(htmlresponse)
    return jsonify(htmlresponse)     
    
@app.route("/searchresultbyqid",methods=["POST","GET"])
def searchresultbyqid():
    print("Content-Type: text/html")
    print()
    candidate=" "
    htmlresponse=[]
    try:
        con = mysql.connector.connect(user="nilesh@registerdbnew1", password="uAeSy9@1", host="registerdbnew1.mysql.database.azure.com", port=3306, database="bu_code",  ssl_ca=r"C:\Users\dell\Downloads\BaltimoreCyberTrustRoot.crt.pem",ssl_disabled=False)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cur=con.cursor()
        print("Connection established")
        if request.method == 'POST':
            search_word = request.form.get("query", False)
            print(search_word)
            search_word= f"%{search_word}%"
            query = ("SELECT * from `result` WHERE `questionid` LIKE %s ORDER BY submit_time DESC LIMIT 20",(search_word,))
            cur.execute(*query)
            candidate = cur.fetchall()
            numrows = int(cur.rowcount)
            username = session['name']
            global fileobj
            candidate = cur.fetchall()
            for arr in candidate:
                    t = arr[6]
                    t=t.strftime('%Y-%m-%d %H:%M:%S') 
                    file = arr[5]
                    fileobj = username + "_" + str(arr[3])+".c"
                    write_file(file, fileobj)
                    content = {'stud_enroll': arr[0], 'stud_name': arr[1], 'stud_batch': arr[2], 'questionid': arr[3], 'question': arr[4], 'submit_time': t, 'plag_score': arr[7],'score' : arr[8]}
                    htmlresponse.append(content)
                    content = {}
    print(htmlresponse)
    return jsonify(htmlresponse)     
    
@app.route("/searchtestbyname",methods=["POST","GET"])
def searchtestbyname():
    print("Content-Type: text/html")
    print()
    candidate=" "
    htmlresponse=[]
    try:
        con = mysql.connector.connect(user="nilesh@registerdbnew1", password="uAeSy9@1", host="registerdbnew1.mysql.database.azure.com", port=3306, database="bu_code",  ssl_ca=r"C:\Users\dell\Downloads\BaltimoreCyberTrustRoot.crt.pem",ssl_disabled=False)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cur=con.cursor()
        print("Connection established")
        if request.method == 'POST':
            search_word = request.form.get("query", False)
            print(search_word)
            search_word= f"%{search_word}%"
            query = ("SELECT * from `questions` WHERE `question` LIKE %s ORDER BY questionid DESC LIMIT 20",(search_word,))
            cur.execute(*query)
            candidate = cur.fetchall()
            print(candidate)
            for result in candidate:
                t = result[6]
                t=t.strftime('%Y-%m-%d %H:%M:%S')
                content = {'testID': result[0], 'testName': result[1], 'input': result[3], 'output': result[4], 'skill': result[5], 'topic': result[2], 'deadline': t}
                htmlresponse.append(content)
                content = {}
    print(htmlresponse)
    return jsonify(htmlresponse)
    
@app.route("/searchtestbyskills",methods=["POST","GET"])
def searchtestbyskills():
    print("Content-Type: text/html")
    print()
    candidate=" "
    htmlresponse=[]
    try:
        con = mysql.connector.connect(user="nilesh@registerdbnew1", password="uAeSy9@1", host="registerdbnew1.mysql.database.azure.com", port=3306, database="bu_code",  ssl_ca=r"C:\Users\dell\Downloads\BaltimoreCyberTrustRoot.crt.pem",ssl_disabled=False)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cur=con.cursor()
        print("Connection established")
        if request.method == 'POST':
            search_word = request.form.get("query", False)
            print(search_word)
            search_word= f"%{search_word}%"
            query = ("SELECT * from `questions` WHERE `topic` LIKE %s ORDER BY questionid DESC LIMIT 20",(search_word,))
            cur.execute(*query)
            candidate = cur.fetchall()
            print(candidate)
            for result in candidate:
                t = result[6]
                t=t.strftime('%Y-%m-%d %H:%M:%S')
                content = {'testID': result[0], 'testName': result[1], 'input': result[3], 'output': result[4], 'skill': result[5], 'topic': result[2], 'deadline': t}
                htmlresponse.append(content)
                content = {}
    print(htmlresponse)
    return jsonify(htmlresponse)   
    


@app.route("/table_update",methods=["POST","GET"])
def table_update():
    msg=''
    try:
        con = mysql.connector.connect(user="nilesh@registerdbnew1", password="uAeSy9@1", host="registerdbnew1.mysql.database.azure.com", port=3306, database="bu_code",  ssl_ca=r"C:\Users\dell\Downloads\BaltimoreCyberTrustRoot.crt.pem",ssl_disabled=False)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cur=con.cursor()
        print("Connection established")
        if request.method == 'POST':
            table=request.form['table']
            if(table=='questions'):
                string = request.form['string']
                signup1=request.form
                question=signup1['question']
                topic=signup1['topic']
                tempinput=signup1['input']
                output=signup1['output']
                skills = request.form['skills']
                t = request.form['deadline']
                t = t.replace("T", " ")
                t = t.replace("-", " ")
                format = '%Y %m %d %H:%M'
                date_object = datetime.strptime(t, format)
                print(date_object)
                #t=t.strftime('%Y-%m-%d %H:%M:%S')
                if not question or not topic or not skills or not date_object or not tempinput or not output:
                    msg="Update Failed. All Form Fields With '*' Are Required."
                    return jsonify(msg)
                print(string)
                cur.execute("UPDATE `questions` SET `question` = %s, `topic` = %s, `input` = %s, `output` = %s, `skills`= %s, `deadline`= %s   WHERE `questionid` = %s ", [question, topic, tempinput, output, skills, date_object,string])
                con.commit()

                cur.close()
                con.close()
                msg = 'Record successfully Updated. Reloading the page...'
            elif(table=='result'):
                string1 = request.form['string1']
                signup1=request.form
                string2=signup1['string2']
                score=signup1['score']
                print("\nValue of score: ",score)
                if not score:
                    msg="Update Failed. All Form Fields With '*' Are Required."
                    return jsonify(msg)
                cur.execute("UPDATE `result` SET `score` = %s WHERE `questionid` = %s and `stud_enroll` = %s", [score, string2, string1])
                con.commit()

                cur.close()
                con.close()
                msg = 'Record successfully Updated. Reloading the page...'
            else:
                msg= 'Error.'
        return jsonify(msg) 

@app.route("/cand_add",methods=["POST","GET"])
def cand_add():
    try:
        con = mysql.connector.connect(user="nilesh@registerdbnew1", password="uAeSy9@1", host="registerdbnew1.mysql.database.azure.com", port=3306, database="bu_code",  ssl_ca=r"C:\Users\dell\Downloads\BaltimoreCyberTrustRoot.crt.pem",ssl_disabled=False)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cur=con.cursor()
        print("Connection established")
        if request.method == 'POST':
            table=request.form['table']
            if(table=='questions'):
                signup1=request.form
                question=signup1['question']
                topic=signup1['topic']
                tempinput=signup1['input']
                output=signup1['output']
                skills = request.form['skills']
                t = request.form['deadline']
                t = t.replace("T", " ")
                t = t.replace("-", " ")
                format = '%Y %m %d %H:%M'
                date_object = datetime.strptime(t, format)
                print(date_object)
                if not question or not topic or not skills or not date_object or not tempinput or not output:
                    msg="Error. All Form Fields With '*' Are Required."
                    return jsonify(msg)
                cur.execute("insert into questions(question,topic,input,output,skills,deadline) values(%s,%s,%s,%s,%s,%s)",(question,topic,tempinput,output,skills,date_object))
                con.commit()
                con.commit()
                cur.close()
                con.close()
                msg = 'Record successfully Added. Please reload.' 
            elif(table=='result'):
                signup1=request.form
                questionid=signup1['questionid']
                code=request.form['code']
                print(questionid)
                if not questionid:
                    msg="Error. Question Id is Required."
                    return jsonify(msg)
                if not code:
                    msg="Error. You submitted a blank code."
                    #GET ALL FIELDS(COULMNS)
                x=datetime.now().strftime("%Y_%m_%d_%H_%M_%S")  
                x=str(x)
                #format = '%Y %m %d %H:%M'
                #date_object = datetime.strptime(x, format)
                date_object=datetime.now()
                username = session['name']
                print(username)
                query = ("SELECT * from `student_login` WHERE `stud_name` = %s",(username,))
                cur.execute(*query)
                candidate = cur.fetchall()
                for arr in candidate:
                    stud_id= arr[0]
                    stud_batch=arr[5]
                query2 = ("SELECT * from `questions` WHERE `questionid` = %s",(questionid,))
                cur.execute(*query2)
                candidate2 = cur.fetchall()
                for arr in candidate2:
                    question= arr[1]
                filename = username + "_" + x +".c"
                print(filename)
                if not os.path.exists(filename):
                    os.open(filename,os.O_CREAT)	
                fd=os.open(filename,os.O_WRONLY)	
                os.truncate(fd,0)
                fileadd=str.encode(code)
                os.write(fd,fileadd)
                os.close(fd)
                sql_insert_blob_query = "INSERT INTO result(stud_enroll, stud_name, stud_batch,questionid,question,stud_test_file,submit_time) VALUES (%s,%s,%s,%s,%s,%s,%s)"
                file = convertToBinaryData(filename)    
                # Convert data into tuple format
                insert_blob_tuple = (stud_id, username, stud_batch, questionid, question, file,date_object)
                cur.execute(sql_insert_blob_query, insert_blob_tuple)
                con.commit()
                con.commit()
                cur.close()
                con.close()
                msg = 'Your code has been successfully submitted.' 
            else:
                msg="error."
    return jsonify(msg)       

@app.route("/cand_delete",methods=["POST","GET"])
def cand_delete():
    msg=""
    try:
        con = mysql.connector.connect(user="nilesh@registerdbnew1", password="uAeSy9@1", host="registerdbnew1.mysql.database.azure.com", port=3306, database="bu_code",  ssl_ca=r"C:\Users\dell\Downloads\BaltimoreCyberTrustRoot.crt.pem",ssl_disabled=False)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cur=con.cursor()
        print("Connection established")
        if request.method == 'POST':
            table= request.form['table']
            if(table=='questions'):
                getid = request.form['string']
                print(getid)
                cur.execute("DELETE FROM `questions` WHERE `questionid` = %s",[getid])
                msg = 'Record deleted successfully'  
            elif(table=='result'):
                string1 = request.form['string1']
                string2 = request.form['string2']
                print(getid)
                cur.execute("DELETE FROM `result` WHERE `questionid` = %s and `stud_enroll` = %s",[ string2, string1])
                msg = 'Record deleted successfully'  
            else:
                msg="error"
        con.commit()

        cur.close()
        con.close()   
    return jsonify(msg)     
    
@app.route('/verify')  
def verify():
  return render_template('verify.html')
  
@app.route('/validate')  
def validate():
  return render_template('validate.html')
  
@app.route('/verifyteacher')  
def verifyteacher():
  return render_template('verifyteacher.html')
  
@app.route('/validateteacher')  
def validateteacher():
  return render_template('validateteacher.html')
    
@app.route('/forpass',methods=["POST","GET"])   
def forpass():  
    print("Content-Type: text/html")
    print()
    try:
        con = mysql.connector.connect(user="nilesh@registerdbnew1", password="uAeSy9@1", host="registerdbnew1.mysql.database.azure.com", port=3306, database="bu_code",  ssl_ca=r"C:\Users\dell\Downloads\BaltimoreCyberTrustRoot.crt.pem",ssl_disabled=False)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cur=con.cursor()
        
        if request.method=='POST':
            pwd=request.form.get("pwd", False)  
            conpwd=request.form.get("conpwd", False)  
            if not pwd or not conpwd:
                error_statement="All Form Fields With '*' Are Required."
                return render_template('fail.html', error_statement=error_statement)
            digi = True if next((chr for chr in pwd if chr.isdigit()), None) else False
            if len(pwd)<8 or digi==False:
                error_statement="Incorrect Password Format. Password must have a minimum length of 8 and must contain a digit. "
                return render_template('fail.html', error_statement=error_statement)
            if pwd!=conpwd:
                error_statement="Passwords do not match. Please enter again. "
                return render_template('fail.html', error_statement=error_statement)
            cur.execute("update `student_login` set `stud_password`=%s where `stud_email`=%s",(pwd,stud_email))
            con.commit()
            
            cur.close()
            con.close()
    flash('Your Password has been successfully updated. Please login again.')
    return render_template('forpass.html')
    
@app.route('/forpassteacher',methods=["POST","GET"])   
def forpassteacher():  
    print("Content-Type: text/html")
    print()
    try:
        con = mysql.connector.connect(user="nilesh@registerdbnew1", password="uAeSy9@1", host="registerdbnew1.mysql.database.azure.com", port=3306, database="bu_code",  ssl_ca=r"C:\Users\dell\Downloads\BaltimoreCyberTrustRoot.crt.pem",ssl_disabled=False)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cur=con.cursor()
        
        if request.method=='POST':
            pwd=request.form.get("pwd", False)  
            conpwd=request.form.get("conpwd", False)  
            if not pwd or not conpwd:
                error_statement="All Form Fields With '*' Are Required."
                return render_template('fail.html', error_statement=error_statement)
            digi = True if next((chr for chr in pwd if chr.isdigit()), None) else False
            if len(pwd)<8 or digi==False:
                error_statement="Incorrect Password Format. Password must have a minimum length of 8 and must contain a digit. "
                return render_template('fail.html', error_statement=error_statement)
            if pwd!=conpwd:
                error_statement="Passwords do not match. Please enter again. "
                return render_template('fail.html', error_statement=error_statement)
            cur.execute("update `teacher_login` set `teacher_pass`=%s where `teacher_email`=%s",(pwd,stud_email))
            con.commit()
            
            cur.close()
            con.close()
    flash('Your Password has been successfully updated. Please login again.')
    return render_template('forpassteacher.html')    

@app.route('/validate',methods=["POST","GET"])   
def otp_check():  
    if request.method=='POST':
        user_otp=request.form.get("otp", False)    
        if otp == int(user_otp):  
            return redirect(url_for('forpass')) 
        else:
            flash('Invalid OTP. Email Verification incomplete.')            
            return redirect(url_for('verify'))
            
@app.route('/validateteacher',methods=["POST","GET"])   
def otp_check_teach():  
    if request.method=='POST':
        user_otp=request.form.get("otp", False)    
        if otp == int(user_otp):  
            return redirect(url_for('forpassteacher')) 
        else:
            flash('Invalid OTP. Email Verification incomplete.')            
            return redirect(url_for('verifyteacher'))

    
@app.route('/verify',methods=["POST","GET"])  
def verifymail():
    try:
        con = mysql.connector.connect(user="nilesh@registerdbnew1", password="uAeSy9@1", host="registerdbnew1.mysql.database.azure.com", port=3306, database="bu_code",  ssl_ca=r"C:\Users\dell\Downloads\BaltimoreCyberTrustRoot.crt.pem",ssl_disabled=False)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cur=con.cursor()
    
        if request.method=='POST':
            global stud_email
            stud_email=request.form.get("email", False)
            sql = "SELECT * FROM `student_login` WHERE `stud_email` = %s"
            cur.execute(sql,(stud_email,))
            cur=cur.fetchall()
            print(cur)
            if len(cur)==1:
                msg = Message('OTP',sender = 'nileshgupta2001@gmail.com', recipients = [stud_email])  
                msg.body = str(otp)  
                mail.send(msg)
                return redirect(url_for('validate'))
            else:
                flash('Email not registered')
                return redirect(url_for('verify'))
                
@app.route('/verifyteacher',methods=["POST","GET"])                  
def verifymailteach():
    try:
        con = mysql.connector.connect(user="nilesh@registerdbnew1", password="uAeSy9@1", host="registerdbnew1.mysql.database.azure.com", port=3306, database="bu_code",  ssl_ca=r"C:\Users\dell\Downloads\BaltimoreCyberTrustRoot.crt.pem",ssl_disabled=False)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cur=con.cursor()
    
        if request.method=='POST':
            global teacher_email
            teacher_email=request.form.get("email", False)
            sql = "SELECT * FROM `teacher_login` WHERE `teacher_email` = %s"
            cur.execute(sql,(teacher_email,))
            cur=cur.fetchall()
            print(cur)
            if len(cur)==1:
                msg = Message('OTP',sender = 'nileshgupta2001@gmail.com', recipients = [teacher_email])  
                msg.body = str(otp)  
                mail.send(msg)
                return redirect(url_for('validateacher'))
            else:
                flash('Email not registered')
                return redirect(url_for('verifyteacher'))
                
                
      
@app.route("/",methods=["POST"])  
def checklogin():     
  try:
    con = mysql.connector.connect(user="nilesh@registerdbnew1", password="uAeSy9@1", host="registerdbnew1.mysql.database.azure.com", port=3306, database="bu_code",  ssl_ca=r"C:\Users\dell\Downloads\BaltimoreCyberTrustRoot.crt.pem",ssl_disabled=False)
    print("Connection established")
  except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with the user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
  else:
    cur=con.cursor()
    signin=request.form
    email=signin['email']
    pwd=signin['pwd']
    if not email:
        error_statement="Email is required"
        return render_template('fail.html', error_statement=error_statement)
    if not pwd:
        error_statement="Password is required"
        return render_template('fail.html', error_statement=error_statement)

    sql = "SELECT * FROM `student_login` WHERE `stud_email` = %s AND `stud_password` =%s"

    cur.execute(sql, (email, pwd))
    #rows=cur.execute("select email,pwd from candidate where email={a} and pwd={b}".format(a=email,b=pwd))
    cur=cur.fetchall()
    print(cur)
    if len(cur)==1:
        username=cur[0][1]
        session["name"]=username
        #flash('Logged in successfully as')
        return render_template('dashboard.html',username=username)
    else:
        flash('Invalid Username and password. Please try again.')
        return render_template('index.html',email=email)
        
@app.route("/teacherlogin",methods=["POST"])  
def checkloginteacher():     
  try:
    con = mysql.connector.connect(user="nilesh@registerdbnew1", password="uAeSy9@1", host="registerdbnew1.mysql.database.azure.com", port=3306, database="bu_code",  ssl_ca=r"C:\Users\dell\Downloads\BaltimoreCyberTrustRoot.crt.pem",ssl_disabled=False)
    print("Connection established")
  except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with the user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
  else:
    cur=con.cursor()
    signin=request.form
    email=signin['email']
    pwd=signin['pwd']
    if not email:
        error_statement="Email is required"
        return render_template('fail.html', error_statement=error_statement)
    if not pwd:
        error_statement="Password is required"
        return render_template('fail.html', error_statement=error_statement)

    sql = "SELECT * FROM `teacher_login` WHERE `teacher_email` = %s AND `teacher_pass` =%s"

    cur.execute(sql, (email, pwd))
    #rows=cur.execute("select email,pwd from candidate where email={a} and pwd={b}".format(a=email,b=pwd))
    cur=cur.fetchall()
    print(cur)
    if len(cur)==1:
        username=cur[0][1]
        session["name"]=username
        #flash('Logged in successfully as')
        return render_template('dashboardteacher.html',username=username)
    else:
        flash('Invalid Username and password. Please try again.')
        return render_template('teacherlogin.html',email=email)
        
      
 
#@app.route("/logout")
#def logout():
   # session["name"] = None
    #return render_template('logout.html')
 
    

if __name__ == '__main__':
  app.run(debug=True)