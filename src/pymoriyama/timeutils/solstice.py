import datetime as dt


summer_solstice_dates = {
    2005: dt.datetime(2005, 6, 21),
    2006: dt.datetime(2006, 6, 21),
    2007: dt.datetime(2007, 6, 22),
    2008: dt.datetime(2008, 6, 21),
    2009: dt.datetime(2009, 6, 21),
    2010: dt.datetime(2010, 6, 21),
    2011: dt.datetime(2011, 6, 22),
    2012: dt.datetime(2012, 6, 21),
    2013: dt.datetime(2013, 6, 21),
    2014: dt.datetime(2014, 6, 21),
    2015: dt.datetime(2015, 6, 22),
    2016: dt.datetime(2016, 6, 21),
    2017: dt.datetime(2017, 6, 21),
    2018: dt.datetime(2018, 6, 21),
    2019: dt.datetime(2019, 6, 22),
    2020: dt.datetime(2020, 6, 21),
    2021: dt.datetime(2021, 6, 21),
    2022: dt.datetime(2022, 6, 21),
    2023: dt.datetime(2023, 6, 21),
    2024: dt.datetime(2024, 6, 21),
    2025: dt.datetime(2025, 6, 21),
    # Add more years as needed
}
winter_solstice_dates = {
    2005: dt.datetime(2005, 12, 22),
    2006: dt.datetime(2006, 12, 22),
    2007: dt.datetime(2007, 12, 22),
    2008: dt.datetime(2008, 12, 21),
    2009: dt.datetime(2009, 12, 21),
    2010: dt.datetime(2010, 12, 22),
    2011: dt.datetime(2011, 12, 22),
    2012: dt.datetime(2012, 12, 21),
    2013: dt.datetime(2013, 12, 22),
    2014: dt.datetime(2014, 12, 22),
    2015: dt.datetime(2015, 12, 22),
    2016: dt.datetime(2016, 12, 21),
    2017: dt.datetime(2017, 12, 22),
    2018: dt.datetime(2018, 12, 22),
    2019: dt.datetime(2019, 12, 22),
    2020: dt.datetime(2020, 12, 21),
    2021: dt.datetime(2021, 12, 22),
    2022: dt.datetime(2022, 12, 22),
    2023: dt.datetime(2023, 12, 22),
    2024: dt.datetime(2024, 12, 21),
    2025: dt.datetime(2025, 12, 21),
}


def days_since_solstice(date: dt.datetime):
    year = date.year
    month = date.month
    if month in [10, 11, 12]:
        solstice = winter_solstice_dates.get(year)
    elif month in [1, 2, 3]:
        solstice = winter_solstice_dates.get(year-1)
    else:
        solstice = summer_solstice_dates.get(year)

    if solstice:
        delta_days = (date - solstice).days
        return delta_days
    else:
        raise ValueError(f"Solstice date not defined for year {year}")

def days_since_winter_solstice(date: dt.datetime, year=None):

    month = date.month
    if year is None:
        year = date.year
        if month > 6:
            solstice = winter_solstice_dates.get(year)
        elif month <= 6:
            solstice = winter_solstice_dates.get(year-1)
    else:
        solstice = winter_solstice_dates.get(year)

    if solstice:
        delta_days = (date - solstice).days
        return delta_days
    else:
        raise ValueError(f"Solstice date not defined for year {year}")

def days_since_summer_solstice(date: dt.datetime, year=None):
    if year is None:
        year = date.year
        

    solstice = summer_solstice_dates.get(year)

    if solstice:
        delta_days = (date - solstice).days
        return delta_days
    else:
        raise ValueError(f"Solstice date not defined for year {year}")
