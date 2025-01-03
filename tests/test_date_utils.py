import unittest

from scielo_log_validator import date_utils


class TestDateUtils(unittest.TestCase):

    def setUp(self):
        self.log_directory = 'tests/fixtures/logs/scielo.wi/'
        self.log_file = 'tests/fixtures/logs/scielo.wi/2024-02-20_caribbean.scielo.org.1.log.gz'
        self.log_file_invalid_name = 'tests/fixtures/logs/scielo.wi/invalid_file_name.log.gz'

    def test_clean_date_is_pattern_yyyy_mm_dd(self):
        date_str = '2024-02-20'
        date_str_cleaned = date_utils.clean_date(date_str)
        self.assertEqual(date_str_cleaned, '2024-02-20')

    def test_clean_date_is_pattern_yyyymmdd(self):
        date_str = '2024-02-20'
        date_str_cleaned = date_utils.clean_date(date_str)
        self.assertEqual(date_str_cleaned, '2024-02-20')

    def test_clean_date_raises_exception(self):
        with self.assertRaises(ValueError):
            date_utils.clean_date('invalid_date')
