import simplejson
from pathlib import Path
import copy
import csv
import os
import sys

# TODO: Use logger object instead of printing output to console.

# TODO: Better handling of deeply-nested JSON files.

def str2bool(str) -> bool:
    """Converts str to bool.

        When importing a JSON, bools are written as strings "true" and "false".
        This function converts them to real Booleans.

        Parameters
        ----------
        str : str
            Boolean value imported as string to convert to Boolean.

        Returns
        -------
        bool
            The Boolean value returned."""

    if str.lower()=='true':
        return True
    elif str.lower()=='false':
        return False


def import_data_from_disk(filepath, headers=None):
    """Routes import task to appropriate function depending on file type.

        Currently, only JSON and CSV are supported.
        The 'headers' parameter is only pertinent to importing CSVs.
        If the file is not found, or has an extension other than '.csv',
        or '.json', prints an error message and returns None.

        Parameters
        ----------
        filepath : str (or Path)
            Full path to the import file, including extension.
        headers : list, optional
            List containing the fieldnames (column names) for a CSV, by default
            None

        Returns
        -------
        list or dict or None
            If importing a JSON, returns a dictionary, if importing a CSV,
            returns a list."""

    data = None
    extension = Path(filepath).suffix.casefold()

    if Path(filepath).exists():
        if extension=='.json':
            data = import_json_from_disk(filepath)
        elif extension=='.csv':
            data = import_csv_from_disk(filepath, headers)
        else:
            print(
                "Data can only be imported from .json and .csv formats."
            )

    else:
        print(
            f"Path {filepath} could not be found."
        )

    return data


def import_json_from_disk(filepath):
    """Decodes a JSON file into a Python iterable.

        Opens a JSON file, parses it, and returns a Python iterable (dict or
        list). If the file contains invalid data, or has a filesize of 0, None
        is returned.

        Parameters
        ----------
        filepath : Path
            Full path to JSON file.

        Returns
        -------
        list or dict or None
            Dictionary created from imported JSON file."""

    data=None

    with open(filepath, 'r', encoding='utf-8', errors='strict') as f:
        if os.stat(filepath).st_size==0:
            print(
                f'{filepath} is empty.'
            )
        else:
            try:
                data = simplejson.load(f)
            except:
                print(
                    f'{filepath} contains invalid JSON data.'
                )

    return data


def import_csv_from_disk(filepath, headers=None):
    """Loads rows from a CSV file into a Python iterable.

        Loads rows from a  CSV file into a Python iterable.
        Returns a list if the CSV contains multiple rows. Each row of the CSV
        becomes a dictionary that is an element of that list. If the CSV
        contains a single row, then that function returns a dictionary encoding
        of that single row.

        If the file contains invalid data, or has a filesize of 0, None is
        returned.

        If 'headers' is 'None', the values in the first row of file f will be
        used as the headers. If a row has more fields than the headers, the
        remaining data will be ignored.
        If a non-blank row has fewer fields than headers, the missing values
        are filled-in with 'None'.

        Parameters
        ----------
        filepath : Path
            Full path to CSV file.
        headers : list or tuple, optional
            headers to use as dictionary keys for each record, by default None

        Returns
        -------
        list or dict or None
            List from imported CSV file. Each element of the list is a dict
            created from a single row of the CSV file."""

    data = None

    with open(filepath, 'r', encoding='utf-8', errors='strict',
              newline='') as f:
        if os.stat(filepath).st_size==0:
            print(
                f'{filepath} is empty.'
            )
        else:
            try:
                # Mostly useful for determining the delimiter used.
                dialect = csv.Sniffer().sniff(f.read(4096))
                f.seek(0)

                reader = csv.DictReader(
                    f, fieldnames=headers, dialect=dialect
                )
                data =list(reader)
            except:
                print(
                    f'{filepath} exists, but could not load it.'
                )

    # Convert String true and false values to Boolean.
    if data is not None:
        for record in data:
            for k,v in record.items():
                if not isinstance(v, list) and v.lower() in ['true', 'false']:
                    record[k] = str2bool(v)

    if len(data)==1:
        data = data[0]

    return data


