from argparse import ArgumentParser
from datetime import datetime, timedelta
from gzip import GzipFile
from ipaddress import ip_address
from time import time
from values import COLLECTION_FILE_NAME_IDENTIFIERS

import magic
import os
import re


app_msg = '''
SciELO Log Validator 0.1
    
This script is responsible for validating log usage records obtained from the SciELO Network Apache Servers.
A validation is composed of two main aspects as follows:
    1) Validation with regard to the file name
    2) Validation with regard to the file content
'''

