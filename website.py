from flask import Flask, render_template, request
import requests
import json
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    file.save("image.png")
    return 'file uploaded'

@app.route('/generate', methods=['POST'])
def generate():
    text = request.form['text']
    font = ImageFont.truetype("arial.ttf", 144)
    width, height = font.getsize(text)
    img = Image.new('RGB', (width, height), color = (0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((0,0), text, fill=(255,255,255), font=font)
    img = img.rotate(-90, expand=True)
    img.save("image.png")
    return 'image generated'
    

app.run(debug=True)