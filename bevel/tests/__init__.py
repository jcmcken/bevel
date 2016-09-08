import unittest
import errno
from bevel import Bevel, InternalError
from mock import Mock, patch
import StringIO
import sys
import tempfile

class Stdout(object):
    stream = sys.stdout

    def __init__(self):
        self.tempfile = tempfile.NamedTemporaryFile(delete=False)

    def capture(self):
        sys.stdout = self.tempfile

    def get(self):
        self.tempfile.flush()
        self.tempfile.seek(0)
        data = self.tempfile.read()
        return data

    def reset(self):
        sys.stdout = sys.__stdout__
        self._reset()

    def _reset(self):
        self.tempfile.close()
        super(Stdout, self).__init__()

class Stderr(Stdout):
    stream = sys.stderr

    def capture(self):
        sys.stderr = self.tempfile

    def reset(self):
        sys.stderr = sys.__stderr__
        self._reset()

class TestCase(unittest.TestCase):
    def setUp(self):
        self.stdout = Stdout()
        self.stderr = Stderr()
        self.stdout.capture()
        self.stderr.capture()

    def tearDown(self):
        self.stdout.reset()
        self.stderr.reset()

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

    def test_resolve_no_args(self):
        self.assertEquals(self.bevel._resolve_args([]), (None, []))

    def test_resolve_args_candidate(self):
        self.bevel._args_to_bin =  Mock(return_value='/foo/bar')
        self.assertEquals(self.bevel._resolve_args(['blah']), ('/foo/bar', []))

    def test_resolve_args_candidate_miss(self):
        self.bevel._args_to_bin =  Mock(return_value=None)
        self.assertEquals(self.bevel._resolve_args(['blah']), (None, ['blah']))

    @patch('subprocess.Popen')
    def test_missing_runtime(self, popen):
        popen.side_effect = OSError(errno.ENOEXEC, 'foo')
        self.assertRaises(InternalError, self.bevel._run, 'foo', ['bar'])

    @patch('subprocess.Popen')
    def test_other_popen_problem(self, popen):
        popen.side_effect = OSError(9, 'foo')
        self.assertRaises(OSError, self.bevel._run, 'foo', ['bar'])

    @patch('subprocess.Popen')
    def test_successful_run(self, popen):
        proc = Mock()
        proc.returncode = 0
        popen.return_value = proc
        self.assertEquals(self.bevel._run('foo', ['bar']), 0)

class BevelRealTestCases(TestCase):
    fixture_dir = 'bevel/tests/fixtures/myapplib'

    def setUp(self):
        self.bevel = Bevel(self.fixture_dir)
        super(BevelRealTestCases, self).setUp()

    def test_has_driver(self):
        for path in [self.fixture_dir, "%s/hasdriver" % self.fixture_dir]:
            self.assertTrue(self.bevel._has_driver(path))
        for path in ["%s/nodriver" % self.fixture_dir]:
            self.assertFalse(self.bevel._has_driver(path))

    def test_subcommands(self):
        self.assertEquals(self.bevel._subcommands([]), ['emptydriver', 'hasdriver', 'hasdriver2', 'takesargs'])
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

    def test_is_empty(self):
        self.assertTrue(self.bevel._is_empty('%s/hasdriver2/_driver' % self.fixture_dir))
        self.assertFalse(self.bevel._is_empty('%s/hasdriver/_driver' % self.fixture_dir))

    def test_missing_command(self):
        self.bevel.run('emptydriver foo')
        self.assertEquals('usage: myapplib emptydriver <subcommand> [arguments] '
                          '[options]\n\nValid subcommands are: subcommand\n\n',
                          self.stdout.get())

    def test_argument_passing(self):
        self.bevel.run('takesargs foo')
        self.assertEquals('foo\n', self.stdout.get())
