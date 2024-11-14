from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def calculate_new_max_bid(row):
    try:
        cpc = row.get('CPC(USD)', 0)
        acos = row.get('ACOS', 0)
        target_acos = row.get('Target ACOS', 30)  # Default target ACOS is 30%
        
        # Replace '-' with a default value (assuming zero)
        if acos == '-' or pd.isna(acos):
            acos = 0
        if cpc == '-' or pd.isna(cpc):
            cpc = 0
        if target_acos == '-' or pd.isna(target_acos):
            target_acos = 30

        cpc = float(str(cpc).replace('$', '').strip())
        acos = float(str(acos).replace('%', '').strip())
        target_acos = float(str(target_acos).replace('%', '').strip())
        
        # Calculate new max bid similar to the desktop app logic
        if acos < (0.84 * target_acos):
            new_max_bid = cpc * 1.2
        else:
            new_max_bid = (cpc / acos) * target_acos if acos != 0 else 0
        
        return round(new_max_bid, 2)
    except Exception as e:
        return 0  # Return 0 in case of any error during calculation

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
            # Read the file (supports Excel and CSV)
            if filename.endswith(('xlsx', 'xls')):
                df = pd.read_excel(filepath, usecols=['Keyword', 'Match Type', 'State', 'Keyword bid(USD)', 'CPC(USD)', 'ACOS'])
            elif filename.endswith('csv'):
                df = pd.read_csv(filepath, usecols=['Keyword', 'Match Type', 'State', 'Keyword bid(USD)', 'CPC(USD)', 'ACOS'])
            else:
                raise ValueError("Unsupported file format")
            
            # Rename 'Keyword' to 'Keyword/Automatic targeting groups' for consistency
            df.rename(columns={'Keyword': 'Keyword/Automatic targeting groups'}, inplace=True)
            
            # Add Target ACOS column with a default value
            df['Target ACOS'] = 30  # Default target ACOS is 30%
            
            # Process data and calculate new max bids
            df['New Max Bid'] = df.apply(calculate_new_max_bid, axis=1)
            
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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error='No file part')
        
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error='No selected file')
        
        target_acos = request.form.get('target_acos', 30)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                # Read the file (supports Excel and CSV)
                if filename.endswith(('xlsx', 'xls')):
                    df = pd.read_excel(filepath, usecols=['Keyword', 'Match Type', 'State', 'Keyword bid(USD)', 'CPC(USD)', 'ACOS'])
                elif filename.endswith('csv'):
                    df = pd.read_csv(filepath, usecols=['Keyword', 'Match Type', 'State', 'Keyword bid(USD)', 'CPC(USD)', 'ACOS'])
                else:
                    raise ValueError("Unsupported file format")
                
                # Rename 'Keyword' to 'Keyword/Automatic targeting groups' for consistency
                df.rename(columns={'Keyword': 'Keyword/Automatic targeting groups'}, inplace=True)
                
                # Add Target ACOS column based on user input
                df['Target ACOS'] = float(target_acos)
                
                # Process data and calculate new max bids
                df['New Max Bid'] = df.apply(calculate_new_max_bid, axis=1)
                
                # Convert to HTML table
                result_html = df.to_html(classes='table table-striped', index=False)
                
                # Clean up
                os.remove(filepath)
                
                return render_template('index.html', table=result_html)
                
            except Exception as e:
                return render_template('index.html', error=str(e))
        
        return render_template('index.html', error='Invalid file type')
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
