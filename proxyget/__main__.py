#! /usr/bin/env python3
"""
proxyget -- __main__.py

author  - fmitchell
created - 2018-Aug-03
"""

import argparse
from pathlib import Path
from urllib import error

from proxyget import proxyget

try:
    from proxyget.proxyget import default_proxy
except ImportError:
    default_proxy = (None, None, "", None)
default_server, default_port, default_domain, default_user = default_proxy


desc = """
Run to retrieve a webpage or file from the given url through a proxy.

If retrieving a file (or to save website html), supply an argument to -o/--out.
If default_proxy.json exists and is correct; --server and --port are optional
(and will use the default if not entered). Otherwise, they are required.
--domain and --user are always optional but will also use any defaults provided
in the json.

Example usage to retrieve a file: 

    $ python -m proxyget http://url/to/file.txt --out ./file.txt
    
Example usage to retrieve an executable file:

    $ python -m proxyget http://url/to/executable.exe -b --out ./exec.exe
    
There are also to sub-commands gitclone and npminstall that will run "git clone"
and "npm install" through the proxy respectively. To run them, do

    $ python -m proxyget.gitclone <args>
"""

def main():

    parser = argparse.ArgumentParser('proxyget', description=desc)


    parser.add_argument('url',
        help="The url to retrieve")

    parser.add_argument('-o', '--out', default=None,
        help="If specified, write the output to this file")

    parser.add_argument('--server', default=default_server,
        help="The proxy server (either an IP or URL)")

    parser.add_argument('--port', type=int, default=default_port,
        help="The port (an integer between 0 and 65535)")

    parser.add_argument('--domain', default=default_domain,
        help="The username domain (can be empty string)")

    parser.add_argument('--user', default=default_user,
        help="The username for the proxy "
             "(will assume OS username if not passed)")

    parser.add_argument('-q', '--quiet', action='store_true',
        help="Select to quiet output")

    parser.add_argument('-b', '--binary', action="store_true",
        help="Set if downloading a binary file")


    args = parser.parse_args()

    out = Path(args.out) if args.out is not None else None

    proxy_info = proxyget.ProxyInfo(args.server, args.port, args.domain,
                                    args.user)

    try:
        proxy_info.assert_correct()
    except TypeError:  # default not defined
        raise ValueError("--server and --port must be provided "
                         "if no default proxy info specified") from None
    except ValueError:  # bad port
        raise

    if args.out:

        if out is None:
            raise ValueError("If '--exe' specified, '--out' must be set")

        if not args.quiet:
            print(f'getting file from {args.url}. Please wait...')
        proxyget.get_file(args.url, out, args.binary, proxy_info=proxy_info,
                          quiet=args.quiet)

    else:

        if not args.quiet:
            print(f'Getting site {args.url}...')
        data = proxyget.get(args.url, proxy_info=proxy_info)

        if data.status_code != 200:
            raise error.HTTPError(args.url, data.status_code, data.text,
                                  data.headers, None)

        print(data.text)

    if not args.quiet:
        print('done')


if __name__ == '__main__':
    main()
