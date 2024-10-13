""" This module contains the DataFormatter class. """
# Copyright (C) 2024 Chancellor - License GPLv3
import json
import os
import sys
import time
import datetime
import math

class DataFormatter:
    """
    This class is responsible for reading the price data from the JSON files, converting the Unix timestamps into
    floats representing years since the coin's epoch (usually the birthday of the coin), and it contains functions
    that provide time related data for drawing the X-axis labels, month grid as well as the epoch year as Gregorian
    calendar year (e.g. for in the graph's legend).

    Attributes:
        epoch (int): Unix timestamp of the coin's epoch. This corresponds with the start of the power law, which is
            usually the coin's birthday.
        price_discovery_timestamp (int): Unix timestamp corresponding with the moment of price discovery. Before this
            time the coin's price doesn't follow a power law yet because adoption didn't took off yet. The coin still
            needs to be discovered beyond the inner circle of developers and network effects still need to kick in. Prices
            before this moment are discarded and not shown in the graph.
        historic_price_file (str): Name of the JSON file containing historic price data. Price data is split in historic data
            and recent data. This data is concatenated and therefore the ending timestamp of the historic data should be one
            day apart from the starting timestamp in the recent data.
        recent_price_file (str): Name of the JSON file containing recent price data. The recent data file can be updated by
            CoinAPI and is a separate file to avoid wasting unnecessary CoinAPI queries that might exceed the (free) daily
            limits of the CoinAPI license. Apart from that, CoinAPI's historic data doesn't go back all the way up till the
            moment of price discovery.
        directory (str): The name of the sub-directory in which the historic and recent price JSON files are located. This
            directory should be located in the power_law/data directory and should follow its three-letter acronym convention,
            e.g. btc (Bitcoin), kas (Kaspa) or eth (Ethereum).
    """

    MONTH_LENGTHS = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    """ List of constant integers representing the number of days in each month of the year. """
    MILLISECONDS_IN_A_YEAR = 1000 * 3600 * 24 * 365.25 # 365.25 to compensate for leap years
    """ Constant integer value representing the number of milliseconds in a year (averaging for leap years). """

    def __init__(self, config: dict):
        """ Constructor for the DataFormatter class. """
        self.epoch = config["epoch_timestamp"]
        self.price_discovery_timestamp = config['price_discovery_timestamp']
        self.historic_price_file = config['historic_price_file']
        self.recent_price_file = config['recent_price_file']
        self.directory = config['directory']

    def get_yeartime(self, timestamp: int) -> float:
        """
        This function converts a Unix timestamp (millisecond format) into a float representing the years since the coin's epoch
        (usually the coin's birthday).

        Args:
            timestamp (int): Unix timestamp to convert.

        Returns:
            float: The float year since the coin's epoch.
        """
        return (timestamp - self.epoch) / DataFormatter.MILLISECONDS_IN_A_YEAR

    def append_new_price_data(self, years: list, prices: list, filename: str):
        """ This function appends the price data in the JSON file filename to the years and prices lists.

        Args:
            years (list): List of floats representing time data in years since epoch (might be empty to start with).
            prices (list): List of floats representing price data (might be empty to start with). Matches with the years list.
            filename (str): Name of the JSON file containing the price data to append.
        """
        try:
            with open(os.path.join(os.path.dirname(__file__), self.directory, filename), 'r', encoding='UTF-8') as file:
                json_data = json.load(file)
                for jd in json_data:
                    # prune data before price discovery
                    if jd[0] >= self.price_discovery_timestamp:
                        # years (float) since start of power law
                        yeartime = self.get_yeartime(jd[0])
                        years.append(yeartime)
                        prices.append(jd[1])
        except FileNotFoundError:
            print("Could not read price data from file " + filename + ". Exiting...")
            if sys.platform != 'win32':
                sys.exit(os.EX_IOERR)
            else:
                sys.exit(1)

    def get_data(self) -> tuple:
        """ This function retrieves the time - prices data from the historic & recent price data JSON files.

        Returns:
            tuple: A tuple containing two lists of floats with time (in years since epoch) and price (in US$) data.
        """
        prices = []
        years = []
        self.append_new_price_data(years, prices, self.historic_price_file)
        self.append_new_price_data(years, prices, self.recent_price_file)
        return years, prices

    def get_first_year_tick(self) -> tuple:
        """
        This function retrieves the first January 1st after price discovery in year-time (i.e. float years since epoch) and
        the actual year it represents (e.g. 2023) as a tuple, which together indicate the first year tick-mark on the X-axis.

        Returns:
            tuple: A tuple of a float representing the year-time of the start of the first Gregorian calendar year after epoch,
                and an integer of the actual Gregorian calendar year it represents (e.g. 2023).
        """
        price_discovery_dt = datetime.datetime.fromtimestamp(self.price_discovery_timestamp / 1000)
        first_year = price_discovery_dt.year + 1
        dt = datetime.datetime(year=first_year, month=1, day=1, hour=23, minute=59, second=59)
        first_year_timestamp = time.mktime(dt.timetuple()) * 1000 # ms
        first_year_in_yeartime = self.get_yeartime(first_year_timestamp) # float years since epoch
        return first_year_in_yeartime, first_year

    def get_year_ticks(self, final_year_in_yeartime: float) -> dict:
        """
        This function retrieves a dictionary of two lists, of which the first is a list of floats representing the year-time (since the
        coin's epoch) of the start of each Gregorian calendar year, and of which the second is a list of integers of the actual
        Gregorian calendar year it represents (e.g. 2023), which together can be used to plot the tick marks and labels on the X-axis.

        Args:
            final_year_in_yeartime (float): The last year (years since the coin's epoch) for which to add a pair in the output dictionary.

        Returns:
            dict: Dictionary of a list of floats (year ticks) and a list of integers (year labels).
        """
        first_year_in_yeartime, first_year = self.get_first_year_tick()
        number_of_year_ticks = math.ceil(final_year_in_yeartime - first_year_in_yeartime) + 1
        year_tick_labels = list(range(0, number_of_year_ticks))
        year_ticks = [y + first_year_in_yeartime for y in year_tick_labels]
        year_tick_labels = [y + first_year for y in year_tick_labels]
        return {'years': year_ticks, 'labels': year_tick_labels}

    def get_months(self, future_years: int) -> list:
        """
        Function that computes the month tick marks (in year-time since the coin's epoch) and its month index [1, 12]. Together these
        can be used to plot the vertical grid of Gregorian calendar months and years.

        Args:
            future_years (int): The number of years for which to compute the month tick marks and month indices.

        Returns:
            list: A list of tuples containing a float representing the month tick marks (in year-time since the coin's epoch) and
                an integer representing the month index [1, 12], with 1 representing the start of the year (1st of January).
        """
        epoch_dt = datetime.datetime.fromtimestamp(self.epoch / 1000)
        year = epoch_dt.year
        month_index = epoch_dt.month
        month_list = []
        # For the epoch's month the epoch's calendar day needs to be subtracted from the number of days in that month.
        prev_month_in_days = 1 - epoch_dt.day
        for _ in range(0, 12 * future_years):
            days_this_month = DataFormatter.MONTH_LENGTHS[month_index - 1]
            if year % 4 == 0: # Leap year
                if month_index == 2: # February
                    days_this_month += 1 # 29 days instead of 28
            # This is the days counter for the next month, e.g. the first month that needs to be drawn is the month
            # after the month in which the epoch occurs (month_index).
            month_in_days = prev_month_in_days + days_this_month
            # Therefore, in the output the month_index needs to be increased by 1 before outputting.
            month_index = (month_index % 12) + 1 # range [1, 12]
            if month_index == 1:
                year += 1
            month_list.append((month_in_days / 365.25, month_index))
            prev_month_in_days = month_in_days
        return month_list

    def get_epoch_year(self) -> float:
        """
        This function retrieves the coin's epoch year as a float Gregorian calendar year. This can be used for e.g. showing the coin's
        power law formula in the graph's legend.

        Returns:
            float: The coin's epoch year as a float Gregorian calendar year.
        """
        epoch_dt = datetime.datetime.fromtimestamp(self.epoch / 1000)
        year = epoch_dt.year
        month_index = epoch_dt.month - 1
        month_lengths = list(DataFormatter.MONTH_LENGTHS)
        leap_day = 0
        if year % 4 == 0: # leap year
            leap_day = 1
        month_lengths[1] += leap_day
        days = sum(month_lengths[0:month_index])
        days += epoch_dt.day
        return year + (days / (365 + leap_day))
