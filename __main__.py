#! /usr/bin/env python3
"""
proxyget -- __main__.py

author  - fmitchell
created - 2018-Aug-03
"""

import argparse
from pathlib import Path
from urllib import error

import proxyget

try:
    from proxyget import default_proxy
except ImportError:
    default_proxy = (None, None, "", None)
default_server, default_port, default_domain, default_user = default_proxy


desc = """
Run to retrieve a webpage or file from the given url through a proxy.

If retrieving a file, pass -f/--file and supply an argument to -o/--out.
If default_proxy.json exists and is correct; --server and --port are optional
(and will use the default if not entered). Otherwise, they are required.
--domain and --user are always optional but will also use any defaults provided
in the json.

Example usage to retrieve a file: 
    ```$ python -m proxyget --file http:/url/to/file.exe --out ./file.exe```
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

    parser.add_argument('-f', '--file', action="store_true",
        help="To retrieve a file, rather than a site (must provide argument "
             "to -o/--out if used)")

    parser.add_argument('-e', '--exe', action="store_true",
        help="deprecated: same as -f/--file")


    args = parser.parse_args()

    out = Path(args.out) if args.out is not None else None

    proxy_info = proxyget.ProxyInfo(args.server, args.port, args.domain,
                                    args.user)

    try:
        proxy_info.assert_correct()
    except TypeError:  # default not defined
        raise ValueError("--server and --port must be provided "
                         "if no default proxy info specified")
    except ValueError:  # bad port
        raise

    if args.file or args.exe:

        if out is None:
            raise ValueError("If '--exe' specified, '--out' must be set")

        print(f'getting file from {args.url}. Please wait...')
        proxyget.get_file(args.url, out, proxy_info=proxy_info)
        print('done')

    else:

        print(f'Getting site {args.url}...')
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


if __name__ == '__main__':
    main()
