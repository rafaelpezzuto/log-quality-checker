from datetime import datetime, timedelta

import re


def clean_date(date_str):
    """
    Cleans and formats a date string.

    If the input date string matches the pattern 'YYYYMMDD', it reformats the string to 'YYYY-MM-DD'.
    If the input date string matches the pattern 'YYYY-MM-DD', it returns the string unchanged.
    Otherwise, it raises a ValueError.

    Args:
        date_str (str): The date string to be cleaned and formatted.

    Returns:
        str: The cleaned and formatted date string.

    Raises:
        ValueError: If the date string does not match the expected patterns.
    """
    if re.match(r'^\d{8}$', date_str):
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
    elif re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return date_str
    else:
        raise ValueError(f"Invalid date format: {date_str}")
   

def extract_min_max_dates(dates):
    """
    Given a list of date tuples, returns the minimum and maximum dates as datetime objects.

    Args:
        dates (list of tuples): A list where each element is a tuple representing a date (year, month, day, ...).

    Returns:
        tuple: A tuple containing two datetime objects, the minimum and maximum dates.

    Example:
        dates = [(2021, 5, 17), (2020, 12, 25), (2022, 1, 1)]
        min_date, max_date = get_min_max_dates(dates)
    """
    return datetime(*min(dates)), datetime(*max(dates))