def export_data_to_disk(filepath, data, delimiter=',', headers=None,
                        trim_long_strings=False):
    """Routes export task to appropriate function depending on file type.

        Currently, only JSON and CSV are supported.
        The 'headers', 'delimiter' and 'trim_long_strings' parameters are only
        pertinent to exporting CSVs.

        Parameters
        ----------
        filepath : str (or Path)
            Full path to the export file, including extension.
        data : dict or list
            The data to (process and) export.
        delimiter : str, optional
            Desired delimiter to use for CSV export, by default ','
        headers : list, optional
            List containing the fieldnames (column names) for the exported CSV,
            by default None
        trim_long_strings : bool, optional
            Trim strings that exceed Excel cell char limit. Only pertinent for
            CSV exports, by default False"""

    extension = Path(filepath).suffix.casefold()

    if extension=='.json':
        export_json_data_to_disk(filepath, data)
    elif extension=='.csv':
        export_csv_data_to_disk(filepath, data, delimiter, headers,
                                trim_long_strings)
    else:
        sys.exit(
                "Exports can only be made to .json and .csv formats."
            )


def export_json_data_to_disk(filepath, data):
    """Encodes a Python dict to JSON object and saves it to a json file on disk.

        Checks if path exists, else creates it and saves the JSON file to it.

        Parameters
        ----------
        filepath : Path
            Full path to JSON file.
        data : list or dict
            list or dict that will be converted to JSON."""

    # ensure_ascii=false works together with the encoding of 'utf-8' in the
    # open keyword. If problems happen with unicode characters, play around
    # with these parameters.
    # See this also: https://bit.ly/3qkbRwe
    # Errors in open is an optional string that specifies how encoding and
    # decoding errors are to be handled—this cannot be used in binary mode. I
    # have currently set it to 'strict' to raise ValueError exceptions
    # whenever there is an encoding error, so I can spot problems. Another
    # option is 'replace', which will cause a replacement marker (such as '?')
    # to be inserted where there is malformed data.

    if data is None:
        print(
            "Nothing to export."
        )

    else:
        dir = Path(filepath).parents[0]
        if not dir.exists():
            Path(dir).mkdir(parents=True, exist_ok=False)

        with open(filepath, 'w', encoding='utf-8', errors='strict') as f:
            simplejson.dump(data, f, ensure_ascii=False, indent=4 * ' ')


def enforce_excel_cell_string_limit(long_string, limit):
    """
        Trims a long string. This function aims to address a limitation of CSV
        files, where very long strings which exceed the char cell limit of Excel
        cause weird artifacts to happen when saving to CSV.
    """
    trimmed_string = ''
    if limit <= 3:
        limit = 4

    if len(long_string) > limit:
        trimmed_string = (long_string[:(limit-3)] + '...')

        return trimmed_string
    else:
        return long_string


