""" Blueprint for querying server capabilities

Author:
    Dominik Schiller <dominik.schiller@uni-a.de>
Date:
    15.11.2023

This module defines a Flask Blueprint for uploading files to the server.
Returns the filepath where the data is stored on the server
"""
import os
import json
from flask import Blueprint, request, redirect, url_for
from pathlib import Path
import tempfile
import random
import string

upload = Blueprint("upload", __name__)
@upload.route("/upload", methods=["POST"])
def upload_file():
    """
    Upload a file to the server for further processing

    Returns:
        str: A relative filepath to the uploaded file

    Example:

    """
    if request.method == "POST":
        file = request.files['file']

        upload_dir = Path(tempfile.tempdir)
        upload_dir.mkdir(parents=False, exist_ok=True)

        fn = ''.join(random.choices(string.ascii_lowercase, k=6)) + '.'+file.filename.split('.')[-1]
        fp = upload_dir / fn
        file.save(fp)
        rel_path = Path(fp.resolve()).relative_to(Path(tempfile.gettempdir()).resolve())
        return str(rel_path)


