import os
import secrets

secret_key = secrets.token_hex(16)  # Generates a 32-character hexadecimal secret key
print(secret_key)

# Define the secret key (change this to a secure value in production)
SECRET_KEY = secret_key

# Define the upload folder for storing temporarily uploaded files
UPLOAD_FOLDER = 'API_pipeline/static/uploads'


