from flask import Flask, request, jsonify, send_from_directory
from steganography import allowed_file, save_temp_file, lsb_decode, lsb_encode
import os
import uuid

app = Flask(__name__, static_folder='../frontend', static_url_path='')

# Ensure temp directory exists
os.makedirs('temp', exist_ok=True)

@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/api/encode', methods=['POST'])
def encode():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    try:
        message = request.form.get('message', '')
        password = request.form.get('password', '')
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400

        # Generate unique filename for output
        original_name = os.path.splitext(file.filename)[0]
        output_filename = f"{original_name}_encoded.png"
        output_path = os.path.join('temp', output_filename)

        # Encode the message
        lsb_encode(
            save_temp_file(file),
            message,
            output_path,
            password
        )

        return jsonify({
            'message': 'Encoding successful',
            'download_url': f'/download/{output_filename}'
        })
    except Exception as e:
        return jsonify({'error': f'Encoding failed: {str(e)}'}), 500

@app.route('/api/decode', methods=['POST'])
def decode():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    try:
        password = request.form.get('password', '')
        message = lsb_decode(
            save_temp_file(file),
            password
        )
        return jsonify({'message': message})
    except ValueError as ve:
        error_msg = str(ve).lower()
        if "password required" in error_msg:
            return jsonify({
                'error': 'This image is password protected. Please provide the password.',
                'requires_password': True
            }), 401
        elif "incorrect password" in error_msg:
            return jsonify({
                'error': 'Incorrect password. Please try again.',
                'requires_password': True
            }), 401
        else:
            return jsonify({'error': f'Decoding failed: {str(ve)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Decoding failed: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory('temp', filename, as_attachment=True)

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)