def export_csv_data_to_disk(filepath, data, delimiter=',',
    headers=None, trim_long_strings=None,):
    """Exports a collection of dictionaries, or a single dictionary to a CSV
        file on disk.

        The function is also able to export to CSV not only collections of
        dicts, but also dicts of dicts or a simple dict. To do so, it employs a
        check on the incoming collection and transforms dicts to collections if
        needed.
        It can handle dicts that look like below:
        - A nested dictionary like this:
        {
            key: {
                    subkey1: value1,
                    subkey2: value2
            },
            {
                    subkey1: value3,
                    subkey2: value4
            }
        }
        In this case, The headers will be the subkeys and each row will contain
        the values of each nested dictionary.
        - Simple dictionary like this:
        {
            key1: value1,
            key2: value2
        }
        In this case, the first row's key and value will become the headers and
        every other [key, val] pair will be an element in the collection that
        will be exported.

        Another thing this function does is to trim very long strings that would
        not fit in a CSV cell. Such behaviour mutates the passed dictionary, so
        we need to use copy.deepcopy() on it first, before editing it and saving
        it to disk.

        Parameters
        ----------
        filepath : Path
            Full path to JSON file.
        data : list or dict
            list or dict that will be converted to CSV.
        delimiter : str, optional
            Desired delimiter to use for CSV export, by default ','
        headers : list, optional
            List containing the fieldnames (column names) for the exported CSV,
            by default None, by default None
        trim_long_strings : bool, optional
            If True, will trim strings that exceed Excel cell char limit,
            by default None"""


    # Avoid the case of an empty dictionary, this will not work.
    if data is None or not data:
        print(
            "Nothing to export."
        )
        return

    to_export_data = copy.deepcopy(data)

    if headers is None:
        if isinstance(to_export_data, dict):
            # If we have a nested dictionary:
            if isinstance(list(to_export_data.values())[0], dict):
                for k,v in to_export_data.items():
                    # Use keys in first nested dict to create the headers.
                    headers = list(v.keys())
                    # then turn the dict to a collection
                    to_export_data = list(to_export_data.values())
                    break
            else:
                # Single dictionary item. Code below produces vertical table.
                count = 0
                temp_data = []
                for k,v in to_export_data.items():
                    if count==0:
                        # Use first [key, val] pair as headers.
                        headers = [k, v]
                        count += 1
                    else:
                        # Add subsequent [key, val] pairs to the collection.
                        temp_data.append({headers[0]:k, headers[1]:v})
                to_export_data = temp_data

        elif isinstance(to_export_data, list):
            headers = [key for key in data[0]]

    # Export the collection.
    with open(filepath, 'w', encoding='utf-8', errors='replace',
        newline='') as f:
        out_writer = csv.DictWriter(f, fieldnames=headers, restval='',
            extrasaction='ignore', delimiter=delimiter)
        out_writer.writeheader()
        for item in to_export_data:
            if trim_long_strings:
                for key, val in item.items():
                # CSV limitation, must trim very long strings.
                    item[key] = enforce_excel_cell_string_limit(str(val), 32750)
            out_writer.writerow(item)


def convert_file(import_path, export_path, headers, delimiter,
                 trim_long_string):

    imported_data = import_data_from_disk(
        filepath=import_path,
        headers=headers
    )

    export_data_to_disk(
        filepath=export_path,
        data=imported_data,
        headers=headers,
        delimiter=delimiter,
        trim_long_strings=trim_long_string
    )


def main():
    # SET THESE
    # import_path: full path to file to import, including file extension.
    import_path = "D:/item.json"
    # export_path: full path to file to export, including file extension.
    export_path = "D:/new_dir/item.csv"

    # ADDITIONAL PARAMS, TYPICALLY NOT NEEDED
    # headers:
    # WHEN THE IMPORTED FILE IS A CSV, If 'headers' is 'None', the
    # values in the first row will be used as the headers.
    # Otherwise, if the first row of the CSV contains data (i.e., there are no
    # headers in the CSV file), specify them as a list, like this:
    # ['name', 'colour', 'code'] etc.
    # WHEN THE EXPORTED FILE IS A CSV, 'headers' determines the names of the
    # fields that will be written in the CSV's first row. If left to 'None'
    # these will be taken from the keys of the JSON file.

    # If a row has more fields than the headers, the remaining data will be
    # ignored. If a non-blank row has fewer fields than headers, the missing
    # values are filled-in with 'None'.
    # By default, 'None'
    headers=None

    # deilimiter: The delimiter to separate values when exporting a CSV, by
    # default ','.
    delimiter = ','

    # Trim strings that exceed Excel cell char limit. Only pertinent for CSV
    # CSV exports, by default False.
    trim_long_string=False


    convert_file(
        import_path=import_path,
        export_path=export_path,
        headers=headers,
        delimiter=delimiter,
        trim_long_string=trim_long_string
    )


if __name__ == '__main__':
    main()