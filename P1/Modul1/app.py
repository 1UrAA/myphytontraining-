from flask import Flask, render_template, request, redirect, url_for
from PIL import Image
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Buat folder upload jika belum ada
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Cek ekstensi file
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Simpan gambar asli untuk ditampilkan
        original_filename = filename
        original_filepath = filepath

        # Buka gambar
        img = Image.open(filepath)

        # Proses Resize (jika ada)
        resize = request.form.get('resize')
        if resize:
            try:
                width, height = map(int, resize.split(','))
                img = img.resize((width, height))
            except ValueError:
                pass  # Jika input resize tidak valid, abaikan

        # Proses Rotate (jika ada)
        rotate = request.form.get('rotate')
        if rotate:
            try:
                img = img.rotate(int(rotate))
            except ValueError:
                pass  # Abaikan jika input rotate tidak valid

        # Proses Crop (jika ada)
        crop = request.form.get('crop')
        if crop:
            try:
                width, height = map(int, crop.split(','))
                img = img.crop((0, 0, width, height))  # Crop dari kiri atas
            except ValueError:
                pass  # Abaikan jika input crop tidak valid

        # Proses Grayscale (jika dipilih)
        if 'grayscale' in request.form:
            img = img.convert('L')

        # Simpan gambar hasil manipulasi dengan nama baru
        processed_filename = 'processed_' + filename
        processed_filepath = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
        img.save(processed_filepath)

        return render_template('index.html', original_filename=original_filename, processed_filename=processed_filename)

    return redirect(url_for('index'))

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

