#! /usr/bin/env python3
# proxyget.py

import string
import functools
import requests
import urllib.request  # don't import . from . -- request + requests = confusing
from pathlib import Path
from getpass import getuser, getpass
from typing import Any, Optional, Dict, NamedTuple, Union, Mapping

__all__ = ['make_proxy', 'make_kwargs', 'get', 'getexe',
           'clear_password_cache', 'ProxyInfo']

PathType = Union[Path, str]

_test_url = "http://example.com"


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
    domain: str
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
            raise TypeError(f'server must be a str, not'
                            f' {self.server.__class__.__name__}')

        if not isinstance(self.domain, str):
            raise TypeError(f'domain must be a str, not'
                            f' {self.domain.__class__.__name__}')

        if self.usr is not None and not isinstance(self.usr, str):
            raise TypeError(f'usr must be None or a str, not'
                            f' {self.usr.__class__.__name__}')

        if not isinstance(self.port, int):
            raise TypeError(f'port must be an int, not'
                            f' {self.port.__class__.__name__}')

        if not (0 <= self.port <= 65535):
            raise ValueError(
                    f"port ({self.port!r}) must be between 0 and 65535 inclusive")

    def copy_with(self, server: str = None, port: int = None,
                  domain: str = None, usr: str = None) -> 'ProxyInfo':
        server = self.server if server is None else server
        port = self.port if port is None else port
        domain = self.domain if domain is None else domain
        usr = self.usr if usr is None else usr
        return ProxyInfo(server, port, domain, usr)


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
    make_proxy_and_save.clear_cache()


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

    info.assert_correct()
    server, port, domain, usr = info

    if debug:
        print(f"Using proxy address: {server!r}")
        print(f"Using domain name: {domain!r}")
        if usr: print(f"using username: {usr!r}")

    usr = usr or getuser()
    usr = make_url_safe(usr)

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



def get(url: str, *args: Any, proxy_info: ProxyInfo, nosave: bool = False,
        **kwargs: Any) -> requests.Response:
    """ Make a request to `url` via a proxy

    :param url: str
        The url to request
    :param args: Any
        Additional positonal args to pass to `requests.get`

    :param proxy_info: ProxyInfo
        a namedtuple of the form
            (server: str, port: int, domain: str, usr: str?)

    :param nosave: bool
        If True, save any passwords entered for a given `proxy_info`. In order
        to clear the password cache, call `clear_password_cache()`
    :param kwargs: Any
        Additional arguments to pass to `requests.get` or
        `urllib.request.urlretrieve`

    :return: requests.Request
        The request object recieved from the URL via the proxy

    :raises: requests.RequestException
        Or any subclass thereof
            e.g. if the url does not exist or the proxy was incorrect
    """

    return requests.get(url, *args,
                        **make_kwargs(proxy_info=proxy_info,
                                      nosave=nosave, **kwargs))


def getexe(url: str, filename: PathType, proxy_info: ProxyInfo,
           nosave: bool = False, **kwargs: Any) -> None:

    proxies = make_proxy(proxy_info) \
        if nosave else make_proxy_and_save(proxy_info)

    handler = urllib.request.ProxyHandler(proxies)
    opener = urllib.request.build_opener(handler)
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(url, str(filename), **kwargs)
