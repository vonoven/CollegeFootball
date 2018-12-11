#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 13:21:56 2018

@author: markvonoven
"""
#packages
import pandas as pd

#settings
first_year = 2014

#dataframes
conference_mstr = pd.read_csv('/Users/markvonoven/Projects/CollegeFootball/input/conference_master.csv')

def get_season_str_yr(gamedate):
    """ Takes the date of a game and 
    returns the season year as a string
    DEPRECATED and replaced with get_season_yr...keeping just in case
    """
    if gamedate.month == 1:  # if this is a bowl game
        str_year = str(gamedate.year - 1)
    else:
        str_year = str(gamedate.year)
    return str_year

def get_season_yr(gamedate):
    """ Takes the date of a game and 
    returns the season year as an int"""
    if gamedate.month == 1:  # if this is a bowl game
        year = gamedate.year - 1
    else:
        year = gamedate.year
    return year

def season_record_to_date(df, team, date):
    """Given a team and date, this function returns the season win percentage as a float
    up to, but not including, that date.  If this is the first game of the season
    it returns the percentage from last season"""
    # account for bowl games that occur in next calendar year
    str_year = get_season_yr(date)
    # locate the full season for this team and calculate wins
    team_season = df[df['Team'] == team].loc[str_year]
    if isinstance(team_season, pd.core.series.Series):
        games = 0
    else:
        games_to_date = team_season[team_season['Date'] < date]
        games = games_to_date.shape[0]
    # account for first game of the season - use last year unless we don't have it
    if ((games == 0) & (str_year != first_year)):
        str_year = date.year - 1
        # Handle errors when there is no last season
        try:
            last_season = df[df['Team'] == team].loc[str_year]
            games = last_season.shape[0]
            wins = last_season['Won'].sum()
            # don't allow to divide by zero
            if games > 0:
                win_perc = wins / games
            else:
                win_perc = 0
        except KeyError:
            win_perc = 0
    elif ((games == 0) & (str_year == first_year)):
        return 0
    else:
        wins = games_to_date['Won'].sum()
        win_perc = wins / games
    return round(win_perc, 3)

def conf_record_to_date(df, team, date):
    """Given a team and date, this function returns the season win percentage against 
    conference teams as a float up to, but not including, that date.  If this is the first 
    conference game of the season it returns the win percentage from last season"""
    # account for bowl games that occur in next calendar year
    str_year = get_season_yr(date)
    # locate the full season for this team and calculate wins
    team_season = df[df['Team'] == team].loc[str_year][df[df['Team'] == team].loc[str_year]['Game_conf'] == 1]
    if isinstance(team_season, pd.core.frame.DataFrame):
        games_to_date = team_season[team_season['Date'] < date]
        games = games_to_date.shape[0]
    else:
        games = 0
    # account for first game of the season - use last year unless we don't have it
    if ((games == 0) & (str_year != first_year)):
        str_year = date.year - 1
        # Handle errors when there is no last season
        try:
            last_season = df[df['Team'] == team].loc[str_year][df[df['Team'] == team].loc[str_year]['Game_conf'] == 1]
            if isinstance(last_season, pd.core.frame.DataFrame):
                games = last_season.shape[0]
                wins = last_season['Won'].sum()
            else:
                games = 0
                wins = 0
            # don't allow to divide by zero
            if games > 0:
                win_perc = wins / games
            else:
                win_perc = 0
        except KeyError:
            win_perc = 0
    elif ((games == 0) & (str_year == first_year)):
        return 0
    else:
        wins = games_to_date['Won'].sum()
        win_perc = wins / games
    
    return round(win_perc, 3)

def get_conf(team, yr):
    try:
        conf_hist = conference_mstr[conference_mstr['School'] == team]
        conf_hist = conf_hist[(conf_hist['From'] <= yr) & (conf_hist['To'] >= yr)]
        return conf_hist['Conf'].values[0]
    except IndexError:
        return 'missing'

def in_conf_game(team1, team2, date):
    yr = get_season_yr(date)
    c1 = get_conf(team1, yr)
    c2 = get_conf(team2, yr)
    if c1 == 'missing':  #team one is not in a conference
        return 0
    elif c1 == c2:
        return 1
    else:
        return 0
    
def season_opps_to_date(df, team, date):
    """Given a team and date, this function returns a list of opponents
    up to, but not including, that date.  If this is the first game of the season
    it returns the list from last season"""
    # account for bowl games that occur in next calendar year
    str_year = get_season_yr(date)
    # locate the full season for this team and calculate wins
    team_season = df[df['Team'] == team].loc[str_year]
    if isinstance(team_season, pd.core.series.Series):
        games = 0
    else:
        games_to_date = team_season[team_season['Date'] < date]
        games = games_to_date.shape[0]
    # account for first game of the season - use last year unless we don't have it
    if ((games == 0) & (str_year != first_year)):
        str_year = date.year - 1
        # Handle errors when there is no last season
        try:
            last_season = df[df['Team'] == team].loc[str_year]
            games = last_season.shape[0]
            # don't allow to divide by zero
            if games > 0:
                opps = last_season['Opp']
            else:
                opps = []
        except KeyError:
            opps = []
    elif ((games == 0) & (str_year == first_year)):
        opps = []
    else:
        opps = games_to_date['Opp']
    return opps

def sos_record_to_date(df, team, date):
    """Given a team and date, this function returns the wins and games of opponents records
    up to, but not including, that date.  If this is the first game of the season
    it returns the numbers from last season"""
    # account for bowl games that occur in next calendar year
    str_year = get_season_yr(date)
    # locate the full season for this team and calculate wins
    team_season = df[df['Team'] == team].loc[str_year]
    if isinstance(team_season, pd.core.series.Series):
        games = 0
    else:
        games_to_date = team_season[team_season['Date'] < date]
        games = games_to_date.shape[0]
    # account for first game of the season - use last year unless we don't have it
    if ((games == 0) & (str_year != first_year)):
        str_year = date.year - 1
        # Handle errors when there is no last season
        try:
            last_season = df[df['Team'] == team].loc[str_year]
            games = last_season.shape[0]
            wins = last_season['Won'].sum()
            # don't allow to divide by zero
            if games > 0:
                win_game_tuple = (wins, games)
            else:
                win_game_tuple = (0, 0)
        except KeyError:
            win_game_tuple = (0, 0)
    elif ((games == 0) & (str_year == first_year)):
        return (0, 0)
    else:
        wins = games_to_date['Won'].sum()
        win_game_tuple = (wins, games)
    return win_game_tuple

def strength_of_schedule(df, team, date):
    opp_wins = 0
    opp_games = 0
    oppopp_wins = 0
    oppopp_games = 0
    opp_list = season_opps_to_date(df, team, date)
    if isinstance(opp_list, pd.core.series.Series):
        for opp in opp_list:  # find the opponents' records
            my_tuple = sos_record_to_date(df, opp, date)
            opp_wins += my_tuple[0]
            opp_games += my_tuple[1]
            oppopp_list = season_opps_to_date(df, opp, date)
            for oppopp in oppopp_list: # find the opponents' opponents' records
                oppopp_tuple = sos_record_to_date(df, oppopp, date)
                oppopp_wins += oppopp_tuple[0]
                oppopp_games += oppopp_tuple[1]
        if (opp_games > 0) & (oppopp_games > 0):
            return round(((2*(opp_wins/opp_games) + (oppopp_wins/oppopp_games))/3), 3)
        elif opp_games > 0:
            return round((2*(opp_wins/opp_games)), 3)
        else:
            return 0
    else:
        return 0
    
def apply_features(orig_df):
    """
    Intended for use with dataframes containing past game history
    This function adds engineered features to the played games for model training
    """
    new_df = orig_df.copy()
    #new_df['Team_SOS'] = new_df.apply(lambda x: strength_of_schedule(new_df, x['Team'], x['Date']), axis=1)
    #print('Added Team_SOS')
    new_df['Game_conf'] = new_df.apply(lambda x: in_conf_game(x['Team'], x['Opp'], x['Date']), axis=1)
    print('Added Game_conf')
    new_df['Team_SRTD'] = new_df.apply(lambda x: season_record_to_date(new_df, x['Team'], x['Date']), axis=1)
    print('Added Team_SRTD')
    new_df['Team_CRTD'] = new_df.apply(lambda x: conf_record_to_date(new_df, x['Team'], x['Date']), axis=1)
    print('Added Team_CRTD')
    new_df['Opp_SRTD'] = new_df.apply(lambda x: season_record_to_date(new_df, x['Opp'], x['Date']), axis=1)
    print('Added Opp_SRTD')
    new_df['Opp_CRTD'] = new_df.apply(lambda x: conf_record_to_date(new_df, x['Opp'], x['Date']), axis=1)
    print('Added Opp_CRTD')
    return new_df

def apply_future_features(future_df, full_history):
    """
    Intended for use with dataframes containing future games
    This function adds engineered features to the future games for model prediction
    NOTE:  A full history dataframe (with features) is required to make this work
    """
    new_df = future_df.copy()
    new_df['Game_conf'] = new_df.apply(lambda x: in_conf_game(x['Team'], x['Opp'], x['Date']), axis=1)
    print('Added Game_conf')
    #new_df['Team_SOS'] = new_df.apply(lambda x: strength_of_schedule(full_history, x['Team'], x['Date']), axis=1)
    #print('Added Team_SOS')
    new_df['Team_SRTD'] = new_df.apply(lambda x: season_record_to_date(full_history, x['Team'], x['Date']), axis=1)
    print('Added Team_SRTD')
    new_df['Team_CRTD'] = new_df.apply(lambda x: conf_record_to_date(full_history, x['Team'], x['Date']), axis=1)
    print('Added Team_CRTD')
    new_df['Opp_SRTD'] = new_df.apply(lambda x: season_record_to_date(full_history, x['Opp'], x['Date']), axis=1)
    print('Added Opp_SRTD')
    new_df['Opp_CRTD'] = new_df.apply(lambda x: conf_record_to_date(full_history, x['Opp'], x['Date']), axis=1)
    print('Added Opp_CRTD')
    return new_df
