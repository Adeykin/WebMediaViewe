import flask
from flask import Flask
from flask import render_template
from flask import request
from flask import send_from_directory
import urllib.parse
import os, sys
import pandas as pd
import cv2
import json

app = Flask(__name__)

imagesPerPage = 10

@app.route("/main/<int:pagesNum>/<int:page>/<path:folderPath>")
def mainPage(pagesNum, page, folderPath):
    if os.path.isfile('/' + folderPath):
        if os.path.basename(folderPath) == 'anno.txt':
            data = pd.read_csv('/' + folderPath, sep=',', header=None).values
            data = data[(data == data).all(axis=1), :]

            data = data[page * pagesNum:(page + 1) * pagesNum, :]
            bbox = ['_'.join(map(str, row)) for row in  data[:, :4]]
            print(bbox)
            labels = data[:, 4] # 'UP'/'DOWN'
            images = data[:, 5].astype(str)

        elif os.path.basename(folderPath) == 'annotation.json':
            print('json')
            obj = json.load(open('/' + folderPath, 'r'))
            images = obj['img_names'][page * pagesNum:(page + 1) * pagesNum]
            bbox = obj['boxes'][page * pagesNum:(page + 1) * pagesNum]
            bbox = ['_'.join(map(str, row)) for row in bbox]
            labels = obj['targets'][page * pagesNum:(page + 1) * pagesNum]
            print(bbox)

        folderPath = os.path.dirname(folderPath)

    else:
        labels = ['NONE', ] * pagesNum
        bbox   = ['NONE', ] * pagesNum
        images = os.listdir('/' + folderPath)[page * pagesNum:(page + 1) * pagesNum]

    pathes = ['/' + folderPath + '/' + image for image in images]
    pairs = zip(pathes, labels, bbox)
    return render_template('index.html', images=pairs, page=page, pagesNum=pagesNum, folderPath=folderPath)


@app.route('/images/<path:filename>/<bbox>/<label>')
def downloadFile(filename, bbox=None, label=None):
    print(filename)
    print(bbox)
    img = cv2.imread('/' + filename)
    if bbox is not None and bbox != 'NONE':
        bbox = list(map(int, bbox.split('_')))
        color = (255,255,255)
        print(label)
        if label is not None and label != 'NONE':
            if label == 'DOWN' or label == '0':
                color = (0,255,0)
            elif label == 'UP' or label == '1':
                color = (0,0,255)
            else:
                color = (255,0,0)
        cv2.rectangle(img, (bbox[0],bbox[1]), (bbox[2],bbox[3]), color=color,thickness=2)
    retval, buffer = cv2.imencode('.png', img)
    response = flask.make_response(buffer.tobytes())
    response.headers['Content-Type'] = 'image/png'
    return response
    #return send_from_directory('/', filename, as_attachment=True)


@app.route("/")
def hello_world():
    return "<url>/main/<pagesNum>/<page>/<path>"
    
    
if __name__ == '__main__':
    port = 5000 if len(sys.argv) == 1 else int(sys.argv[1])
    app.run(debug=True, host='0.0.0.0', port=port)
