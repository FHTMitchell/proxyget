# Proxyget

Use to retrieve files and web APIs through proxies you have access to but 
no admin control

## Installation

`git clone` this repository and then install using `pip install`

If installing behind a proxy you might need to do something like this

    $ git config --global --add http.proxy "http://<username>:<password>@<proxy-server>:<port>"
    $ git clone https://github.com/fhtmitchell/proxyget.git
    $ git config --global --unset http.proxy
    
On the bright side `proxyget.gitclone` will do this for you automatically when 
you have it installed.

## Requirements

* `python >= 3.6.0`
* `requests >= 2.20.0`

## Usage 

To run in python

    $ python
    >>> import proxyget
    >>> proxyget.get(...)

or in terminal:

    $ python -m proxyget ...
    
To download file either in python

    proxyget.get_file(<url>)
    
or in terminal
    
    $ python -m proxyget <url> --out <outfile.html>
    $ python -m proxyget <url> -b --out <outfile.exe>  # binary file
    
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

For example

    {
        "server": "255.1.1.127",
        "port": 80,
        "domain": ""
    }

___

There are two additional subcommands `proxyget.gitclone` and `proxyget.npminstall` 
that will run `git clone` and `npm install` directly. For these to work the 
`default_proxy.json` must have been created. Run from the terminal as

    $ python -m proxyget.gitclone <url.git>
