# Proxyget

Use to retrieve files and web APIs through proxies you have access to but 
no admin control

___

For Python must be version 3.6 or greater

To run in python

    $ python
    >>> import proxyget
    >>> proxyget.get(...)

or in terminal:

    $ python -m proxyget ...
    
To download file either in python

    proxyget.get_file(<url>)
    
or in terminal
    
    $ python -m proxyget <url> --out <outfile.exe>
    
For further help

    $ python -m proxyget --help

___ 

To avoid putting in the proxy address each time create a file in the 
[proxyget](proxyget) subdirectory called `default_proxy.json` of the form

    {
      "server": <address_as_string>,
      "port": <port_as_int>,
      "domain": <domain_as_string_can_be_empty>
    }
