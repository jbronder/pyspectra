# file: wdstable.py
# -----------------------------------------------------------------------------
# Description: A web spectra library for outputting to the terminal. 
#
# TODO
# [ ] Update docstrings
# [ ] Test configurations (import unittest)
# [ ] Output spectras in toml, csv, json, xml formats
# [ ] Requests are placed in to a localized SQL database for retrival.
# -----------------------------------------------------------------------------

import csv
import json
import io

from typing import BinaryIO, Callable

# Debug modules
import pdb
import pprint

REQUEST_LABELS = {
    'date' : 'Date', 
    'referenceDocument' : 'Reference Document',
    'status' : 'Status',
    'url' : 'URL',
    'parameters' : 'Parameters',
    }

INPUT_LABELS = {
    'latitude' : 'Latitude',
    'longitude' : 'Longitude',
    'riskCategory' : 'Risk Category',
    'siteClass' : 'Site Class',
    'title' : 'Title'
    }

DESCRIPTION_LABELS = {
    'pgauh' : 'Uniform Hazard PGA',
    'pgad' : 'Deterministic Factored PGA',
    'pga' : 'MCEr PGA',
    'fpga' : 'Fa PGA',
    'pgam' : 'Site Mod. PGA',
    'ssrt' : 'Probabilistic Risk Targeted SS',
    'crs' : 'Coefficent of Risk (0.2s)',
    'ssuh' : 'Factored UH SS',
    'ssd' : 'Factored Det. SS',
    'ss' : 'Short Spectra (SS) MCEr',
    'fa' : 'Short Spectra Fa Factor',
    'sms' :'Site-Modified SS (Sms)',
    'sds' : 'Design Spectra (Sds)',
    'sdcs' : 'Seismic Design Category via Sds',
    's1rt' : 'Probabilistic Risk Targeted S1',
    'cr1' : 'Coefficient of risk (1.0s)',
    's1uh' : 'Factored UH S1',
    's1d' : 'Factored Det. S1',
    's1' : 'S1 MCEr',
    'fv' : 'S1 Fv Factor',
    'sm1' : 'Site-Modified S1 (Sm1)',
    'sd1' : 'Design Spectra (Sd1)',
    'sdc1' : 'Seismic Design Category via Sd1',
    'sdc' : 'Seismic Design Category via Sds and Sd1',
    'tl' : 'Long-period Transition, Tl (seconds)',
    't-sub-l' : 't-sub-l (DEPRECATED)',
    'cv' : 'Vertical Coefficient (Cv)',
    'twoPeriodDesignSpectrum' : 'Two Period Horizontal Design Spectrum',
    'twoPeriodMCErSpectrum' : 'Two Period MCEr Spectrum',
    'verticalDesignSpectrum' : 'Vertical Design Spectrum',
    'verticalMCErSpectrum' : 'Vertical MCEr Spectrum'
    }

def append_output_descriptions(
        data_rows: list[tuple[any,...]],
        labels: dict[str, str]
        ):
    """Appends a short description for each parameter present in the output
    table.

    Parameters
    ----------
    data_rows : list[tuple[any,...]]

    labels : dict[str, str]
        
    """
    # find applicable descriptions based on the parameter

    # append descriptions in a new tuple row
    output = []
    for row in data_rows:
        if row[0] in labels:
            label = labels[row[0]]
            param, value = row
            output.append((param, value, label))
    return output

def filter_out_parameters(data_rows: list[tuple[any, ...]], *filter_args):
    """Mutates the list in-place to filter out parameters.

    Parameters
    ----------
    data_rows : list[tuple[any, ...]]
        A list of tuples containing data for each row

    filter_args : tuple[str,...]
        A tuple of parameters that are to be filtered out of the data_rows
        object.
    """
    removal = []
    for data in data_rows:
        for filter_field in filter_args:
            if data[0] == filter_field:
                removal.append(data)
    for item in removal:
        data_rows.remove(item)

