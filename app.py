from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from manga_ocr import MangaOcr
from inference_sdk import InferenceHTTPClient
from deep_translator import (GoogleTranslator, LingueeTranslator)
import requests
from PIL import Image, ImageDraw, ImageFont
from manga_ocr import MangaOcr
import textwrap
from deep_translator import GoogleTranslator
import glob
import shutil
from flask_cors import CORS
import random


CLIENT = InferenceHTTPClient(
    api_url="https://outline.roboflow.com",
    api_key="dKCE2LogwKR8xnrIR2S1"
)

mocr = MangaOcr()
print(mocr)
translator = GoogleTranslator(source='ja', target='vi')

import easyocr
reader = easyocr.Reader(['ch_tra', 'en'])

translator = GoogleTranslator(source='ja', target='vi')

path_result = 'D:\Learn\FLASK_API\img_result\\'
font_size = 16


def getResponseTranslateManga(path, index):
  print('start '+ index)
  imgPIL = Image.open(path)
  print('start--'+ index)

  results = CLIENT.infer(path, model_id="manga-text-detection-xyvbw/2")
  for res_idx, res in enumerate(results['predictions']):
    # if 'clean_text' == res['class'] or 'clean_text' == res['messy_text']: continue
    print('res_idx '+ str(res_idx))
    width = res['width']
    height = res['height']
    x = res['x'] - width / 2
    y = res['y'] - height / 2
    image_crop = imgPIL.crop((x, y, x + width, y + height ))
    image_crop = image_crop.convert('RGB')
    image_crop.save('context.jpg')

    text = mocr(image_crop)
    textTranslate = translator.translate(text)
    print('textTranslate '+ textTranslate)
    draw = ImageDraw.Draw(imgPIL)
    draw.rectangle(((x, y), (x + width, y + height)), fill="white")
    font = ImageFont.truetype("D:\Learn\FLASK_API\Roboto-Italic-VariableFont_wdth,wght.ttf", font_size)
    offset = y
    print('draw text ')
    for line in textwrap.wrap(textTranslate, width=int(width / 5)):
        draw.text((x - 10, offset - 10), line, fill="black", font = font)
        offset += font_size
  filePath = path_result + str(random.randint(10, 100)) + '_images_translated_.png'
  imgPIL.save(filePath)

  return filePath

def concatImages():
  imageConcats = [Image.open(x) for x in sorted(glob.glob(path_result + '*'))]
  widths, heights = zip(*(i.size for i in imageConcats))
  width = max(widths)
  height = sum(heights)

  new_im = Image.new('RGB', (width, height))

  x_offset = 0
  for im in imageConcats:
    new_im.paste(im, (0, x_offset))
    print(im.size)
    x_offset += im.size[1]

  new_im.save('test.jpg')


app = Flask(__name__)
CORS(app)

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST', 'GET'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'contexts.jpg')
        print(file_path)
        file.save(file_path)

        filess = sorted(glob.glob("D:\\Learn\\FLASK_API\\uploads\\*"))
        for index, filee in enumerate(filess):
            filePath = getResponseTranslateManga(filee, str(index))

        files = glob.glob('D:\\Learn\\FLASK_API\\uploads\\*')
        # for f in files:
        #     os.remove(f)
        os.remove("./context.jpg")
        return jsonify({'message': 'File successfully uploaded', 'filename': filePath}), 200
    else:
        return jsonify({'error': 'Invalid file type'}), 400
    

if __name__ == '__main__':
    app.run(debug=True)
    