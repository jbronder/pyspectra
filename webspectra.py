#!/usr/bin/env python3

# file: webspectra.py
# -----------------------------------------------------------------------------
# A command line program to serve as a URL function call to obtain the design
# spectra from the USGS web service.
#------------------------------------------------------------------------------

import argparse
import csv
import json
import pprint
import sys
import urllib.parse
import urllib.request

from types import SimpleNamespace
from urllib.error import URLError

# Web Spectra Specific Modules
from wdstable import DESCRIPTION_LABELS, METADATA_LABELS, Extractor, Table, \
        append_output_descriptions

def _output_user_request(input_parameters: dict[str, any]):
    print("User Input:")
    pprint.pprint(input_parameters)

def unzip_and_collect(
        spectrum: list[list[float]]
        ) -> tuple[list[float],list[float]]:
    """Converts a list of spectrum pairs into a tuple of two lists denoted as
    'points_tuple' with tuple[0] representing the period and tuple[1]
    representing the ordinates.

    Parameters
    ----------
    spectrum : list[list[float]]

    Returns
    -------
    points_tuple : tuple[list[float], list[float]]
    """
    periods = []
    ordinates = []
    for points in spectrum[1]:
        periods.append(points[0])
        ordinates.append(points[1]) 
    return (periods, ordinates)

def spectrum_to_json(spectrum: list[list[float]] | SimpleNamespace) -> str:
    """Converts spectrum series data into a JSON string.

    Parameters
    ----------
    spectrum : list[list[float]] | SimpleNamespace

    Returns
    -------
    json_str : str

    """
    result = {}
    if isinstance(spectrum[1], SimpleNamespace):
        result['periods'] = spectrum[1].periods
        result['ordinates'] = spectrum[1].ordinates
    else:
        points = unzip_and_collect(spectrum)
        result['periods'] = points[0]
        result['ordinates'] = points[1]
    return json.dumps(result)

def spectrum_to_csv_to_stdout(spectrum: list[list[float]] | SimpleNamespace):
    csv_stdout = csv.writer(sys.stdout)
    if isinstance(spectrum[1], SimpleNamespace): 
        for i in range(len(spectrum[1].periods)):
            csv_stdout.writerow([spectrum[1].periods[i], spectrum[1].ordinates[i]])
    else:
        points = unzip_and_collect(spectrum)
        for i in range(len(points[0])):
            csv_stdout.writerow([points[0][i], points[1][i]])

def make_request(args: dict[str, any]):
    """Consolidates user arguments to make a well-formed query.
    Parameters
    ----------
    args : dict[str, any]
    """
    try:
        parameters = {} # for storing query parameters
        # carry out request
        ROOT_URL = 'https://earthquake.usgs.gov/ws/designmaps/'
        REF_DOCUMENT = args.std
        parameters['latitude'] = args.latitude
        parameters['longitude'] = args.longitude
        parameters['riskCategory'] = args.risk_category
        parameters['siteClass'] = args.site_class
        parameters['title'] = 'Example'

        PARAMETERS_ENCODED = urllib.parse.urlencode(parameters)
        FULL_URL = ROOT_URL + REF_DOCUMENT + '.json?' + PARAMETERS_ENCODED
        with urllib.request.urlopen(FULL_URL) as response:
            response_string = response.read().decode('utf-8')

            # outputs only spectrum data
            if args.spectrum:
                ext = Extractor(response_string)
                spectrum_label_mapping = {
                        "two-design": "twoPeriodDesignSpectrum",
                        "two-mcer": "twoPeriodMCErSpectrum",
                        "vert-design": "verticalDesignSpectrum",
                        "vert-mcer": "verticalMCErSpectrum",
                        "multi-design": "multiPeriodDesignSpectrum",
                        "multi-mcer": "multiPeriodMCErSpectrum",
                        "risk-targeted": "riskTargetedSpectrum",
                        "84th": "eightyFourthSpectrum",
                        }
                all_spectra: list[tuple[any, ...]] = ext.extract_spectra()

                if len(all_spectra) == 0:
                    print('No spectra series data is provided for this site.')
                else:
                    for spectrum in all_spectra:
                        if spectrum[0] == spectrum_label_mapping[args.spectrum]:
                            if args.output == 'json':
                                print(spectrum_to_json(spectrum))
                            else:
                                spectrum_to_csv_to_stdout(spectrum) 

            # outputs everything but spectrum data
            else:
                if args.output == 'json':
                    print(response_string)
                else:
                    ext = Extractor(response_string)
                
                    in_headings = ("Input", "Values")
                    user_req = ext.extract_input()
                    tbl_in = Table(in_headings, user_req)
                    tbl_in.render()

                    out_headings = ("Parameters", "Values", "Description")
                    svs = ext.extract_svs()
                    out_svs = append_output_descriptions(svs, DESCRIPTION_LABELS)
                    tbl_out = Table(out_headings, out_svs)
                    tbl_out.render()

                    meta_headings = ("Metadata", "Values", "Description")
                    metadata_svs = ext.extract_metadata_svs()
                    out_metadata_svs = append_output_descriptions(
                            metadata_svs, METADATA_LABELS)
                    tbl_meta = Table(meta_headings, out_metadata_svs)
                    tbl_meta.render()
    except URLError:
        raise

