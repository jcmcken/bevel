# bevel

A simple, shell script subcommand framework.

## Overview

``bevel`` takes a directory with a particular structure and maps each file in the
directory tree to a subcommand.

For example, given the following directory structure...

```text
myapp/
├── db
│   ├── cluster
│   │   ├── _driver
│   │   └── status
│   ├── create
│   ├── destroy
│   ├── _driver
│   └── migrate
└── _driver
```

...``bevel`` will create a CLI app that matches the tree, e.g. commands might look
something like:

```text
$ myapp db cluster status
Cluster OK!
$ myapp
usage: myapp <subcommand> [subcommands] [options] [arguments]

Valid subcommands: db

$ myapp db
usage: myapp db [subcommands] [options] [arguments]

Valid subcommands: cluster, create, destroy, migrate

```

## Writing a ``bevel`` App

To generate a ``bevel`` app, first plan out your command hierarchy with plain
old directories and files. A directory corresponds to a command which has 
subcommands, and a file corresponds to a command which does not have other
subcommands.

Next, each directory needs to have a special file called ``_driver``. This script
implements the execution of the parent command. Typically, this script will simply
print the valid subcommands.

Lastly, you need to ensure that each of your scripts meets two criteria:

* Scripts must be readable and executable.
* Scripts must have a shebang line (e.g. ``#!/bin/bash``) which indicates the runtime
  to use when executing the script.

The only caveat to these criteria is that you may leave driver scripts (``_driver``) 
empty. When this is done, ``bevel`` will print a default usage message which simply
shows the valid subcommands for the parent command, e.g.:

```text
$ cat /path/to/myapp/_driver
$ myapp
usage: myapp <subcommand> [arguments] [options]

Valid subcommands are: db 
``` 

Other than that, if any of these criteria are not true, ``bevel`` will simply disregard the file (i.e.
won't consider it a command).

To aid in the detection of problems, ``bevel`` provides the ``--verify`` option. When 
run against your command hierarchy, it will let you know if there are any obvious
problems. In some cases (e.g. if you have a ``README``), "bad" results are simply
false positives and can be ignored.

## Wiring Up the App

Now that you have your command hierarchy set up, you'll need to write a driver.
To do this, simply generate a wrapper script and call ``bevel`` with the appropriate 
arguments.

For example, create ``/usr/bin/myapp`` with these contents:

```bash
#!/bin/bash

bevel --bindir /path/to/myapp/ --args "$*"
```

(Here, ``/path/to/myapp/`` is the directory containing the top-most ``_driver`` file 
in your command hierarchy.)

When a user executes this wrapper, ``bevel`` will delegate execution to the appropriate
command or subcommand in the command hierarchy you established previously. 

## Autocompletion

``bevel`` will automatically generate subcommand completion for you. All you need
to do is edit your ``.bashrc`` or create a script in ``/etc/profile.d``, and call
``bevel`` with the ``--complete`` option.

For example:

```bash
#!/bin/bash

COMPLETER="bevel --bindir /path/to/myapp/ --complete"

complete -C "$COMPLETER" myapp
```
