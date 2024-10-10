""" This module contains a function to compute a linear regression (or RANSAC) fit in log-log space. """
# Copyright (C) 2024 Chancellor - License GPLv3
import math
from sklearn import linear_model
# from sklearn.metrics import r2_score

def compute_regression(time: list, price: list, linear_ransacn: bool = True) -> tuple:
    """
    This function computes a linear regression (or RANSAC) fit in log-log space. Because of the log-log space, the fit
    actually represents a power law function of the form $y = ax^k$, of which $a$ and $k$ are the unknowns to be estimated.

    Args:
        time (list): List of floats containing the time data since the start of the power law.
        price (list): List of floats containing the price data since the start of the power law. Should match with the time list.
        linear_ransacn (bool, optional): True when using linear regression, false when using RANSAC. Defaults to True.

    Returns:
        tuple: Tuple containing the defining parameters of a power law function fitting the data, i.e. the multiplier $a$,
            the exponent $k$ and a measure for the quality of the fit $r^2$.
    """
    X = [[math.log(t, 10)] for t in time] # pylint: disable=invalid-name
    y = [math.log(p, 10) for p in price]

    regressor = None
    if linear_ransacn:
        regressor = linear_model.LinearRegression()
    else:
        regressor = linear_model.RANSACRegressor()

    regressor.fit(X, y)

    estimate = None
    if linear_ransacn:
        estimate = regressor
    else:
        estimate = regressor.estimator_

    a = 10**estimate.intercept_
    k = estimate.coef_[0]
    r2 = regressor.score(X, y) # identical to sklearn.metrics.r2_score(y, regressor.predict(X))
    return a, k, r2

def compute_regression_over_time(time: list, price: list, sample_rate: int = 10) -> dict:
    """
    This function applies compute_regression() every 1 in sample_rate days on all data up till that day and collects all
    regression results ($a$, $k$ and $R^2$).

    Args:
        time (list): A list of time (X-axis) data.
        price (list): A list of price (Y-axis) data, corresponding with the time list.
        sample_rate (int): Only sample 1 out of sample_rate days (runtime optimization).

    Returns:
        dict: A dictionary with 4 lists containing the regression results (keys 'a', 'k' and 'r2') and the corresponding time (key 't').
    """
    minimum_number_of_samples = 30 # Apply regression only on a minimum_number_of_samples.
    regression_results = {'t': [], 'a': [], 'k': [], 'r2': []}
    # Apply linear regression starting with a minimum of 30 days of data.
    for index in range(minimum_number_of_samples, len(time)):
        if index % sample_rate == 0:
            a, k, r2 = compute_regression(time[:index], price[:index])
            regression_results['t'].append(time[index])
            regression_results['a'].append(a)
            regression_results['k'].append(k)
            regression_results['r2'].append(r2)
    return regression_results
