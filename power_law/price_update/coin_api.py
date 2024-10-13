""" This module contains CoinAPI related functions for updating price data. """
# Copyright (C) 2024 Chancellor - License GPLv3
import datetime
import json
import os
import sys
from urllib.error import HTTPError, URLError
from coinapi_rest_v1.restapi import CoinAPIv1

def __read_license_file() -> str:
    """ This function returns the license code from the coinapi_license.txt file. """
    with open(os.path.join(os.path.dirname(__file__), 'coinapi_license.txt'), 'r', encoding='UTF-8') as file:
        return file.read().rstrip()

def __get_first_timestamp(directory: str, filename: str) -> int:
    """ This function returns the first Unix timestamp from the price data json file located in ../data/directory/filename.

    Args:
        directory (str): The directory in the ../data folder from which to read the file specified by filename.
        filename (str): The filename of the file containing the price data from which to retrieve the first Unix timestamp.

    Returns:
        int: First Unix timestamp in the file specified by filename.
    """
    try:
        with open(os.path.join(os.path.dirname(__file__), '../data', directory, filename), 'r', encoding='UTF-8') as file:
            json_data = json.load(file)
            return json_data[0][0]
    except FileNotFoundError:
        print("Could not read first timestamp from file " + filename + ". Exiting...")
        if sys.platform != 'win32':
            sys.exit(os.EX_IOERR)
        else:
            sys.exit(1)

def __write_timestamp_price_pairs(ohlcv_historical_data: list, directory: str, filename: str):
    """ This function writes the time - price data (ohlcv_historical_data) to a JSON file specified by the filename argument.

    Args:
        ohlcv_historical_data (list): A list containing dictionaries with trading related data (e.g. timestamps, prices, volumes etc.).
            This function uses keys 'time_close' and 'price_close', which are the timestamps and prices at the closing of the market,
            which is non-existent for crypto assets because of 24/7 trading, but corresponds with midnight Greenwich time (UTC 0).
        directory (str): The directory in the ../data folder to which to write the file specified by filename.
        filename (str): The filename of the file to write the time - price data to. Should be a JSON file with .json extension.
    """
    timestamp_price_pair_array = []
    for period in ohlcv_historical_data:
        time_close_str = period['time_close']
        time_close_dt = datetime.datetime.fromisoformat(time_close_str[:-5]).astimezone(datetime.timezone.utc)
        timestamp_ms = (int)(time_close_dt.replace(tzinfo=datetime.timezone.utc).timestamp() * 1000)
        price = period['price_close']
        timestamp_price_pair_array.append([timestamp_ms, price])
    try:
        with open(os.path.join(os.path.dirname(__file__), '../data', directory, filename), 'w', encoding='UTF-8') as file:
            json.dump(timestamp_price_pair_array, file, indent=2)
        print("Successfully updated price data in file " + filename)
    except PermissionError as err:
        print("PermissionError (" + str(err) + ") while trying to write to file " + filename + ". Price data not updated.")
    except OSError as err:
        print("OSError (" + str(err) + ") while trying to write to file " + filename + ". Price data not updated.")
    except Exception as err: # pylint: disable=broad-except
        print("Exception (" + str(err) + ") while trying to write to file " + filename + ". Price data not updated.")

def __retrieve_coinapi_data(directory: str, filename: str):
    """
    This function retrieves CoinAPI time - price data for the coin specified by the directory string (btc, kas, eth), and writes it
    to a JSON file named filename in location ../data/directory.

    Args:
        directory (str): The directory in the ../data folder to which to write the file specified by filename.
            Should be either 'btc', 'kas' or 'eth' (or some future coin still to be added).
        filename (str): The filename of the file to write the time - price data to. Should be a JSON file (with .json extension).
    """
    first_timestamp = __get_first_timestamp(directory, filename)
    try:
        api = CoinAPIv1(__read_license_file())

        dt = datetime.datetime.fromtimestamp(first_timestamp / 1000)
        start_date = datetime.date(dt.year, dt.month, dt.day).isoformat()
        data_id = 'BITSTAMP_SPOT_BTC_USD'
        if directory == 'kas':
            data_id = 'GATEIO_SPOT_KAS_USDT'
        if directory == 'eth':
            data_id = 'COINBASE_SPOT_ETH_USD'

        ohlcv_historical_data = api.ohlcv_historical_data(data_id, {'period_id': '1DAY', 'time_start': start_date, 'limit': 1000})

        __write_timestamp_price_pairs(ohlcv_historical_data, directory, filename)
    except FileNotFoundError:
        print("No coinapi_license.txt file found in the power_law/price_update folder."
              "Please create one and add your license code to it. Price data not updated.")
    except HTTPError:
        print("Reading price data via CoinAPI failed."
              "Please check that your power_law/price_update/coinapi_license.txt file contains a valid license. Price data not updated.")
    except URLError:
        print("Reading price data via CoinAPI failed. Are you connected to the internet? Price data not updated.")
    except Exception as err: # pylint: disable=broad-except
        print("Exception (" + str(err) + ") occurred while reading price data via CoinAPI. Price data not updated.")

def update_price_data(config: dict):
    """
    This function updates the price data for the coin specified by the config dictionary argument. The dictionary should contain keys
    config['directory'], which is a string that is both the directory name and the coin's name ('btc', 'kas' or 'eth'), and
    config['recent_price_file'], which is the filename string of the YAML file in the ../data/config['directory']/ folder containing
    recent price data.

    Args:
        config (dict): Dictionary containing the keys 'directory' and 'recent_price_file' keys.
    """
    __retrieve_coinapi_data(config['directory'], config['recent_price_file'])

def update_license_code(license_code: str):
    """ This function updates the CoinAPI license code in file power_law/price_update/coinapi_license.txt.

    Args:
        license_code (str): String containing the CoinAPI license code (format: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX)
    """
    with open(os.path.join(os.path.dirname(__file__), 'coinapi_license.txt'), 'w', encoding='UTF-8') as file:
        file.write(license_code)
    print("CoinAPI license code was changed to: " + license_code)
