import unittest
from bevel import Bevel
from mock import Mock, patch

class BevelTestCase(unittest.TestCase):
    def setUp(self):
        self.bevel = Bevel('/foo')

    def test_args_to_path(self):
        self.assertEquals(self.bevel._args_to_path([]), '/foo')
        self.assertEquals(self.bevel._args_to_path(['bar']), '/foo/bar')
        self.assertEquals(self.bevel._args_to_path(['bar', 'baz']), '/foo/bar/baz')

    @patch('os.path.isdir')
    def test_get_bin_dir(self, isdir):
        isdir.return_value = True
        self.assertEquals(self.bevel._get_bin('/foo/bar'), '/foo/bar/_driver')        

    @patch('os.path.isfile')
    def test_get_bin(self, isfile):
        isfile.return_value = True
        self.assertEquals(self.bevel._get_bin('/foo/bar'), '/foo/bar')        
        
    def test_get_bin_missing(self):
        self.assertEquals(self.bevel._get_bin('/foo/bar'), None)        

    def test_command_is_valid(self):
        for cmd in ['foo', '48']:
            self.assertTrue(self.bevel._is_valid_name(cmd))
        for cmd in ['_foo', '-', '']:
            self.assertFalse(self.bevel._is_valid_name(cmd))

    def test_args_are_valid(self):
        self.assertFalse(self.bevel._args_are_valid(['-lskdjf'])) 
        self.assertFalse(self.bevel._args_are_valid(['foo bar'])) 
        self.assertTrue(self.bevel._args_are_valid([])) 
        self.assertTrue(self.bevel._args_are_valid(['foo', 'bar'])) 

