#! /usr/bin/env python3
"""
proxyget -- __main__.py

author  - fmitchell
created - 2018-Aug-03
"""

import argparse
from pathlib import Path
from urllib import error
from warnings import warn

import proxyget

try:
    from proxyget.defaults import default
except ImportError:
    warn('No ProxyInfo named default found in proxyget/defaults.py')
    default = (None,) * 4

default_server, default_port, default_domain, default_user = default

if __name__ == '__main__':

    parser = argparse.ArgumentParser('proxyget')

    parser.add_argument('url')

    parser.add_argument('-o', '--out', default=None)

    parser.add_argument('--server', default=default_server)

    parser.add_argument('--port', type=int, default=default_domain)

    parser.add_argument('--domain', default=default_port)

    parser.add_argument('--user', default=None)

    parser.add_argument('-e', '--exe', action="store_true")

    args = parser.parse_args()

    out = Path(args.out) if args.out is not None else None

    proxy_info = proxyget.ProxyInfo(args.server, args.port, args.domain,
                                    args.user)

    try:
        proxy_info.assert_correct()
    except TypeError:  # default not defined
        raise ValueError("--server, --port and --domain must all be provided"
                         " if no default proxy info specified")
    except ValueError:  # bad port
        raise

    if args.exe:

        if out is None:
            raise ValueError("If '--exe' specified, '--out' must be set")
        proxyget.getexe(args.url, out, proxy_info=proxy_info)
        print('done')

    else:

        data = proxyget.get(args.url, proxy_info=proxy_info)

        if data.status_code != 200:
            raise error.HTTPError(args.url, data.status_code, data.text,
                                  data.headers, None)

        if out is None:
            print(data.text)
        else:
            if not out.parent.exists():
                raise FileNotFoundError(
                        f'{out.parent} directory does not exist')

            with out.open('w') as f:
                f.write(data.text)
            print('done')
