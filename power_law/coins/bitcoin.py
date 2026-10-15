""" Module containing the Bitcoin class. """
# Copyright (C) 2024 Chancellor - License GPLv3
import math
import numpy as np

from power_law.coins.common_coin import CommonCoin
from power_law.trendline.decreasing_trendline import DecreasingTrendline

class Bitcoin(CommonCoin):
    """
    This class contains Bitcoin specific functionality, such as plotting its decreasing upper trendline, its halvings,
    and its periodic trendlines which are based on Bitcoin's halving cycles. It derives from base class CommonCoin.

    Attributes:
        halvings (list): List of integers representing Unix timestamps (in ms) of the moments on which Bitcoin's halvings occurred.
        future_halvings_duration (float): Float representing the expected duration of future Bitcoin halvings in years (~4 years).
        decreasing_trendline (DecreasingTrendline): A DecreasingTrendline object representing Bitcoin's decreasing upper trendline.
    """
    def __init__(self, config: dict):
        """ Constructor of the Bitcoin class.

        Args:
            config (dict): Dictionary containing the general and coin (i.e. Bitcoin) configuration from the config.yaml file, and
                the command line arguments (used in base class CommonCoin).
        """
        super().__init__(config)
        self.halvings = config['coin']['data']['halvings']
        self.future_halvings_duration = config['coin']['data']['future_halvings']
        decreasing_trendline_endpoint_timestamp = config['coin']['decreasing_upper_trendline']['endpoint_timestamp']
        decreasing_trendline_endpoint_year = self.data_formatter.get_yeartime(decreasing_trendline_endpoint_timestamp)
        self.decreasing_trendline = DecreasingTrendline.config(
            {'decreasing_upper_trendline':  config['coin']['decreasing_upper_trendline'],
             'endpoint_year': decreasing_trendline_endpoint_year })

    def plot_bitcoin(self):
        """
        This function plots all Bitcoin graph elements, i.e. the common graph elements (plotted by the base class) and
        the Bitcoin specific graph elements, such as its decreasing upper trendline, its halvings, and its periodic trendlines.
        """
        self.common_plotting()

        self.plot_halvings()

        years_decreasing_trendline, decreasing_trendline_points = self.plot_decreasing_trendline()

        self.plot_periodic_trendline(self.years_extended, self.upper_trendline_points, True)
        self.plot_periodic_trendline(years_decreasing_trendline, decreasing_trendline_points, False)

        normalized_price = CommonCoin.compute_normalized_price(self.prices, self.lower_trendline_points, decreasing_trendline_points)
        self.get_plotter().plot_multicolored(self.years, self.prices, normalized_price, False)
        self.get_plotter().show()

    def plot_halvings(self) -> list:
        """ This function plots the Bitcoin halvings (both from the past as in the future) as a grid of vertical lines. """
        halvings_in_yeartime = []
        for timestamp in self.halvings:
            halvings_in_yeartime.append(self.data_formatter.get_yeartime(timestamp))
        next_halving = halvings_in_yeartime[-1] + self.future_halvings_duration
        while next_halving < math.ceil(self.last_year):
            halvings_in_yeartime.append(next_halving)
            next_halving += 4

        self.get_plotter().plot_halvings(halvings_in_yeartime, self.upper_trendline_points[-1])

    def plot_decreasing_trendline(self):
        """ Function responsible for plotting the decreasing trendline. """
        # The endpoint of the decreasing trendline is normally decreasing_trendline.endpoint_year, but could differ in case the
        # self.years_extended range is limited to somewhere before decreasing_trendline.endpoint_year by the future_years setting.
        years_decreasing_trendline = list(np.arange(self.years_extended[0],
            min(self.decreasing_trendline.endpoint_year, self.years_extended[-1]), 1/365.25))
        decreasing_trendline_points = self.decreasing_trendline.compute_list(years_decreasing_trendline)
        textual_formula = self.decreasing_trendline.get_formula(self.data_formatter.get_epoch_year())
        label = "Decreasing resistance: " + textual_formula
        self.get_plotter().plot(years_decreasing_trendline, decreasing_trendline_points, 'darkred', label)
        return years_decreasing_trendline, decreasing_trendline_points

    def plot_periodic_trendline(self, time: list, upper_trendline: list, light_colormap: bool):
        """ Function responsible for plotting the periodic trendlines based on Bitcoin's halving cycle. """
        periodic_trendline_points, periodic_trendline_normalized = self.create_periodic_trendline(time, upper_trendline)
        self.get_plotter().plot_multicolored(time, periodic_trendline_points, periodic_trendline_normalized, light_colormap)

    def create_periodic_trendline(self, time: list, upper_trendline_points: list) -> tuple:
        """ Function that creates the periodic trendline based on Bitcoin's halving cycle.

        Args:
            time (list): List of floats representing the years since Bitcoin's epoch.
            upper_trendline_points (list): List of floats representing the prices of the upper trendline for which to create
                the periodic trendline. Matches with the time list.

        Returns:
            tuple: A tuple containing two lists of floats. The first list represents the prices of the periodic trendline and the second
                list the normalized prices of the periodic trendline (used for multi-color plotting).
        """
        # Each cycle is a power of (1 - |sin|) interpolated in log space between the lower and upper trendline: sharp tops, a fast
        # decline and a long period near the lower trendline. Assume that the 2nd halving cycle and beyond all have the same
        # duration (even though that's not completely true).
        cycle_duration = self.future_halvings_duration
        top_offset = 1.1 # cycle tops at top_offset + n * cycle_duration years since epoch
        steepness = 1.5
        # The short first cycle peaks at its actual top and ends at the bottom of the regular cycles. Both touch the lower trendline
        # with zero slope there, so the merged trendline and its slope are continuous.
        first_cycle_top = self.data_formatter.get_yeartime(1307570400000) # 09-06-2011
        first_cycle_end = top_offset + cycle_duration / 2
        first_cycle_half_duration = first_cycle_end - first_cycle_top
        merged_cycles = []
        for t, ut, lt in zip(time, upper_trendline_points, self.lower_trendline_points):
            if t < first_cycle_top - first_cycle_half_duration:
                n = 0.0
            elif t < first_cycle_end:
                n = (1 - abs(math.sin(math.pi * (t - first_cycle_top) / (2 * first_cycle_half_duration)))) ** steepness
            else:
                n = (1 - abs(math.sin(math.pi * (t - top_offset) / cycle_duration))) ** steepness
            merged_cycles.append(lt * (ut / lt) ** n)
        normalized_cycles = [(p - lt) / (ut - lt) for p, lt, ut in zip(merged_cycles, self.lower_trendline_points, upper_trendline_points)]
        return merged_cycles, normalized_cycles
