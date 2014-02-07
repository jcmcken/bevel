import os
import copy
import sys
import optparse
import re

_RE_VALID_COMMAND = '^[a-zA-Z0-9]+$'
RE_VALID_COMMAND = re.compile(_RE_VALID_COMMAND)

class InvalidCommand(RuntimeError): pass

class Bevel(object):
    DRIVER_NAME = '_driver'

    def __init__(self, bin_dir):
        self.bin_dir = bin_dir 

    def _args_to_path(self, args):
        return os.path.join(self.bin_dir, os.path.sep.join(args)).rstrip('/')

    def _get_bin(self, path):
        if os.path.isdir(path):
            bin = os.path.join(path, self.DRIVER_NAME)
        elif os.path.isfile(path):
            bin = path
        else:
            bin = None
        return bin

    def _is_valid_name(self, command):
        # Is ``command`` a valid command name?
        return bool(RE_VALID_COMMAND.match(command))

    def _args_are_valid(self, args):
        return all(map(self._is_valid_name, args))

    def subcommands(self, args):
        bin = self.resolve_args(args)
        if not self._is_driver_file(bin):
            return []

        basedir = os.path.dirname(bin)
        return [ i for i in os.listdir(basedir) if self._appears_as_command(os.path.join(basedir, i)) ]

    def _appears_as_command(self, path):
        return self._is_driver_command(path) or self._is_regular_cmd(path) 

    def _has_driver(self, path):
        return os.path.isfile(os.path.join(path, self.DRIVER_NAME))

    def _is_regular_cmd(self, bin):
        return not self._is_driver_file(bin) and \
            self._is_valid_name(os.path.basename(bin))

    def _is_driver_command(self, path):
        return self._has_driver(path) and self._is_valid_name(os.path.basename(path))
        
    def _is_driver_file(self, bin):
        return bin.endswith(os.path.sep + self.DRIVER_NAME) 

    def resolve_args(self, args):
        lookup_args = copy(args)
        bin = None
        while lookup_args:
            if self._args_are_valid(args):
                bin = self._get_bin(self._args_to_path(lookup_args))
                if bin is not None:
                    break
            lookup_args.pop(-1)
        if bin is None:
            raise InvalidCommand(args)
        return bin 

def create_cli():
    cli = optparse.OptionParser()
    cli.add_option('-b', '--bindir',
        help="The directory location of your `bevel' scripts")
    cli.add_option('-v', '--verify', action='store_true',
        help="Verify that your `bevel' commands are properly set up and configured")
    return cli

def main(argv=None):
    cli = create_cli()
    opts, args = cli.parse_args(argv)

    if not opts.bindir:
        cli.error('must pass bin directory (-b/--bindir)')

    if not os.path.isdir(opts.bindir):
        cli.error('no such directory "%s"' % opts.bindir)

    app = Bevel(opts.bindir)

    if opts.verify:
        app.verify()
        raise SystemExit

    app.run(argv)

if __name__ == '__main__':
    main()
