from flask import Flask, render_template, request, send_from_directory
import qrcode
from PIL import Image
from io import BytesIO
import os
import base64

app = Flask(__name__,template_folder='templates')

# Use /tmp for Vercel since other directories are read-only
image_folder = '/tmp/images'
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate_qr', methods=['GET', 'POST'])
def generate_qr():
    if request.method == 'POST':
        text = request.form.get('text')
        fill_color = request.form.get('fill_color', '#000000')
        back_color = request.form.get('back_color', '#ffffff')
        box_size = int(request.form.get('box_size', 10))

        # Generate QR code with customization options
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)

        img = qr.make_image(fill_color=fill_color, back_color=back_color)

        # Save the QR code image to an in-memory file
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)

        # Convert the image to base64
        img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')

        # Pass the base64-encoded image to the template
        return render_template('generate_qr.html', qr_code=img_base64)

    return render_template('generate_qr.html')

if __name__ == '__main__':
    app.run(debug=True)