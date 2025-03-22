import os
import requests
import json
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MRISA_API_URL'] = 'http://localhost:5000/search'  # MRISA runs on this endpoint

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    # Check if the request has a URL
    if 'image_url' in request.form and request.form['image_url']:
        image_url = request.form['image_url']
    # Check if the request has a file
    elif 'image' in request.files:
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            # Convert local path to a URL that MRISA can access
            image_url = request.host_url + filepath
        else:
            return jsonify({"error": "Invalid file format"}), 400
    else:
        return jsonify({"error": "No image provided"}), 400

    # Prepare the payload for MRISA
    payload = {
        "image_url": image_url
    }
    
    try:
        # Send the request to the MRISA API
        response = requests.post(
            app.config['MRISA_API_URL'],
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )
        
        # Get the response and return the results
        if response.status_code == 200:
            results = response.json()
            return jsonify(results)
        else:
            return jsonify({"error": f"MRISA API error: {response.text}"}), response.status_code
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the Flask app on a different port than MRISA
    app.run(debug=True, port=8080)