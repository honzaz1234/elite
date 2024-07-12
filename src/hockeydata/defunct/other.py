def get_season_stats(sel_wiki, table_ind, start_date_ind, end_date_ind):
    dict_dates = {}
    xpath_start_date = get_table_xpath(table_ind, start_date_ind)
    start_dates = sel_wiki.xpath(xpath_start_date).getall()
    start_dates = [string_ for string_ in start_dates if len(string_)>3]
    xpath_end_date = get_table_xpath(table_ind, end_date_ind)
    end_dates = sel_wiki.xpath(xpath_end_date).getall()
    end_dates = [string_ for string_ in end_dates if len(string_)>3 or string_=="TBD"]
    print(start_dates)
    print(end_dates)
    xpath_seasons = get_table_xpath(table_ind, 2)
    seasons = sel_wiki.xpath(xpath_seasons).getall()
    seasons = [string_ for string_ in seasons if len(string_)>3]
    print(seasons)
    year_list = get_all_season_years(seasons)
    for ind in range(len(start_dates)):
          start_date = get_date_string(start_dates[ind], year_list[ind][0])
          end_date = get_date_string(end_dates[ind], year_list[ind][1])
          dict_dates[seasons[ind]] = [start_date, end_date]
    return dict_dates

          

def get_table_xpath(table_ind, col_ind):
        xpath = ("//table[@class='wikitable'][" 
                        + str(table_ind) 
                        + "]//tr[not(.//i)]/td["
                        + str(col_ind)
                        + "]//text()")
        return xpath

def get_all_season_years(season_list):
      year_list = []
      for season in season_list:
            year_tuple = get_season_years(season)
            year_list.append(year_tuple)
      return year_list


def get_season_years(season_string):
      if len(season_string)==4:
           return season_string, season_string
      start_year = season_string[0:4]
      print(season_string)
      if season_string[3] == "9":
           if season_string[2] == "9":
                season_string = "2000" + season_string[5:]
           else:
                season_string = (season_string[0:2] 
                                    + str(int(season_string[2]) + 1)
                                    + "0" 
                                    + season_string[4:])
                print(season_string)
      end_year = season_string[0:2] + season_string[5:]
      return start_year, end_year
      
def month_string_to_number(month_str):
    # Define a dictionary mapping month names and abbreviations to numbers
   month_map = {
        'January': 1, 'Jan': 1,
        'February': 2, 'Feb': 2,
        'March': 3, 'Mar': 3,
        'April': 4, 'Apr': 4,
        'May': 5,
        'June': 6, 'Jun': 6,
        'July': 7, 'Jul': 7,
        'August': 8, 'Aug': 8,
        'September': 9, 'Sep': 9, 'Sept': 9,
        'October': 10, 'Oct': 10,
        'November': 11, 'Nov': 11,
        'December': 12, 'Dec': 12
    }

    # Normalize the input string to lowercase to make the function case-insensitive

    # Check if the normalized month string is in the month_map dictionary
   if month_str in month_map:
      num_string = str(month_map[month_str])
   else:
      raise ValueError(f"Invalid month name: {month_str}")
   if len(num_string) == 1:
          num_string = "0" + num_string
   return num_string
   
def get_date_string(month_day_string, year):
     if month_day_string=="TBD":
          return month_day_string 
     month = re.findall('^([A-Za-z]+)\s', month_day_string)[0]
     month_num = month_string_to_number(month)
     day = re.findall('\s(.+)', month_day_string)[0]
     if len(day)==1:
          day = "0" + day
     return str(year) + "-" + month_num + "-" + str(day)