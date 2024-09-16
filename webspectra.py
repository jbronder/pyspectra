#!/usr/bin/env python3

# file: webspectra.py
# -----------------------------------------------------------------------------
# A command line program to serve as a URL function call to obtain the design
# spectra from the USGS web service.
#------------------------------------------------------------------------------

import argparse
import pprint
import urllib.parse
import urllib.request

# Web Spectra Specific Modules
from wdstable import DESCRIPTION_LABELS, METADATA_LABELS, Extractor, Table, append_output_descriptions, filter_out_parameters

def _output_user_request(input_parameters: dict):
    print("User Input:")
    pprint.pprint(input_parameters)

# Building the command line utility
parser = argparse.ArgumentParser(
        prog = 'webspectra.py',
        description = 'A command utility to obtain USGS seismic accelerations.',
        epilog = 'NOTE: Currently under development. Use at own risk.'
        )

parser.add_argument(
    'std', 
    metavar='std', 
    help='Design Standard', 
    choices=['asce7-22', 'asce7-16', 'asce7-10', 'asce7-05',
    'nehrp-2020', 'nehrp-2015', 'nehrp-2009',
    'ibc-2015', 'ibc-2012',
    'aashto-2009',
    ],
    )
parser.add_argument('latitude', help='Site Latitude', type=float)
parser.add_argument('longitude', help='Site Longitude', type=float)
parser.add_argument(
    'risk_category', 
    help='Risk Category', 
    metavar='risk_category', 
    choices=['I', 'II', 'III', 'IV']
    )
parser.add_argument(
    'site_class', 
    help='Site Class',
    metavar='site_class',
    choices=['A', 'B', 'C', 'D', 'D-default', 'E', 'F'],
    )
parser.add_argument('-o', '--output', 
    help='output format', 
    choices=['json', 'table'],
    default='table',
    )
args = parser.parse_args()

# Using command arguments to form into a well-formed request
parameters = {} # for storing query parameters

ROOT_URL = 'https://earthquake.usgs.gov/ws/designmaps/'
REF_DOCUMENT = args.std
parameters['latitude'] = args.latitude
parameters['longitude'] = args.longitude
parameters['riskCategory'] = args.risk_category
parameters['siteClass'] = args.site_class
parameters['title'] = 'Example'

PARAMETERS_ENCODED = urllib.parse.urlencode(parameters)
FULL_URL = ROOT_URL + REF_DOCUMENT + '.json?' + PARAMETERS_ENCODED

# Carry out request...
with urllib.request.urlopen(FULL_URL) as response:
    response_string = response.read().decode('utf-8')
    if args.output == 'json':
        print(response_string)
    else:
        ext = Extractor(response_string)
    
        in_headings = ("Input", "Values")
        user_req = ext.extract_input()
        tbl_in = Table(in_headings, user_req)
        tbl_in.write_to_file("out.txt")

        out_headings = ("Parameters", "Values", "Description")
        svs = ext.extract_svs()
        out_svs = append_output_descriptions(svs, DESCRIPTION_LABELS)
        tbl_out = Table(out_headings, out_svs)
        tbl_out.write_to_file("out.txt", True)

        meta_headings = ("Metadata", "Values", "Description")
        metadata_svs = ext.extract_metadata_svs()
        out_metadata_svs = append_output_descriptions(metadata_svs, METADATA_LABELS)
        tbl_meta = Table(meta_headings, out_metadata_svs)
        tbl_meta.write_to_file("out.txt", True)
