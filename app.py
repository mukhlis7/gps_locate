from flask import Flask , render_template, request ,redirect
import smtplib
import requests
import pyrebase
import json
import regex as re
import random

app = Flask(__name__)

def send_mail_lowbalance_err(low_balance):

        message = "Subject: ALERT! SMS Toolkit Location API Report\n\nReport From:\nLogs:\n Data=\n\n"+low_balance

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("dashdashpass7@gmail.com","createpassword")
        server.sendmail("dashdashpass7@gmail.com", "mukhlisg7@gmail.com", message)
        server.quit()


# root
@app.route("/")
def index():
    """
    this is a root dir of my server
    :return: str
    """
    return "This is root!!!!"


# GET
@app.route('/api/locate')
def locate_with_cellid():


    api_key_url = "http://www.dashfiles.ml/smstoolkit/opencellid_api_keys.txt"

    web_result = requests.get(api_key_url).text
    req_data = re.findall("(?:#)(.*)(?:#)", web_result)

    random_api_key = random.randint(0,len(req_data))

    api_key_with_colon = req_data[random_api_key-1]

    req_data_splited = api_key_with_colon.split(":")

    api_key = req_data_splited[0]


    api_key_no = req_data_splited[1]

    #apikey_opencellid = "df5183df94f98f"

    user_target = request.args.get('usermob')
    mcc = request.args.get('mcc')
    mnc = request.args.get('mnc')
    lac = request.args.get('lac')
    cellid = request.args.get('cellid')

    url = "https://us1.unwiredlabs.com/v2/process.php"

    payload = "{\"token\": \""+api_key+"\",\"radio\": \"gsm\",\"mcc\": "+ mcc + ",\"mnc\": " + mnc + ",\"cells\": [{\"lac\": "+ lac + ",\"cid\": " + cellid + "}],\"address\": 1}"

    response_opencellid = requests.request("POST", url, data=payload)

    location = response_opencellid.text

    location_object = json.loads(location)

    status = location_object['status']
    balance = location_object['balance']
    lat = location_object['lat']
    lon = location_object['lon']
    accuracy = location_object['accuracy']
    address = location_object['address']

    if (balance < 100):
	low_balance = "Your OpenCellID API key Number ["+str(random_api_key)+"] Balance is Less than 100(hundrad) Please Change API key"
	
	send_mail_lowbalance_err(low_balance)

    config = {
    "apiKey": "AIzaSyAYxoc5CXMmzHQE_YuaP9kPdjxI15YOiko",
    "authDomain": "sms-toolkit.firebaseapp.com",
    "databaseURL": "https://sms-toolkit.firebaseio.com",
    "storageBucket": "sms-toolkit.appspot.com"
    }

    firebase = pyrebase.initialize_app(config)

    db = firebase.database()

    #data = {"status": + status}#"Balance": "+balance + "Latitude":"+lat + "Longitude":" +lan+"Accuracy":" +accuracy + "Address":" +address}
    
    data = {"Status": str(status)}
    data['Balance'] = str(balance)
    data['Latitude'] = str(lat)
    data['Logitude']= str(lon)
    data['Accuracy'] =  str(accuracy)
    data['Address'] = str(address)

    db.child(user_target).child("GSM Location").set(data)


    return "Data Loadded"
    
  
