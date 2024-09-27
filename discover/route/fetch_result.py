""" Blueprint for retrieving a job's log file

Author:
    Dominik Schiller <dominik.schiller@uni-a.de>
Date:
    27.10.2023

This module defines a Flask Blueprint for retrieving a job's log file.

"""
import flask
from flask import Blueprint, request, abort
from discover.utils.job_utils import get_job_id_from_request_form
from discover.utils import env
from pathlib import Path
import tempfile
import shutil
fetch_result = Blueprint("fetch_result", __name__)

import zipfile
import os
from discover_utils.utils.string_utils import string_to_bool
from flask import send_file, current_app
from mimetypes import guess_type

def supported_file(x: Path):
    file_names = [
    ]
    file_starts_with = [
        '.'
    ]
    file_ext = [

    ]
    return not (x.name in file_names or any([x.name.startswith(s) for s in file_starts_with]) or x.suffix in file_ext)

#https://stackoverflow.com/questions/24612366/delete-an-uploaded-file-after-downloading-it-from-flask
#https://stackoverflow.com/questions/40853201/remove-file-after-flask-serves-it/40854330#40854330
def download_and_remove_dir(job_dir: Path, delete_after_download=False):

    to_del = []
    if delete_after_download:
        to_del.append(job_dir)

    files = list(filter(lambda x: supported_file(x) and x.is_file(), job_dir.rglob('*')))

    download_fp = None
    if len(files) > 1:
        zip_fp = Path(tempfile.gettempdir()) / (job_dir.name + '.zip')
        zipfolder = zipfile.ZipFile(zip_fp, 'w', compression=zipfile.ZIP_STORED)
        for file in files:
            zipfolder.write(file, arcname=file.relative_to(job_dir.parent))
        zipfolder.close()
        download_fp = zip_fp
        to_del.append(download_fp)
    elif len(files) == 1:
        download_fp = files[0]
    else:
        raise FileNotFoundError(f'{files}')

    def generate():
        with open(download_fp, mode="rb") as f:
            while chunk := f.read(1024):
                yield chunk

        for d in to_del:
            d: Path
            print(f'Deleting {d}')
            if d.is_file():
                os.remove(d)
            if d.is_dir():
                shutil.rmtree(d)



    mt = guess_type(download_fp)[0]
    r = current_app.response_class(generate(), mimetype=mt)
    r.headers.set('Content-Disposition', 'attachment', filename=download_fp.name)
    return r


@fetch_result.route("/fetch_result", methods=["POST"])
def fetch_thread():
    """
    Retrieve the results of a specific job.

    This route allows retrieving the data file  for a job by providing the job's unique identifier in the request.

    Returns:
        dict: Data object for the respective job. 404 if not data has been found

    Example:
        >>> POST /log
        >>> {"job_id": "12345"}
        {"message": "Log file content here..."}
    """
    if request.method == "POST":
        request_form = request.form.to_dict()
        job_id = get_job_id_from_request_form(request_form)
        delete_after_download = request_form.get('delete_after_download', False)
        if isinstance(delete_after_download, str):
            delete_after_download = string_to_bool(delete_after_download)

        shared_dir = os.getenv(env.NOVA_SERVER_TMP_DIR)
        job_dir = Path(shared_dir) / job_id

        if not job_dir.exists():
            raise FileNotFoundError(f'No data for job id {job_id} found on server.')

        else:
            return download_and_remove_dir(job_dir, delete_after_download)


