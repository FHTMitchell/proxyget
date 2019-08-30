#! /usr/bin/env python3
# proxyget.py
""" Simple library for retrieving websites and online files through a proxy """

import functools
import json
import string
from getpass import getpass, getuser
from pathlib import Path
from typing import Any, Dict, Mapping, NamedTuple, Optional, Union
from warnings import warn

import requests

from . import utils

__all__ = ['make_proxy', 'make_kwargs', 'get', 'get_file',
           'clear_password_cache', 'ProxyInfo',
           'default_proxy', 'default_proxy_path', 'get_default_proxy']

PathType = Union[Path, str]
default_proxy_path: Path = Path(__file__).parent / 'default_proxy.json'
_test_url = "http://example.com"


# ProxyInfo class

class ProxyInfo(NamedTuple):
    """ Simple namedtuple used to hold proxy info to create the proxies.

    server: str
        The server address with any form of (where pppp is the port number)
            xxx.xxx.xxx.xxx:pppp
            abc.def.gh:pppp
    domain: str
        The user domain of the form
            domain\
    user: str?
        The username in the domain. If None, will assume the same as your OS
        username.
    """

    server: str
    port: int
    domain: str = ""
    usr: Optional[str] = None

    def assert_correct(self) -> None:
        """
        Check that this is a valid proxy state

        :returns: None
        :raises: TypeError
            If an attribute it the wrong type
        :raises: ValueError
            If port is not a valid port number
        """

        if not isinstance(self.server, str):
            raise TypeError(f"server must be a str, not"
                            f" {self.server.__class__.__name__}")

        if not isinstance(self.domain, str):
            raise TypeError(f"domain must be a str, not"
                            f" {self.domain.__class__.__name__}")

        if self.usr is not None and not isinstance(self.usr, str):
            raise TypeError(f"usr must be None or a str, not"
                            f" {self.usr.__class__.__name__}")

        if not isinstance(self.port, int):
            raise TypeError(f"port must be an int, not"
                            f" {self.port.__class__.__name__}")

        if not (0 <= self.port <= 65535):
            raise ValueError(f"port ({self.port!r}) must be between"
                             f" 0 and 65535 inclusive")

    def copy_with(self, *, server: str = None, port: int = None,
                  domain: str = None, usr: str = None) -> 'ProxyInfo':
        """A copy of this PoxyInfo with any arguments overriding the equivelent
        values in this
        """
        server = self.server if server is None else server
        port = self.port if port is None else port
        domain = self.domain if domain is None else domain
        usr = self.usr if usr is None else usr
        return ProxyInfo(server, port, domain, usr)

    @classmethod
    def from_json(cls, file: PathType) -> 'ProxyInfo':
        """Load a ProxyInfo from a json file holding a single object of the form
        {
            "server": <a string>,
            "port": <an int>,
            "domain": <an optional string>,
            "usr": <an optional string>
        }
        """
        with open(file) as f:
            return ProxyInfo(**json.load(f))


# helpers

def make_url_safe(s: str) -> str:
    """
    Replace a string with a url safe version
    """
    no_replace = set(string.digits + string.ascii_letters + '%')
    s = s.replace('%', '%25')  # must replace % first

    sset = set(s) - no_replace
    for c in sset:
        s = s.replace(c, f"%{ord(c):X}")
    return s


def clear_password_cache() -> None:
    """ Clear the passwords cache """
    make_proxy_and_save.cache_clear()


@functools.lru_cache(maxsize=None)
def make_proxy_and_save(info: ProxyInfo) -> Mapping[str, str]:
    """Wrapper around `make_proxy` but saves results of the same argument
    to a hidden cache.

    To clear the cache, call `clear_password_cache()`.
    """
    return make_proxy(info)


def make_proxy(info: ProxyInfo, *, debug: bool = False) -> Mapping[str, str]:
    """
    Generate the http and https proxy string

    :param info: ProxyInfo
        a namedtuple of the form
            (server: str, port: int, domain: str, usr: str?)
    :param debug: bool
        If True run in debug mode and don't ask user for a password

    :return: Mapping[str, str]
        A dictionary with keys ['http', 'https'] of the form:
            {
              http:  http://{domain}\{usr}:{passwd}@{server}
              https: https://{domain}\{usr}:{passwd}@{server}
            }
    """

    ProxyInfo.assert_correct(info)  # call from class so user can pass a tuple
    server, port, domain, usr = info

    if debug:
        print(f"using proxy address: {server}:{port}")
        print(f"using domain name: {domain}")
        if usr: print(f"using username: {usr}")

    usr = make_url_safe(usr or getuser())

    if domain:
        if not domain.endswith('\\'):
            domain += '\\'
        domain = make_url_safe(domain)

    if not debug:
        prompt = f"Please enter the password for {usr}: "
        passwd = getpass(prompt)
        passwd = make_url_safe(passwd)
        print()
    else:
        passwd = "<DEBUGPASSWD>"

    proxies = {
        'http': fr'http://{domain}{usr}:{passwd}@{server}:{port}',
        'https': fr'https://{domain}{usr}:{passwd}@{server}:{port}'
    }
    if debug:
        print(f"proxies = {proxies}")

    return proxies



