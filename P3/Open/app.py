import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from skimage.io import imread

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # Max 5MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Fungsi membuat dan menyimpan histogram
def save_histogram(image_array, filename):
    plt.figure()
    plt.hist(image_array.ravel(), bins=256, color='gray', alpha=0.7)
    plt.title('Histogram')
    plt.xlabel('Pixel Value')
    plt.ylabel('Frequency')
    hist_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    plt.savefig(hist_path)
    plt.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return "Tidak ada file diunggah", 400
    file = request.files['image']
    if file.filename == '':
        return "Tidak ada file yang dipilih", 400
    if not allowed_file(file.filename):
        return "Format file tidak diizinkan", 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        image = imread(filepath)
    except Exception as e:
        return f"Gagal membaca file gambar: {e}", 400

    # Proses masking warna biru
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    blue1 = np.array([110, 50, 50])
    blue2 = np.array([130, 255, 255])
    mask = cv2.inRange(hsv, blue1, blue2)

    kernel = np.ones((5, 5), np.uint8)
    opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # Simpan citra hasil
    mask_path = os.path.join(app.config['UPLOAD_FOLDER'], 'mask_' + filename)
    opening_path = os.path.join(app.config['UPLOAD_FOLDER'], 'opening_' + filename)
    cv2.imwrite(mask_path, mask)
    cv2.imwrite(opening_path, opening)

    # Simpan histogram
    save_histogram(image, 'hist_' + filename)
    save_histogram(mask, 'hist_mask_' + filename)
    save_histogram(opening, 'hist_opening_' + filename)

    return render_template('result.html',
                           original=filename,
                           mask='mask_' + filename,
                           opening='opening_' + filename,
                           hist_original='hist_' + filename,
                           hist_mask='hist_mask_' + filename,
                           hist_opening='hist_opening_' + filename)

@app.errorhandler(413)
def too_large(e):
    return "File terlalu besar. Maksimal 5MB.", 413

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