# Building the command line utility
parser = argparse.ArgumentParser(
        prog = 'webspectra.py',
        description = 'A command utility to obtain USGS seismic design data and spectra.',
        epilog = 'Ver: 0.1.0. Currently under development. Use at own risk.'
        )

latitude_arg_template = {
        "dest": "latitude",
        "help": "Site Latitude",
        "type": float,
        }

longitude_arg_template = {
        "dest": "longitude",
        "help": "Site Longitude",
        "type": float,
        }

risk_category_arg_template = {
        "dest": "risk_category",
        "help": "Risk Category: ['I', 'II', 'III', 'IV']",
        "metavar": "risk_category",
        "choices": ['I', 'II', 'III', 'IV'],
        }

site_class_arg_template_one = {
    "dest": "site_class",
    "help": "Site Class: ['A', 'B', 'C', 'D', 'E']",
    "metavar": "site_class",
    "choices": ['A', 'B', 'C', 'D', 'E']
}

site_class_arg_template_two = {
    "dest": "site_class",
    "help": "Site Class: ['A', 'B', 'B-estimated', 'C', 'D', 'D-default','E']",
    "metavar": "site_class",
    "choices": ['A', 'B', 'B-estimated', 'C', 'D', 'D-default','E']
}

site_class_arg_template_three = {
    "dest": "site_class",
    "help": "Site Class: ['A', 'B', 'BC', 'C', 'CD', 'D', 'DE','E', 'default']",
    "metavar": "site_class",
    "choices": ['A', 'B', 'BC', 'C', 'CD', 'D', 'DE','E', 'default']
}

subparsers = parser.add_subparsers(help='available design standards')

# asce7-22 subcommand
asce722_parser = subparsers.add_parser(
    'asce7-22', 
    aliases=['asce'],
    description="Seismic design data from the ASCE 7-22 design standard.",
    help='ASCE 7-22 help'
    )
asce722_parser.add_argument(**latitude_arg_template)
asce722_parser.add_argument(**longitude_arg_template)
asce722_parser.add_argument(**risk_category_arg_template)
asce722_parser.add_argument(**site_class_arg_template_three)
asce722_parser.add_argument(
    '-s', '--spectrum',
    help='request spectrum only',
    choices=['two-design', 'two-mcer',
            'vert-design', 'vert-mcer', 
            'multi-design', 'multi-mcer',
            'risk-targeted', '84th',
            ],
    )
asce722_parser.set_defaults(std='asce7-22', fn=make_request)

# asce7-16 subcommand
asce716_parser = subparsers.add_parser(
    'asce7-16', 
    description="Seismic design data from the ASCE 7-16 design standard.",
    help='ASCE 7-16 help'
    )
asce716_parser.add_argument(**latitude_arg_template)
asce716_parser.add_argument(**longitude_arg_template)
asce716_parser.add_argument(**risk_category_arg_template)
asce716_parser.add_argument(**site_class_arg_template_two)
asce716_parser.add_argument(
    '-s', '--spectrum',
    help='request spectrum only',
    choices=['two-design', 'two-mcer'
             'vert-design', 'vert-mcer',
             ],
)
asce716_parser.set_defaults(std='asce7-16', fn=make_request)

# asce7-10 subcommand
asce710_parser = subparsers.add_parser(
    'asce7-10', 
    description='Seismic design data from the ASCE 7-10 design standard.',
    help='ASCE 7-10 help'
    )
asce710_parser.add_argument(**latitude_arg_template)
asce710_parser.add_argument(**longitude_arg_template)
asce710_parser.add_argument(**risk_category_arg_template)
asce710_parser.add_argument(**site_class_arg_template_one)
asce710_parser.add_argument(
    '-s', '--spectrum',
    help='request spectrum only',
    choices=['two-design', 'two-mcer'],
)
asce710_parser.set_defaults(std='asce7-10', fn=make_request)

