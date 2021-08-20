import numpy as np
from flask import Flask, request
from redcap import Project
from flask import jsonify
import requests
import pandas as pd
import sys


app = Flask(__name__)


@app.route('/')
def hello_world():
    api_url = 'https://redcap34.mdanderson.org/api/'
    api_key = 'BC107D101DB6A3444C1303A4C8D57FAC'
    project = Project(api_url, api_key)
    data = project.export_records(records=[1],fields=['bmi'])
    #print(data)
    return jsonify(data)

@app.route("/register", methods=["POST"])
def register():
    # this line goes to the console/terminal in flask dev server
    print(request.form.to_dict())
    if(request.form.to_dict()['instrument']=="participant_contact_and_scheduling_form_appendix_b"):
        post_rn=request.form.to_dict()['record']
        api_url = 'http://localhost/redcapstd/api/'
        api_key = '5FC5EA62E4CCA75AC76A1EAFB4CAA5C9'
        project = Project(api_url, api_key)
        data = project.export_records(records=[post_rn], fields=['y_b1_first_record','y_hh_id_exists'])
        print(type(data))
        print(type(data))
        first_hh=data[0]['y_b1_first_record']
        target_hh = data[0]['y_hh_id_exists']
        if (first_hh=='1'):
            return ('', 204)
        r_hh=project.export_reports(format='df',report_id=39)
        r_hh_row=r_hh.loc[r_hh['y_hh_id'] == target_hh]

        r_hh_row.insert(0,'record_id',post_rn)
        r_hh_row.drop(['y_hh_id'],axis=1,inplace=True)
        r_hh_row.reset_index(drop=True,inplace=True)
        print(r_hh_row.dtypes)
        #we need to convert all numerical fields which are of type float by default in a df to int, but leave string as objects
        m = r_hh_row.select_dtypes(np.number)
        r_hh_row[m.columns] = m.round().astype('Int64')

        print(r_hh_row.dtypes)
        r_imp_file=r_hh_row.to_csv('C:/REDCap/PROTECT/POC/fam.csv', index = False)
        r_imp=r_hh_row.to_csv(index=False)

        response = project.import_records(r_imp, format='csv', date_format='MDY')
        return response
    else:
        return ('', 204)

    #project.import_records()
    # this line prints out the form to the browser
   # return jsonify(data)

if __name__ == '__main__':
    app.run()
