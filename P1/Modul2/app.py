# Import library yang dibutuhkan
from flask import Flask, render_template, request, redirect, url_for, session
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import os
import cv2

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Konfigurasi folder untuk menyimpan file yang di-upload
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

# Kunci rahasia untuk menyimpan data di session
app.secret_key = 'secretkey'

# Halaman utama (form upload)
@app.route('/')
def index():
    return render_template('index.html')  # Menampilkan halaman upload

# Proses upload file
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(url_for('index'))  # Jika tidak ada file, kembali ke halaman awal

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))  # Jika nama file kosong, kembali ke halaman awal

    if file:
        # Simpan file ke folder upload
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Simpan nama file ke dalam session
        session['original_filename'] = file.filename
        return redirect(url_for('edit_page'))  # Arahkan ke halaman edit

# Halaman untuk memilih filter dan mode warna
@app.route('/edit', methods=['GET', 'POST'])
def edit_page():
    filename = session.get('original_filename')  # Ambil nama file asli dari session
    processed_filename = session.get('processed_filename')  # Ambil file hasil jika sudah ada

    if request.method == 'POST':
        # Ambil filter yang dipilih dan mode warna
        selected_filters = request.form.getlist('filters')
        color_mode = request.form.get('color_mode', 'original')

        # Buka gambar yang diupload
        img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Proses peningkatan kualitas gambar sesuai filter dan warna yang dipilih
        img = improve_image_quality(img, selected_filters, color_mode)

        # Simpan hasil ke file baru
        processed_filename = 'processed_' + filename
        processed_filepath = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
        img.save(processed_filepath)

        # Simpan nama file hasil ke session
        session['processed_filename'] = processed_filename
        return redirect(url_for('result_page'))  # Arahkan ke halaman hasil

    # Jika metode GET, tampilkan halaman edit
    return render_template('edit.html', original_filename=filename, processed_filename=processed_filename)

# Halaman untuk menampilkan hasil gambar yang telah diproses
@app.route('/result')
def result_page():
    original_filename = session.get('original_filename')
    processed_filename = session.get('processed_filename')
    return render_template('result.html', original_filename=original_filename, processed_filename=processed_filename)

# Fungsi utama untuk memproses gambar berdasarkan filter dan mode warna
def improve_image_quality(img, filters, color_mode):
    # Ubah mode warna gambar sesuai pilihan
    if color_mode == 'grayscale':
        img = img.convert('L')  # Hitam putih (grayscale)
    elif color_mode == 'blackwhite':
        # Threshold ke hitam/putih (binary)
        img = img.convert('L').point(lambda x: 0 if x < 128 else 255, '1').convert('L')
    elif color_mode == 'sepia':
        # Efek sepia menggunakan matrix transformasi
        img = img.convert('RGB')
        sepia_img = np.array(img).astype(np.float32)
        sepia_matrix = np.array([[0.393, 0.769, 0.189],
                                 [0.349, 0.686, 0.168],
                                 [0.272, 0.534, 0.131]])
        sepia_img = sepia_img @ sepia_matrix.T
        sepia_img = np.clip(sepia_img, 0, 255).astype(np.uint8)
        img = Image.fromarray(sepia_img)
    elif color_mode == 'invert':
        # Membalik warna (negatif)
        img = Image.fromarray(255 - np.array(img.convert('RGB')))

    # Terapkan filter sesuai pilihan user
    if 'contrast' in filters:
        img = ImageEnhance.Contrast(img).enhance(1.5)  # Tingkatkan kontras
    if 'brightness' in filters:
        img = ImageEnhance.Brightness(img).enhance(1.2)  # Tingkatkan kecerahan

    if 'blur' in filters:
        # Gunakan OpenCV untuk efek blur
        img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        img = cv2.GaussianBlur(img, (5, 5), 0)
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    if 'sharpen' in filters:
        img = img.filter(ImageFilter.SHARPEN)  # Menajamkan gambar
    if 'detail' in filters:
        img = img.filter(ImageFilter.DETAIL)  # Tambahkan detail
    if 'edge' in filters:
        img = img.filter(ImageFilter.EDGE_ENHANCE)  # Tingkatkan tepi gambar
    if 'emboss' in filters:
        img = img.filter(ImageFilter.EMBOSS)  # Tambahkan efek timbul

    return img  # Kembalikan gambar hasil edit

# Menjalankan aplikasi di localhost:5070 dalam mode debug
if __name__ == '__main__':
    app.run(debug=True, port=5030)
