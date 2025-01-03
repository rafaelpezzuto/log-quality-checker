import unittest

from scielo_log_validator import file_utils


class TestFileUtils(unittest.TestCase):

    def setUp(self):
        self.log_directory = 'tests/fixtures/logs/scielo.wi/'
        self.log_file = 'tests/fixtures/logs/scielo.wi/2024-02-20_caribbean.scielo.org.1.log.gz'
        self.log_file_invalid_name = 'tests/fixtures/logs/scielo.wi/invalid_file_name.log.gz'

    def test_open_file(self):
        with file_utils.open_file(self.log_file) as f:
            self.assertTrue(f.read())
    
    def test_extract_mimetype_from_path_is_gz(self):
        gzip_mimes = ['application/gzip', 'application/x-gzip']
        mimetype = file_utils.extract_mime_from_path(self.log_file)
        self.assertIn(mimetype, gzip_mimes)

    def test_extract_collection_from_path_is_valid(self):
        log_file_collection = file_utils.extract_collection_from_path(self.log_file)
        self.assertEqual(log_file_collection, 'wid')

    def test_extract_collection_from_path_is_none(self):
        path_to_non_existing_file = '/path/to/nothing'
        log_file_collection = file_utils.extract_collection_from_path(path_to_non_existing_file)
        self.assertIsNone(log_file_collection)

    def test_extract_file_extension_from_path_is_gz(self):
        self.assertEqual(file_utils.extract_file_extension_from_path(self.log_file), '.gz')

    def test_extract_file_extension_from_path_raises_exception(self):
        with self.assertRaises(Exception):
            file_utils.extract_file_extension_from_path('/path/to/file')
