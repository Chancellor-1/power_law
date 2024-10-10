""" Module providing the Plotter class, which is responsible for the actual plotting of the graph. """
# Copyright (C) 2024 Chancellor - License GPLv3
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter

from power_law.visualization import colormap
from power_law.visualization import common_plotter

class Plotter:
    """ This class contains functions for plotting the graph.

    Attributes:
        ax (Axes): Axes object that gives control over the plotting of the graph.
        line_width (float): Line width for plotting of the graphs themselves (not e.g. the grid and halvings).
    """

    def __init__(self, config: dict):
        """ Constructor for the Plotter class.

        Args:
            config (dict): Dictionary containing general and plot configuration from the config.yaml file and scale from the
                command line arguments.
        """
        # Removes the minor logarithmic tick marks
        plt.rcParams['xtick.minor.size'] = 0
        plt.rcParams['xtick.minor.width'] = 0
        common_plotter.set_resolution(config['general']['image_resolution'])

        _, self.ax = plt.subplots()
        common_plotter.set_grid(self.ax, 'y')

        if config['scale'][3:] == 'log':
            self.ax.set_xscale('log')
        if config['scale'][:3] == 'log':
            self.ax.set_yscale('log')

        self.ax.set_title(config['plot']['title'])
        self.ax.set_xlabel(config['plot']['x_label'])
        self.ax.set_ylabel(config['plot']['y_label'])

        self.line_width = config['general']['line_width']

    def plot_months(self, month_list: list, max_price: float):
        """
        Plots vertical grid for every month in the Gregorian calendar. Every vertical line corresponding with the start of a
        year is drawn black with line width 1, while all other months are drawn dark grey with line width 0.5.

        Args:
            month_list (list): A list of tuples with two fields; the first a float representing the year since epoch, the
                second the month index in range [1, 12], with 1 the start of the next year.
            max_price (float): The maximum price in the plot, needed to determine the height of the vertical month grid.
        """
        for month in month_list:
            line_width = 0.5
            color = 'darkgrey'
            if month[1] == 1:
                line_width = 1.0
                color = 'black'
            self.ax.plot([month[0], month[0]], [0, max_price], marker = 'None', color = color, linewidth = line_width)

    def plot_trendlines(self, lower_trendline: list, upper_trendline: list, time: list, labels: tuple):
        """
        This function plots the upper and lower trendlines (also called resistance and support) and sets the limits of
        the graphs axes based on the extremes of both trendlines.

        Args:
            lower_trendline (list): List of floats representing the price of the lower (supporting) trendline.
            upper_trendline (list): List of floats representing the price of the upper (resisting) trendline.
            time (list): List of floats representing years since the coin's epoch (usually the birthday of the coin).
            labels (tuple): Tuple of strings with the legend labels for the lower and upper trendline.
        """
        self.ax.set_xlim(time[0], time[-1])
        self.ax.set_ylim(lower_trendline[0], upper_trendline[-1])
        self.ax.plot(time, lower_trendline, color = 'darkblue', linewidth = self.line_width, label = labels[0])
        self.ax.plot(time, upper_trendline, color = 'lightcoral', linewidth = self.line_width, label = labels[1])

    def plot(self, time: list, price: list, color: str, label: str):
        """ This function plots the time - price data in the graph with the arguments' color.

        Args:
            time (list): List of floats representing years since the coin's epoch (usually the birthday of the coin).
            price (list): List of floats with the price data to plot. Matches with the time data.
            color (str): Color with which to plot the graph.
            label (str): Label for the legend.
        """
        self.ax.plot(time, price, color = color, linewidth = self.line_width, label = label)

    def plot_multicolored(self, time: list, price: list, normalized_price: list, light_colormap: bool):
        """ This function plots the time - price data in the graph with the use of a color map based on the normalized price,
        i.e. the price with respect to the upper and lower trendlines (usually in the range [0, 1]).

        Args:
            time (list): List of floats representing years since the coin's epoch (usually the birthday of the coin).
            price (list): List of floats with the price data to plot. Matches with the time data.
            normalized_price (list): List of floats with the normalized price with respect to the upper and lower trendlines.
                In the range [0, 1] when the price is between the upper and lower trendlines, but could get outside this range.
            light_colormap (bool): True when plotting this graph with a light (somewhat transparent) colormap; False when using
                the regular colormap.
        """
        line_collection = colormap.get_multicolored_line_collection(time, price, normalized_price, light_colormap, self.line_width)
        # line =
        self.ax.add_collection(line_collection)
        # axcb = self.fig.colorbar(line)
        # axcb.set_label("Halving cycle heatmap")

    def set_xticks(self, x_axis_ticks: dict):
        """
        This function plots custom ticks and labels along the horizontal axis. A custom X-axis is needed because even though time
        starts at 0 (needed for plotting the horizontal axis logarithmically), we still want to show the actual Gregorian calendar
        years along the horizontal axis.

        Args:
            x_axis_ticks (dict): A dictionary containing a list of floats representing the time of the start of each Gregorian calendar
                year in years since the coin's epoch (usually it's birthday) and a list of integers (the labels) representing years
                according to the Gregorian calendar since the coin's epoch.
        """
        self.ax.set_xticks(x_axis_ticks['years'])
        self.ax.set_xticklabels(x_axis_ticks['labels'])
        # removes minor ticklabels on X-axis when zooming in
        self.ax.get_xaxis().set_minor_formatter(NullFormatter())

    def show(self):
        """ This function shows the plot and its legend in the upper left corner. """
        common_plotter.set_legend(self.ax, self.line_width)
        common_plotter.show()

    def plot_halvings(self, halvings: list, max_price: float):
        """ This function plots the Bitcoin halvings as a grid of vertical red lines and marks them with the text 'halving' at the top.

        Args:
            halvings (list): List of floats representing years since the coin's epoch (usually the birthday of the coin) at which the
                Bitcoin halvings have occurred or are predicted to occur.
            max_price (float): The maximum price in the plot, needed to determine the height of the vertical halving grid.
        """
        for halving_time in halvings:
            self.ax.plot([halving_time, halving_time], [0, max_price], marker = 'None', color = 'red', linewidth = 1.0)
            self.ax.text(halving_time, max_price, 'halving', color = 'red', fontsize = 6)
