from flask import Flask, request
from redcap import Project
from flask import jsonify
import requests
import pandas as pd
import sys


app = Flask(__name__)


@app.route('/')
def hello_world():
    api_url = 'https://redcap2.mdanderson.org/api/'
    api_key = 'BC107D101DB6A3444C1303A4C8D57FAC'
    project = Project(api_url, api_key)
    data = project.export_records(records=[1],fields=['bmi'])
    #print(data)
    return jsonify(data)

@app.route("/register", methods=["POST"])
def register():
    # this line goes to the console/terminal in flask dev server
    print(request.form.to_dict())
    post_rn=request.form.to_dict()['record']
    api_url = 'http://localhost/redcap/api/'
    api_key = 'C3127D2CDE7E60708F89FFAAB01C0F49'
    project = Project(api_url, api_key)
    data = project.export_records(records=[post_rn], fields=['mrn'])
    print(type(data))
    print(type(data[0]))
    mrn=data[0]['mrn']
    print(mrn)
    #now lets import data
    #get payload from external system
    #to_import = {'record_id': post_rn, 'f_name':'Joe', 'l_name':'Shmoe', 'dob': '02/14/2000'}
    #to_import=requests.get("https://roadsdev.mdanderson.org/ws/api/Mosaiq/treatmentsText/" + mrn)
    to_import=requests.get('https://roadsdev.mdanderson.org/ws/api/Mosaiq/treatmentText/'+mrn)
    #up=to_import.json()
    #mosq=to_import.content.decode("utf-8")
    mosq = to_import.text
    up={'record_id': [post_rn],'mosiaq_txt':[mosq]}
    df=pd.DataFrame(up)
    print(up)
    response = project.import_records(df, date_format='MDY')

    #project.import_records()
    # this line prints out the form to the browser
   # return jsonify(data)

if __name__ == '__main__':
    app.run()
