#!/usr/bin/env python
# -*- coding: utf-8 -*-
#import multiprocessing
import multiprocessing.dummy as multiprocessing
import importlib
import sys
from pathlib import Path
import io
import os
from typing import Tuple

from psychopy import gui  # Fetch default gui handler (qt if available)
from psychopy import __version__ # Get the PsychoPy version currently in use

from PIL import Image, UnidentifiedImageError, ImageOps

from tqdm import tqdm

import aes

target_size = (512, 512)

# For some reason this was missing from the ImageOps bundled with PIL in psychopy, including it from the sources here
def cover(
    image: Image.Image, size: Tuple[int, int], method: int = Image.Resampling.BICUBIC
) -> Image.Image:
    """
    Returns a resized version of the image, so that the requested size is
    covered, while maintaining the original aspect ratio.

    :param image: The image to resize.
    :param size: The requested output size in pixels, given as a
                 (width, height) tuple.
    :param method: Resampling method to use. Default is
                   :py:attr:`~PIL.Image.Resampling.BICUBIC`.
                   See :ref:`concept-filters`.
    :return: An image.
    """

    im_ratio = image.width / image.height
    dest_ratio = size[0] / size[1]

    if im_ratio != dest_ratio:
        if im_ratio < dest_ratio:
            new_height = round(image.height / image.width * size[0])
            if new_height != size[1]:
                size = (size[0], new_height)
        else:
            new_width = round(image.width / image.height * size[1])
            if new_width != size[0]:
                size = (new_width, size[1])
    return image.resize(size, resample=method)

def encrypt_file(work_package):
    image_path, output_directory, bytes_password, format, = work_package
    #print(f"Encrypting {path}")
    pil_image = Image.open(image_path).convert("RGB")
    pil_image = cover(pil_image, target_size)
    output_buffer = io.BytesIO()
    pil_image.save(output_buffer, format=format)
    encrypted_file = aes.encrypt(bytes_password, output_buffer.getvalue())
    with open(output_directory / image_path.with_suffix(f'.{format}').name, 'wb') as out_fp:
        out_fp.write(encrypted_file)
    #print(f"Done encrypting {path}")
    return image_path


def filter_image_files(image_path):
    #print(f"Encrypting {path}")
    try:
        image = Image.open(image_path)
        return True
    except UnidentifiedImageError:
        return False
    
    
def main():
    #import soundfile
    #print(soundfile.available_formats())

    # Create dlg
    dlg = gui.Dlg(title="Alternativ för kryptering")
    # Add each field manually
    dlg.addField('Lösenord', tip='Lösenord som används för att kryptera data')
    #dlg.addField('Filformat att spara till', tip='Filformat som används för att lagra data. JPEG är att föredra då filernas storlek blir mindre, men det kommer ta bort information från bilden', choices=('png', 'jpeg'), initial='jpeg')
    #dlg.addField('Filer att söka efter', tip='Sök efter filer i samma katalog av dem här typen', choices=('Ljudfiler (.wav, .flac)', 'Alla filer'), initial='Ljudfiler (.wav, .flac)')

    # Call show() to show the dlg and wait for it to close (this was automatic with DlgFromDict
    thisInfo = dlg.show()
    if dlg.OK: # This will be True if user hit OK...
        #password, format, search_choice = thisInfo
        password, = thisInfo
    
        data_files = gui.fileOpenDlg(prompt='Välj filer att kryptera (alla filer i samma katalog kommer genomsökas)')
        parents = set(Path(data_file).parent for data_file in data_files)
        #print(data_files)
        # if search_choice == 'Ljudfiler (.wav, .flac)':
        #     glob_patterns = ('*.flac', '*.wav')
        # else:
        #     glob_patterns = ('*',)
        glob_patterns = ('*',)
        data_files = set()
        for glob_pattern in glob_patterns:
            for parent in parents:
                data_files.update(parent.glob(glob_pattern))
        
        data_files = [data_file for data_file in data_files if filter_image_files(data_file)]
        
        output_directory = Path(__file__).parent / 'encrypted_data'
        output_directory.mkdir(parents=True, exist_ok=True)
        
        bytes_password = bytes(password, encoding='utf8')
        with multiprocessing.Pool() as pool:
            format = 'jpeg'
            work_packages = [(image_path, output_directory, bytes_password, format) for image_path in data_files]
            for path in tqdm(pool.imap_unordered(encrypt_file, work_packages), desc="Encrypting files", total=len(data_files)):
                pass
            
        gui.infoDlg("Data har krypterats", prompt=f"Krypterad data har sparats till katalogen:\n {str(output_directory.absolute())}")
        
    else:
        print('User cancelled') # ...or False, if they hit Cancel



if __name__ == '__main__':
    main()