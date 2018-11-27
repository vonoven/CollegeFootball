# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# import packages
import urllib3
import certifi
import csv
from bs4 import BeautifulSoup
import re
import pandas as pd
import datetime

#settings
http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where())
first_season = 2014
last_complete_season = 2017
history_list = ['2014', '2015', '2016', '2017']
yrs_list = ['2014', '2015', '2016', '2017', '2018']
today = datetime.datetime.today()
G_year = today.year
history_filepath = './SRinput/current/schedule_history.csv'

#define some helper functions
def monthToNum(shortMonth):
    return{
            'Jan' : 1, 'Feb' : 2, 'Mar' : 3, 'Apr' : 4, 'May' : 5, 'Jun' : 6,
            'Jul' : 7, 'Aug' : 8, 'Sep' : 9, 'Oct' : 10, 'Nov' : 11, 'Dec' : 12
    }[shortMonth]

def dateToTimeStamp(datestring, timestring):
    """
    Given the following formats for datestring and timestring, function returns a valid datetime
    datestring = 'May 28, 2005'
    timestring = '2:00 PM'
    """
    dlength = len(datestring)
    mon = monthToNum(datestring[0:3])
    year = int(datestring[dlength-4:])
    middle = datestring[3:-4]
    day = int(middle.strip().strip(','))
    if timestring == '0':
        return datetime.datetime(year, mon, day)
    else:
        tlength = len(timestring)
        M = timestring[tlength-2:]
        hour = int(timestring[:timestring.find(':')])
        if (M == 'PM') & (hour != 12):
            hour = int(timestring[:timestring.find(':')]) + 12
        minute = int(timestring[timestring.find(':')+1:timestring.find(':')+3])
    return datetime.datetime(year, mon, day, hour, minute)

def winner_home(string):
    """
    Used for the schedule tables in Sports-Reference.com to create
    a binary Game_home column, since they use @ symbols in the original
    Added N for use with the Gamelogs
    """
    if string == '@':
        return 0
    elif string == 'N':
        return 0
    else:
        return 1
    
def fill_time(timestamp):
    """
    Helper function to fill empty Time values
    for games where the time is missing (i.e. All of 2015 Season)
    """
    if len(timestamp) > 0:
        return timestamp
    else:
        return '0'
    
def concat_mult_ref_tables(filename, yrs):
    """Return a dataframe that concatenates all 
    files across a list of years, with the year set as a key
    """
    # create a list to store the dfs
    df_list = []
    headerlist = ['Year', 'Weeknum', 'Date', 'Time', 'Day', 'Team', 'Team_Pts', 'At_sym', 'Opp', 'Opp_Pts', 'Notes']
    
    for yr in yrs: 
        temp_df = None   #clear out the df
        temp_df = pd.read_csv('./SRinput/' + str(yr) + '/schedule' + str(yr) + '.csv', header=None)  #read in the file
        df_list.append(temp_df)
        
    final_df = pd.concat(df_list, ignore_index = True)
    final_df.columns = headerlist
    
    return final_df

def get_nz_rank(team):
    """
    Each team name in the schedule is preceded with a ranking (if ranked) - this function
    extracts the ranking and normalizes it for use in data modeling
    """
    ff = team[0:4]
    start_paren = ff.find('(')
    end_paren = ff.find(')')
    if end_paren > 0:
        return 1 - (int(team[start_paren+1:end_paren]) / 25)
    else:
        return 0
    
def drop_rank(team):
    """
    Used to standardize team names after extracting the rank (if it exists)
    """
    ff = team[0:4]
    end_paren = ff.find(')')
    if end_paren > 0:
        return team[end_paren+1:].strip()  # the first character of ranked teams has a shitty unicode character
    else:
        return team  
    
def flipper(flag):
    """
    Flips 1's to 0's and vice versa
    """
    if flag == 0:
        return 1
    if flag == 1:
        return 0
    
