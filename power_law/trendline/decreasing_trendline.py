""" This module contains the DecreasingTrendline class. """
# Copyright (C) 2024 Chancellor - License GPLv3
from power_law.trendline.trendline import Trendline

class DecreasingTrendline(Trendline):
    """ This class represents a decreasing exponential trendline. It derives from base class Trendline.

    Attributes:
        k_decrease (float): Float value representing the amount that the initial exponential value (k) decreases over time from epoch
        till endpoint_year.
        endpoint_year (float): Float representing the year since Bitcoin epoch at which the decreasing trendline stops, i.e.
            hits the supporting trendline.
    """

    def __init__(self, a: float, k: float, k_decrease: float, endpoint_year: float):
        """ Constructor for the DecreasingTrendline class. """
        super().__init__(a, k)
        self.k_decrease = k_decrease
        self.endpoint_year = endpoint_year

    @classmethod
    def config(cls, config: dict):
        """ Config based constructor. """
        a, k = Trendline.get_trendline_parameters(config['decreasing_upper_trendline'])
        return cls(a, k, config['decreasing_upper_trendline']['formula']['k_decrease'], config['endpoint_year'])

    def compute_list(self, xs: list) -> list:
        """ This function computes the decreasing trendline points from the xs list argument.

        Args:
            xs (list): A list of floats for which to compute the corresponding decreasing trendline values.

        Returns:
            list: A list of floats representing the decreasing trendline values corresponding with the xs list.
        """
        # Note that endpoint_year is normally xs[-1], but xs[-1] could be smaller in case the xs range is limited to somewhere
        # before endpoint_year due to the future_years command line argument.
        return [self.a * x ** (self.k - (x / self.endpoint_year) * self.k_decrease) for x in xs]

    def get_formula(self, epoch_year: float) -> str:
        """ This function returns the decreasing trendline formula in textual form.

        Args:
            epoch_year (float): Float representing the epoch (usually the coin's birthday) of the coin in Gregorian calendar years.

        Returns:
            str: String representing the decreasing trendline formula textually.
        """
        endpoint_year_str = f"{self.endpoint_year:.3f}"
        epoch_year_str = f"{epoch_year:.3f}"
        endpoint_actual_year_str = f"{epoch_year + self.endpoint_year:.3f}"
        k = f"{self.k:.2f}"
        k_decr = f"{self.k_decrease:.2f}"
        a = f"{self.a:.5f}"
        return "$price = " + a + r" \cdot (year - " + epoch_year_str + ") ^{" + k + " - " + k_decr + r" \cdot ((year - " + epoch_year_str + \
            ") / " + endpoint_year_str + ")}$ for $year$ in range $[" + epoch_year_str + ", " + endpoint_actual_year_str + "]$"
