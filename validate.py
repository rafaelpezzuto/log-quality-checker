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


def _get_execution_mode(path: str):
    if os.path.exists(path):
        if os.path.isfile(path):
            return 'validate-file'
    else:
        raise FileNotFoundError()
    return 'validate-directory'


def _get_validation_functions(validation):
    validation_list = []

    if 'path' in validation:
        validation_list.append(validate_path)

    if 'content' in validation:
        validation_list.append(validate_content)

    return validation_list


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


def _open_file(path):
    file_mime = file_type(path)

    if file_mime == 'application/gzip':
        return GzipFile(path, 'rb')

    elif file_mime == 'application/text':
        return open(path, 'r')


def _is_ip_local_or_remote(ip: str):
    ipa = ip_address(ip)
    if ipa.is_global:
        return 'remote'
    return 'local'


def _extract_year_month_day_hour(log_date: str):
    dt = datetime.strptime(log_date, '%d/%b/%Y:%H:%M:%S %z')
    return dt.year, dt.month, dt.day, dt.hour


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


def _evaluate_ip_results(ip):
    if ip['remote'] < ip['local']:
        return False
    return True


def _evaluate_ymdh_results(ymdh: dict, file_date: str):
    file_date_object = datetime.strptime(file_date, '%Y-%m-%d')   
    min_date_object, max_date_object = datetime(*min(ymdh)), datetime(*max(ymdh))

    # há dados de dias diferentes no conteúdo do arquivo
    if (min_date_object.year != max_date_object.year) or \
    (min_date_object.month != min_date_object.month) or \
    (min_date_object.day != min_date_object.day):
        return False

    # a menor data registrada é muito anterior à data indicada no nome do arquivo
    if min_date_object < file_date_object - timedelta(days=2):
        return False

    # a maior data registrada é muito anterior à data indicada no nome do arquivo
    if max_date_object < file_date_object - timedelta(days=2):
        return False

    # há datas muito posteriores à data indicada no nome do arquivo
    if min_date_object > file_date_object + timedelta(days=2):
        return False

    # há datas muito posteriores à data indicada no nome do arquivo
    if max_date_object > file_date_object + timedelta(days=2):
        return False
    
    return True


def validate_path(path):
    results = {}

    for func in [
        file_name_date,
        file_name_collection,
        file_name_has_paperboy_format,
        file_type
    ]:
        results[func.__name__] = func(path)

    return results


def validate_content(path):
    results = {}

    file_data = _open_file(path)

    for func in [
        log_content,
    ]:
        results[func.__name__] = func(file_data)

    return results


def run_validations(path: str, validations: list):
    validation_results = {}

    for val in validations:
        v_results = val(path)
        validation_results[val.__name__] = {'results': v_results}

    validation_results.update(evaluate_result_validations(validation_results))
    
    return validation_results


def evaluate_result_validations(results):
    evaluation_ip = _evaluate_ip_results(results['validate_content']['results']['log_content']['ip'])
    evaluation_date = _evaluate_ymdh_results(
        results['validate_content']['results']['log_content']['datetime'],
        results['validate_path']['results']['file_name_date']
    )

    return {
        'valid_ip': evaluation_ip, 
        'valid_date': evaluation_date
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
