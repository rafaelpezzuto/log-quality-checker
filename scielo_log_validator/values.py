COLLECTION_FILE_NAME_IDENTIFIERS = {
    '_scielo.ar': 'arg',
    '_scielo.bo': 'bol',
    '_scielo.1.br': 'scl',
    '_scielo.2.br': 'scl',
    '_scielo.cl': 'chl',
    '_scielo.co': 'col',
    '_scielo.cr': 'cru',
    '_scielo.cu': 'cub',
    '_scielo.ec': 'ecu',
    '_scielo.mx': 'mex',
    '_scielo.py': 'pry',
    '_scielo.pe': 'per',
    '_scielo.pt': 'prt',
    '_scielo.sp.1': 'ssp',
    '_scielo.sp.2': 'ssp',
    '_scielo.za': 'sza',
    '_scielo.es': 'esp',
    '_scielo.uy': 'ury',
    '_scielo.ven': 'ven',
    '_caribbean.scielo.org.1': 'wid',
    '_caribbean.scielo.org.2': 'wid',
    '_scielo.data': 'dat',
    '_scielo.preprints': 'pre',
    '_scielo.pepsic': 'psi',
    '_scielo.revenf': 'rev',
    '_scielo.ss': 'sss',
}

PATTERN_Y_M_D = r'\d{4}-\d{2}-\d{2}'

PATTERN_YMD = r'\d{4}\d{2}\d{2}'

PATTERN_PAPERBOY = r'^\d{4}-\d{2}-\d{2}[\w|\.]*\.log\.gz$'

PATTERN_IP_DATETIME_OTHERS = r'^([\w|\W]* |)(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(.*)\] (\".*\")(.*)$'

PATTERN_IP_DATETIME_RESOURCE_STATUS_LENGHT_REFERRER_EQUIPMENT = r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(.*)\] \"GET (.*) .*\" (\d{3}) (\d*) \"(.*)\" \"(.*)\"$'
