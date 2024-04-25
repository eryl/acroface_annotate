#!/usr/bin/env python
# -*- coding: utf-8 -*-

import importlib
import multiprocessing
import sys
from pathlib import Path

#module_name = 'cryptography'
#crypt_path = Path(__file__).parent / 'packages' / 'cryptography_win'
#
#
#spec = importlib.util.spec_from_file_location(module_name, crypt_path)
#cryptography_package = importlib.util.module_from_spec(spec)

#spec.loader.exec_module(module)

#import cryptography
#sys.modules["cryptography"] = cryptography
#from cryptography.fernet import Fernet
#from cryptography.hazmat.primitives import hashes
#from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
#
#import base64
import os

from psychopy import gui  # Fetch default gui handler (qt if available)
from psychopy import __version__
from tqdm import tqdm # Get the PsychoPy version currently in use
## You can explicitly choose one of the qt/wx backends like this:
## from psychopy.gui import wxgui as gui
## from psychopy.gui import qtgui as gui

import aes

def decrypt_file(work_package):
    encrypted_path, output_directory, bytes_password = work_package
    with open(encrypted_path, 'rb') as fp:
        file_bytes = fp.read()
        decrypted_file = aes.decrypt(bytes_password, file_bytes)
        with open(output_directory / encrypted_path.name, 'wb') as out_fp:
            out_fp.write(decrypted_file)
    return encrypted_path
    
def main():
    # Create dlg
    dlg = gui.Dlg(title="Decryption settings", pos=(200, 400))
    # Add each field manually
    #dlg.addText('Subject Info', color='Blue')
    dlg.addField('Decryption key*', tip='secret password with which to encrypt the data')
    # Call show() to show the dlg and wait for it to close (this was automatic with DlgFromDict
    thisInfo = dlg.show()

    data_files = gui.fileOpenDlg(prompt='Select files to decrypt')
    print(data_files)

    if dlg.OK: # This will be True if user hit OK...
        output_directory = Path(__file__).parent / 'decrypted_data'
        output_directory.mkdir(parents=True, exist_ok=True)
        
        password, = thisInfo
        bytes_password = bytes(password, encoding='utf8')
        work_packages = [(Path(encrypted_path), output_directory, bytes_password) for encrypted_path in data_files]
        with multiprocessing.Pool() as pool:
            for path in tqdm(pool.imap_unordered(decrypt_file, work_packages), desc="Decrypting files", total=len(data_files)):
                pass
    else:
        print('User cancelled') # ...or False, if they hit Cancel


if __name__ == '__main__':
    main()