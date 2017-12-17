#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import os

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types

import argparse

def get_labels(file_name):
    client = vision.ImageAnnotatorClient()
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()
    image = types.Image(content=content)
    response = client.label_detection(image=image)
    return response.label_annotations


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "use google cloud vision api")
    parser.add_argument("--image", type=str, help = "Image file path", required=True)
    args = parser.parse_args()
    labels = get_labels(args.image)
    print(labels)
