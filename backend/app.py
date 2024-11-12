from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def calculate_suggested_bid(row):
    # Implement your bid optimization logic here
    # This is a simple example - you should replace with your actual algorithm
    if row['acos'] > 30:
        return row['current_bid'] * 0.9
    elif row['acos'] < 15:
        return row['current_bid'] * 1.1
    return row['current_bid']

@app.route('/api/process-ppc', methods=['POST'])
def process_ppc():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Read Excel file
            df = pd.read_excel(filepath)
            
            # Process data and calculate suggested bids
            df['suggested_bid'] = df.apply(calculate_suggested_bid, axis=1)
            
            # Convert to JSON
            result = df.to_dict('records')
            
            # Clean up
            os.remove(filepath)
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)