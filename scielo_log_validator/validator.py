# -*- coding: UTF-8 -*-
from argparse import ArgumentParser
from datetime import datetime, timedelta
from gzip import GzipFile
from ipaddress import ip_address
from scielo_log_validator import exceptions, values

import magic
import os
import operator
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
    for file_identifier in values.COLLECTION_FILE_NAME_IDENTIFIERS:
        if file_identifier in path:
            return file_identifier


def _get_date_from_file_name(path):
    head, tail = os.path.split(path)
    for pattern in [values.PATTERN_Y_M_D, values.PATTERN_YMD]:
        match = re.search(pattern, tail)
        if match:
            return match.group()


def _has_file_name_paperboy_format(path):
    head, tail = os.path.split(path)
    if re.match(values.PATTERN_PAPERBOY, tail):
        return True


def _open_file(path):
    file_mime = _get_mimetype_from_file(path)

    if file_mime in ('application/gzip', 'application/x-gzip'):
        return GzipFile(path, 'rb')
    elif file_mime in ('application/text', 'text/plain'):
        return open(path, 'r')
    elif file_mime in ('application/x-empty'):
        raise exceptions.LogFileIsEmptyError('Arquivo %s está vazio' % path)
    else:
        raise exceptions.InvalidLogFileMimeError('Arquivo %s é inválido' % path)


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


def _get_content_summary(path, total_lines, sample_lines):
    ips = {'local': 0, 'remote': 0}
    datetimes = {}
    invalid_lines = 0

    eval_lines = set(range(0, total_lines, int(total_lines/sample_lines)))
    line_counter = 0

    with _open_file(path) as data:
        for line in data:
            decoded_line = line.decode().strip() if isinstance(line, bytes) else line.strip()
            line_counter += 1

            if line_counter in eval_lines:
                match = re.search(values.PATTERN_IP_DATETIME_OTHERS, decoded_line)

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

    return {
        'ips': ips,
        'datetimes': datetimes,
        'invalid_lines': invalid_lines,
        'total_lines': total_lines
    }


def _count_lines(path):
    try:
        with _open_file(path) as fin:
            return sum(1 for line in fin)
    except EOFError:
        raise exceptions.TruncatedLogFileError('Arquivo %s está truncado' % path)
    except exceptions.InvalidLogFileMimeError:
        raise exceptions.InvalidLogFileMimeError('Arquivo %s é inválido' % path)
    except exceptions.LogFileIsEmptyError:
        raise exceptions.LogFileIsEmptyError('Arquivo %s está vazio' % path)


def _analyse_ips_from_content(results):
    remote_ips = results.get('content', {}).get('summary', {}).get('ips', {}).get('remote', 0)
    local_ips = results.get('content', {}).get('summary', {}).get('ips', {}).get('local', 0)
    total_lines = results.get('content', {}).get('summary', {}).get('total_lines', 0)

    # se não houver linhas com IP detectado ou a validação não foi executada
    if (remote_ips == 0 and local_ips == 0) or total_lines == 0:
        return False

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


def _get_min_max_dates(dates):
    return datetime(*min(dates)), datetime(*max(dates))


def _date_is_much_lower(date_object, file_date_object, days_delta):
    if date_object < file_date_object - timedelta(days=days_delta):
        return True


def _date_is_much_greater(date_object, file_object_date, days_delta):
    if date_object > file_object_date + timedelta(days=days_delta):
        return True


def _analyse_dates(results, days_delta=2):
    file_path_date = results.get('path', {}).get('date', '')
    file_content_dates = results.get('content', {}).get('summary', {}).get('datetimes', {})
    probably_date = results.get('probably_date')

    # se não houver contéudo ou a validação não for executada
    if not file_path_date or not file_content_dates:
        return False

    # o arquivo é inválido se não for possível obter uma data a partir do nome do arquivo
    try:
        file_date_object = datetime.strptime(file_path_date, '%Y-%m-%d')
    except ValueError:
        return False

    # se a data provável do arquivo é muito menor do que a data indicada no nome do arquivo
    if _date_is_much_lower(probably_date, file_date_object, days_delta):
        return False

    # se a data provável do arquivo é muito maior do que a data indicada no nome do arquivo
    if _date_is_much_greater(probably_date, file_date_object, days_delta):
        return False

    return True


def _validate_path(path, sample_size=0.1):
    results = {}

    for func_impl, func_name in [
        (_get_date_from_file_name, 'date'),
        (_get_collection_from_file_name, 'collection'),
        (_has_file_name_paperboy_format, 'paperboy'),
        (_get_mimetype_from_file, 'mimetype')
    ]:
        results[func_name] = func_impl(path)

    return results


def _validate_content(path, sample_size=0.1):
    try:
        total_lines = _count_lines(path)
        sample_lines = int(total_lines * sample_size)   
        return {'summary': _get_content_summary(path, total_lines, sample_lines)}
    except exceptions.TruncatedLogFileError:
        return {'summary': {'total_lines': {'error': 'Arquivo está truncado'},}}


def validate(path, validations, sample_size):
    results = {}

    for val in validations:
        val_results = val(path, sample_size)
        results[val.__name__.replace('_validate_', '')] = val_results

    _compute_results(results)

    return results


def _get_date_frequencies(results):
    file_content_dates = results.get('content', {}).get('summary', {}).get('datetimes', {})

    ymd_to_freq = {}
    for k, frequency in file_content_dates.items():
        year, month, day, hour = k
        if (year, month, day) not in ymd_to_freq:
            ymd_to_freq[(year, month, day)] = 0
        ymd_to_freq[(year, month, day)] += frequency

    return ymd_to_freq


def _compute_probably_date(results):
    ymd_to_freq = _get_date_frequencies(results)

    try:
        ymd, freq = sorted(ymd_to_freq.items(), key=operator.itemgetter(1)).pop()
        y, m, d = ymd
        return datetime(y, m, d)
    except ValueError:
        return {'error': 'Não foi possível determinar uma data provável'}
    except IndexError:
        return {'error': 'Dicionário de datas está vazio'}


def _compute_results(results):
    # verifica se conjunto de ips é válido (há poucos ips locais)
    results['is_valid'] = {'ips': _analyse_ips_from_content(results)}

    # computa data provável dos dados
    results['probably_date'] = _compute_probably_date(results)

    # analisa se data provável é muito diferente da data indicada no nome do arquivo
    results['is_valid'].update({'dates': _analyse_dates(results)})

    # atribui valor da validação resultante
    results['is_valid'].update(
        {
            'all': results['is_valid']['ips'] and results['is_valid']['dates']
        }
    )


def main():
    parser = ArgumentParser()
    parser.add_argument('-p', '--path', help='arquivo ou diretório a ser verificado', required=True)
    parser.add_argument('-s', '--sample_size', help='tamanho da amostra a ser verificada', default=0.1, type=float)
    parser.add_argument('--check_file_name_only', default=False, help='indica para validar apenas o nome e o caminho do(s) arquivo(s)', action='store_true')
    params = parser.parse_args()

    execution_mode = _get_execution_mode(params.path)
    validations = _get_validation_functions(params.check_file_name_only)

    print(app_msg)
    from pprint import pprint

    if execution_mode == 'validate-file':
        results = validate(params.path, validations, params.sample_size)
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