def clean_past_schedule(schedule_mstr):
    """
    Given a schedule of games from Sports-Reference.com, this function will employ 
    several functions to clean up the data, including:
        Creating a valid Timestamp
        Reducing to only the played games
        Standardizing team names and extracting any rankings
        Creating the Game_home indicator
        Eliminating any cancelled games
        Adding the Won column
        "Doubling up" the schedule, so every team is listed individually (therefore each game has two rows)
    """
    # Fill any missing Time values with 0
    schedule_mstr['Time'] = schedule_mstr.apply(lambda x: fill_time(x['Time']), axis=1)
    # Adjust the date column to a true datetime dtype and remove Time column
    schedule_mstr['Date'] = schedule_mstr.apply(lambda x: dateToTimeStamp(x['Date'], x['Time']), axis=1)
    # Keep only the games that have been played
    schedule_mstr = schedule_mstr[schedule_mstr['Date'] < today]
    # Drop Time column, no longer necessary
    schedule_mstr = schedule_mstr.drop('Time', axis=1)
    # Extract rankings where applicable from team names
    schedule_mstr['Team_rank'] = schedule_mstr.apply(lambda x: get_nz_rank(x['Team']), axis=1)
    schedule_mstr['Opp_rank'] = schedule_mstr.apply(lambda x: get_nz_rank(x['Opp']), axis=1)
    # Create binary value for home games and drop @ symbol column
    schedule_mstr['Game_home'] = schedule_mstr.apply(lambda x: winner_home(x['At_sym']), axis=1)
    schedule_mstr = schedule_mstr.drop('At_sym', axis=1)
    # Clean up team names
    schedule_mstr['Team'] = schedule_mstr.apply(lambda x: drop_rank(x['Team']), axis=1)
    schedule_mstr['Opp'] = schedule_mstr.apply(lambda x: drop_rank(x['Opp']), axis=1)
    # Drop any cancelled games (games with NaN in the scores column)
    canc_games_list = schedule_mstr[schedule_mstr['Team_Pts'].isnull()]
    schedule_mstr = schedule_mstr.drop(canc_games_list.index.values.astype(int))
    # Add won column before adding loser rows
    schedule_mstr['Won'] = 1
    
    dopplegngr = schedule_mstr.copy()
    # rename columns to perform the 'swap'
    dopplegngr.columns = ['Year', 'Weeknum', 'Date', 'Day', 'Opp', 'Opp_Pts', 'Team',
                          'Team_Pts', 'Notes', 'Opp_rank', 'Team_rank', 'Game_home', 'Won']
    # rearrange the columns so the axis matches the original
    cols = ['Year', 'Weeknum', 'Date', 'Day', 'Team', 'Team_Pts', 
                            'Opp', 'Opp_Pts', 'Notes', 'Team_rank', 'Opp_rank', 'Game_home', 'Won']
    dopplegngr = dopplegngr[cols]
    dopplegngr['Game_home'] = dopplegngr.apply(lambda x: flipper(x['Game_home']), axis=1)
    dopplegngr['Won'] = dopplegngr.apply(lambda x: flipper(x['Won']), axis=1)

    schedule_mstr = pd.concat([schedule_mstr, dopplegngr])
    
    cols = ['Year', 'Date', 'Team', 'Opp', 'Won', 'Game_home', 'Team_rank', 'Opp_rank']
    schedule_mstr = schedule_mstr[cols]
    schedule_mstr.set_index('Year', inplace=True)
    schedule_mstr['Season'] = schedule_mstr.index
    cols1 = ['Season', 'Date', 'Team', 'Opp', 'Won', 'Game_home', 'Team_rank', 'Opp_rank']
    schedule_mstr = schedule_mstr[cols1]
    schedule_mstr = schedule_mstr.sort_index()
    
    return schedule_mstr