class Extractor:
    """Extraction of JSON data for further processing into a table for 
    presentation. 
    
    An extractor object will generate a list of tuples such that each field will
    take the form:
        (field0, field1, field2, ...., field_n-2, field_n-1)
    
    Example
    -------
    < TODO : Example Goes Here >
    """
    def __init__(self, json_res: dict[str, any] | BinaryIO):
        if not isinstance(json_res, dict):
            self._json_res = self._flatten_dict(json.load(json_res))
        else:
            self._json_res = self._flatten_dict(json_res)
    
    def extract_svs(self) -> list[tuple[any, ...]]:
        """Generate a list of data rows where single value data from the JSON
        response.

        Returns
        -------
        svs : list[tuple[any, ...]]
            A list of data row tuples.
        """
        svs = []
        # filter out list objects
        for k, v in self._json_res.items():
            if k.find("response.data") != -1 and not isinstance(v, list):
                k_entry = self._parse_suffix(k)
                svs.append((k_entry, v))
        return svs

    def extract_spectra(self) -> list[tuple[any, ...]]: 
        """Extract response JSON data for the Design and or MCE Spectra.

        Returns
        -------
        spectra: list[tuple[str, ...]]
        """
        # needs a check if this is available in the first place. It may not exist
        spectra = []
        for k, v in self._json_res.items():
            if k.find("Spectrum") != -1:
                k_entry = self._parse_suffix(k)
                spectra.append((k_entry, v))
        return spectra

    def extract_input(self) -> list[tuple[any, ...]]:
        """Extract JSON client request.
        """
        client_req = []
        for k, v in self._json_res.items():
            if k.find("request") != -1:
                # filter out fully-qual'd 'url' and the 'status' tags
                if k.find("url") == -1 and k.find("status") == -1: 
                    k_entry = self._parse_suffix(k)
                    client_req.append((k_entry, v))
        return client_req

    def extract_metadata(self) -> list[tuple[any, ...]]:
        """Extract metadata from JSON response."""
        metadata = []
        for k, v in self._json_res.items():
            if k.find("metadata") != -1:
                k_entry = self._parse_suffix(k)
                metadata.append((k_entry, v))
        return metadata 

    def _flatten_dict(self, kv_map: dict[str, any]) -> dict[str, any]:
        """Resolve nested dicts into a single level dict.

        Parameters
        ----------
        kv_map : dict[str, any]
            a dict with other nested dicts

        Returns
        -------
        flat_dict : dict[str, any]
            a flattened dict
        """
        kv_list = []
        self._flatten_dict_helper(kv_map, kv_list, "")
        flat_dict = dict(kv_list)
        return flat_dict

    def _flatten_dict_helper(
            self,
            kv_map: dict[str, any], 
            kv_list: list[tuple[str, any]],
            parent_key: str = "" 
            ):
        for k, v in kv_map.items():
            if len(parent_key) != 0:
                key_str = parent_key + '.' + str(k)
            else:
                key_str = str(k)
            if not isinstance(v, dict):
                kv_list.append((key_str, v))
            else:
                self._flatten_dict_helper(kv_map[k], kv_list, parent_key=key_str)

    def _parse_suffix(self, key_str: str) -> str:
        r_index = key_str.rfind('.')
        return key_str[r_index+1:]


class Table: 
    """Generating a table for printing out to a console or to be written to an 
    external file.


    Example
    -------

    < TODO Add example here. >

    Parameters
    ----------
    headings : tuple
        a tuple of strings denoting the sequential order of table headings 

    data_rows : list
        a list of tupled data rows
    """
    def __init__(
        self, 
        headings: tuple[str, ...], 
        data_rows: list[tuple[str, ...]]
        ):
        # headings and data_row tuple match check
        if len(headings) != len(data_rows[0]):
            raise ValueError("Headings count and data fields mismatch.")

        self._ncols = len(headings) # num_columns of the table
        data_rows.insert(0, headings) # combine headings and data
        self._data = data_rows # a list of tuples

    def render(self):
        """Prepare a table to be viewed onto the terminal."""
        out_table = self._make_table()
        print('\n'.join(out_table))
    
    def write_to_file(self, f_name: str, append: bool = False):
        """Render a table to be written to a file or appended to an existing
        file.

        Parameters
        ----------
        f_name : str
            Name of the output file.

        append : bool
            Append to file, when true. Overwrite contents of file, otherwise.
        """
        out_table = self._make_table()
        if append:
            with open(f_name, mode='a', encoding="utf-8") as fa:
                fa.write('\n')
                fa.write('\n'.join(out_table))
                print(f"table appended to {f_name}")
        else:
            with open(f_name, mode='w', encoding="utf-8") as fw:
                fw.write('\n'.join(out_table))
                print(f"table written to {f_name}")

    def _get_column_widths(self) -> list[int]:
        col_widths = [0 for i in range(self._ncols)]
        # check widths of data_rows
        for row_tup in self._data:
            for i, data in enumerate(row_tup):
                if len(str(data)) > col_widths[i]:
                    col_widths[i] = len(str(data))
        return col_widths

    def _format_row(self, row_dex: int, col_widths: list[int]) -> str:
        str_list = []
        str_list.append("| ")
        for i, data in enumerate(self._data[row_dex]):
            str_list.append(str(data).ljust(col_widths[i]))
            str_list.append(" | ") 
        out_str = "".join(str_list)
        out_str = out_str.strip()
        return out_str

    def _add_borders(self, tbl_str: list[str]):
        border_len = len(tbl_str[0]) 
        border = border_len * '-'
        tbl_str.insert(0, border)
        tbl_str.insert(2, border)
        tbl_str.insert(len(tbl_str), border)

    def _make_table(self) -> list[str]:
        tbl_strs = [] 
        col_widths = self._get_column_widths()
        for index, _ in enumerate(self._data):
            row_str = self._format_row(index, col_widths)
            tbl_strs.append(row_str)
        self._add_borders(tbl_strs)
        return tbl_strs
    
if __name__ == '__main__':
    # the code below is intended to test with a local file if an internet
    # connection cannot be found
    with open("response.json", mode='rb') as fr:
        ext = Extractor(fr)
        # New Psuedo-testing of Classes
    
    in_headings = ("Input", "Values")
    user_req = ext.extract_input()
    filter_out_parameters(user_req, "status", "url")
    tbl_in = Table(in_headings, user_req)
    tbl_in.write_to_file("out.txt")

    out_headings = ("Parameters", "Values", "Description")
    svs = ext.extract_svs()
    out_svs = append_output_descriptions(svs, DESCRIPTION_LABELS)
    tbl_out = Table(out_headings, out_svs)
    tbl_out.write_to_file("out.txt", True)

    meta_headings = ("Metadata", "Values")
    tbl_meta = Table(meta_headings, ext.extract_metadata())
    tbl_meta.write_to_file("out.txt", True)

