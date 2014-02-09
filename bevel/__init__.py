import os
import copy
import sys
import optparse
import re
import shlex
import logging
import time
import subprocess
import errno
import pprint

json = None
for lib in ['json', 'simplejson']:
    try:
        json = __import__(lib)
    except ImportError:
        pass

LOG = logging.getLogger('bevel')

_RE_VALID_COMMAND = '^[a-zA-Z0-9]+$'
RE_VALID_COMMAND = re.compile(_RE_VALID_COMMAND)

class InvalidCommand(RuntimeError): pass
class InvalidBevel(ValueError): pass
class InternalError(RuntimeError): pass

class Bevel(object):
    DRIVER_NAME = '_driver'

    def __init__(self, bin_dir):
        self.bin_dir = bin_dir.rstrip('/')
        self.name = os.path.basename(self.bin_dir)
        if not self._is_valid_name(self.name):
            raise InvalidBevel(self.bin_dir) 

    def _args_to_path(self, args):
        result = os.path.join(self.bin_dir, os.path.sep.join(args)).rstrip('/')
        LOG.debug("args %s corresponds to path '%s'" % (args, result))
        return result

    def _get_bin(self, path):
        bin = None
        if os.path.isdir(path):
            bin = os.path.join(path, self.DRIVER_NAME)
        elif os.path.isfile(path):
            bin = path
        if bin and not os.path.isfile(bin):
            bin = None
        LOG.debug("command path '%s' corresponds to script '%s'" % (path, bin))
        return bin

    def _is_valid_name(self, command):
        # Is ``command`` a valid command name?
        result = bool(RE_VALID_COMMAND.match(command))
        LOG.debug("'%s' is a valid command name? %s" % (command, result))
        return result

    def _args_are_valid(self, args):
        """
        Whether all ``args`` have valid command names
        """
        return all(map(self._is_valid_name, args))

    def _subcommands(self, args):
        bin, parsed_args = self._resolve_args(args)
        if not self._is_driver_file(bin):
            return []

        basedir = os.path.dirname(bin)
        result = [ i for i in os.listdir(basedir) if self._appears_as_command(os.path.join(basedir, i)) ]
        LOG.debug("subcommands for %s are %s" % (args, result))
        return result

    def _appears_as_command(self, path):
        """
        Whether a particular ``path`` appears as a command/subcommand
        """
        return self._is_driver_command(path) or self._is_regular_command(path) 

    def _has_driver(self, path):
        """
        Whether a particular command directory has a driver file
        """
        result = os.path.isfile(os.path.join(path, self.DRIVER_NAME))
        LOG.debug("path '%s' has a driver? %s" % (path, result))
        return result

    def _is_runnable(self, path):
        """
        Whether a particular path is a runnable script
        """
        runnable = os.access(path, os.R_OK|os.X_OK) and os.path.isfile(path)
        LOG.debug("script '%s' is runnable? %s" % (path, runnable))
        return runnable

    def _is_regular_command(self, bin):
        result = not self._is_driver_file(bin) and os.path.isfile(bin) and \
            self._is_valid_name(os.path.basename(bin)) and \
            self._has_driver(os.path.dirname(bin)) and self._is_runnable(bin)
        LOG.debug("'%s' is a leaf command? %s" % (bin, result))
        return result

    def _is_driver_command(self, path):
        result = self._has_driver(path) and self._is_valid_name(os.path.basename(path))
        LOG.debug("'%s' is a parent command? %s" % (path, result))
        return result
        
    def _is_driver_file(self, bin):
        """
        Whether a particular path is command driver
        """
        result = bin.endswith(os.path.sep + self.DRIVER_NAME) and \
            self._is_runnable(bin) 
        LOG.debug("'%s' is a driver script? %s" % (bin, result))
        return result

    def _args_to_bin(self, args):
        """
        Convert command-line arguments to a script path
        """
        result = None
        if self._args_are_valid(args):
            result = self._get_bin(self._args_to_path(args))
        if result is not None and not self._is_runnable(result):
            result = None
        LOG.debug("converted args %s to valid script '%s'" % (args, result))
        return result

    def _resolve_args(self, args):
        """
        Resolve the next available subcommand from command-line arguments.
        
        E.g. if ``baz`` is an invalid subcommand to ``foo bar``, then resolve
        ``foo bar`` so that you can automatically call usage 
        """
        lookup_args = copy.copy(args)
        remainder = []
        bin = None
        while lookup_args:
            candidate = self._args_to_bin(lookup_args)
            LOG.debug('candidate script for %s is "%s"' % (args, candidate))
            if candidate is not None:
                LOG.debug('selecting candidate "%s"' % candidate)
                bin = candidate
                break
            LOG.debug('skipping candidate "%s"' % candidate)
            remainder.append(lookup_args.pop(-1))
        if bin is None:
            bin = self._args_to_bin(lookup_args)
        # remainder args were populated backwards, so reverse them
        remainder.reverse()
        results = (bin, remainder)
        LOG.debug('args %s resolve to script path "%s" with remainder args %s' % (args, results[0], results[1]))
        return results

    def _parse_args(self, args):
        """
        Convert string arguments to an array
        """
        parsed = shlex.split(args)
        LOG.debug('parsed "%s" as %s' % (args, parsed))
        return parsed

    def _run(self, script, args):
        """
        Run ``script`` with arguments ``args``
        """
        LOG.info("running script '%s' with args %s" % (script, args))
        now = time.time()
        full_args = [script] + args
        try:
            proc = subprocess.Popen(full_args)
            proc.communicate()
            code = proc.returncode
        except OSError, e:
            if e.errno == errno.ENOEXEC:
                raise InternalError('could not determine subcommand runtime')
            else: raise
                
        LOG.info("command finished in %3f seconds with return code %d" % ((time.time() - now), code))
        return code

    def run(self, args, noop=False):
        bin, remainder_args = self._resolve_args(self._parse_args(args))
        # TODO: don't call bin with remainder args if command resolves
        #       fuzzily; just call ``self._run(bin)`` 
        code = None
        if bin is None:
            raise InternalError('could not resolve any valid, runnable scripts')
        if not noop:
            code = self._run(bin, remainder_args)
        return code

    def _complete(self, args):
        subcommands = self._subcommands(args)
        if not args:
            result = subcommands
        else:
            result = [ i for i in subcommands if i.startswith(args[-1]) ]
        return result

    def complete(self, args):
        return self._complete(self._parse_args(args))

    def _verify(self):
        bad = {
          'permissions': {
            'dirs': [],
            'files': [],
          }
        }
        for basedir, dirs, files in os.walk(self.bin_dir):
            for dir in dirs:
                fullname = os.path.join(basedir, dir)
                if not os.access(fullname, os.R_OK|os.X_OK):
                    bad['permissions']['dirs'].append(fullname)
            for file in files:
                fullname = os.path.join(basedir, file)
                if not self._is_runnable(fullname):
                    bad['permissions']['files'].append(fullname)
        return bad

    def verify(self):
        data = self._verify()
        if json:
            result = json.dumps(data, indent=2)
        else:
            result = pprint.pformat(data)
        return result