# asce7-05 subcommand
asce705_parser = subparsers.add_parser(
    'asce7-05',
    description='Seismic design data from the ASCE 7-05 design standard.',
    help='ASCE 7-05 help'
)
asce705_parser.add_argument(**latitude_arg_template)
asce705_parser.add_argument(**longitude_arg_template)
asce705_parser.add_argument(**risk_category_arg_template)
asce705_parser.add_argument(**site_class_arg_template_one)
asce705_parser.add_argument(
    '-s', '--spectrum',
    help='request spectrum only',
    choices=['two-design', 'two-mcer'],
    )
asce705_parser.set_defaults(std='asce7-05', fn=make_request)

# nehrp-2020 subcommand
nehrp2020_parser = subparsers.add_parser(
    'nehrp-2020',
    aliases=['nehrp'],
    description='Seismic design data from the NEHRP 2020 document.',
    help='NEHRP 2020 help',
)
nehrp2020_parser.add_argument(**latitude_arg_template)
nehrp2020_parser.add_argument(**longitude_arg_template)
nehrp2020_parser.add_argument(**risk_category_arg_template)
nehrp2020_parser.add_argument(**site_class_arg_template_three)
nehrp2020_parser.set_defaults(std='nehrp-2020', fn=make_request)

# nehrp-2015 subcommand
nehrp2015_parser = subparsers.add_parser(
    'nehrp-2015',
    description='Seismic design data from NEHRP 2015 document.',
    help="NEHRP 2015 help",
)
nehrp2015_parser.add_argument(**latitude_arg_template)
nehrp2015_parser.add_argument(**longitude_arg_template)
nehrp2015_parser.add_argument(**risk_category_arg_template)
nehrp2015_parser.add_argument(**site_class_arg_template_two)
nehrp2015_parser.set_defaults(std='nehrp-2015', fn=make_request)

# nehrp-2009 subcommand
nehrp2009_parser = subparsers.add_parser(
    'nehrp-2009',
    description='Seismic design data from NEHRP 2009 document.',
    help='NEHRP 2009 help',
)
nehrp2009_parser.add_argument(**latitude_arg_template)
nehrp2009_parser.add_argument(**longitude_arg_template)
nehrp2009_parser.add_argument(**risk_category_arg_template)
nehrp2009_parser.add_argument(**site_class_arg_template_one)
nehrp2009_parser.set_defaults(std='nehrp-2009', fn=make_request)

# ibc-2015 subcommand
ibc2015_parser = subparsers.add_parser(
    'ibc-2015',
    aliases=['ibc'],
    description='Seismic design data from IBC 2015 code.',
    help='IBC 2015 help',
    )
ibc2015_parser.add_argument(**latitude_arg_template)
ibc2015_parser.add_argument(**longitude_arg_template)
ibc2015_parser.add_argument(**risk_category_arg_template)
ibc2015_parser.add_argument(**site_class_arg_template_one)
ibc2015_parser.set_defaults(std='ibc-2015', fn=make_request)

# ibc-2009 subcommand
ibc2009_parser = subparsers.add_parser(
    'ibc-2009',
    description='Seismic design data from IBC 2009 code.',
    help='IBC 2009 help',
    )
ibc2009_parser.add_argument(**latitude_arg_template)
ibc2009_parser.add_argument(**longitude_arg_template)
ibc2009_parser.add_argument(**risk_category_arg_template)
ibc2009_parser.add_argument(**site_class_arg_template_one)
ibc2009_parser.set_defaults(std='ibc-2009', fn=make_request)

# aashto-2009 subcommand
aashto2009_parser = subparsers.add_parser(
    'aashto-2009',
    aliases=['aashto'],
    description='Seismic design data from the AASHTO 2009 standard.',
    help='AASHTO 2009 help',
)
aashto2009_parser.add_argument(**latitude_arg_template)
aashto2009_parser.add_argument(**longitude_arg_template)
aashto2009_parser.add_argument(**risk_category_arg_template)
aashto2009_parser.add_argument(**site_class_arg_template_one)
aashto2009_parser.set_defaults(std='aashto-2009', fn=make_request)

parser.add_argument('-o', '--output', 
    help='output format', 
    choices=['json', 'table'],
    default='table',
    )

args = parser.parse_args()
args.fn(args)
