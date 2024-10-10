""" Module providing the CommonCoin class, which is the base class for coin classes Btc, Kaspa and Ethereum. """
# Copyright (C) 2024 Chancellor - License GPLv3
import math
import numpy as np

from power_law.data.data_formatter import DataFormatter
from power_law.trendline.trendline import Trendline
from power_law.visualization.plotter import Plotter
from power_law.trendline import regression

class CommonCoin:
    """
    This class contains the common functionality for all coin classes (Btc, Kaspa and Ethereum). It retrieves price data from the
    DataFormatter class, creates power law trend lines with the Trendline class and plots the graph with the Plotter class.

    Attributes:
        config (dict): Dictionary containing the general and coin configuration from the config.yaml file, and the command line
            arguments.
        data_formatter (DataFormatter): A DataFormatter object responsible for formatting and retrieving time and price data and
            other data related functions.
        years (list): List of floats representing time in years since epoch (usually the coin's birthday, so effectively years is
            the coin's age). This list corresponds with the prices list.
        prices (list): List of floats representing the coin's prices in US$ corresponding with the years (i.e. age) list.
        last_year (float): The latest age of the coin (according to the last yaml time-price data) + future_years (i.e. the number
            of years that the trendlines predict the price in the future)
        years_extended (list): List of floats similar to years, but extending into the future for future_years (rounded up to the
            nearest integer).
        lower_trendline (Trendline): Power law Trendline object representing the bottom of the price channel; also called support.
        upper_trendline (Trendline): Power law Trendline object representing the top of the price channel; also called resistance.
        lower_trendline_points (list): List of floats representing the bottom of the price channel. Corresponds with years_extended.
        upper_trendline_points (list): List of floats representing the top of the price channel. Corresponds with years_extended.
        x_axis_ticks (dict): A dictionary containing a list of floats representing the time of the start of each Gregorian calendar
            year in years since the coin's epoch (usually it's birthday) and a list of integers (the labels) representing years
            according to the Gregorian calendar since the coin's epoch.
        __plotter (Plotter): The (private) plotter that actually plots the graph. Because instantiating this object immediately
            spawns a GUI, it is initialized as None and only constructed once it's used (through the get_plotter() function).
    """

    def __init__(self, config: dict):
        """ Constructor for the CommonCoin class.

        Args:
            config (dict): Dictionary containing the general and coin configuration from the config.yaml file, and the command line
                arguments.
        """

        self.config = config

        self.data_formatter = DataFormatter(config['coin']['data'])
        self.years, self.prices = self.data_formatter.get_data()

        self.last_year = self.years[-1] + config['arguments']['future_years']
        self.years_extended = list(np.arange(self.years[0], math.ceil(self.last_year), 1/365.25))

        self.lower_trendline = Trendline.config(config['coin']['lower_trendline'])
        self.upper_trendline = Trendline.config(config['coin']['upper_trendline'])

        self.lower_trendline_points = self.lower_trendline.compute_list(self.years_extended)
        self.upper_trendline_points = self.upper_trendline.compute_list(self.years_extended)

        # Member variable because its are accessed by the YoyRoi class to compute the year-over-year price appreciation.
        self.x_axis_ticks = self.data_formatter.get_year_ticks(self.last_year)

        # Make sure CommonCoin instance can exist without Plotter, since creating a Plotter immediately spawns a GUI window.
        # E.g. the YoyRoi class instantiates Btc, Kaspa and Ethereum classes, all without wanting to show their price charts.
        self.__plotter = None

    def get_plotter(self) -> Plotter:
        """
        This function gives access to the private __plotter object that is responsible for the actual plotting of the graph. It gets
        constructed on the first call (__plotter is None after object initialization).

        Returns:
            Plotter: A Plotter object.
        """
        if self.__plotter is None:
            plot_config = { 'plot' : self.config['coin']['plot'],
                            'general' : self.config['general'],
                            'scale' : self.config['arguments']['scale'] }
            self.__plotter = Plotter(plot_config)
        return self.__plotter

    def __get_label(self, prefix: str, trendline: Trendline) -> str:
        """ Helper function that creates a label entry for in the graph's legend matching with the trendline argument.

        Args:
            prefix (str): Prefix name for the trendline (e.g. Support or Resistance).
            trendline (Trendline): a Trendline object, used for extracting its formula in textual form.

        Returns:
            str: The label for this trendline.
        """
        epoch_year = self.data_formatter.get_epoch_year()
        return prefix + trendline.get_formula(epoch_year)

    def common_plotting(self):
        """
        This function is responsible for plotting common graph elements, such as a month grid, upper and lower trendlines,
        Gregorian calendar year labels along the horizontal axis and optionally a regression line.
        """
        month_list = self.data_formatter.get_months(math.ceil(self.last_year))
        self.get_plotter().plot_months(month_list, self.upper_trendline_points[-1])
        labels = (self.__get_label("Support: ", self.lower_trendline), self.__get_label("Resistance: ", self.upper_trendline))
        self.get_plotter().plot_trendlines(self.lower_trendline_points, self.upper_trendline_points, self.years_extended, labels)
        self.get_plotter().set_xticks(self.x_axis_ticks)

        if self.config['arguments']['regression']:
            self.regression_analysis()

    @staticmethod
    def compute_normalized_price(prices: list, lower_trendline: list, upper_trendline: list) -> list:
        """ Computes a list of normalized prices with respect to the lower and upper trendline arguments.

        Args:
            prices (list): List of floats of actual prices.
            lower_trendline (list): List of floats of lower trendline prices.
            upper_trendline (list): List of floats of upper trendline prices.

        Returns:
            list: List of floats of normalized prices. Normally in the range [0, 1] with 0 touching the lower trendline and
                1 touching the upper trendline, although it can exceed these bounds since the price could briefly go outside
                of these trendlines.
        """
        return [(price - lt) / (ut - lt) for price, lt, ut in zip(prices, lower_trendline, upper_trendline)]

    def regression_analysis(self):
        """
        This function performs linear regression in log-log space and constructs a power law trendline from it which is shown in the graph.
        """
        a, k, r2 = regression.compute_regression(self.years, self.prices)
        regression_trendline = Trendline(a, k)
        regression_points = regression_trendline.compute_list(self.years_extended)
        self.get_plotter().plot(self.years_extended, regression_points, 'purple',
            self.__get_label("Regression ($R^2: " + f"{r2:.3f}" + "$): ", regression_trendline))
