import numpy as np
from flask import Flask, request
from redcap import Project
from flask import jsonify
import requests
import pandas as pd
import sys
from logging.config import fileConfig

app = Flask(__name__)
fileConfig('logging.cfg')

@app.route('/')
def hello_world():
    api_url = 'https://redcap.mdanderson.org/api/'
    api_key = 'BC107D101DB6A3444C1303A4C8D57FAC'
    project = Project(api_url, api_key)
    data = project.export_records(records=[1],fields=['bmi'])
    app.logger.debug("Process default result")
    return jsonify(data)

@app.route("/register", methods=["POST"])
def register():
    # this line goes to the console/terminal in flask dev server
    # read the parameters from external file
    with open('C:/REDCap/PROTECT/POC/hh_params.txt') as f:
        d = dict(l.strip().split('=') for l in f)
        project = Project(d.get('api_url'), d.get('hh_api_key'))
        report_id=d.get('report_id')
    print(request.form.to_dict())
    if(request.form.to_dict()['instrument']=="participant_contact_and_scheduling_form_appendix_b"):
        post_rn=request.form.to_dict()['record']

        data = project.export_records(records=[post_rn], fields=['y_b1_first_record','y_hh_id_exists','y_b1_use_same_info'])
        print(type(data))
        print(type(data))
        first_hh=data[0]['y_b1_first_record']
        use_hh_info=data[0]['y_b1_use_same_info']
        target_hh = data[0]['y_hh_id_exists']
        if (first_hh=='1' or use_hh_info=='0'):
            return ('', 204)
        r_hh=project.export_reports(format='df',report_id=report_id)
        r_hh_row=r_hh.loc[r_hh['y_hh_id'] == target_hh]

        r_hh_row.insert(0,'record_id',post_rn)
        r_hh_row.drop(['y_hh_id'],axis=1,inplace=True)
        r_hh_row.reset_index(drop=True,inplace=True)
        print(r_hh_row.dtypes)
        #we need to convert all numerical fields which are of type float by default in a df to int, but leave string as objects
        m = r_hh_row.select_dtypes(np.number)
        r_hh_row[m.columns] = m.round().astype('Int64')

        print(r_hh_row.dtypes)
        #r_imp_file=r_hh_row.to_csv('C:/REDCap/PROTECT/POC/fam.csv', index = False)
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
