import os
import copy

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

    def resolve_args(self, args):
        lookup_args = copy(args)
        bin = None
        while lookup_args:
            bin = self._get_bin(self._args_to_path(lookup_args))
            if bin is not None:
                # found a hit
                break
            lookup_args.pop(-1)
        return bin 
