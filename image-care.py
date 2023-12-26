from flask import Flask, request, send_file
from rembg import remove
from PIL import Image
import uuid
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def crop_to_nontransparent(image):
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    bbox = image.getbbox()
    if bbox is not None:
        return image.crop(bbox)
    else:
        return None

@app.route('/process-image', methods=['POST'])
def process_image():
    # check if header auth is set
    if 'Authorization' not in request.headers:
        return "No authorization header", 401
    
    if 'image' not in request.files:
        return "No image file in request", 400

    file = request.files['image']
    if file.filename == '':
        return "No selected file", 400

    try:
        input_image = Image.open(file.stream)
        output_image = remove(input_image)
        final_image = crop_to_nontransparent(output_image)

        if final_image:
            ud = str(uuid.uuid4())
            final_path = '/var/www/html/images/' + ud + '.png'
            final_image.save(final_path)
            return ud, 200
        else:
            return "Image processing failed", 500

    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    # enable cors
    app.config['CORS_HEADERS'] = 'Content-Type'
    app.run(debug=True, port=5000)
    print("Server started")
