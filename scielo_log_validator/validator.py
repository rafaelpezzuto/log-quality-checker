# -*- coding: UTF-8 -*-
from argparse import ArgumentParser
from datetime import datetime, timedelta
from gzip import GzipFile
from ipaddress import ip_address
from scielo_log_validator.values import (
    COLLECTION_FILE_NAME_IDENTIFIERS,
    PATTERN_IP_DATETIME_OTHERS,
    PATTERN_PAPERBOY,
    PATTERN_Y_M_D,
    PATTERN_YMD
)

import magic
import os
import re


MIN_ACCEPTABLE_PERCENT_OF_REMOTE_IPS = float(os.environ.get('MIN_ACCEPTABLE_PERCENT_OF_REMOTE_IPS', '10'))


app_msg = '''
SciELO Log Validator
    
This script is responsible for validating log usage records obtained from the SciELO Network Apache Servers.
A validation is composed of two main aspects as follows:
    1) Validation with regard to the file name
    2) Validation with regard to the file content
'''


def _get_execution_mode(path):
    if os.path.exists(path):
        if os.path.isfile(path):
            return 'validate-file'
    else:
        raise FileNotFoundError()
    return 'validate-directory'


def _get_validation_functions(check_file_name_only):
    if check_file_name_only:
        return [_validate_path]
    return [_validate_path, _validate_content]


def _get_mimetype_from_file(path):
    with open(path, 'rb') as fin:
        magic_code = magic.from_buffer(fin.read(2048), mime=True)
        return magic_code


def _get_collection_from_file_name(path):
    for file_identifier in COLLECTION_FILE_NAME_IDENTIFIERS:
        if file_identifier in path:
            return file_identifier


def _get_date_from_file_name(path):
    head, tail = os.path.split(path)
    for pattern in [PATTERN_Y_M_D, PATTERN_YMD]:
        match = re.search(pattern, tail)
        if match:
            return match.group()


def _has_file_name_paperboy_format(path):
    head, tail = os.path.split(path)
    if re.match(PATTERN_PAPERBOY, tail):
        return True


def _open_file(path):
    file_mime = _get_mimetype_from_file(path)

    if file_mime == 'application/gzip':
        return GzipFile(path, 'rb')

    elif file_mime == 'application/text':
        return open(path, 'r')


def _is_ip_local_or_remote(ip):
    ipa = ip_address(ip)
    if ipa.is_global:
        return 'remote'
    return 'local'


def _extract_year_month_day_hour(log_date):
    # descarta offset
    log_date = log_date.split(' ')[0]
    dt = datetime.strptime(log_date, '%d/%b/%Y:%H:%M:%S')
    return dt.year, dt.month, dt.day, dt.hour


def _get_content_summary(data):
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
        'ips': ips,
        'datetimes': datetimes,
        'invalid_lines': invalid_lines,
        'total_lines': total_lines
    }


def _count_lines(path):
    file_data = _open_file(path)
    total_lines = sum(1 for line in file_data)
    file_data.close()
    return total_lines


def _analyse_ips_from_content(results):
    remote_ips = results.get('content', {}).get('summary', {}).get('ips', {}).get('remote', 0)
    local_ips = results.get('content', {}).get('summary', {}).get('ips', {}).get('local', 0)
    total_lines = results.get('content', {}).get('summary', {}).get('total_lines', 0)

    # se não houver linhas com IP detectado ou a validação não foi executada
    if (remote_ips == 0 and local_ips == 0) or total_lines == 0:
        return None

    # computa percentual de IPs remotos em relação ao total de linhas
    percent_remote_ips = float(remote_ips)/float(total_lines) * 100

    # computa percentual de IPs locais em relação ao total de linhas
    percent_local_ips = float(local_ips)/float(total_lines) * 100

    # o arquivo é válido se houver maior percentual de IPs remotos
    if percent_remote_ips > percent_local_ips:
        return True

    # o arquivo é válido se houver um percentual mínimo de IPs remotos
    if percent_remote_ips > MIN_ACCEPTABLE_PERCENT_OF_REMOTE_IPS:
        return True

    return False


