from flask import Flask, render_template, request
import requests
import json
from PIL import Image, ImageDraw, ImageFont
import time
import websocket
import urllib.request
import uuid
import random
import pyduinocli

filename = "image.png"
resize_width = int(144/4)

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
  file = request.files['file']
  file.save(filename)
  img = resize_image(filename, resize_width)
  generate_code(img)
  return render_template('index.html', img="static/" + filename.replace(".png", "_small.png?t=" + str(time.time())))

@app.route('/generate', methods=['POST'])
def generate():
  text = request.form['text']
  font = ImageFont.truetype("arial.ttf", 144)
  width, height = font.getsize(text)
  img = Image.new('RGB', (width, height), color = (0, 0, 0))
  d = ImageDraw.Draw(img)
  d.text((0,0), text, fill=(255,255,255), font=font)
  img = img.rotate(-90, expand=True)
  img.save(filename)
  img = resize_image(filename, resize_width)
  generate_code(img)
  return render_template('index.html', img="static/" + filename.replace(".png", "_small.png?t=" + str(time.time())))

@app.route('/generatesd', methods=['POST'])
def generatesd():
  postext = request.form['text']

  workflow = open("comfyuiapi.json").read()
  prompt_to_image(workflow, postext, "", True)
  img = resize_image(filename, resize_width)
  generate_code(img)
  return render_template('index.html', img="static/" + filename.replace(".png", "_small.png?t=" + str(time.time())))

@app.route('/uploadarduino', methods=['POST'])
def uploadarduino():
  upload_arduino()
  return render_template('index.html')

def resize_image(filename, new_width):
  img = Image.open(filename)
  width, height = img.size
  new_height = int(new_width * height / width)
  new_height = min(new_height, 200)
  img = img.resize((new_width, new_height))
  img.save(filename.replace(".png", "_small.png"))
  img.save("static/" + filename.replace(".png", "_small.png"))
  return img

def generate_code(img):
  with open("aparams.ino", "w") as f:
    f.write("const int height = " + str(img.height) + ";\n")
    for y in range(0, img.height):
      print("Row", y)
      # const char string_0[] PROGMEM = "String 0";
      f.write("const char color_" + str(y) + "[] PROGMEM = {")
      for x in range(0, img.width):
        r, g, b = 0, 0, 0
        try:
            r, g, b = img.getpixel((x, y))
        except:
            r, g, b, _ = img.getpixel((x, y))
        r = r // 43
        g = g // 43
        b = b // 43
        f.write(str(r*36 + g*6 + b + 1) + ", ")
      f.write("0};\n")

      # const char * const string_table[] PROGMEM = {string_0, string_1, string_2};
    f.write("const char * const color_table[] PROGMEM = {")
    for y in range(0, img.height):
      f.write("color_" + str(y) + ", ")

    f.write("};\n")
    

def open_websocket_connection():
  server_address='127.0.0.1:8188'
  client_id=str(uuid.uuid4())
  ws = websocket.WebSocket()
  ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
  return ws, server_address, client_id

def queue_prompt(prompt, client_id, server_address):
  p = {"prompt": prompt, "client_id": client_id}
  headers = {'Content-Type': 'application/json'}
  data = json.dumps(p).encode('utf-8')
  req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data, headers=headers)
  return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type, server_address):
  data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
  url_values = urllib.parse.urlencode(data)
  with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
      return response.read()

def load_workflow(workflow_path):
  try:
      with open(workflow_path, 'r') as file:
          workflow = json.load(file)
          return json.dumps(workflow)
  except FileNotFoundError:
      print(f"The file {workflow_path} was not found.")
      return None
  except json.JSONDecodeError:
      print(f"The file {workflow_path} contains invalid JSON.")
      return None
  
def prompt_to_image(workflow, positve_prompt, negative_prompt='', save_previews=False):
  prompt = json.loads(workflow)
  prompt.get("13")['inputs']['noise_seed'] = random.randint(10**14, 10**15 - 1)
  prompt.get("6")['inputs']['text'] = positve_prompt

  if negative_prompt != '':
    prompt.get("7")['inputs']['text'] = negative_prompt

  generate_image_by_prompt(prompt, save_previews)

def generate_image_by_prompt(prompt, save_previews=False):
  try:
    ws, server_address, client_id = open_websocket_connection()
    prompt_id = queue_prompt(prompt, client_id, server_address)['prompt_id']
    track_progress(prompt, ws, prompt_id)
    images = get_images(prompt_id, server_address, save_previews)
    for image in images:
      with open(filename, 'wb') as file:
        file.write(image['image_data'])
  finally:
    ws.close()

def track_progress(prompt, ws, prompt_id):
  node_ids = list(prompt.keys())
  finished_nodes = []

  while True:
      out = ws.recv()
      if isinstance(out, str):
          message = json.loads(out)
          if message['type'] == 'progress':
              data = message['data']
              current_step = data['value']
              print('In K-Sampler -> Step: ', current_step, ' of: ', data['max'])
          if message['type'] == 'execution_cached':
              data = message['data']
              for itm in data['nodes']:
                  if itm not in finished_nodes:
                      finished_nodes.append(itm)
                      print('Progess: ', len(finished_nodes), '/', len(node_ids), ' Tasks done')
          if message['type'] == 'executing':
              data = message['data']
              if data['node'] not in finished_nodes:
                  finished_nodes.append(data['node'])
                  print('Progess: ', len(finished_nodes), '/', len(node_ids), ' Tasks done')

              if data['node'] is None and data['prompt_id'] == prompt_id:
                  break #Execution is done
      else:
          continue
  return

def get_history(prompt_id, server_address):
  with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
      return json.loads(response.read())
  
def get_images(prompt_id, server_address, allow_preview = False):
  output_images = []

  history = get_history(prompt_id, server_address)[prompt_id]
  for node_id in history['outputs']:
      node_output = history['outputs'][node_id]
      output_data = {}
      if 'images' in node_output:
          for image in node_output['images']:
              if allow_preview and image['type'] == 'temp':
                  preview_data = get_image(image['filename'], image['subfolder'], image['type'], server_address)
                  output_data['image_data'] = preview_data
              if image['type'] == 'output':
                  image_data = get_image(image['filename'], image['subfolder'], image['type'], server_address)
                  output_data['image_data'] = image_data
      output_data['file_name'] = image['filename']
      output_data['type'] = image['type']
      output_images.append(output_data)
  return output_images
   
def upload_arduino():
  arduino = pyduinocli.Arduino("./arduino-cli")
  brds = arduino.board.list()

  if len(brds['result']) == 0:
    print("No boards found")
    return
  
  print(brds['result'])

  port = brds['result'][0]['port']['address']
  fqbn = "arduino:avr:nano:cpu=atmega328old"

  arduino.compile(fqbn=fqbn, sketch="../Base")
  arduino.upload(fqbn=fqbn, sketch="../Base", port=port)

app.run(debug=True)