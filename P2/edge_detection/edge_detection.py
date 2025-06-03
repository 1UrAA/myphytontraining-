import cv2  # Library OpenCV untuk pemrosesan gambar
import os   # Library OS, bisa digunakan untuk manajemen file/direktori

def detect_edges(image_path, output_path):
    """
    Fungsi untuk mendeteksi tepi pada sebuah gambar dan menyimpannya ke file output.
    
    Parameters:
    - image_path: path ke file gambar input
    - output_path: path untuk menyimpan hasil gambar deteksi tepi
    
    Returns:
    - output_path: path dari file hasil deteksi tepi
    """

    # Membaca gambar dari path yang diberikan
    img = cv2.imread(image_path)

    # Mengonversi gambar ke grayscale agar lebih mudah diproses
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Mengaburkan gambar menggunakan Gaussian Blur untuk mengurangi noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Mendeteksi tepi menggunakan algoritma Canny
    edges = cv2.Canny(blurred, threshold1=50, threshold2=150)

    # Menyimpan gambar hasil deteksi tepi ke path output
    cv2.imwrite(output_path, edges)

    # Mengembalikan path output sebagai hasil fungsi
    return output_path
