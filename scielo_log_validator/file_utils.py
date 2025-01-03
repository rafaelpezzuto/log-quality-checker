from gzip import GzipFile

import bz2
import magic
import os
import re

from scielo_log_validator import exceptions, values, date_utils


# Define the default handlers for different MIME types
DEFAULT_MIME_HANDLERS = {
    'application/gzip': GzipFile,
    'application/x-gzip': GzipFile,
    'application/x-bzip2': bz2.open,
    'application/text': open,
    'text/plain': open,
    'application/x-empty': None
}


def open_file(path, mime_handlers=DEFAULT_MIME_HANDLERS):
    """
    Opens a file and returns its content based on its MIME type.

    Args:
        path (str): The path to the file to be opened.
        mime_handlers (dict, optional): A dictionary mapping MIME types to handler functions. 
                                        Defaults to DEFAULT_MIME_HANDLERS.

    Raises:
        exceptions.InvalidLogFileMimeError: If the file's MIME type is not supported.
        exceptions.LogFileIsEmptyError: If the file is empty.

    Returns:
        object: The content of the file as processed by the appropriate handler function.
    """
    file_mime = extract_mime_from_path(path)

    if file_mime not in mime_handlers:
        raise exceptions.InvalidLogFileMimeError('File %s is invalid' % path)

    if file_mime == 'application/x-empty':
        raise exceptions.LogFileIsEmptyError('File %s is empty' % path)

    return mime_handlers[file_mime](path, 'rb' if 'application' in file_mime else 'r')


def extract_mime_from_path(path, buffer_size=2048):
    """
    Determines the MIME type of a file based on its content.

    Args:
        path (str): The file path to read and determine the MIME type.
        buffer_size (int, optional): The number of bytes to read from the file for MIME type detection. Defaults to 2048.

    Returns:
        str: The MIME type of the file.

    Raises:
        FileNotFoundError: If the file at the given path does not exist.
        IOError: If there is an error reading the file.
    """
    mime = magic.Magic(mime=True)
    with open(path, 'rb') as fin:
        magic_code = mime.from_buffer(fin.read(buffer_size))
        return magic_code


def extract_collection_from_path(path, collection_identifiers=None):
    """
    Extracts the collection identifier from the given file path.

    This function iterates over a dictionary of collection file name identifiers
    and checks if any of these identifiers are present in the provided file path.
    If a match is found, the corresponding collection ID is returned.

    Args:
        path (str): The file path to be checked for collection identifiers.
        collection_identifiers (dict, optional): A dictionary where keys are file name identifiers 
                                                 and values are collection IDs. 
                                                 If not provided, defaults to values.COLLECTION_FILE_NAME_IDENTIFIERS.

    Returns:
        str: The collection identifier if found in the file path, otherwise None.
    """
    if collection_identifiers is None:
        collection_identifiers = values.COLLECTION_FILE_NAME_IDENTIFIERS

    for file_identifier, collection_id in collection_identifiers.items():
        if file_identifier in path:
            return collection_id
    return None

