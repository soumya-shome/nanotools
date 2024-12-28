from django.shortcuts import render
import qrcode
from io import BytesIO
import base64
import os

# Use /tmp for temporary storage in server environments
image_folder = '/tmp/images'
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

def index(request):
    return render(request, 'qr_generator/generate_qr.html')

def generate_qr(request):
    if request.method == 'POST':
        text = request.POST.get('text', '')
        fill_color = request.POST.get('fill_color', '#000000')
        back_color = request.POST.get('back_color', '#ffffff')
        box_size = int(request.POST.get('box_size', 10))

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)

        img = qr.make_image(fill_color=fill_color, back_color=back_color)

        # Save to in-memory file
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)

        # Convert to base64
        img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
        
        return render(request, 'qr_generator/generate_qr.html', {'qr_code': img_base64})

    return render(request, 'qr_generator/generate_qr.html')
