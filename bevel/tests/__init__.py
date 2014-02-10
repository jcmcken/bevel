import unittest
from bevel import Bevel
from mock import Mock, patch

class BevelInitializationTestCases(unittest.TestCase):
    def test_different_paths(self):
        Bevel('/foo/')
        Bevel('/foo')
        Bevel('foo')

class BevelStubTestCases(unittest.TestCase):
    def setUp(self):
        self.bevel = Bevel('/foo')

    def test_args_to_path(self):
        self.assertEquals(self.bevel._args_to_path([]), '/foo')
        self.assertEquals(self.bevel._args_to_path(['bar']), '/foo/bar')
        self.assertEquals(self.bevel._args_to_path(['bar', 'baz']), '/foo/bar/baz')

    @patch('os.path.isdir')
    @patch('os.path.isfile')
    def test_get_bin_dir(self, isdir, isfile):
        isdir.return_value = True
        isfile.return_value = True
        self.assertEquals(self.bevel._get_bin('/foo/bar'), '/foo/bar/_driver')        
    
    @patch('os.path.isdir')
    @patch('os.path.isfile')
    def test_get_bin_dir(self, isfile, isdir):
        isdir.return_value = True
        isfile.return_value = False
        self.assertEquals(self.bevel._get_bin('/foo/bar'), None)        

    @patch('os.path.isfile')
    def test_get_bin(self, isfile):
        isfile.return_value = True
        self.assertEquals(self.bevel._get_bin('/foo/bar'), '/foo/bar')        
        
    def test_get_bin_missing(self):
        self.assertEquals(self.bevel._get_bin('/foo/bar'), None)        

    def test_command_is_valid(self):
        for cmd in ['foo', '48', 'foo-bar', 'foo-bar-baz']:
            self.assertTrue(self.bevel._is_valid_name(cmd))
        for cmd in ['_foo', '-', 'foo-', '--bar', 'foo--bar', 'foo--', 'foo-bar--baz']:
            self.assertFalse(self.bevel._is_valid_name(cmd))

    def test_args_are_valid(self):
        self.assertFalse(self.bevel._args_are_valid(['-lskdjf'])) 
        self.assertFalse(self.bevel._args_are_valid(['foo bar'])) 
        self.assertTrue(self.bevel._args_are_valid([])) 
        self.assertTrue(self.bevel._args_are_valid(['foo', 'bar'])) 

    def test_completion(self):
        self.bevel._subcommands = Mock(return_value=['foo', 'bar', 'baz'])
        self.assertEquals(self.bevel._complete(['f']), ['foo'])
        self.assertEquals(self.bevel._complete([]), ['foo', 'bar', 'baz'])
        self.assertEquals(self.bevel._complete(['b']), ['bar', 'baz'])
        self.assertEquals(self.bevel._complete(['foo', 'b']), ['bar', 'baz'])
        self.assertEquals(self.bevel._complete(['blah']), [])
        self.assertEquals(self.bevel._complete(['foo', 'blah']), [])

class BevelRealTestCases(unittest.TestCase):
    fixture_dir = 'bevel/tests/fixtures/myapplib'

    def setUp(self):
        self.bevel = Bevel(self.fixture_dir)

    def test_has_driver(self):
        for path in [self.fixture_dir, "%s/hasdriver" % self.fixture_dir]:
            self.assertTrue(self.bevel._has_driver(path))
        for path in ["%s/nodriver" % self.fixture_dir]:
            self.assertFalse(self.bevel._has_driver(path))

    def test_subcommands(self):
        self.assertEquals(self.bevel._subcommands([]), ['hasdriver', 'hasdriver2'])
        self.assertEquals(self.bevel._subcommands(['hasdriver', 'subcommand']), [])

    def test_is_regular_command(self):
        self.assertTrue(self.bevel._is_regular_command('%s/hasdriver/subcommand' % self.fixture_dir))
        self.assertFalse(self.bevel._is_regular_command('%s/nodriver/subcommand' % self.fixture_dir))

    def test_completion(self):
        for str_args, expected in (
          ('hasdrive ', []),
          ('hasdrive', ['hasdriver', 'hasdriver2']),
          ('hasdriver ', ['dashed-command', 'subcommand']),
          ('hasdriver', ['hasdriver', 'hasdriver2']),
          ('hasdriver s', ['subcommand']),
          ('hasdriver f', []),
        ):
            self.assertEquals(self.bevel.complete(str_args), expected)

    def test_appears_as_command(self):
        self.assertTrue(self.bevel._appears_as_command('%s/hasdriver' % self.fixture_dir))
        self.assertFalse(self.bevel._appears_as_command('%s/hasbaddriver' % self.fixture_dir))
