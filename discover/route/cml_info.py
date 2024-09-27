""" Blueprint for querying server capabilities

Author:
    Dominik Schiller <dominik.schiller@uni-a.de>
Date:
    14.09.2023

This module defines a Flask Blueprint for querying the server for its capabilities.
Returns a list of all available server-module trainer and chains in json format.

"""
import os
import json
from flask import Blueprint, request
from discover.utils import env
from discover_utils.utils.json_utils import ChainEncoder, TrainerEncoder
from discover_utils.utils.ssi_xml_utils import Chain, Trainer
from discover_utils.utils.request_utils import parse_cml_filter
from pathlib import Path
from glob import glob

cml_info = Blueprint("cml_info", __name__)

def filter(trainer_io_list: list, filter_list: list) -> bool:

    if len(trainer_io_list) != len(filter_list):
        return False

    for f in filter_list:
        super_type_f, sub_type_f, specific_type_f = parse_cml_filter(f)
        for t in trainer_io_list:
            super_type_t, sub_type_t, specific_type_t = parse_cml_filter(t.io_data)

            check_super_type =  super_type_f == super_type_t
            check_sub_type =  (sub_type_f is not None and sub_type_f == sub_type_t) or sub_type_f is None
            check_specifc_type =  (specific_type_f is not None and specific_type_f == specific_type_t) or specific_type_f is None
            if not (check_super_type and check_sub_type and check_specifc_type):
                return False
    return True

@cml_info.route("/cml_info", methods=["POST"])
def info():
    """
    Query the server to return information about all

    This route allows querying the server for all available DISCOVER modules

    Returns:
        dict: A JSON response containing the status of the requested job.

    Example:

    """
    if request.method == "POST":

        cml_dir = os.getenv(env.DISCOVER_CML_DIR)

        if not cml_dir:
            return None

        cml_dir = str(Path(cml_dir).resolve())

        trainer_files = glob(cml_dir + '/**/*.trainer', recursive = True)
        chain_files = glob(cml_dir + '/**/*.chain', recursive = True)

        trainer_ok = {}
        trainer_faulty = {}
        chains_ok = {}
        chains_faulty = {}

        request_form = request.form.to_dict()
        input_filter = json.loads(request_form.get('input_filter', '[]'))
        output_filter = json.loads(request_form.get('output_filter', '[]'))


        for tf in trainer_files:
            t = Trainer()
            rtf = str(Path(tf).relative_to(cml_dir))
            try:
                t.load_from_file(tf)
                inputs_ok = filter([x for x in t.meta_io if x.io_type=='input'], input_filter) if input_filter else True
                outputs_ok = filter([x for x in t.meta_io if x.io_type=='output'], output_filter) if output_filter else True
                if not (inputs_ok and outputs_ok):
                    continue
                trainer_ok[rtf] = json.dumps(t, cls=TrainerEncoder)
            except Exception as e:
                trainer_faulty[rtf] = str(e)

        for cf in chain_files:
            c = Chain()
            rcf = str(Path(cf).relative_to(cml_dir))
            try:
                c.load_from_file(cf)
                chains_ok[rcf] = json.dumps(c, cls=ChainEncoder)
            except Exception as e:
                chains_faulty[rcf] = str(e)


        return {
            'chains_ok' : chains_ok,
            'chains_faulty' : chains_faulty,
            'trainer_ok' : trainer_ok,
            'trainer_faulty' : trainer_faulty
        }