def enable_debug():
    logging.basicConfig()
    LOG.setLevel(logging.DEBUG)

def create_cli():
    cli = optparse.OptionParser(prog='bevel')
    cli.add_option('-a', '--args', default="",
        help="Arguments as passed from your CLI application")
    cli.add_option('-b', '--bindir',
        help="The directory location of your `bevel' scripts")
    cli.add_option('-c', '--complete', action='store_true',
        help="Instead of running your `bevel' app, just autocomplete the last subcommand.")
    cli.add_option('-n', '--noop', action='store_true',
        help="Do everything normally, except don't run any scripts.")
    cli.add_option('-d', '--debug', action='store_true',
        help="Print debug messages to stdout")
    cli.add_option('-V', '--verify', action='store_true',
        help="Verify that your `bevel' commands are properly set up and configured."
             " This option is for development purposes. Returns a data structure "
             "containing all of the directories or files that may be incorrect.")
    return cli

def main(argv=None):
    cli = create_cli()
    opts, args = cli.parse_args(argv)

    if opts.debug:
        enable_debug()

    if not opts.bindir:
        cli.error('must pass bin directory (-b/--bindir)')

    if not os.path.isdir(opts.bindir):
        cli.error('no such directory "%s"' % opts.bindir)

    app = Bevel(opts.bindir)

    if opts.verify:
        print app.verify()
        raise SystemExit

    if opts.complete:
        completion = app.complete(opts.args)
        print '\n'.join(completion)
        raise SystemExit

    try:
        returncode = app.run(opts.args, noop=opts.noop)
        raise SystemExit(returncode)
    except InternalError, e:
        sys.stderr.write("%s: internal error: %s\n" % (app.name, e.args[0]))
        raise SystemExit(1)

if __name__ == '__main__':
    main()
