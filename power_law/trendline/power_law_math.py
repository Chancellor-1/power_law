""" This module contains power law related mathematical functions. """
# Copyright (C) 2024 Chancellor - License GPLv3
import math

def compute_power_law_from_points(x0: float, f0: float, x1: float, f1: float) -> tuple:
    """
    This function computes the defining parameters $a$ (multiplier) and $k$ (exponent) of a power law function $y = ax^k$
    from two points on the power law curve $(x_0, f_0)$ and $(x_1, f_1)$.

    Attributes:
        x0 (float): X-coordinate of first point lying on the power law curve.
        f0 (float): Y-coordinate of first point lying on the power law curve.
        x1 (float): X-coordinate of second point lying on the power law curve.
        f1 (float): Y-coordinate of second point lying on the power law curve.

    Returns:
        tuple: Tuple with values $a$ and $k$.
    """

    # Also see https://en.wikipedia.org/wiki/Log%E2%80%93log_plot on finding a & k in y = a * x ^ k.
    # For a point on the power law curve (x_0, F(x_0)) and a second point (x_1, F(x_1)) below holds:
    # y = F(x_0) * (x / x_0) ^ (log(F(x_1) / F(x_0)) / log(x_1 / x_0))
    k = math.log10(f1 / f0) / math.log10(x1 / x0) # exponent
    a = f0 / (x0 ** k) # scaling factor
    return a, k

def power_law(a: float, k: float, x: float) -> float:
    """ This function computes the output of the power law function $y = ax^k$.

    Args:
        a (float): Multiplier $a$ in $y = ax^k$.
        k (float): Exponent $k$ in $y = ax^k$.
        x (float): Input value $x$ in $y = ax^k$.

    Returns:
        float: Output value $y$ in $y = ax^k$.
    """
    return a * x ** k

def power_law_list(a: float, k: float, xs: list) -> list:
    """ This function computes the output of the power law function $y = ax^k$ for multiple inputs in list xs.

    Args:
        a (float): Multiplier $a$ in $y = ax^k$.
        k (float): Exponent $k$ in $y = ax^k$.
        xs (list): List of floats containing input values ($x$'s) for which to compute the output $y$ in $y = ax^k$.

    Returns:
        float: Output values ($y$'s) in $y = ax^k$ for all $x$'s in list xs.
    """
    return [power_law(a, k, x) for x in xs]
