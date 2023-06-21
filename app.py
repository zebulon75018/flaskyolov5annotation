from flask import Flask, render_template, jsonify, request
from flask import send_from_directory

import yaml
import pprint
import sys
import glob
import os
import json
from shutil import copyfile


app = Flask(__name__)

scale = 2.0
ske = { } 
with open(sys.argv[1], 'r') as file:
   ske = yaml.safe_load(file)

print(ske)


def gettxtfromjpg(filename):
    filename = filename.replace("images","labels").replace(".jpg",".txt")
    filename = filename.replace("/static/","")
    return filename

def saveresult(filename, result):
    copyfile(filename,"%s.backup" % (filename))
    with open(filename, 'w') as file:
        for r in result:
            file.write("%s %f %f %f %f\n" % (r["label"],r["x_center"],r["y_center"],r["width"],r["height"]))

    
@app.route('/')
def index():
    print(os.getcwd())
    print("%s/*.jpg" % ( ske["train"]))
    lstimg = glob.glob("%s/*.jpg" % ( ske["train"]))
    pprint.pprint(lstimg)
    return render_template('index.html',lstimg = lstimg)

@app.route('/save/', methods=['POST'])
def save():
    filename = request.form['filenamepix']
    filename = gettxtfromjpg(filename)
    w =  float(request.form['w']) *scale
    h =  float(request.form['h']) *scale
    rects = json.loads(request.form['rects'])
    pprint.pprint(rects)
    result = []
    for r in rects:
       result.append({"label":r["label"], 
                      "x_center":r["left"]/(w) + r["width"]/(w*2),
                      "y_center": r["top"]/(h) + r["height"]/(h*2),
                      "width":r["width"]/w,
                      "height":r["height"]/h})
    saveresult(filename, result)
    print(filename)
    print(rects)
    print(w)
    print(h)
    return ""

@app.route('/data', methods=['GET'])
def data():
    filename = request.args.get('filename')
    filename = gettxtfromjpg(filename)
    #filename = filename.replace("images","labels").replace(".jpg",".txt")
    #filename = filename.replace("/static/","")
    with open(filename) as f:
         lines = f.readlines()
    data = []
    for line in lines:
        label, x_center, y_center, width, height = line.strip().split(' ')
        x_min = float(x_center) - float(width) / 2
        y_min = float(y_center) - float(height) / 2
        x_max = float(x_center) + float(width) / 2
        y_max = float(y_center) + float(height) / 2

        item = {
            'label': label,
            'bbox': [x_min, y_min, x_max, y_max]
        }
        data.append(item)

    return data

    
@app.route('/cdn/<path:filepath>')
def download_file(filepath):
    filepath = filepath.replace("-","/")
    print(filepath)
    dir,filename = os.path.split(filepath)
    print(dir)
    print(filename)

    return send_from_directory(dir, filename, as_attachment=False)


@app.route('/saveall', methods=['POST'])
def saveall():
    with open('char_cfg.yaml', 'w') as file:
           documents = yaml.dump(ske, file) 
    return  ""

@app.route('/save_position', methods=['POST'])
def save_position():
    position = request.get_json()
    # Save the position to a database or perform any other action
    print(position)
    for s in ske["skeleton"]:
       if s["name"] == position["name"]:
            s["loc"] = [position["left"]+2.5,position["top"]+2.5]

    return jsonify({'message': 'Position saved successfully'})

if __name__ == '__main__':
    app.run(debug=True,port = 5001)
