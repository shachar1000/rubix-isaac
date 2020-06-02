from flask import Flask, send_file, render_template, request, jsonify, make_response, Response, url_for, session
import cv2
import base64
import numpy as np
import io
from PIL import Image
from reddit import detect
import json
#from flask_scss import Scss
from sassutils.wsgi import SassMiddleware
import secrets
from flask_sqlalchemy import SQLAlchemy
import string
import random

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
#Scss(app, static_dir='static', asset_dir='assets')
app.config["SECRET_KEY"] = secrets.token_urlsafe(16)

app.wsgi_app = SassMiddleware(app.wsgi_app, {
    'app': ('static/sass', 'static/css', '/static/css')
})

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///color'

db = SQLAlchemy(app)


class rubixColors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(4), unique=True) # so we don't accidently get 2 identical codes
    colors = db.Column(db.String(800))
    
    def __repr__(self):
        return '<rubixColors {}>'.format(self.code)
    


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        if request.files:
            files = request.files.getlist('files[]')
            if 'colors' in session:
                session.pop('colors')

            for file in files:
                # imgString = base64.b64decode(file)
                # npArray = np.fromstring(imgString, np.uint8)
                # image = cv2.imdecode(npArray, cv2.IMREAD_ANYCOLOR)
                # cv2.imshow("frame", image)
                # cv2.waitKey()
                pil_image = Image.open(io.BytesIO(file.read())) # basically bytes
                open_cv_image_raw = np.array(pil_image.convert('RGB')) 
                # BGR is RGB[::-1]
                open_cv_image_raw = open_cv_image_raw[:, :, ::-1].copy()
                # I can also try to do cvtColor with RGB2BGR (slower?)
                # cv2.imshow("frame", open_cv_image)
                # cv2.waitKey(0)
                
                cv2.imwrite('01.jpeg',open_cv_image_raw)
                
                response = detect(open_cv_image_raw)
                
                open_cv_image = response["image"]
                
                imencoded = cv2.imencode(".jpg", open_cv_image)[1]

                jpg_as_text_detected = base64.b64encode(imencoded)
                
                #now we have to convert opencv to jpg base 64 for the raw image as well
                
                imencoded = cv2.imencode(".jpg", open_cv_image_raw)[1]
                
                jpg_as_text_raw = base64.b64encode(imencoded)
                
                #"imageRaw": jpg_as_text_raw.decode('utf-8')
                return Response(json.dumps({"imageDetected": jpg_as_text_detected.decode('utf-8'), "colors_matrix": response["colors_matrix"]}))
    return "ok"
        
@app.route("/change", methods=['POST', 'GET'])
def change():
    # imgb64fromHTML = request.json["image"]
    # new = cv2.imdecode(np.fromstring(base64.b64decode(imgb64fromHTML), dtype=np.uint8), cv2.IMREAD_COLOR)
    new = cv2.imread('01.jpeg')
    
    if 'colors' in session:
        session["colors"][request.json["colorName"]] = request.json["value"]
    else:
        session["colors"] = {request.json["colorName"] : request.json["value"]}
    app.logger.info(session.get("colors"))
    response = detect(new, session.get("colors"))
    
    finalFixed = response["image"]
    
    imencode = cv2.imencode('.jpg', finalFixed)[1]
    jpg_as_text_final = base64.b64encode(imencode)
    
    #cv2.imshow("frame", finalFixed)
    #cv2.waitKey(0)
    return Response(json.dumps({"image": jpg_as_text_final.decode('utf-8'), "colors_matrix": response["colors_matrix"]}))
                    
                    
@app.route("/getCode", methods=['POST', 'GET'])                    
def getCode():
    if request.method == 'POST':
        listOfMatrices = request.get_json()['storeColors']
        matrixString = ''.join([''.join(''.join(x[0] for x in y) for y in matrix) for matrix in listOfMatrices]) #only first letter
        passCode = ''.join(random.choice(string.ascii_lowercase) for _ in range(4))
        row = rubixColors(code=passCode, colors=matrixString)
        db.session.add(row)
        db.session.commit()
        app.logger.info(matrixString)
        return Response(json.dumps({"code": passCode}))
        
@app.route("/useCode", methods=['POST', 'GET'])
def useCode():
    app.logger.info(request.get_json())
    stringColor = rubixColors.query.filter_by(code=request.get_json()['code']).first().colors
    app.logger.info(stringColor)
    return Response(json.dumps({"stringColor": stringColor}))
    
@app.route("/getExe")
def getExe():
    return send_file('rubix.exe',
                     mimetype='application/exe',
                     attachment_filename='rubix.exe',
                     as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
