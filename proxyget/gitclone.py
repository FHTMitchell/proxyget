#/!usr/bin/env python3

"""
Bypass SSTL proxy so can clone github repos from outside. If set_local
option is True, the newly clone repo will be updated so the proxy is set
locally within the repo.
"""

import sys

if sys.version_info < (3, 6):
    raise RuntimeError("Requires python 3.6.0 or higher, you are using {}.{}.{}"
                       .format(*sys.version_info[:3]))

import os
import time
import argparse
from . import share

prog_name = "proxyget.gitclone"

set_cmd = r"git config --global --add http.proxy {}"
unset_cmd = r"git config --global --unset http.proxy"
clone_cmd = r"git clone {} {}"
set_local_cmd = r"git config --add http.proxy {}"
set_local_email_cmd = r"git config --add user.email {}"


# noinspection PyUnboundLocalVariable
def main(url: str, dir_: str = "", set_local: bool = True, email: str = None,
         verbose: bool = False) -> None:

    log = share.logger(verbose)
    cwd = os.getcwd()

    if " " in url:
        raise ValueError(f"spaces cannot be in url: {url!r}")
    project_name: str = dir_ or os.path.splitext(url.split('/')[-1])[0]

    proxy: str = share.make_proxy()

    os.system(unset_cmd)
    try:
        log("Setting global proxy")
        share.run_cmd(set_cmd.format(proxy), 'setting global proxy')
        log("Cloning...")
        share.run_cmd(clone_cmd.format(url, dir_), 'cloning')
        if set_local or email:
            time.sleep(1)
            os.chdir(project_name)
            if set_local:
                log("Setting local proxy")
                share.run_cmd(set_local_cmd.format(proxy), 'setting local proxy')
            if email:
                log("Setting local email")
                share.run_cmd(set_local_email_cmd.format(email),
                              'setting local email')
    finally:
        log("Unsetting global proxy")
        os.system(unset_cmd)
        os.chdir(cwd)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog=prog_name,
            description="Clone a git repo using external proxy")

    parser.add_argument('url', help='git repo url')

    parser.add_argument('--dir', '-d', default='',
            help='optionally set directory to clone to')

    parser.add_argument('--no-set-local', '-n', action='store_false',
            help='do not set the proxy in local config')

    parser.add_argument('--email', '-e', default=None,
            help='if given, set as your email in the local config')

    parser.add_argument('--verbose', '-v', action='store_true',
            help='run in verbose mode')

    args = parser.parse_args()

    main(args.url, args.dir, args.no_set_local, args.email, args.verbose)
