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

## Usage

To use ``bevel``, generate a wrapper script and call ``bevel`` with the appropriate 
arguments.

For example, create ``/usr/bin/myapp`` with these contents:

```bash
#!/bin/bash

bevel --bindir /path/to/myapp/ --args "$*"
```

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
