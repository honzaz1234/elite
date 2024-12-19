def convert_season_format(season):
    """
    Converts a season string from 'yyyy-yy' to 'yyyy-yyyy' or returns it unchanged 
    """
    try:
        if (len(season) == 9 
            and season[4] == '-' 
            and season[:4].isdigit() 
            and season[5:].isdigit()):
            return season  # Return unchanged

        # If in 'yyyy-yy' format, convert to 'yyyy-yyyy'
        if (len(season) == 7 
            and season[4] == '-' 
            and season[:4].isdigit() 
            and season[5:].isdigit()):
            start_year, end_suffix = season.split('-')
            start_year = int(start_year)
            end_year = int(f"{start_year // 100}{end_suffix}")
            return f"{start_year}-{end_year}"
        raise ValueError
    except ValueError:
        raise ValueError("Invalid season format. Expected 'yyyy-yy'"
                         " or 'yyyy-yyyy'.")