def clean_future_schedule(schedule_mstr):
    """
    Given a schedule of games from Sports-Reference.com, this function will employ 
    several functions to clean up the data, including:
        Creating a valid Timestamp
        Reducing to only the future games
        Standardizing team names and extracting any rankings
        Creating the Game_home indicator
        Adding the Won column with TBD
    """
    # Fill any missing Time values with 0
    schedule_mstr['Time'] = schedule_mstr.apply(lambda x: fill_time(x['Time']), axis=1)
    # Adjust the date column to a true datetime dtype and remove Time column
    schedule_mstr['Date'] = schedule_mstr.apply(lambda x: dateToTimeStamp(x['Date'], x['Time']), axis=1)
    # Save the upcoming games for later
    future_mstr = schedule_mstr[schedule_mstr['Date'] > today]
    # Drop Time column, no longer necessary
    future_mstr = future_mstr.drop('Time', axis=1)
    # Extract rankings where applicable from team names
    future_mstr['Team_rank'] = future_mstr.apply(lambda x: get_nz_rank(x['Team']), axis=1)
    future_mstr['Opp_rank'] = future_mstr.apply(lambda x: get_nz_rank(x['Opp']), axis=1)
    # Create binary value for home games and drop @ symbol column
    future_mstr['Game_home'] = future_mstr.apply(lambda x: winner_home(x['At_sym']), axis=1)
    future_mstr = future_mstr.drop('At_sym', axis=1)
    # Clean up team names
    future_mstr['Team'] = future_mstr.apply(lambda x: drop_rank(x['Team']), axis=1)
    future_mstr['Opp'] = future_mstr.apply(lambda x: drop_rank(x['Opp']), axis=1)
    # Add the won column with TBD just for concatenation purposes
    future_mstr['Won'] = 'TBD'
    
    cols = ['Year', 'Date', 'Team', 'Opp', 'Won', 'Game_home', 'Team_rank', 'Opp_rank']
    future_mstr = future_mstr[cols]
    future_mstr.set_index('Year', inplace=True)
    future_mstr['Season'] = future_mstr.index
    cols1 = ['Season', 'Date', 'Team', 'Opp', 'Won', 'Game_home', 'Team_rank', 'Opp_rank']
    future_mstr = future_mstr[cols1]
    
    return future_mstr
    
def get_season_played_games():
    """
    Master function for getting all the played games this season
    and cleaning them up.  This function returns a list of played games,
    by team (two rows for each game), ready for model training
    """
    print("Initiate get_season_played_games")
    #scrape the data and write the .csv files
    games = []
    url = "http://www.sports-reference.com/cfb/years/"+str(G_year)+"-schedule.html"
    response = http.request('GET', url)
    soup = BeautifulSoup(response.data, features="html.parser")
    cnt = 0
    for row in soup.findAll('tr'):
        try:
            col1=row.findAll('th')
            Rank=col1[0].string
            col=row.findAll('td')
            Weeknum = col[0].get_text()
            Date = col[1].get_text()
            Time = col[2].get_text()
            Day = col[3].get_text()
            Winner = col[4].get_text()
            Pts = col[5].get_text()
            At_sym = col[6].get_text()
            Loser = col[7].get_text()
            Pts2 = col[8].get_text()
            TV = col[9].get_text()
            Notes = col[10].get_text()
            Year = G_year
            games.append([Year, Weeknum, Date, Time, Day, Winner, Pts, At_sym, Loser, Pts2, Notes])
            cnt += 1
        except:
            pass
    print("Finished scraping " + str(G_year) + " schedule with " + str(cnt) + " rows")
    
    schedule_mstr = pd.DataFrame(games, columns=['Year', 'Weeknum', 'Date', 'Time', 'Day', 'Team',
                                                 'Team_Pts', 'At_sym', 'Opp', 'Opp_Pts', 'Notes'])
    
    schedule_mstr = clean_past_schedule(schedule_mstr)
    gm_cnt = schedule_mstr.shape[0]
    
    print("Successfully loaded " + str(gm_cnt/2) + " played games from " + str(G_year))
    
    return schedule_mstr


