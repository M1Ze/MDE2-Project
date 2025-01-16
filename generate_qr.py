import qrcode
import os
from io import BytesIO
from PIL import Image
from io import BytesIO

def generate_qr_code_pic(patient_identifier):

    # Define QR code content
    qr_content = f"Patient ID: {patient_identifier}"

    # Generate QR code
    img = qrcode.make(qr_content)

    # Define file path
    file_path = f"QR_Codes/{patient_identifier}.png"
    os.makedirs("QR_Codes", exist_ok=True)  # Ensure the directory exists

    # Save the QR code as an image
    img.save(file_path)

    return file_path

def generate_qr_code_binary(patient_identifier):
    """
    Generates a QR code for the given patient identifier and returns its binary data.
    """
    # Define QR code content
    qr_content = f"Patient ID: {patient_identifier}"

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_content)
    qr.make(fit=True)

    # Save the QR code image to a BytesIO buffer
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_code_binary = buffer.getvalue()
    buffer.close()

    return qr_code_binary

def display_qr_code(qr_code_binary):
    # Displays the QR code image from binary data.
    buffer = BytesIO(qr_code_binary)
    img = Image.open(buffer)
    img.show()  # Opens the QR code in the default image viewer
    buffer.close()

if __name__ == "__main__":
    patient_identifier = input("Patient ID: ")
    print(generate_qr_code_binary(patient_identifier))
    display_qr_code(generate_qr_code_binary(patient_identifier))
    # qr_code_path = generate_qr_code_pic(patient_identifier)
    # print(f"QR code saved at: {qr_code_path}")
