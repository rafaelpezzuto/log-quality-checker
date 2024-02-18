COLLECTION_FILE_NAME_IDENTIFIERS = {
    '_scielo.ar',
    '_scielo.bo',
    '_scielo.1.br',
    '_scielo.2.br',
    '_scielo.cl',
    '_scielo.co',
    '_scielo.cr',
    '_scielo.cu',
    '_scielo.ec',
    '_scielo.mx',
    '_scielo.py',
    '_scielo.pe',
    '_scielo.pt',
    '_scielo.sp.1',
    '_scielo.sp.2',
    '_scielo.za',
    '_scielo.es',
    '_scielo.uy',
    '_scielo.ven',
    '_caribbean.scielo.org.1',
    '_caribbean.scielo.org.2',
    '_scielo.data',
    '_scielo.preprints',
    '_scielo.pepsic',
    '_scielo.revenf',
    '_scielo.ss',
}

PATTERN_Y_M_D = r'\d{4}-\d{2}-\d{2}'

PATTERN_YMD = r'\d{4}\d{2}\d{2}'

PATTERN_PAPERBOY = r'^\d{4}-\d{2}-\d{2}[\w|\.]*\.log\.gz$'

PATTERN_IP_DATETIME_OTHERS = r'^([\w|\W]* |)(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(.*)\] (\".*\")(.*)$'

PATTERN_IP_DATETIME_RESOURCE_STATUS_LENGHT_REFERRER_EQUIPMENT = r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(.*)\] \"GET (.*) .*\" (\d{3}) (\d*) \"(.*)\" \"(.*)\"$'
