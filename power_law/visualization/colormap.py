""" This module contains functions related to color map conversion and creating color-coded line collections. """
# Copyright (C) 2024 Chancellor - License GPLv3
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Colormap
from matplotlib.collections import LineCollection
from matplotlib import cm

def get_multicolored_line_collection(x: list, y: list, n: list, light_colormap: bool, line_width: float) -> LineCollection:
    """
    This function returns a LineCollection of line segments between all consecutive points (e.g. between
    (x[0], y[0]) and (x[1], y[1]) and so forth) and chooses a color for each line segment based on a
    color map (either 'jet', or a light version derived from that) and the normalized values from list n.

    Args:
        x (list): List of X-axis values.
        y (list): List of Y-axis values.
        n (list): List y, but then normalized to [0, 1] or slightly outside this range. Used for color coding line segments.
        light_colormap (bool): False for using color map 'jet', True for using a light version of 'jet'.
        line_width (float): Line width used for plotting.

    Returns:
        LineCollection: The color-coded collection of lines representing the graph data to be plotted.
    """
    data = np.array([x, y]) # Shape [2, n], e.g. [[x1, x2, x3, ...], [y1, y2, y3, ...]]
    data_t = data.T # Shape [n, 2], e.g. [[x1, y1], [x2, y2], [x3, y3], ...]

    # Shape [n, 1, 2], e.g. [[[x1, y1]], [[x2, y2]], [[x3, y3]], ...]
    points = data_t.reshape(-1, 1, 2) # pylint: disable=too-many-function-args
    segments = np.concatenate([points[:-1], points[1:]], axis = 1) # Shape [n, 2, 2], e.g. [[[x1, y1], [x2, y2]], [[x2, y2], [x3, y3]], ...]
    norm = plt.Normalize(min(n), max(n))
    colormap = cm.get_cmap('jet')
    if light_colormap:
        colormap = __cmap_map(lambda x: x/3 + 0.666, colormap)
    line_collection = LineCollection(segments, cmap = colormap, norm = norm, linewidth = line_width)
    line_collection.set_array(n)
    return line_collection

def __cmap_map(function, colormap: Colormap) -> LinearSegmentedColormap:
    """
    Applies function (which should operate on vectors of shape 3: [r, g, b]), on colormap.
    This routine will break any discontinuous points in a Colormap.

    Args:
        function: Conversion function for the colormap.
        colormap (Colormap): The colormap to be converted by the function.

    Returns:
        LinearSegmentedColormap: The converted color map.
    """
    cdict = colormap._segmentdata # pylint: disable=protected-access
    step_dict = {}
    # Firt get the list of points where the segments start or end
    for key in ('red', 'green', 'blue'):
        step_dict[key] = list(map(lambda x: x[0], cdict[key]))
    step_list = sum(step_dict.values(), [])
    step_list = np.array(list(set(step_list)))
    # Then compute the LUT, and apply the function to the LUT
    old_lut = np.array(list(map(lambda step : np.array(colormap(step)[0:3]), step_list)))
    new_lut = np.array(list(map(function, old_lut)))
    # Now try to make a minimal segment definition of the new LUT
    cdict = {}
    for i, key in enumerate(['red','green','blue']):
        this_cdict = {}
        for j, step in enumerate(step_list):
            if step in step_dict[key]:
                this_cdict[step] = new_lut[j, i]
            elif new_lut[j,i] != old_lut[j, i]:
                this_cdict[step] = new_lut[j, i]
        colorvector = list(map(lambda x: x + (x[1], ), this_cdict.items()))
        colorvector.sort()
        cdict[key] = colorvector

    return LinearSegmentedColormap('colormap', cdict, 1024)
