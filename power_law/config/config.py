""" Module providing the Config class used for configuration parsing """
# Copyright (C) 2024 Chancellor - License GPLv3
import os
import sys
import argparse
from importlib.metadata import version
import yaml

class Config:
    """
    This class can parse the command line arguments and it can parse the configuration YAML file.

    Attributes:
        parser (argparse.ArgumentParser): The argument parser.
        args (argparse.Namespace): Namespace containing all arguments.
        yaml_config (dict): Dictionary of data from the config.yaml file.
    """

    def __init__(self):
        """ Constructor for the Config class. """
        self.parser = argparse.ArgumentParser(prog='pow_law',
            description="This tool can visualize the Bitcoin, Kaspa or Ethereum price together with "
                        "its power law price channel, among other related functionality.")
        self.parser.add_argument('-v', '--version', action='version', version=version('pow_law'))
        self.parser.add_argument('-u', '--update', action='store_true',
            help="Update price data of selected asset(s) ('-b', '-k', '-e' or '-a') via CoinAPI "
                 "(valid CoinAPI license needed).")
        self.parser.add_argument('-r', '--regression', action='store_true',
            help="Perform regression analysis and show regression line in plot (combine with '-b', '-k' or '-e').")
        self.parser.add_argument('-s', '--scale', action='store', type=str, default='loglog', choices=['loglog', 'loglin', 'linlin'],
            help="Sets the graph scaling to either linear price & linear time (-s linlin), "
                 "logarithmic price & linear time (-s loglin) or log price & log time (-s loglog). Default: loglog.")
        self.parser.add_argument('-y', '--years', action='store', type=int, default=8,
            help="Number of future years to plot beyond the current price data (extending the power law trendlines). Default: 8.")
        asset_type = self.parser.add_mutually_exclusive_group(required=True)
        asset_type.add_argument('-k', '--kaspa', action='store_true',
            help="Show price data and power law price channels for Kaspa.")
        asset_type.add_argument('-b', '--bitcoin', action='store_true',
            help="Show price data and power law price channels for Bitcoin.")
        asset_type.add_argument('-e', '--ethereum', action='store_true',
            help="Show price data and 'power law' price channels for Ethereum.")
        asset_type.add_argument('-a', '--all', action='store_true',
            help="Show year-over-year return on investment based on supporting trendline for all assets.")
        asset_type.add_argument('-r2', '--r2_over_time', action='store_true',
            help="Show regression results and R^2 over time for all assets.")
        asset_type.add_argument('-l', '--license', action='store', type=str, help="Sets the CoinAPI license code.")

        self.args = argparse.Namespace(scale = 'loglog', future_years = 8, regression = False) # default coin arguments

        self.yaml_config = self.__get_yaml_config()

    def get_program_arguments(self) -> argparse.Namespace:
        """
        This function retrieves the command line arguments (in case of valid arguments other than '-v' and '-h').

        Returns:
            argparse.Namespace: Object storing the command line arguments as attributes.
        """
        self.args = self.parser.parse_args()
        self.__verify_arguments()
        return self.args

    def import_arguments(self, args: list) -> argparse.Namespace:
        """
        This function converts the input list into an argparse.Namespace object.
        This can be useful when using this package from within e.g. a Jupyter Notebook.

        Args:
            args (list): List of command line arguments, e.g. ['-b', '-y 3']

        Returns:
            argparse.Namespace: Object storing the input arguments as attributes.
        """
        self.args = self.parser.parse_args(args)
        self.__verify_arguments()
        return self.args

    def get_coin_config(self, coin: str) -> dict:
        """
        Retrieves the coin configuration specified by the coin string argument.

        Args:
            coin (str): String specifying the coin type ('btc', 'eth', 'kas' or 'all')
        """
        if coin == 'all':
            return { 'yaml' : self.yaml_config, 'arguments' : self.__get_coin_arguments() }
        return { 'coin' : self.yaml_config[coin], 'general' : self.yaml_config['general'], 'arguments' : self.__get_coin_arguments() }

    def __verify_arguments(self):
        """ Private function to verify (and possibly adjust) the parsed arguments. """
        if self.args.years < 0 or self.args.years > 116:
            print("Future years cannot be less than 0 or greater than 116. Exiting...")
            sys.exit(os.EX_CONFIG)

        if self.args.all and self.args.scale == 'loglog':
            print("YoY ROI plot doesn't support logarithmic scaling of the horizontal axis. Plotting linear X-axis.")
            self.args.scale = 'loglin'

        if self.args.r2_over_time and self.args.scale != 'linlin':
            print("The regression results plot doesn't support logarithmic scaling. Plotting linear axes.")
            self.args.scale = 'linlin'

        if self.args.r2_over_time and self.args.update:
            print("No price data update possible in regression over time mode (use '-u' in combination with '-b', '-k', '-e' or '-a').")

    def __get_coin_arguments(self) -> dict:
        """
        This function returns the command line arguments for the coin classes as a dictionary.
        Should be called after get_program_arguments() or import_arguments(); otherwise uses default settings.
        """
        return { 'scale': self.args.scale, 'future_years': self.args.years, 'regression': self.args.regression }

    def __get_yaml_config(self) -> dict:
        """ This function returns the configuration in the config.yaml file as a dictionary. """
        try:
            with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'r', encoding='UTF-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print("Could not load the power_law/config/config.yaml file. Does it exist? Exiting...")
            sys.exit(os.EX_IOERR)
