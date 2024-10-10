""" Module providing the YoyRoi class, which is used for plotting year-over-year return on investment for all assets. """
# Copyright (C) 2024 Chancellor - License GPLv3
import matplotlib.pyplot as plt
from matplotlib import ticker

from power_law.coins.bitcoin import Bitcoin
from power_law.coins.kaspa import Kaspa
from power_law.coins.ethereum import Ethereum
from power_law.config.config import Config
from power_law.trendline.trendline import Trendline
from power_law.visualization import common_plotter

class YoyRoi:
    """ This class can show a graph with the year-over-year return on investment of all coin assets based on their supporting trendlines.

    Attributes:
        ax (Axes): Axes object that gives control over the plotting of the graph.
        btc_yoy_roi (dict): Dictionary of a list of integers representing Gregorian calendar years and a list of floats representing
            the year-over-year return on investment for Bitcoin.
        kas_yoy_roi (dict): Dictionary of a list of integers representing Gregorian calendar years and a list of floats representing
            the year-over-year return on investment for Kaspa.
        eth_yoy_roi (dict): Dictionary of a list of integers representing Gregorian calendar years and a list of floats representing
            the year-over-year return on investment for Ethereum.
        start_year (int): Integer representing the Gregorian calendar year to which the X-axis minimum (starting year) of the graph is
            set. This value is read from the config.yaml file. This value should be at minimum equal to the year corresponding to the
            second January 1st after the oldest coin's epoch (Bitcoin: January 3rd 2009), which is 2011 (first YoY ROI value
            computed from 1-1-2011 - 1-1-2010 difference), and it should be smaller than the current year + future_years (command line
            argument). If not, the X-axis minimum will be capped to either one of those limits.
        line_width (float): Float value representing the width of the lines of the graphs. This value is read from the config.yaml file.
    """

    def __init__(self, config: Config):
        """ Constructor of the YoyRoi class.

        Args:
            config (Config): Instance of the Config class used to configure this class and its attributes.
        """
        config_all = config.get_coin_config('all')
        common_plotter.set_resolution(config_all['yaml']['general']['image_resolution'])

        _, self.ax = plt.subplots()
        scale = config_all['arguments']['scale']
        if scale[:3] == 'log':
            self.ax.set_yscale('log')

        btc = Bitcoin(config.get_coin_config('btc'))
        kas = Kaspa(config.get_coin_config('kas'))
        eth = Ethereum(config.get_coin_config('eth'))

        self.btc_yoy_roi = self.compute_yoy_roi(btc.lower_trendline, btc.x_axis_ticks['years'], btc.x_axis_ticks['labels'])
        self.kas_yoy_roi = self.compute_yoy_roi(kas.lower_trendline, kas.x_axis_ticks['years'], kas.x_axis_ticks['labels'])
        self.eth_yoy_roi = self.compute_yoy_roi(eth.lower_trendline, eth.x_axis_ticks['years'], eth.x_axis_ticks['labels'])

        self.start_year = config_all['yaml']['yoyroi']['start_year']
        self.line_width = config_all['yaml']['general']['line_width']

    def compute_yoy_roi(self, trendline: Trendline, years: list, year_labels: list) -> dict:
        """
        This function computes the year-over-year return on investment based on the trendline for each year in the years
        (float year since epoch) / year_labels (integer Gregorian calendar year) list.

        Args:
            trendline (Trendline): Trendline object that is used to compute the prices corresponding to each year in the years list.
            years (list): List of floats representing years since the coin's epoch.
            year_labels (list): List of integers representing Gregorian calendar years. Corresponds with the years list.

        Returns:
            dict: Dictionary of a list of integers representing Gregorian calendar years and a list of floats representing
                the year-over-year return on investment.
        """
        prices = trendline.compute_list(years)
        yoy_roi = []
        last_price = None
        for price in prices:
            if last_price is not None:
                yoy_roi.append(100 * (price - last_price) / last_price)
            last_price = price
        return {'years': year_labels[:-1], 'roi': yoy_roi}

    @staticmethod
    def get_year_index(years: list, year_of_which_to_find_index: int) -> int:
        """
        Returns the index in the years list of the year_of_which_to_find_index. If it cannot be found, returns 0.
        This is a helper function for the set_axes_limits() function to find the maximum ROI value within the years
        range [x_min, x_max], which might be extending beyond the limits of the years list for this specific coin,
        because this range is determined by the data range of all coins (and the start_year). In that case, 0 is
        returned (the ROI for all coins decreases over time so is highest at the start, characteristic for power-laws).

        Args:
            years (list): List of integers representing Gregorian calendar years.
            year_of_which_to_find_index (int): Integer representing the year of which to find the index in the years list.

        Returns:
            int: The index in the years list of the year_of_which_to_find_index.
        """
        try:
            return years.index(year_of_which_to_find_index)
        except ValueError:
            return 0

    def set_axes_limits(self):
        """
        This function sets the limits of the horizontal (time) axis based on all available data and the start_year.
        Consecutively, the maximum of the vertical (ROI) axis is set based on all available ROI data within the time limits.
        """
        x_min = min(self.btc_yoy_roi['years'][0], self.kas_yoy_roi['years'][0], self.eth_yoy_roi['years'][0])
        x_max = max(self.btc_yoy_roi['years'][-1], self.kas_yoy_roi['years'][-1], self.eth_yoy_roi['years'][-1])
        if self.start_year >= x_min and self.start_year < x_max:
            x_min = self.start_year
        else:
            print("YoY ROI start year is set outside of the valid time range [" +
                str(x_min) + ", " + str(x_max) + "]. Start year set to start of data range.")
        self.ax.set_xlim(x_min, x_max)
        # The maximum ROI for each coin is at self.xxx_yoy_roi['roi'][0] for each coin since the ROI decreases over time, but
        # this value might be beyond the range [x_min, x_max], which is where the get_year_index() function comes in.
        y_max = max(self.btc_yoy_roi['roi'][YoyRoi.get_year_index(self.btc_yoy_roi['years'], x_min)],
                    self.kas_yoy_roi['roi'][YoyRoi.get_year_index(self.kas_yoy_roi['years'], x_min)],
                    self.eth_yoy_roi['roi'][YoyRoi.get_year_index(self.eth_yoy_roi['years'], x_min)])
        # For some reason the plot is not always tightly fitted around the data by default, so overrule the y_max bound.
        self.ax.set_ybound(lower = None, upper = y_max)

    def plot_yoy_roi(self):
        """ This function plots the year-over-year return on investment graph for all assets. """
        self.ax.plot(self.btc_yoy_roi['years'], self.btc_yoy_roi['roi'], color='orange',
            label='BTC YoY ROI (in %)', linewidth = self.line_width)
        self.ax.plot(self.kas_yoy_roi['years'], self.kas_yoy_roi['roi'], color='turquoise',
            label='KAS YoY ROI (in %)', linewidth = self.line_width)
        self.ax.plot(self.eth_yoy_roi['years'], self.eth_yoy_roi['roi'], color='slateblue',
            label='ETH YoY ROI (in %)', linewidth = self.line_width)

        self.set_axes_limits()
        self.ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
        self.ax.set_title("Year-over-year return on investment for BTC, KAS and ETH based on supporting trendline")
        self.ax.set_xlabel("Time (years)")
        self.ax.set_ylabel("YoY ROI (in %)")
        common_plotter.set_grid(self.ax, 'both')
        common_plotter.set_legend(self.ax, self.line_width)
        common_plotter.show()
