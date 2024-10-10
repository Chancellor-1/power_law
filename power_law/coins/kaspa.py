""" This module contains the Kaspa class. """
# Copyright (C) 2024 Chancellor - License GPLv3
from power_law.coins.common_coin import CommonCoin

class Kaspa(CommonCoin):
    """ This class contains the specifics for plotting the Kaspa power law graph. This class derives from CommonCoin. """

    def plot_kaspa(self):
        """ This function plots the Kaspa power law graph. """
        self.common_plotting()

        normalized_price = CommonCoin.compute_normalized_price(self.prices, self.lower_trendline_points, self.upper_trendline_points)
        self.get_plotter().plot_multicolored(self.years, self.prices, normalized_price, False)

        self.get_plotter().show()
