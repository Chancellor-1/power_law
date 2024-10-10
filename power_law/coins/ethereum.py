""" This module contains the Ethereum class. """
# Copyright (C) 2024 Chancellor - License GPLv3
from power_law.coins.common_coin import CommonCoin

class Ethereum(CommonCoin):
    """ This class contains the specifics for plotting the Ethereum power law graph. This class derives from CommonCoin. """

    def plot_ethereum(self):
        """ This function plots the Ethereum power law graph. """
        self.common_plotting()

        normalized_price = CommonCoin.compute_normalized_price(self.prices, self.lower_trendline_points, self.upper_trendline_points)
        self.get_plotter().plot_multicolored(self.years, self.prices, normalized_price, False)

        self.get_plotter().show()
