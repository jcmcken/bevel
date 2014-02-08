import os
import copy
import sys
import optparse
import re
import shlex
import logging
import time

LOG = logging.getLogger('bevel')

_RE_VALID_COMMAND = '^[a-zA-Z0-9]+$'
RE_VALID_COMMAND = re.compile(_RE_VALID_COMMAND)

class InvalidCommand(RuntimeError): pass
class InvalidBevel(ValueError): pass

class Bevel(object):
    DRIVER_NAME = '_driver'

    def __init__(self, bin_dir):
        self.bin_dir = bin_dir.rstrip('/')
        self.app_name = os.path.basename(self.bin_dir)
        if not self._is_valid_name(self.app_name):
            raise InvalidBevel(self.bin_dir) 

    def _args_to_path(self, args):
        return os.path.join(self.bin_dir, os.path.sep.join(args)).rstrip('/')

    def _get_bin(self, path):
        bin = None
        if os.path.isdir(path):
            bin = os.path.join(path, self.DRIVER_NAME)
        elif os.path.isfile(path):
            bin = path
        if bin and not os.path.isfile(bin):
            bin = None
        return bin

    def _is_valid_name(self, command):
        # Is ``command`` a valid command name?
        return bool(RE_VALID_COMMAND.match(command))

    def _args_are_valid(self, args):
        return all(map(self._is_valid_name, args))

    def subcommands(self, args):
        bin, parsed_args = self._resolve_args(args)
        if not self._is_driver_file(bin):
            return []

        basedir = os.path.dirname(bin)
        return [ i for i in os.listdir(basedir) if self._appears_as_command(os.path.join(basedir, i)) ]

    def _appears_as_command(self, path):
        return self._is_driver_command(path) or self._is_regular_command(path) 

    def _has_driver(self, path):
        return os.path.isfile(os.path.join(path, self.DRIVER_NAME))

    def _is_regular_command(self, bin):
        return not self._is_driver_file(bin) and os.path.isfile(bin) and \
            self._is_valid_name(os.path.basename(bin)) and \
            self._has_driver(os.path.dirname(bin))

    def _is_driver_command(self, path):
        return self._has_driver(path) and self._is_valid_name(os.path.basename(path))
        
    def _is_driver_file(self, bin):
        return bin.endswith(os.path.sep + self.DRIVER_NAME) 

    def _args_to_bin(self, args):
        result = None
        if self._args_are_valid(args):
            result = self._get_bin(self._args_to_path(args))
        return result

    def _resolve_args(self, args):
        lookup_args = copy.copy(args)
        remainder = []
        bin = None
        while lookup_args:
            bin = self._args_to_bin(lookup_args)
            if bin is not None:
                break
            remainder.append(lookup_args.pop(-1))
        if bin is None:
            bin = self._args_to_bin(lookup_args)
        return bin, remainder

    def _parse_args(self, args):
        return shlex.split(args)

    def _run(self, script, args):
        LOG.info("running script '%s' with args %s" % (script, args))
        now = time.time()
        # run it
        LOG.info("command finished in %3f seconds" % (time.time() - now))

    def run(self, args):
        bin, remainder_args = self._resolve_args(self._parse_args(args))
        self._run(bin, remainder_args)

def create_cli():
    cli = optparse.OptionParser()
    cli.add_option('-a', '--args', default="",
        help="Arguments as passed from your CLI application")
    cli.add_option('-b', '--bindir',
        help="The directory location of your `bevel' scripts")
    cli.add_option('-V', '--verify', action='store_true',
        help="Verify that your `bevel' commands are properly set up and configured")
    cli.add_option('-d', '--debug', action='store_true',
        help="Print debug messages to stdout")
    return cli

def main(argv=None):
    cli = create_cli()
    opts, args = cli.parse_args(argv)

    if opts.debug:
        logging.basicConfig()
        LOG.setLevel(logging.DEBUG)

    if not opts.bindir:
        cli.error('must pass bin directory (-b/--bindir)')

    if not os.path.isdir(opts.bindir):
        cli.error('no such directory "%s"' % opts.bindir)

    app = Bevel(opts.bindir)

    if opts.verify:
        app.verify()
        raise SystemExit

    app.run(opts.args)

if __name__ == '__main__':
    main()
