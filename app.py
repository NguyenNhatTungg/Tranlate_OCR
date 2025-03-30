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


def getResponseTranslateManga(path, filename):
  imgPIL = Image.open(path)

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
  filePath = path_result + filename + '_images_translated_.png'
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

def delete_files_in_directory(directory_path):
    try:
        files = os.listdir(directory_path)
        for file in files:
            file_path = os.path.join(directory_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print("All files deleted successfully.")
    except:
        print("Error occurred while deleting files.")


@app.route('/upload', methods=['POST', 'GET'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    delete_files_in_directory('D:\\Learn\\FLASK_API\\uploads')

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        print(filename);
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(file_path)
        file.save(file_path)

        file_path = os.path.join("D:\\Learn\\FLASK_API\\uploads", filename)
        filePath = getResponseTranslateManga('D:\\Learn\\FLASK_API\\uploads\\' + filename, filename)

        # for f in files:
        #     os.remove(f)
        os.remove("./context.jpg")
        return jsonify({'message': 'File successfully uploaded', 'filename': filePath}), 200
    else:
        return jsonify({'error': 'Invalid file type'}), 400


@app.route('/zip', methods=['POST', 'GET'])
def zip_file():
    shutil.make_archive('D:\\Learn\\FLASK_API\\result', 'zip', path_result)
    return jsonify({'message': 'zip successfully'}), 200

@app.route('/clean', methods=['POST', 'GET'])
def clean():
    delete_files_in_directory('D:\\Learn\\FLASK_API\\img_result')
    return jsonify({'message': 'clean successfully'}), 200


if __name__ == '__main__':
    app.run(debug=True)
    