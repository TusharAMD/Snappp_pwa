from flask import Flask, jsonify, render_template,request
import cv2
from rembg.bg import remove
import numpy as np
import io
from PIL import Image,ImageFile
import base64
import requests
import pymongo

app = Flask(__name__)

# Renders index.html which contains simple form asking for email id and image
@app.route('/')
def home():
    return render_template('index.html')
# On clicking submit get the file input from the form and update in database
@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        email = request.form["email"]
        f = request.files['file']
        f.save(f.filename)
        
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        input_path = f.filename
        output_path = 'out.png'

        f = np.fromfile(input_path)
        result = remove(f)
        img = Image.open(io.BytesIO(result)).convert("RGBA")
        img.save(output_path)
        
        with open(f"{output_path}", "rb") as file:
            url = "https://api.imgbb.com/1/upload"
            payload = {
                "key": "c4b63af118f97f88cdeea980cdb4d6c9",
                "image": base64.b64encode(file.read()),
            }
            res = requests.post(url, payload)
            print(res.json()["data"]["url"])
            image=res.json()["data"]["url"]
        
        curr_data = {"email":email,"image":image}
        
        client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.wonbr.mongodb.net/myFirstDatabase?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE")
        db = client['Snappp']
        collection = db["pwa"]
        x = collection.find_one({"email":email})
        if x:
            myquery = { "email":email }
            newvalues = { "$set": curr_data} 
            collection.update_one(myquery, newvalues)
        else:
            collection.insert_one(curr_data)
        
        
        
    return "<h1>Done</h1>"


@app.route('/offline.html')
def offline():
    return app.send_static_file('offline.html')


@app.route('/service-worker.js')
def sw():
    return app.send_static_file('service-worker.js')


if __name__ == '__main__':
    app.run(debug=True, port=8082, host="0.0.0.0")
