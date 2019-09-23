[![Proxy.Py](ProxyPy.png)](https://github.com/abhinavsingh/proxy.py)

[![License](https://img.shields.io/github/license/abhinavsingh/proxy.py.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![PyPi Downloads](https://img.shields.io/pypi/dm/proxy.py.svg?color=green)](https://pypi.org/project/proxy.py/)
[![Docker Pulls](https://img.shields.io/docker/pulls/abhinavsingh/proxy.py?color=green)](https://hub.docker.com/r/abhinavsingh/proxy.py)
[![Build Status](https://travis-ci.org/abhinavsingh/proxy.py.svg?branch=develop)](https://travis-ci.org/abhinavsingh/proxy.py/)
[![No Dependencies](https://img.shields.io/static/v1?label=dependencies&message=none&color=green)](https://github.com/abhinavsingh/proxy.py)
[![Coverage](https://coveralls.io/repos/github/abhinavsingh/proxy.py/badge.svg?branch=develop)](https://coveralls.io/github/abhinavsingh/proxy.py?branch=develop)

[![Python 3.5](https://img.shields.io/badge/python-3.5-blue.svg)](https://www.python.org/downloads/release/python-350/)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![Checked with mypy](https://img.shields.io/static/v1?label=mypy&message=checked&color=blue)](http://mypy-lang.org/)

[![Maintenance](https://img.shields.io/static/v1?label=maintained%3F&message=yes&color=green)](https://gitHub.com/abhinavsingh/proxy.py/graphs/commit-activity)
[![Ask Me Anything](https://img.shields.io/static/v1?label=need%20help%3F&message=ask&color=green)](https://twitter.com/imoracle)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-green.svg)](https://github.com/abhinavsingh/proxy.py/issues)

Features
--------

- Lightweight
    - Distributed as a single file module `~50KB`
    - Uses only `~5-20MB` RAM
    - No external dependency other than standard Python library
- Programmable
    - Optionally enable builtin Web Server
    - Customize proxy and http routing via [plugins](https://github.com/abhinavsingh/proxy.py/blob/develop/plugin_examples.py)
    - Enable plugin using command line option e.g. `--plugins plugin_examples.SaveHttpResponses`
    - Plugin API is currently in development state, expect breaking changes.
- Supports `http`, `https`, `http2` and `websockets` request proxy
- Optimized for large file uploads and downloads
- IPv4 and IPv6 support
- Basic authentication support
- Can serve a [PAC (Proxy Auto-configuration)](https://en.wikipedia.org/wiki/Proxy_auto-config) file

Install
-------

#### Stable version

	$ pip install --upgrade proxy.py

#### Development version

    $ pip install git+https://github.com/abhinavsingh/proxy.py.git@develop

#### Docker image

    $ docker run -it -p 8899:8899 --rm abhinavsingh/proxy.py:v1.0.0

By default `docker` binary is started with following flags:

    --hostname 0.0.0.0 --port 8899 --ipv4

To override input flags, start docker image as follows.
For example, to check `proxy.py --version`:

    $ docker run -it \
        -p 8899:8899 \
        --entrypoint /app/proxy.py \
        --rm abhinavsingh/proxy.py:v1.0.0 \
        --version

[![WARNING](https://img.shields.io/static/v1?label=MacOS&message=warning&color=red)](https://github.com/moby/vpnkit/issues/469)
`docker` support is currently BROKEN on `macOS` due to incompatibility with [vpnkit](https://github.com/moby/vpnkit/issues/469).

Usage
-----

```
$ proxy.py -h
usage: proxy.py [-h] [--backlog BACKLOG] [--basic-auth BASIC_AUTH]
                [--client-recvbuf-size CLIENT_RECVBUF_SIZE]
                [--disable-headers DISABLE_HEADERS] [--disable-http-proxy]
                [--hostname HOSTNAME] [--ipv4] [--enable-web-server]
                [--log-level LOG_LEVEL] [--log-file LOG_FILE]
                [--log-format LOG_FORMAT] [--num-workers NUM_WORKERS]
                [--open-file-limit OPEN_FILE_LIMIT] [--pac-file PAC_FILE]
                [--pac-file-url-path PAC_FILE_URL_PATH] [--pid-file PID_FILE]
                [--plugins PLUGINS] [--port PORT]
                [--server-recvbuf-size SERVER_RECVBUF_SIZE] [--version]

proxy.py v1.0.0

optional arguments:
  -h, --help            show this help message and exit
  --backlog BACKLOG     Default: 100. Maximum number of pending connections to
                        proxy server
  --basic-auth BASIC_AUTH
                        Default: No authentication. Specify colon separated
                        user:password to enable basic authentication.
  --client-recvbuf-size CLIENT_RECVBUF_SIZE
                        Default: 1 MB. Maximum amount of data received from
                        the client in a single recv() operation. Bump this
                        value for faster uploads at the expense of increased
                        RAM.
  --disable-headers DISABLE_HEADERS
                        Default: None. Comma separated list of headers to
                        remove before dispatching client request to upstream
                        server.
  --disable-http-proxy  Default: False. Whether to disable
                        proxy.HttpProxyPlugin.
  --hostname HOSTNAME   Default: 127.0.0.1. Server IP address.
  --ipv4                Whether to listen on IPv4 address. By default server
                        only listens on IPv6.
  --enable-web-server   Default: False. Whether to enable
                        proxy.HttpWebServerPlugin.
  --log-level LOG_LEVEL
                        Valid options: DEBUG, INFO (default), WARNING, ERROR,
                        CRITICAL. Both upper and lowercase values are allowed.
                        You may also simply use the leading character e.g.
                        --log-level d
  --log-file LOG_FILE   Default: sys.stdout. Log file destination.
  --log-format LOG_FORMAT
                        Log format for Python logger.
  --num-workers NUM_WORKERS
                        Defaults to number of CPU cores.
  --open-file-limit OPEN_FILE_LIMIT
                        Default: 1024. Maximum number of files (TCP
                        connections) that proxy.py can open concurrently.
  --pac-file PAC_FILE   A file (Proxy Auto Configuration) or string to serve
                        when the server receives a direct file request. Using
                        this option enables proxy.HttpWebServerPlugin.
  --pac-file-url-path PAC_FILE_URL_PATH
                        Default: /. Web server path to serve the PAC file.
  --pid-file PID_FILE   Default: None. Save parent process ID to a file.
  --plugins PLUGINS     Comma separated plugins
  --port PORT           Default: 8899. Server port.
  --server-recvbuf-size SERVER_RECVBUF_SIZE
                        Default: 1 MB. Maximum amount of data received from
                        the server in a single recv() operation. Bump this
                        value for faster downloads at the expense of increased
                        RAM.
  --version, -v         Prints proxy.py version.

Proxy.py not working? Report at:
https://github.com/abhinavsingh/proxy.py/issues/new
```
