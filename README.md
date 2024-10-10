# Power law trendlines for Bitcoin & Kaspa

This repository contains Python code that can visualize the Bitcoin, Kaspa (and Ethereum) price together with their power law price channels and/or regression lines on linear, log-linear or log-log graphs. These graphs were first shown in [this Medium article](https://medium.com/@chancelloronbrinkofbailout/bitcoin-kaspa-dacc84b6d65d).

Additionally, it can show the year-over-year return on investment for all these assets based on the supporting trendline and it can show the regression results (including $R^2$) over time for all assets. With a valid (free) CoinAPI license all price data can be kept up-to-date (see below). All graphs are interactive, meaning you can zoom in for a close-up.

Note that Ethereum was added just for reference. It's price doesn't follow a power-law convincingly. Its upper and lower trendlines only have 2 price points supporting them, and the regression line has an $R^2$ of just ~0.8 (compared to an $R^2$ of ~0.95 for Bitcoin and Kaspa) and it doesn't continue trending between the bounding trendlines. Nonetheless, it seems to be the only other cryptocurrency that has a price development that at least somewhat follows a power-law.

## Installation

### Installation from PyPI - The Python Package Index server (recommended)

#### Windows (>=10)

Please make sure Python (>=3.8) is installed. If not, go to e.g. Microsoft Store, search for `python` and install a version >= 3.8. Next, open a command prompt, confirm that Python >= 3.8 was properly installed (with `py --version`), and execute:
```
> py -m venv .venv
> .venv\Scripts\activate
(.venv) > py -m pip install --upgrade pip
(.venv) > py -m pip install pow-law
```

After installation you can execute this tool with e.g. flag `-h` (for showing its use):
```
(.venv) > pow-law -h
```

Deactivate the Python virtual environment when you're done:
```
(.venv) > deactivate
```

Don't forget to re-activate the Python virtual environment (from the installation directory) when you want to use this tool again:
```
> .venv\Scripts\activate
(.venv) > pow-law -h
```

#### Ubuntu (>=20.04)

Ubuntu 20.04 and later has Python >=3.8 pre-installed (confirm with `python3 --version`). Make sure you have Python packages `pip` (confirm with `python3 -m pip --version`) and `venv` (confirm with e.g. `python3 -m venv --h`) installed. If not, please execute:
```
$ sudo apt-get update && sudo apt-get install python3-venv
```
and/or
```
$ python3 -m ensurepip --default-pip
```

Next, install the `pow-law` tool with:
```
$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv) $ python3 -m pip install --upgrade pip
(.venv) $ python3 -m pip install pow-law
```

After installation you can execute this tool with e.g. flag `-h` (for showing its use):
```
(.venv) $ pow-law -h
```

Deactivate the Python virtual environment when you're done:
```
(.venv) $ deactivate
```

Don't forget to re-activate the Python virtual environment (from the installation directory) when you want to use this tool again:
```
$ source .venv/bin/activate
(.venv) $ pow-law -h
```

### From the Github repository

Go to the [pow-law github repository](https://github.com/Chancellor-1/power_law), click the green `<> Code` button, click `Download ZIP` and extract the ZIP archive, or open a terminal / command prompt and execute: `git clone https://github.com/Chancellor-1/power_law.git` (for this Git needs to be installed).

#### Windows (>=10)

Please make sure Python (>=3.8) is installed. If not, go to e.g. Microsoft Store, search for `python` and install a version >= 3.8. Next, open a command prompt, confirm that Python >= 3.8 was properly installed (with `py --version`), go to the root of this repository and execute:
```
> .\setup.bat
```

After installation you can execute this tool with e.g. flag `-h` (for showing its use):
```
> .\run.bat -h
```

#### Ubuntu (>=20.04)

Ubuntu 20.04 and later has Python >=3.8 pre-installed (confirm with `python3 --version`). Make sure you have Python packages `pip` (confirm with `python3 -m pip --version`) and `venv` (confirm with e.g. `python3 -m venv --h`) installed. If not, please execute:
```
sudo apt-get update && sudo apt-get install python3-venv
```
and/or
```
python3 -m ensurepip --default-pip
```

Next, open a command prompt, go to the root of this repository and execute:
```
$ ./setup.sh
```

After installation you can execute this tool with e.g. flag `-h` (for showing its use):
```
$ ./run.sh -h
```

#### Other operating systems

Since Python can run on pretty much any OS it should be quite straightforward to install this package on e.g. macOS or other Unix/Linux-based OS's, possibly with some minor adaptations.

## Some usage examples

Below examples assume you've activated the Python virtual environment that you used for the installation. When running from within the repository and outside the virtual environment, you can also use the `./run.sh` (Ubuntu) or `.\run.bat` (Windows) scripts.

1. To show the Bitcoin price (`-b`), together with its regression line (`-r`) and extend its trendlines for 5 future years (`-y 5`) on a log-log chart (`-s loglog`, which is the default) do:
```
(.venv) $ pow-law -b -r -y 5
```

2. To show the Kaspa price (`-k`) on a log-linear chart (`-s loglin`) and extend its trendlines for 8 years (`-y 8`, which is the default) and update it's price via CoinAPI (`-u`, for this you need a valid CoinAPI license; see paragraph `Updating prices` below)
```
(.venv) $ pow-law -k -s loglin -u
```

3. To show the Ethereum price (`-e`), together with its regression line (`-r`) and no future years (`-y 0`) on a regular linear chart (`-s linlin`) do:
```
(.venv) $ pow-law -e -r -y 0 -s linlin
```

4. To show the year-over-year return on investment (`-a`) for all assets for 15 future years (`-y 15`) on a regular linear chart (`-s linlin`) do:
```
(.venv) $ pow-law -a -y 15 -s linlin
```

5. To show the regression results and the $R^2$ over time for all assets (`-r2`) on a linear chart (only option for this mode) do:
```
(.venv) $ pow-law -r2 -s linlin
```

For more advanced settings please take a look at the `./power_law/config/config.yaml` file. From this configuration file the trendlines can be updated and graph settings can be adjusted (e.g. resolution, line widths, YoY ROI start year etc.).

## Updating prices

Price data for all assets can be updated via CoinAPI, but you need a valid license for this. You can obtain a (free) CoinAPI license from [coinapi.io](https://www.coinapi.io/get-free-api-key?product_id=market-data-api). Once you have a CoinAPI license code, execute below (the X's represent your license code; make sure to include the hyphens):
```
(.venv) $ pow-law -l XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
```

After this, the price data for the selected asset (`-b` for Bitcoin, `-k` for Kaspa, `-e` for Ethereum, `-a` for all assets) can be updated by adding the `-u` flag.

### Note for developers

If you're a developer you can make sure the updated `power_law/price_update/coinapi_license.txt` no longer shows up as a changed file in the git repository with:
```
git update-index --assume-unchanged ./power_law/price_update/coinapi_license.txt
```

This ensures that you're not accidentally committing your license code. You can undo this with the `--no-assume-unchanged` git flag.

## Generating documentation

This project uses Google style Docstrings. You can generate documentation with e.g. `pdoc` (install with `pip install pdoc`). Generating documentation with `pdoc` in e.g. output folder `docs` can be done with `pdoc -d google -o docs --math ./power_law`.

## Contact

If you have comments or suggestions please contact me via chancelloronbrinkofbailout@gmail.com. In case you value this tool and would like to buy me a coffee, please feel free to do so via:

```
kaspa:qz7zuyjn6xwy5m9drflgk3rdw6ljlqy0rcjwnrvft2s022vcw88ccw0q2s5ev
```

## License

The GNU General Public License v3 applies to this software package. Please see file `LICENSE` in the root of this project for the full license notice.
