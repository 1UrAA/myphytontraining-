from flask import Flask, render_template, request, redirect, url_for
import os
from edge_detection import detect_edges

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            output_path = os.path.join(UPLOAD_FOLDER, 'edges_' + file.filename)
            detect_edges(filepath, output_path)

            return render_template('index.html', original=file.filename, processed='edges_' + file.filename)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(port=5080)
