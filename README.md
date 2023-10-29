## Running

This is the lovebrew [bundler site](http://bundle.lovebrew.org) automation suite. First, dependencies via `pip install -e .`. Once that is done, determine what test file to run:

1. Frontend
  -  The [webserver client](https://github.com/lovebrew/lovebrew-frontend) and [webserver backend](https://github.com/lovebrew/lovebrew-webserver) must be running together locally.
2. Backend
  - The [webserver backend](https://github.com/lovebrew/lovebrew-webserver) must be running locally.

In either case, you must make a `config.toml` within `bundler_qa`:
```toml
[driver]
base_url = "{webclient url}"
data_url = "{webserver url}"
browser  = "{chrome,firefox}"
```

Once done, run `pip -m pytest bundler_qa/{file}.py` to run the desired tests.
