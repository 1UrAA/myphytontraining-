import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # Max 5MB

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('image')
    if not file or file.filename == '':
        return "Tidak ada file diunggah.", 400
    if not allowed_file(file.filename):
        return "Format file tidak didukung.", 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Proses gambar
    img = cv2.imread(filepath, 0)
    if img is None:
        return "Gagal membaca gambar.", 400

    kernel = np.ones((5, 5), np.uint8)
    erosion = cv2.erode(img, kernel, iterations=1)
    dilation = cv2.dilate(img, kernel, iterations=1)

    # Simpan citra hasil
    erosi_path = os.path.join(app.config['UPLOAD_FOLDER'], 'erosi_' + filename)
    dilasi_path = os.path.join(app.config['UPLOAD_FOLDER'], 'dilasi_' + filename)
    cv2.imwrite(erosi_path, erosion)
    cv2.imwrite(dilasi_path, dilation)

    # Simpan histogram ke gambar
    def save_histogram(image, path):
        plt.figure()
        plt.hist(image.ravel(), bins=256)
        plt.title('Histogram')
        plt.savefig(path)
        plt.close()

    hist_original = os.path.join(app.config['UPLOAD_FOLDER'], 'hist_asli_' + filename)
    hist_erosi = os.path.join(app.config['UPLOAD_FOLDER'], 'hist_erosi_' + filename)
    hist_dilasi = os.path.join(app.config['UPLOAD_FOLDER'], 'hist_dilasi_' + filename)
    save_histogram(img, hist_original)
    save_histogram(erosion, hist_erosi)
    save_histogram(dilation, hist_dilasi)

    return render_template('result.html',
        original=filename,
        erosi='erosi_' + filename,
        dilasi='dilasi_' + filename,
        hist_asli='hist_asli_' + filename,
        hist_erosi='hist_erosi_' + filename,
        hist_dilasi='hist_dilasi_' + filename
    )

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

