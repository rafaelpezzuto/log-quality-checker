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