def _analyse_dates(results):
    file_path_date = results.get('path', {}).get('date', '')
    file_content_dates = results.get('content', {}).get('summary', {}).get('datetimes', {})

    # se não houver contéudo ou a validação não for executada
    if not file_path_date or not file_content_dates:
        return None

    # o arquivo é inválido se não for possível obter uma data a partir do nome do arquivo
    try:
        file_date_object = datetime.strptime(file_path_date, '%Y-%m-%d')
    except ValueError:
        return False

    min_date_object, max_date_object = datetime(*min(file_content_dates)), datetime(*max(file_content_dates))

    # se há dados de dias diferentes no conteúdo do arquivo
    if (min_date_object.year != max_date_object.year) or \
    (min_date_object.month != min_date_object.month) or \
    (min_date_object.day != min_date_object.day):
        return False

    # se a menor data registrada é muito anterior à data indicada no nome do arquivo
    if min_date_object < file_date_object - timedelta(days=2):
        return False

    # se a maior data registrada é muito anterior à data indicada no nome do arquivo
    if max_date_object < file_date_object - timedelta(days=2):
        return False

    # se há datas muito posteriores à data indicada no nome do arquivo
    if min_date_object > file_date_object + timedelta(days=2):
        return False

    # se há datas muito posteriores à data indicada no nome do arquivo
    if max_date_object > file_date_object + timedelta(days=2):
        return False
    
    return True


def _validate_path(path):
    results = {}

    for func in [
        (_get_date_from_file_name, 'date'),
        (_get_collection_from_file_name, 'collection'),
        (_has_file_name_paperboy_format, 'paperboy'),
        (_get_mimetype_from_file, 'mimetype')
    ]:
        results[func[1]] = func[0](path)

    return results


def _validate_content(path):
    results = {}

    file_data = _open_file(path)

    for func in [
        (_get_content_summary, 'summary'),
    ]:
        results[func[1]] = func[0](file_data)

    return results


def validate(path, validations):
    results = {}

    for val in validations:
        val_results = val(path)
        results[val.__name__.replace('_validate_', '')] = val_results

    _compute_results(results)
    
    return results


def _compute_probably_date(results):
    file_content_dates = results.get('content', {}).get('summary', {}).get('datetimes', {})

    ymd_to_freq = {}
    for k, frequency in file_content_dates.items():
        year, month, day, hour = k
        if (year, month, day) not in ymd_to_freq:
            ymd_to_freq[(year, month, day)] = 0
        ymd_to_freq[(year, month, day)] += frequency

    ymd, freq = sorted(ymd_to_freq.items(), key=operator.itemgetter(1)).pop()
    y, m, d = ymd

    try:
        return datetime(y, m, d)
    except ValueError:
        print('It was not possible to determine a probably date')


def _compute_results(results):
    results['is_valid'] = {'ips': _analyse_ips_from_content(results)}
    results['is_valid'].update({'dates': _analyse_dates(results)})
    results['is_valid'].update({'all':
        results['is_valid']['ips'] and results['is_valid']['dates']
    })


def main():
    parser = ArgumentParser()
    parser.add_argument('-p', '--path', help='arquivo ou diretório a ser verificado', required=True)
    parser.add_argument('--check_file_name_only', default=False, help='indica para validar apenas o nome e o caminho do(s) arquivo(s)', action='store_true')
    params = parser.parse_args()

    execution_mode = _get_execution_mode(params.path)
    validations = _get_validation_functions(params.check_file_name_only)

    print(app_msg)
    from pprint import pprint
    
    if execution_mode == 'validate-file':
        results = validate(params.path, validations)
        print(params.path)
        pprint(results)

    elif execution_mode == 'validate-directory':
        for root, dirs, files in os.walk(params.path):
            for file in files:
                file_path = os.path.join(root, file)
                results = validate(file_path, validations)
                print(params.path)
                pprint(results)


if __name__ == '__main__':
    main()
