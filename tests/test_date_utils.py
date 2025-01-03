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

    def test_extract_min_max_dates(self):
        dates = [(2021, 5, 17), (2020, 12, 25), (2022, 1, 1)]
        min_date, max_date = date_utils.extract_min_max_dates(dates)
        self.assertEqual(min_date, date_utils.datetime(2020, 12, 25))
        self.assertEqual(max_date, date_utils.datetime(2022, 1, 1))

    def test_date_is_significantly_earlier(self):
        date_object = date_utils.datetime(2020, 1, 1)
        reference_date = date_utils.datetime(2020, 1, 10)
        self.assertTrue(date_utils.date_is_significantly_earlier(date_object, reference_date, 5))

    def test_date_is_significantly_later(self):
        date_object = date_utils.datetime(2020, 1, 20)
        reference_date = date_utils.datetime(2020, 1, 10)
        self.assertTrue(date_utils.date_is_significantly_later(date_object, reference_date, 5))
