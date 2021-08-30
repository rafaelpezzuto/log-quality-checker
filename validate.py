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


def file_type(path):
    with open(path, 'rb') as fin:
        magic_code = magic.from_buffer(fin.read(2048), mime=True)
        return magic_code


def file_name_collection(path):
    for file_identifier in COLLECTION_FILE_NAME_IDENTIFIERS:
        if file_identifier in path:
            return file_identifier


def file_name_date(path):
    head, tail = os.path.split(path)
    for pattern in [PATTERN_Y_M_D, PATTERN_YMD]:
        match = re.search(pattern, tail)
        if match:
            return match.group()


def file_name_has_paperboy_format(path):
    head, tail = os.path.split(path)
    if re.match(PATTERN_PAPERBOY, tail):
        return True

def _is_ip_local_or_remote(ip: str):
    ipa = ip_address(ip)
    if ipa.is_global:
        return 'remote'
    return 'local'


def log_content(data):
    ips = {'local': 0, 'remote': 0}
    datetimes = {}
    invalid_lines = 0
    total_lines = 0

    for row in data:
        decoded_row = row.decode().strip()
        match = re.search(PATTERN_IP_DATETIME_OTHERS, decoded_row)
        if match and len(match.groups()) == 3:
            ip_value = match.group(1)            
            ip_type = _is_ip_local_or_remote(ip_value)
            ips[ip_type] += 1

            matched_datetime = match.group(2)
            year, month, day, hour = _extract_year_month_day_hour(matched_datetime)

            if (year, month, day, hour) not in datetimes:
                datetimes[(year, month, day, hour)] = 0
            datetimes[(year, month, day, hour)] += 1

        else:
            invalid_lines += 1
        total_lines += 1
    
    return {
        'ip': ips,
        'datetime': datetimes, 
        'invalid_lines': invalid_lines,
        'total_lines': total_lines
    }
def _print_header():
    print(app_msg)

    header = '\t'.join([
        'file_path',
        'file_date',
        'file_collection',
        'file_type',
        'file_name_is_paperboy',
        'valid_ip',
        'valid_date',
        'invalid_lines',
        'total_lines',
        'ip_local',
        'ip_remote'
    ])
    print(header)


def print_results(results, file_path):
    line = '\t'.join(
        [file_path] +
        [
            str(results['validate_path']['results'][x]) for x in [
                'file_name_date',
                'file_name_collection',
                'file_type',
                'file_name_has_paperboy_format']
        ] +
        [
            str(results['valid_ip']),
            str(results['valid_date'])
        ] +
        [
            str(results['validate_content']['results']['log_content'][z]) for z in [
                'invalid_lines',
                'total_lines']
        ] +
        [
            str(results['validate_content']['results']['log_content']['ip'][k]) for k in [
                'local',
                'remote'
            ]
        ]
    )
    print(line)
