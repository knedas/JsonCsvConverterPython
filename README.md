# JsonCsvConverterPython
Work in progress on a Python script to convert CSV to JSON and the other way around.
The difficulty (and challenge) in this conversion lies in the different structures of those two formats: JSON is hierarchical, whereas CSV is flat.
The more nested a JSON is, the harder it becomes to produce a desirable output for the needs of each user.
Currently, the tool handles a few common cases, but additional work is needed to provide more control to the user on how to flatten the JSON hierarchies.

## Usage
- Skip to the end of the source in main() function and enter the parameters as needed:
    - import_path: full path to file to import, including file extension. Example: 'D:/folder/file.json'
    - export_path: full path to file to export, including file extension. Example: 'D:/folder/file.csv'
- There are additional parameters with explanation in source, but the defaults should do for most cases.
- Run with Python3.

## Requirements
- Python interpreter 3.8.5 and above

## Limitations
- May not work as intended for heavily-nested JSONs.
