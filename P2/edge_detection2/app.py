from flask import Flask, render_template, request, redirect, url_for, session
import os
from edge_detection import save_edges

app = Flask(__name__)
app.secret_key = 'random_secret_key'  # Diperlukan untuk session

UPLOAD_FOLDER = os.path.join('static', 'upload')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded_files = request.files.getlist('files')
        uploaded_filenames = []

        for file in uploaded_files:
            if file and file.filename != '':
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)
                save_edges(file.filename, app.config['UPLOAD_FOLDER'])
                uploaded_filenames.append(file.filename)

        session['last_uploaded'] = uploaded_filenames
        return redirect(url_for('result'))

    return render_template('index.html')

@app.route('/result')
def result():
    grouped_by_method = {
        'canny': [],
        'sobel': [],
        'laplacian': []
    }

    last_uploaded = session.get('last_uploaded', [])

    for filename in last_uploaded:
        name, _ = os.path.splitext(filename)
        for method in grouped_by_method:
            method_filename = f"{name}_{method}.jpg"
            if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], method_filename)):
                grouped_by_method[method].append(method_filename)

    return render_template('result.html', grouped_by_method=grouped_by_method)

if __name__ == "__main__":
    app.run(debug=True, port=5070)
