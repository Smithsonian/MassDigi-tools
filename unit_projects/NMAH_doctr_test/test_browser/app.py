#!flask/bin/python
#
# Viz
#
# Import flask
from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template
from flask import redirect
from flask import url_for
from uuid import UUID
import json
import pandas as pd
import locale
import sys
from rapidfuzz import fuzz
import numpy as np
import glob
from pathlib import Path
import os 
import csv

# MySQL
# import mysql.connector

# import settings

# Set locale for number format
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

app = Flask(__name__)

# Disable strict trailing slashes
app.url_map.strict_slashes = False


# @app.route('/', methods=['GET'], provide_automatic_options=False)
# @app.route('/<filename>', methods=['GET'], provide_automatic_options=False)
# def submit(filename=None):
#     """Display a file and the associated info"""

#     # Get images
#     # list_of_files = glob.glob("static/cards/*.jpg")
#     list_of_files = [os.path.basename(x) for x in glob.glob("static/cards/*.jpg")]


@app.route('/', methods=['GET'], provide_automatic_options=False)
def show_file():
    """Display a file and the associated info"""

    # Get images
    # list_of_files = glob.glob("static/cards/*.jpg")
    list_of_files = [os.path.basename(x) for x in glob.glob("static/cards/*.jpg")]
    filename = request.args.get("filename")
    model = request.args.get("model")
    # Check if project exists
    if filename is not None:        
        # Get data from JSON
        with open("static/paleo_ocr_annotations_2-19-2025_Final.json", 'r') as file:
            groundtruthdata = json.load(file)
        allfiles_index = []
        allfiles = []
        for img in groundtruthdata['_via_img_metadata']:
            allfiles_index.append(img.split('.jpg')[0].split('/')[-1])
            allfiles.append(img)

        file_stem = Path(filename).stem
        model_results = glob.glob("static/models/*.csv")
        results_df = pd.DataFrame()

        if model is None:
            model = "tesseract_default"
        
        for model_res in model_results:
            model_df = pd.read_csv(model_res, sep="|", on_bad_lines="skip", quoting=csv.QUOTE_NONE)
            results_df = pd.concat([results_df, model_df])

        results_df = results_df[results_df['filename'] == file_stem]
        results_df = results_df[results_df['model'] == model]
        # results_df = results_df.sort_values(by=['vertices_y_0', 'vertices_x_0'])
        print(results_df)
        results_df = results_df.dropna(subset=['vertices_x_0', 'vertices_x_1', 'vertices_y_0', 'vertices_y_1'])
        print(results_df)
        results_df_json = json.loads(results_df.to_json(orient = "records", index = False))
        
        image = "cards/{}.jpg".format(file_stem)
        
        model_text_df = pd.DataFrame(columns=('text', 'x', 'y', 'width', 'height'))
        model_text = []
        y = None
        x = None
        i = 0
        y_thres = 10
        x_thres = 50
        for row in results_df_json:
            model_text_df.loc[len(model_text_df)] = [
                                                row['word'],
                                                row['vertices_x_0'], 
                                                row['vertices_y_0'], 
                                                int(row['vertices_x_1']) - int(row['vertices_x_0']), 
                                                int(row['vertices_y_1']) - int(row['vertices_y_0'])
                                                ]
            if y != None:
                # If in a similar line based on y
                if abs(int(row['vertices_y_0']) - y) < y_thres:
                    if x != None:
                        # Check if this one comes after the last one
                        print(int(row['vertices_x_0']))
                        print(x)
                        print(int(row['vertices_x_0']) - x)
                        if int(row['vertices_x_0']) > x:
                            if (len(model_text) == i):
                                print(1)
                                if abs(int(row['vertices_x_0']) - x) < x_thres:
                                    print(4)
                                    model_text[i-1] = "{} {}".format(model_text[i-1], row['word'])
                                else:
                                    print(3)
                                    model_text.append(row['word'])
                                    i += 1
                            else:
                                model_text.append(row['word'])
                                i += 1
                        else:
                            if (len(model_text) == i):
                                print(2)
                                if (x - int(row['vertices_x_1'])) < x_thres:
                                    model_text[i-1] = "{} {}".format(row['word'], model_text[i-1])
                                else:
                                    model_text.append(row['word'])
                                    i += 1
                            else:
                                model_text.append(row['word'])
                                i += 1
                    else:
                        if (len(model_text) == i):
                            model_text[i-1] = "{} {}".format(model_text[i-1], row['word'])
                        else:
                            model_text.append(row['word'])
                            i += 1
                else:
                    model_text.append(row['word'])
                    i += 1
            else:
                model_text.append(row['word'])
                i += 1
            y = int(row['vertices_y_0'])
            x = int(row['vertices_x_0'])
            print(model_text)
            

        # Ground truth data
        file_address = allfiles[allfiles_index.index(file_stem)]
        thisfile_data = groundtruthdata['_via_img_metadata'][file_address]
        extracted_text_df = pd.DataFrame(columns=('text', 'x', 'y', 'width', 'height'))
        extracted_text = []
        
        y = None
        i = 0
        for row in thisfile_data['regions']:
            extracted_text_df.loc[len(extracted_text_df)] = [row['region_attributes']['text'],
                                               row['shape_attributes']['x'], 
                                               row['shape_attributes']['y'], 
                                               row['shape_attributes']['width'], 
                                               row['shape_attributes']['height'] 
                                               ]
            if y != None:
                if abs(row['shape_attributes']['y'] - y) < 5.0:
                    if (len(extracted_text) == i):
                        extracted_text[i-1] = "{}  {}".format(extracted_text[i-1], row['region_attributes']['text'])
                    else:
                        extracted_text.append(row['region_attributes']['text'])
                        i += 1
                else:
                    extracted_text.append(row['region_attributes']['text'])
                    i += 1
            else:
                extracted_text.append(row['region_attributes']['text'])
                i += 1
            y = row['shape_attributes']['y']


    else:
        filename = ""
        file_stem = None
        results_df = pd.DataFrame()
        image = ""
        extracted_text = pd.DataFrame()
        extracted_text_df = pd.DataFrame()
        model_text = pd.DataFrame()

    return render_template('filename.html', list_of_files=list_of_files,
                           image=image,
                           filename=filename,
                           file_stem=file_stem,
                           model=model,
                           extracted_text=extracted_text,
                           extracted_text_df = results_df,
                           model_text=model_text,
                           datatables=[results_df.to_html(table_id='file_table', index=False, border=0,
                                                         escape=False,
                                                         classes=["display", "compact", "table-striped"])])



#####################################
if __name__ == '__main__':
    app.run(threaded=False, debug=True)
    