def make_kwargs(proxy_info: ProxyInfo, *, nosave: bool = False,
                **kwargs: Any) -> Dict[str, Any]:
    """Form the proxy kwargs for requests or urllib

    :param proxy_info: ProxyInfo
        a namedtuple of the form
            (server: str, port: int, domain: str, usr: str?)
    :param nosave: bool
        If True, save any passwords entered for a given `proxy_info`. In order
        to clear the password cache, call `clear_password_cache()`
    :param kwargs: Any
        Additional arguments to pass to `requests.get` or
        `urllib.request.urlretrieve`

    :return: Dict[str, Any]
        The keyword arguments with 'verify' and 'proxies' added
    """

    if 'verify' not in kwargs:
        kwargs['verify'] = False

    if 'proxies' not in kwargs:
        proxies = make_proxy(proxy_info) \
            if nosave else make_proxy_and_save(proxy_info)
        kwargs['proxies'] = proxies

    return kwargs


# main events

def get(url: str, *args: Any, proxy_info: ProxyInfo = None, stream: bool = False,
        nosave: bool = False, **kwargs: Any) -> requests.Response:
    """ Make a request to `url` via a proxy


    :param url: str
        The url to request

    :param args: Any
        Additional positonal args to pass to `requests.get`

    :param proxy_info: ProxyInfo?
        a namedtuple of the form
            (server: str, port: int, domain: str, usr: str?)
        If None, use the default_proxy (if exists)

    :param stream: bool
         See requests.request. If True, use with:
            with proxyget.get(..., stream=True) as response: ...

    :param nosave: bool
        If True, save any passwords entered for a given `proxy_info`. In order
        to clear the password cache, call `clear_password_cache()`

    :param kwargs: Any
        Additional arguments to pass to `requests.get`

    :return: requests.Request
        The request object recieved from the URL via the proxy

    :raises: requests.RequestException
        Or any subclass thereof
            e.g. if the url does not exist or the proxy was incorrect
    """
    if proxy_info is None:
        proxy_info = default_proxy
    try:
        return requests.get(url, *args, stream=stream,
                            **make_kwargs(proxy_info=proxy_info,
                                          nosave=nosave, **kwargs))
    except requests.exceptions.ProxyError:
        msg = "Error with proxy: probable username-password incorrect combination"
        raise requests.exceptions.ProxyError(msg)



def get_file(url: str, filename: PathType, binary: bool,
             proxy_info: ProxyInfo = None, nosave: bool = False,
             quiet: bool = False, **kwargs: Any) -> None:

    log = print if not quiet else lambda *a, **k: None

    with get(url, proxy_info=proxy_info, stream=True, nosave=nosave, **kwargs) \
            as response:

        size: Optional[float] = utils.dict_get_ignore_case(
                response.headers,
                key='content-length',
                default=None
        )
        if size is not None:
            size = float(size)

        pbar = utils.ProgressBar()

        if size is not None and not quiet:
            log(f'Writing {utils.write_bytes(size)} to "{filename!s}"')
            pbar.print_init()
        elif not quiet:
            log("Unable to get content-length from header (case insensitive)")

        with open(filename, 'wb' if binary else 'w') as f:
            total = 0
            chunk_size = 1024
            for chunk in response.iter_content(chunk_size):
                try:
                    f.write(chunk)
                except TypeError:
                    raise TypeError("trying to write bytes as unicode text - "
                                    "try running in binary (-b) mode")
                total += chunk_size
                if size is not None and not quiet:
                    pbar.print_progress(total, size)
            if size is not None and not quiet:
                pbar.print_end()

# defaults

def get_default_proxy() -> ProxyInfo:
    """ Get the default proxy with a more useful error on not being defined

    :return: ProxyInfo
        The default proxy
    :Raises: RuntimeError
        If there is no default proxy
    """
    try:
        return default_proxy
    except (NameError, AttributeError):
        raise RuntimeError("No default proxy found -- "
                           "please supply one") from None

# Attempt to import the default_proxy
# If it fails, default_proxy will not be an attribute of this file and
# a warning will be raised
try:
    default_proxy = ProxyInfo.from_json(default_proxy_path)
except FileNotFoundError:
    warn(f"No defaults file found @ {default_proxy_path}")
except json.JSONDecodeError as e:
    warn(f"Unable to decode json @ {default_proxy_path}: {e}")
except (TypeError, ValueError) as e:
    warn(f"Incorrect proxy json @ {default_proxy_path}: {e}")
# unexpected exceptions are raised


if __name__ == '__main__':
    print('ERROR: this file should not be run as a script -- to run proxyget use\n'
          '$ python -m proxyget ...')
