#! /usr/bin/env python3
"""
proxy -- npminstall.py

author  - fmitchell
created - 2018-Apr-19
"""

import sys
from . import share

prog_name = 'proxyget.npminstall'
install_cmd = r'npm --proxy {} install {}'


def main(*args):
    if '--help' in args or '-h' in args:
        share.run_cmd('npm install --help')
    else:
        proxy: str = share.make_proxy()
        args_str = ' '.join(args)
        share.run_cmd(install_cmd.format(proxy, args_str),
                      f'installing package(s)')


if __name__ == '__main__':
    main(*sys.argv[1:])
