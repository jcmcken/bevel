# Changelog

## Version 0.3.0

- **New**: Setting the ``BEVEL_DEBUG`` environment variable to a value will now
  enable ``bevel`` debug logging (similar to passing ``--debug`` to ``bevel``).
  This can be used in downstream ``bevel`` applications to see what's going on.
- **Fix**: ``bevel`` should no longer throw any 'missing logger' Python warnings.
- **Fix**: Invalid commands should now execute the parent driver instead of
  silently doing nothing (e.g. if there is no driver, print the parent command's
  usage)

## Version 0.2.0

- **New**: The application name can now be overridden with ``-N``/``--app-name``.
- **Fix**: The ``--verify`` option now correctly lists all detected problems.
- **Fix**: Commands and subcommands can now contain dashes where it makes sense
  (e.g. ``foo-bar`` is valid but ``foo--bar`` is not).
- **New**: Executing a command corresponding to an empty ``_driver`` file will
  automatically print a usage message showing you the valid subcommands. (This
  way, you don't necessarily even have to write the driver scripts)
- **New**: Added Python 2.4 compatibility (e.g. compatible with RHEL5-based distros)

## Version 0.1.0

- Initial release
