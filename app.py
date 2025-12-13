import os
from io import BytesIO
from flask import Flask, request, send_file, jsonify, make_response
from PIL import Image
from pillow_heif import register_heif_opener

# Register HEIC opener
register_heif_opener()

app = Flask(__name__)

ALLOWED_FORMATS = {'jpg', 'png'}

# --- NEW PART: A Simple Home Page ---
@app.route('/', methods=['GET'])
def home():
    # This HTML creates a simple button to upload a file directly in the browser
    return """
    <html>
        <body>
            <h1>HEIC Converter is Live! 🟢</h1>
            <p>Select an HEIC file to convert:</p>
            <form action="/convert" method="post" enctype="multipart/form-data">
                <input type="file" name="file" accept=".heic">
                <br><br>
                <label>Convert to:</label>
                <select name="format">
                    <option value="jpg">JPG</option>
                    <option value="png">PNG</option>
                </select>
                <br><br>
                <input type="submit" value="Convert Image">
            </form>
        </body>
    </html>
    """

# --- THE CONVERSION LOGIC (Same as before) ---
@app.route('/convert', methods=['POST'])
def convert_heic():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    output_format = request.form.get('format', 'jpg').lower()
    
    if output_format not in ALLOWED_FORMATS:
        return jsonify({"error": "Invalid format"}), 400

    try:
        image = Image.open(file.stream)
        output_buffer = BytesIO()
        
        if output_format == 'jpg':
            image = image.convert("RGB")
            image.save(output_buffer, format='jpeg', quality=85)
            mime_type = 'image/jpeg'
        else:
            image.save(output_buffer, format='png')
            mime_type = 'image/png'
        
        output_buffer.seek(0)
        
        return send_file(
            output_buffer,
            mimetype=mime_type,
            as_attachment=True,
            download_name=f"converted.{output_format}"
        )
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Conversion failed"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
