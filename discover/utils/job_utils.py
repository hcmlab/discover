"""Utility modules for NOVA-Server Jobs

Author:
    Dominik Schiller <dominik.schiller@uni-a.de>
Date:
    13.09.2023

"""

import random
from datetime import datetime
from enum import Enum
from discover.utils.thread_utils import status_thread_wrapper
from . import log_utils
from ..data import ANIMALS, COLORS


def get_job_id_from_request_form(request_form):
    """
    Returns the logging key from the provided request form
    Args:
        request_form (dict): Request form from Nova

    Returns:

    """
    key = request_form.get("jobID", None)

    if key is None:
        key = f"{get_random_name()}"

    return key


def get_random_name(
    combo=(COLORS, ANIMALS), separator: str = " ", style: str = "capital"
):
    if not combo:
        raise Exception("combo cannot be empty")

    random_name = []
    for word_list in combo:
        part_name = random.choice(word_list)
        if style == "capital":
            part_name = part_name.capitalize()
        if style == "lowercase":
            part_name = part_name.lower()
        if style == "uppercase":
            part_name = part_name.upper()
        random_name.append(part_name)
    return separator.join(random_name)


JOBS = {}


class JobStatus(Enum):
    WAITING = 0
    RUNNING = 1
    FINISHED = 2
    ERROR = 3


class Job:
    def __init__(self, job_key, interactive_url=None, log_path=None, details=None, job_type=None):
        self.start_time = None
        self.end_time = None
        self.progress = None
        self.status = JobStatus.WAITING
        self.job_key = job_key
        self.interactive_url = interactive_url
        self.log_path = log_path
        self.details = details
        self.job_type = job_type
        self.execution_handler = None

    def serializable(self):
        # Only include serializable fields, avoid execution_handler which contains locks
        # Try to get job type from execution handler if available
        job_type = self.job_type
        if not job_type and self.execution_handler and hasattr(self.execution_handler, 'action'):
            job_type = self.execution_handler.action.value if hasattr(self.execution_handler.action, 'value') else str(self.execution_handler.action)
        
        return {
            'job_key': str(self.job_key),
            'job_type': str(job_type) if job_type else 'Unknown',
            'status': str(self.status.name if hasattr(self.status, 'name') else self.status),
            # 'progress': str(self.progress) if self.progress else '',  # TODO: Implement progress tracking per session and overall sessions
            'start_time': str(self.start_time) if self.start_time else '',
            'end_time': str(self.end_time) if self.end_time else '',
            'log_path': str(self.log_path) if self.log_path else '',
            'details': str(self._sanitize_details()) if self.details else '',
            'interactive_url': str(self.interactive_url) if self.interactive_url else ''
        }

    def run(self):
        self.execution_handler.run()

    def cancel(self):
        self.execution_handler.cancel()
    
    def _sanitize_details(self):
        """Sanitize sensitive information from job details"""
        from . import log_utils
        return log_utils.sanitize_sensitive_data(self.details)


@status_thread_wrapper
def add_new_job(job_key, interactive_url=None, request_form=None):
    log_path = log_utils.get_log_path_for_thread(job_key)
    job_details = log_utils.get_log_conform_request(request_form)
    job = Job(job_key, interactive_url, log_path, details=job_details)
    JOBS[job_key] = job
    return True

@status_thread_wrapper
def get_job(job_key):
    return JOBS[job_key]

@status_thread_wrapper
def remove_job(job_key):
    try:
        del JOBS[job_key]
    except KeyError:
        print(f"Key {job_key} is not in the dictionary")


@status_thread_wrapper
def update_status(job_key, status: JobStatus):
    try:
        JOBS[job_key].status = status

        if status == JobStatus.RUNNING:
            JOBS[job_key].start_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        if status == JobStatus.FINISHED or status == JobStatus.ERROR:
            JOBS[job_key].end_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    except KeyError:
        print(f"Key {job_key} is not in the dictionary")


@status_thread_wrapper
def update_progress(job_key, progress: str):
    try:
        JOBS[job_key].progress = progress
    except KeyError:
        print(f"Key {job_key} is not in the dictionary")


@status_thread_wrapper
def set_log_path(job_key, log_path):
    try:
        JOBS[job_key].log_path = log_path
    except KeyError:
        print(f"Key {job_key} is not in the dictionary")


@status_thread_wrapper
def get_log_path(job_key):
    try:
        return JOBS[str(job_key)].log_path
    except KeyError:
        print(f"Key {job_key} is not in the dictionary")


@status_thread_wrapper
def get_all_jobs():
    return [job.serializable() for job in JOBS.values()]
