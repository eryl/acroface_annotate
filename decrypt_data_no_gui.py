#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import importlib
import multiprocessing
import sys
from pathlib import Path


import os

from tqdm import tqdm # Get the PsychoPy version currently in use

import aes

def decrypt_file(work_package):
    encrypted_path, output_directory, bytes_password = work_package
    with open(encrypted_path, 'rb') as fp:
        file_bytes = fp.read()
        decrypted_file = aes.decrypt(bytes_password, file_bytes)
        
        with open(output_directory / encrypted_path.with_suffix('').name, 'wb') as out_fp:
            out_fp.write(decrypted_file)
    return encrypted_path
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('encrypted_dir', type=Path)
    parser.add_argument('decryption_dir', type=Path)
    args = parser.parse_args()
    
    data_files = sorted([file for file in args.encrypted_dir.iterdir() if '.enc' == file.suffix])
    password = input("Please enter decryption key:")
    bytes_password = bytes(password, encoding='utf8')
    work_packages = [(Path(encrypted_path), args.decryption_dir, bytes_password) for encrypted_path in data_files]
    args.decryption_dir.mkdir(exist_ok=True, parents=True)
    with multiprocessing.Pool() as pool:
        for path in tqdm(pool.imap_unordered(decrypt_file, work_packages), desc="Decrypting files", total=len(data_files)):
            pass



if __name__ == '__main__':
    main()