""" This module contains plotting related helper functions for e.g. the classes Plotter, YoyRoi and RegressionOverTime. """
# Copyright (C) 2024 Chancellor - License GPLv3
from importlib.metadata import version
import matplotlib.pyplot as plt

def set_resolution(resolution: list):
    """ Function to set default graph window resolution.

    Args:
        resolution (list): List of two integers with the horizontal and vertical resolution of the graph window in pixels.
    """
    dpi = 80
    plt.rcParams['figure.dpi'] = dpi
    plt.rcParams['figure.figsize'] = (resolution[0] / dpi, resolution[1] / dpi)

def set_grid(ax: plt.Axes, axis: str):
    """ Function to set grid line width and color uniformly for all plots.

    Args:
        ax (plt.Axes): Axes object for which to set the grid.
        axis (str): String defining for which axis/axes to set the grid ('x', 'y' or 'both')
    """
    ax.grid(axis = axis, which = 'both', color = '0.65', linewidth = 0.5)

def set_legend(ax: plt.Axes, line_width: float):
    """ Function to set legend in upper left corner and increase legend line width for greater visibility.

    Args:
        ax (plt.Axes): Axes object for which to set the legend.
        line_width (float): Float representing the line width used for plotting the graphs. The legend line will be twice as thick.
    """
    legend = ax.legend(loc='upper left')
    for line in legend.get_lines():
        line.set_linewidth(line_width * 2)

def show():
    """ This function shows the plot in a window with tight layout and uniform title for all plots. """
    plt.tight_layout()
    plt.get_current_fig_manager().set_window_title("Power Law v" + version('pow-law'))
    plt.show()
