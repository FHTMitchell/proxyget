proxyget - for getting through proxies you have access to but no admin
control

python must be version 3.6 or greater

To run in python

    $ python
    >>> import proxyget
    >>> proxyget.get(...)

or in terminal:
(proxyget directory must be in PYTHONPATH or current working directory)

    $ python -m proxyget ...
    
To download file either in python

    proxyget.get_file(<url>)
    
or in terminal
    
    $ python -m proxyget --file <url> --out <outfile.exe>
    
For futher help

    $ python -m proxyget --help