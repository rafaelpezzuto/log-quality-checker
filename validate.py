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

PATTERN_Y_M_D = r'\d{4}-\d{2}-\d{2}'
PATTERN_YMD = r'\d{4}\d{2}\d{2}'
PATTERN_PAPERBOY = r'^\d{4}-\d{2}-\d{2}[\w|\.]*\.log\.gz$'
PATTERN_IP_DATETIME_OTHERS = r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(.*)\] \"(.*)\"$'
PATTERN_IP_DATETIME_RESOUCE_STATUS_LENGHT_REFERRER_EQUIPMENT = r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(.*)\] \"GET (.*) .*\" (\d{3}) (\d*) \"(.*)\" \"(.*)\"$'