def get_season_future_games():
    """
    Master function for getting all the remaining games this season
    and cleaning them up.  This function returns a list of future games,
    ready for model prediction
    """
    print("Initiate get_season_future_games")
    #scrape the data and write the .csv files
    games = []
    url = "http://www.sports-reference.com/cfb/years/"+str(G_year)+"-schedule.html"
    response = http.request('GET', url)
    soup = BeautifulSoup(response.data, features="html.parser")
    cnt = 0
    for row in soup.findAll('tr'):
        try:
            col1=row.findAll('th')
            Rank=col1[0].string
            col=row.findAll('td')
            Weeknum = col[0].get_text()
            Date = col[1].get_text()
            Time = col[2].get_text()
            Day = col[3].get_text()
            Winner = col[4].get_text()
            Pts = col[5].get_text()
            At_sym = col[6].get_text()
            Loser = col[7].get_text()
            Pts2 = col[8].get_text()
            TV = col[9].get_text()
            Notes = col[10].get_text()
            Year = G_year
            games.append([Year, Weeknum, Date, Time, Day, Winner, Pts, At_sym, Loser, Pts2, Notes])
            cnt += 1
        except:
            pass
    print("Finished scraping " + str(G_year) + " schedule with " + str(cnt) + " rows")
    
    schedule_mstr = pd.DataFrame(games, columns=['Year', 'Weeknum', 'Date', 'Time', 'Day', 'Team',
                                                 'Team_Pts', 'At_sym', 'Opp', 'Opp_Pts', 'Notes'])
    
    future_mstr = clean_future_schedule(schedule_mstr)
    gm_cnt = future_mstr.shape[0]
    
    print("Successfully loaded future_mstr with " + str(gm_cnt) + " remaining games in " + str(G_year))
    
    return future_mstr

def create_history():
    """
    This function is intended for one-time usage, creating and saving a valid history
    of played games.  Future intent is to write an append function which will replace the need
    to rewrite history every time we want to update the models
    """
    games = []
    #scrape the data and write the .csv files
    for year in range(first_season, last_complete_season+1):
        url = "http://www.sports-reference.com/cfb/years/"+str(year)+"-schedule.html"
        response = http.request('GET', url)
        soup = BeautifulSoup(response.data, features="html.parser")
        cnt = 0
        for row in soup.findAll('tr'):
            try:
                col1=row.findAll('th')
                Rank=col1[0].string
                col=row.findAll('td')
                Weeknum = col[0].get_text()
                Date = col[1].get_text()
                Time = col[2].get_text()
                Day = col[3].get_text()
                Winner = col[4].get_text()
                Pts = col[5].get_text()
                At_sym = col[6].get_text()
                Loser = col[7].get_text()
                Pts2 = col[8].get_text()
                TV = col[9].get_text()
                Notes = col[10].get_text()
                Year = year
                games.append([Year, Weeknum, Date, Time, Day, Winner, Pts, At_sym, Loser, Pts2, Notes])
                cnt += 1
            except:
                pass
        print("Finished scraping " + str(year) + " schedule with " + str(cnt) + " rows")
        
    schedule_mstr = pd.DataFrame(games, columns=['Year', 'Weeknum', 'Date', 'Time', 'Day', 'Team',
                                                 'Team_Pts', 'At_sym', 'Opp', 'Opp_Pts', 'Notes'])
        
    schedule_mstr = clean_past_schedule(schedule_mstr)
        
    schedule_mstr.to_csv(history_filepath)
    print("Saved history schedule to " + history_filepath)
    
def get_history():
    """
    Pulls in the existing history of played games and preps the data for modeling
    """
    gametime_mstr = pd.read_csv(history_filepath)
    gametime_mstr = gametime_mstr.drop('Unnamed: 0', axis=1)
    cols = ['Year', 'Date', 'Team', 'Opp', 'Won', 'Game_home', 'Team_rank', 'Opp_rank']
    gametime_mstr = gametime_mstr[cols]
    gametime_mstr.set_index('Year', inplace=True)
    gametime_mstr['Season'] = gametime_mstr.index
    cols1 = ['Season', 'Date', 'Team', 'Opp', 'Won', 'Game_home', 'Team_rank', 'Opp_rank']
    gametime_mstr = gametime_mstr[cols1]
    gametime_mstr['Date'] = pd.to_datetime(gametime_mstr['Date'])
    return gametime_mstr
    