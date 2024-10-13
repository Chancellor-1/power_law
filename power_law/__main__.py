#!/usr/bin/env python3
# Copyright (C) 2024 Chancellor - License GPLv3
""" Main power_law package entry point. """
import sys
import os

from power_law.config.config import Config
from power_law.coins.bitcoin import Bitcoin
from power_law.coins.kaspa import Kaspa
from power_law.coins.ethereum import Ethereum
from power_law.price_update import coin_api
from power_law.visualization.yoy_roi import YoyRoi
from power_law.visualization.regression_over_time import RegressionOverTime

def main() -> int:
    """ Main entry point. """
    config = Config()
    args = config.get_program_arguments()

    if args.bitcoin:
        btc_config = config.get_coin_config('btc')
        if args.update:
            coin_api.update_price_data(btc_config['coin']['data'])
        btc = Bitcoin(btc_config)
        btc.plot_bitcoin()
    elif args.kaspa:
        kas_config = config.get_coin_config('kas')
        if args.update:
            coin_api.update_price_data(kas_config['coin']['data'])
        kas = Kaspa(kas_config)
        kas.plot_kaspa()
    elif args.ethereum:
        eth_config = config.get_coin_config('eth')
        if args.update:
            coin_api.update_price_data(eth_config['coin']['data'])
        eth = Ethereum(eth_config)
        eth.plot_ethereum()
    elif args.all:
        if args.update:
            coin_api.update_price_data(config.get_coin_config('btc')['coin']['data'])
            coin_api.update_price_data(config.get_coin_config('kas')['coin']['data'])
            coin_api.update_price_data(config.get_coin_config('eth')['coin']['data'])
        yoyroi = YoyRoi(config)
        yoyroi.plot_yoy_roi()
    elif args.r2_over_time:
        regression_over_time = RegressionOverTime(config)
        regression_over_time.plot_regression_over_time()
    else: # only flag left is `-l` for CoinAPI license update
        coin_api.update_license_code(args.license)

    return os.EX_OK if sys.platform != 'win32' else 0

if __name__ == "__main__":
    sys.exit(main())
