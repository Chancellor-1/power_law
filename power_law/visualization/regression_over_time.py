""" This module contains the class RegressionOverTime. """
# Copyright (C) 2024 Chancellor - License GPLv3
import matplotlib.pyplot as plt
from matplotlib import ticker

from power_law.coins.bitcoin import Bitcoin
from power_law.coins.kaspa import Kaspa
from power_law.coins.ethereum import Ethereum
from power_law.config.config import Config
from power_law.trendline import regression
from power_law.visualization import common_plotter

class RegressionOverTime:
    """
    This class is responsible for plotting the parameters $a$ and $k$ (of the power law function $ y=ax^k$)
    resulting from linear regression (or RANSAC) over time, i.e. regression is applied every several days
    (for runtime optimization) on all data until that moment of time, as if that moment is the current moment
    in time and there is no more data available. Additionally, the coefficient of determination ($R^2$) is
    plotted over time as well, which can be considered a measure of the quality of the fit. For a good model,
    both parameters $a$ and $k$ should settle on a single value after a while and $R^2$ should get close to 1
    and no longer decrease, e.g. at the time of writing for Bitcoin for the past ~7 years $0.010 <= a <= 0.014$,
    $5.6 <= k <= 5.8$ and $R^2 > 0.9$. Kaspa is still young, but it's looking good since it seems $a$ and $k$
    are settling close to a single value with $R^2 > 0.9$ since 2024 and increasing rapidly.

    Attributes:
        axs (ndarray): Array of Axes objects of size 3x3 (3 graphs per coin: 1 for $a$, 1 for $k$ and 1 for $R^2$).
        btc (Bitcoin): Instance of the Bitcoin class.
        kas (Kaspa): Instance of the Kaspa class.
        eth (Ethereum): Instance of the Ethereum class.
        line_width (float): Line width of the plotted lines in the graph.
    """

    def __init__(self, config: Config):
        """ Constructor for RegressionOverTime class. """
        config_all = config.get_coin_config('all')
        common_plotter.set_resolution(config_all['yaml']['general']['image_resolution'])

        _, self.axs = plt.subplots(3, 3)

        self.btc = Bitcoin(config.get_coin_config('btc'))
        self.kas = Kaspa(config.get_coin_config('kas'))
        self.eth = Ethereum(config.get_coin_config('eth'))

        self.line_width = config_all['yaml']['general']['line_width']

    def __plot_regression_results(self, years: list, prices: list, row: int, coin_name: str, color: str, epoch: float):
        """ This function makes 3 plots in one sub-plots row with the regression results over time,
            all for 1 coin (that goes by the name coin_name): 1 for $a$, 1 for $k$ and 1 for $R^2$.

        Args:
            years (list): List of floats representing years since start of epoch.
            prices (list): List of floats representing prices. Corresponds with years.
            row (int): Integer representing the sub-plots row in which to plot (range [0, 2]).
            coin_name (str): A string with the coin name ('Bitcoin', 'Kaspa' or 'Ethereum').
            color (str): A string with the color name used for plotting the graph.
            epoch (float): A float representing the Gregorian calendar year of the coin's epoch.
        """
        regression_result = regression.compute_regression_over_time(years, prices)

        regression_result['t'] = [t + epoch for t in regression_result['t']]
        a_ax = self.axs[row, 0]
        a_label = "$a$ (multiplier) of the power law function $y = ax^k$ of " + coin_name + " over time"
        a_ax.plot(regression_result['t'], regression_result['a'],
            label = a_label, linewidth = self.line_width, color = color)
        a_ax.set_title(a_label)
        a_ax.set_ylabel("$a$ (multiplier) as resulted from regression")

        if coin_name == 'Bitcoin':
            a_ax.set_ybound(0.0, 0.03)
        elif coin_name == 'Kaspa':
            a_ax.set_ybound(0.012, 0.035)
        else:
            a_ax.set_ybound(9.0, 21.0)

        k_ax = self.axs[row, 1]
        k_label = "$k$ (exponent) of the power law function $y = ax^k$ of " + coin_name + " over time"
        k_ax.plot(regression_result['t'], regression_result['k'],
            label = k_label, linewidth = self.line_width, color = color)
        k_ax.set_title(k_label)
        k_ax.set_ylabel("$k$ (exponent) as resulted from regression")

        if coin_name == 'Bitcoin':
            k_ax.set_ybound(4.6, 7.5)
        elif coin_name == 'Kaspa':
            k_ax.set_ybound(1.7, 2.8)
        else:
            k_ax.set_ybound(1.0, 3.8)

        r2_ax = self.axs[row, 2]
        r2_label = "$R^2$ (a measure of quality of fit) of the power law function of " + coin_name + " over time"
        r2_ax.plot(regression_result['t'], regression_result['r2'],
            label = r2_label, linewidth = self.line_width, color = color)
        r2_ax.set_title(r2_label)
        r2_ax.set_ylabel("$R^2$ (coefficient of determination)")
        r2_ax.set_ybound(0.37, 1.0)

    def plot_regression_over_time(self):
        """
        This function plots 9 graphs (3x3) with the regression results ($k$, $a$ and $R^2$) over time
        for all 3 assets (btc, kas and eth).
        """
        self.__plot_regression_results(self.btc.years, self.btc.prices,
            0, 'Bitcoin', 'orange', self.btc.data_formatter.get_epoch_year())
        self.__plot_regression_results(self.kas.years, self.kas.prices,
            1, 'Kaspa', 'turquoise', self.kas.data_formatter.get_epoch_year())
        self.__plot_regression_results(self.eth.years, self.eth.prices,
            2, 'Ethereum', 'slateblue', self.eth.data_formatter.get_epoch_year())

        for ax in self.axs.flat:
            common_plotter.set_grid(ax, 'both')
            common_plotter.set_legend(ax, self.line_width)
            ax.set_xlabel("Time (years)")
            ax.xaxis.set_major_locator(ticker.MultipleLocator(1))

        common_plotter.show()
