import datetime
import unittest

from scielo_log_validator import validator


class TestValidator(unittest.TestCase):

    def setUp(self):
        self.log_directory = 'tests/fixtures/logs/scielo.wi/'
        self.log_file = 'tests/fixtures/logs/scielo.wi/2024-02-20_caribbean.scielo.org.1.log.gz'
        self.log_file_invalid_name = 'tests/fixtures/logs/scielo.wi/invalid_file_name.log.gz'

    def test_get_execution_mode_is_file(self):
        exec_mode = validator.get_execution_mode(self.log_file)
        self.assertEqual(exec_mode, 'validate-file')

    def test_get_execution_mode_is_directory(self):
        exec_mode = validator.get_execution_mode(self.log_directory)
        self.assertEqual(exec_mode, 'validate-directory')

    def test_get_execution_mode_is_invalid(self):
        path_to_non_existing_file = '/path/to/nothing'
        with self.assertRaises(FileNotFoundError):
            validator.get_execution_mode(path_to_non_existing_file)

    def test_extract_year_month_day_hour(self):
        timestamp = '12/Mar/2023:14:22:30 +0000'
        y, m, d, h = validator.get_year_month_day_hour_from_date_str(timestamp)
        self.assertEqual((y, m, d, h), (2023, 3, 12, 14))

    def test_count_lines(self):
        obtained_nlines = validator.get_total_lines(self.log_file)
        expected_nlines = 7160
        self.assertEqual(obtained_nlines, expected_nlines)

    def test_validate_ip_distribution_is_true(self):
        results = {
            'content': {
                'summary': {
                    'ips': {'remote': 5, 'local': 3},
                    'total_lines': 10
                }
            }
        }
        self.assertTrue(validator.validate_ip_distribution(results))

    def test_validate_ip_distribution_is_false(self):
        results = {
            'content': {
                'summary': {
                    'ips': {'remote': 0, 'local': 3},
                    'total_lines': 8
                }
            }
        }
        self.assertFalse(validator.validate_ip_distribution(results))

    def test_validate_ip_distribution_is_false_9_percent_remote(self):
        results = {
            'content': {
                'summary': {
                    'ips': {'remote': 9, 'local': 91},
                    'total_lines': 100
                }
            }
        }
        self.assertFalse(validator.validate_ip_distribution(results))

    def test_validate_ip_distribution_is_true_11_percent_remote(self):
        results = {
            'content': {
                'summary': {
                    'ips': {'remote': 11, 'local': 89},
                    'total_lines': 100
                }
            }
        }
        self.assertTrue(validator.validate_ip_distribution(results))

    def test_validate_date_consistency_is_true(self):
        results = {
            'path': {'date': '2023-01-01'},
            'content': {'summary': {'datetimes': {(2023, 1, 1, 0): 1}}},
            'probably_date': validator.datetime(2023, 1, 1)
        }
        self.assertTrue(validator.validate_date_consistency(results))

    def test_validate_date_consistency_is_false(self):
        results = {
            'path': {'date': '2023-01-01'},
            'content': {'summary': {'datetimes': {(2023, 10, 30, 0): 1}}},
            'probably_date': validator.datetime(2023, 10, 30)
        }
        self.assertFalse(validator.validate_date_consistency(results))

    def test_validate_path(self):
        path = self.log_file_invalid_name
        results = validator.validate_path_name(path)
        self.assertIn('date', results)
        self.assertIn('collection', results)
        self.assertIn('paperboy', results)
        self.assertIn('mimetype', results)
        self.assertIn('extension', results)

    def test_validate_content(self):
        results = validator.validate_content(self.log_file)
        self.assertIn('summary', results)

    def test_validate_results_false(self):
        obtained_results = validator.pipe_validate(self.log_file)
        expected_results = {
            'path': {
                'date': '2024-02-20', 
                'collection': 'wid', 
                'paperboy': True, 
                'mimetype': 'application/gzip', 
                'extension': '.gz'
            }, 
            'content': {
                'summary': {
                    'datetimes': {
                        (2024, 2, 21, 0): 22, 
                        (2024, 2, 21, 1): 34, 
                        (2024, 2, 21, 2): 21, 
                        (2024, 2, 21, 3): 35, 
                        (2024, 2, 21, 4): 29, 
                        (2024, 2, 21, 5): 22, 
                        (2024, 2, 21, 6): 29, 
                        (2024, 2, 21, 7): 43, 
                        (2024, 2, 21, 8): 29, 
                        (2024, 2, 21, 9): 30, 
                        (2024, 2, 21, 10): 35, 
                        (2024, 2, 21, 11): 25, 
                        (2024, 2, 21, 12): 27, 
                        (2024, 2, 21, 13): 31, 
                        (2024, 2, 21, 14): 31, 
                        (2024, 2, 21, 15): 29, 
                        (2024, 2, 21, 16): 23, 
                        (2024, 2, 21, 17): 24, 
                        (2024, 2, 21, 18): 29, 
                        (2024, 2, 21, 19): 28, 
                        (2024, 2, 21, 20): 37, 
                        (2024, 2, 21, 21): 33, 
                        (2024, 2, 21, 22): 33, 
                        (2024, 2, 21, 23): 36,
                    },
                    'ips': {'local': 700, 'remote': 15}, 
                    'invalid_lines': 0,
                    'total_lines': 7160,
                }
            }, 
            'is_valid': {
                'ips': False, 'dates': True, 'all': False}, 
                'probably_date': datetime.datetime(2024, 2, 21, 0, 0)
            }
        self.assertDictEqual(obtained_results, expected_results)
        self.assertFalse(obtained_results['is_valid']['all'])

    def test_validate_only_path_is_false(self):
        obtained_results = validator.pipe_validate(self.log_file, apply_path_validation=True, apply_content_validation=False)
        expected_results = {
            'path': {
                'date': '2024-02-20', 
                'collection': 'wid', 
                'paperboy': True, 
                'mimetype': 'application/gzip', 
                'extension': '.gz'
            }, 
            'is_valid': {
                'ips': False, 'dates': False, 'all': False}, 
                'probably_date': {'error': 'Date dictionary is empty'}
            }
        self.assertDictEqual(obtained_results, expected_results)
        self.assertFalse(obtained_results['is_valid']['all'])

    def test_get_date_frequencies(self):
        results = {
            'content': {
                'summary': {
                    'datetimes': {(2023, 1, 1, 0): 1, (2023, 1, 1, 1): 2}
                }
            }
        }
        frequencies = validator.get_date_frequencies(results)
        self.assertEqual(frequencies, {(2023, 1, 1): 3})

    def test_compute_probably_date(self):
        results = {
            'content': {
                'summary': {
                    'datetimes': {(2023, 1, 1, 0): 1, (2023, 1, 1, 1): 2}
                }
            }
        }
        self.assertEqual(validator.get_probably_date(results), validator.datetime(2023, 1, 1))
