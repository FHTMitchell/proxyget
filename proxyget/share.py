#! /usr/bin/env python3
"""
proxy -- share.py

author  - fmitchell
created - 2018-Apr-19
"""
from __future__ import annotations

import os
import functools

import proxyget

default_proxy_info = proxyget.default_proxy

def make_proxy(proxy_info: proxyget.ProxyInfo = default_proxy_info) -> str:
    r""" Make a proxy of the form `http://{domain}\{user}:{password}@{server}`

    :param proxy_info: ProxyInfo
        server: str - URL or IP
        domain: str - username domain
        user: str? - username or None (if None, will get automatically)
    :return: proxy string
    """
    return proxyget.make_proxy(proxy_info)['http']


def logger(verbose: bool):
    """ Produces a logger function which only prints if the initial verbose value
    was true

    :param verbose:
    :return: callable function which takes the arguments of print
    """
    @functools.wraps(print)
    def printer(*args, **kwargs) -> None:
        if verbose:
            print(*args, **kwargs)
    return printer


def run_cmd(cmd: str, name: str = None) -> None:
    """ Run the command given

    :param cmd: The complete command
    :param name: Optional name of command for error message (name failed ...)
    :return: None
    """
    exit_code = os.system(cmd)
    if exit_code != 0:
        name = name if name is not None else cmd
        raise RuntimeError(f"{name} failed with exit code {exit_code}")


if __name__ == '__main__':
    raise RuntimeError("proxyget.share cannot be run")
