from flask import Flask
from flask import render_template
from flask import request
from flask import send_from_directory
import urllib.parse
import os, sys
import pandas as pd

app = Flask(__name__)

imagesPerPage = 10

@app.route("/main/<int:pagesNum>/<int:page>/<path:folderPath>")
def mainPage(pagesNum, page, folderPath):
    if os.path.exists('/' + folderPath + '/anno.txt'):
        data = pd.read_csv('/' + folderPath + '/anno.txt', sep=',', header=None).values
        data = data[(data == data).all(axis=1), :]

        data = data[page * pagesNum:(page + 1) * pagesNum, :]
        labels = data[:, 4]
        images = data[:, 5].astype(str)
    else:
        labels = ['NONE', ] * pagesNum
        images = os.listdir('/' + folderPath)[page * pagesNum:(page + 1) * pagesNum]

    pathes = ['/' + folderPath + '/' + image for image in images]
    pairs = zip(pathes, labels)
    return render_template('index.html', images=pairs, page=page, pagesNum=pagesNum, folderPath=folderPath)


@app.route('/images/<path:filename>')
def downloadFile(filename):
    return send_from_directory('/', filename, as_attachment=True)


@app.route("/")
def hello_world():
    return "<url>/main/<pagesNum>/<page>/<path>"
    
    
if __name__ == '__main__':
    port = 5000 if len(sys.argv) == 1 else int(sys.argv[1])
    app.run(debug=True, host='0.0.0.0', port=port)
