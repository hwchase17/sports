def year_string_to_year(yr_string):
    """Transform a year string (YYYY-YY) to year as an int."""
    return yr_string[:4]


def year_to_year_string(year):
    '''Transform a year (YYYY) to a year string (YYYY-YY)'''
    last_two_digits = str(year % 100 + 1).zfill(2)
    return '{}-{}'.format(year, last_two_digits)


def filter_to_players_active_during_year(df, year, start_year_col, end_year_col):
    """Filter a dataframe with a start and end year to rows when given year is in range."""
    after_start_mask = df[start_year_col] <= year
    before_end_mask = df[end_year_col] >= year
    return df[after_start_mask & before_end_mask]
