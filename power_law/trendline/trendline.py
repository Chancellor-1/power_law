""" This module contains the Trendline class. """
# Copyright (C) 2024 Chancellor - License GPLv3
from power_law.trendline import power_law_math

class Trendline:
    """ This class represents a power law trendline.

    Attributes:
        k (float): Exponent in function $y = ax^k$.
        a (float): Multiplier in function $y = ax^k$.
    """

    def __init__(self, a: float, k: float):
        """ Constructor for the Trendline class. """
        self.a = a
        self.k = k

    @classmethod
    def config(cls, config: dict):
        """ Config based constructor. """
        a, k = Trendline.get_trendline_parameters(config)
        return cls(a, k)

    @staticmethod
    def get_trendline_parameters(config: dict) -> tuple:
        """
        This function derives or computes the values $k$ and $a$ in power law function $y = ax^k$ from the trendline configuration
        argument coming from the config.yaml file. If config['use_points'] is set to True then $k$ and $a$ are computed from points
        $p_1$ and $p_2$ (two points on the power law curve) with the compute_power_law_from_points() function.

        Args:
            config (dict): Trendline configuration dictionary (from config.yaml file).

        Returns:
            tuple: Tuple of floats a and k.
        """
        a = config['formula']['a']
        k = config['formula']['k']
        if config['use_points']:
            p1 = config['points']['p1']
            p2 = config['points']['p2']
            a, k = power_law_math.compute_power_law_from_points(p1[0], p1[1], p2[0], p2[1])
        return a, k

    def compute(self, x: float) -> float:
        """ Computes the output of the power law function for input value $x$.

        Args:
            x (float): Input value for power law function $y = ax^k$.

        Returns:
            float: Output ($y$) of power law function $y = ax^k$.
        """
        return power_law_math.power_law(self.a, self.k, x)

    def compute_list(self, xs: list) -> list:
        """ Computes the output of the power law function for all input values in list xs.

        Args:
            xs (list): List of input values ($x$'s) for the power law function $y = ax^k$.

        Returns:
            list: List of output values ($y$'s) of the power law function $y = ax^k$.
        """
        return power_law_math.power_law_list(self.a, self.k, xs)

    def get_formula(self, epoch_year: float) -> str:
        """
        This function outputs a textual representation of the power law function $y = ax^k$, with $x$ = (year - epoch_year),
        with year the time expressed as a float fractional Gregorian calendar year and epoch_year the float fractional
        Gregorian calendar year of the start of the power law function (usually the birthday of the coin).

        Args:
            epoch_year (float): The fractional Gregorian calendar year of the start of the power law (usually the birthday of the coin).

        Returns:
            str: Textual representation of the power law function $y = ax^k$, with $x$ = (year - epoch_year).
        """
        return "$price = " + f"{self.a:.5f}" + r" \cdot (year - " + f"{epoch_year:.3f}" + ") ^{" + f"{self.k:.4f}" + "}$"
