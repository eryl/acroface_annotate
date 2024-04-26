#!/usr/bin/env python
# -*- coding: utf-8 -*-
#import multiprocessing
import multiprocessing.dummy as multiprocessing
import argparse

import importlib
import sys
from pathlib import Path
import io
import os
from typing import Tuple

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
    output_file = output_directory / (image_path.with_suffix('').name + f'.{format}.enc')
    with open(output_file, 'wb') as fp:
        fp.write(encrypted_file)
    return output_file


def filter_image_files(image_path):
    #print(f"Encrypting {path}")
    try:
        image = Image.open(image_path)
        return True
    except UnidentifiedImageError:
        return False
    
def main():
    parser = argparse.ArgumentParser(description="Script to encrypt image data")
    parser.add_argument('source_dir', help="Directory with image files to encrypt", type=Path)
    parser.add_argument('--output_directory', help="directory to store encrypted data to", default=Path("encrypted_data"), type=Path)
    args = parser.parse_args()
    
    password = input("Please enter encryption key:")
    
    data_files = [data_file for data_file in args.source_dir.iterdir() if filter_image_files(data_file)]
        
    bytes_password = bytes(password, encoding='utf8')
    args.output_directory.mkdir(exist_ok=True, parents=True)
    with multiprocessing.Pool() as pool:
        format = 'jpeg'
        work_packages = [(image_path, args.output_directory, bytes_password, format) for image_path in sorted(data_files)]
        for name in tqdm(pool.imap_unordered(encrypt_file, work_packages), desc="Encrypting files", total=len(data_files)):
            pass


if __name__ == '__main__':
    main()