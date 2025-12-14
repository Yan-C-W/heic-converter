import os
from io import BytesIO
from flask import Flask, request, send_file, jsonify, make_response
from PIL import Image
from pillow_heif import register_heif_opener

# Register HEIC opener
register_heif_opener()

app = Flask(__name__)

ALLOWED_FORMATS = {'jpg', 'png'}

# --- HOME PAGE (Visual Interface) ---
@app.route('/', methods=['GET'])
def home():
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

# --- THE CONVERSION LOGIC ---
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
        
        # --- NEW LOGIC: Preserve the filename ---
        # 1. Get the original filename (e.g., "receipt_december.heic")
        original_name = file.filename
        
        # 2. Split the name from the extension 
        # os.path.splitext("receipt.heic") becomes ("receipt", ".heic")
        # [0] grabs just the first part ("receipt")
        name_without_ext = os.path.splitext(original_name)[0]
        
        # 3. Create the new full name (e.g., "receipt_december.jpg")
        new_filename = f"{name_without_ext}.{output_format}"
        
        return send_file(
            output_buffer,
            mimetype=mime_type,
            as_attachment=True,
            download_name=new_filename # <--- Updated to use the new variable
        )
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Conversion failed"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
