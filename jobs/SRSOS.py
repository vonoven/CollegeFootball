#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 11 10:56:21 2018

@author: markvonoven
"""

import pandas as pd
from jobs import SRfeatures

first_year = 2014
df = pd.read_csv('/Users/markvonoven/Projects/CollegeFootball/SRinput/current/past_games.csv')
df.set_index(['Season', 'Gamecode'], inplace=True)
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values(by=['Date'])

def season_opps_to_date(team, date):
    """Given a team and date, this function returns a list of opponents
    up to, but not including, that date.  If this is the first game of the season
    it returns the list from last season"""
    opps_list = []
    # account for bowl games that occur in next calendar year
    str_year = SRfeatures.get_season_yr(date)
    # locate the full season for this team and calculate wins
    try:
        team_season = df[df['Team'] == team].loc[str_year]
    except KeyError:
        opps_list = []
        return opps_list
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
            if isinstance(last_season, pd.core.series.Series):
                opps_list = last_season['Opp']
            # don't allow to divide by zero
            elif games > 0:
                opps_list = last_season['Opp'].tolist()
            else:
                opps_list = []
        except KeyError:
            opps_list = []
    elif ((games == 0) & (str_year == first_year)):
        opps_list = []
    else:
        opps_list = games_to_date['Opp'].tolist()
    return opps_list

def sos_record_to_date(team, date, exc):
    """Given a team and date, this function returns the wins and games of opponents records
    up to, but not including, that date.  If this is the first game of the season
    it returns the numbers from last season"""
    # account for bowl games that occur in next calendar year
    str_year = SRfeatures.get_season_yr(date)
    # locate the full season for this team and calculate wins
    try:
        team_season = df[df['Team'] == team].loc[str_year]
    except KeyError:
        return (0, 0)
    if isinstance(team_season, pd.core.series.Series):
        games = 0
    else:
        games_to_date = team_season[team_season['Date'] < date]
        games_to_date = games_to_date[games_to_date['Opp'] != exc]  # don't count head to head matchups
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

def strength_of_schedule(team, date, verbose=False):
    if verbose:
        print('Attempting to find Strength of Schedule for ' + team + ' as of ' + str(date))
    opp_wins = 0
    opp_games = 0
    oppopp_wins = 0
    oppopp_games = 0
    opp_list = season_opps_to_date(team, date)
    if verbose:
        print('List of recent opponents for ' + team + ': ' + str(opp_list))
    # there was no list of opponents
    if not opp_list:
        if verbose:
            print('Sorry...did not find any!  SOS is ZERO!')
        return 0
    # the list of opponents was only one item
    elif type(opp_list) == str:
        if opp_list != team:
            my_tuple = sos_record_to_date(opp_list, date, team)
            opp_wins += my_tuple[0]
            opp_games += my_tuple[1]
            if verbose:
                print('I found one opponent...it is ' + opp_list + ' with ' + str(my_tuple[0]) + ' wins in ' + str(my_tuple[1]) + ' games')
        oppopp_list = season_opps_to_date(df, opp_list, date)
        if not oppopp_list:
            pass
        else:
            for oppopp in oppopp_list: # find the opponents' opponents' records
                if oppopp != team:
                    oppopp_tuple = sos_record_to_date(oppopp, date, team)
                    oppopp_wins += oppopp_tuple[0]
                    oppopp_games += oppopp_tuple[1]
    # we have a full list of opponents to check
    else:
        for opp in opp_list:  # find the opponents' records
            my_tuple = sos_record_to_date(opp, date, team)
            opp_wins += my_tuple[0]
            opp_games += my_tuple[1]
            if verbose:
                print('     ' + opp + ' had ' + str(my_tuple[0]) + ' wins in ' + str(my_tuple[1]) + ' games')
            oppopp_list = season_opps_to_date(opp, date)
            if not oppopp_list:
                pass
            elif type(oppopp_list) == str:
                if oppopp_list != team:
                    oppopp_tuple = sos_record_to_date(oppopp_list, date, team)
                    oppopp_wins += oppopp_tuple[0]
                    oppopp_games += oppopp_tuple[1]
                    if verbose:
                        print('I found one opponent...it is ' + oppopp_list + ' with ' + str(oppopp_tuple[0]) + ' wins in ' + str(oppopp_tuple[1]) + ' games')
            else:
                for oppopp in oppopp_list: # find the opponents' opponents' records
                    if oppopp != team:
                        oppopp_tuple = sos_record_to_date(oppopp, date, team)
                        oppopp_wins += oppopp_tuple[0]
                        oppopp_games += oppopp_tuple[1]
                        if verbose:
                            print('          ' + oppopp + ' had ' + str(oppopp_tuple[0]) + ' wins in ' + str(oppopp_tuple[1]) + ' games')
                    else:
                        if verbose:
                            print('          ' + oppopp + ' game and record was ignored because of head to head matchup')

    if oppopp_games == 0:
        if opp_games == 0:
            return 0
        else:
            if verbose:
                print('Total opponents record:  ' + str(opp_wins) + ' wins in ' + str(opp_games) + ' games')
            return round((opp_wins/opp_games), 3)
    else:
        if verbose:
            print('Total opponents record:  ' + str(opp_wins) + ' wins in ' + str(opp_games) + ' games')
            print('Total opponents opponents record:  ' + str(oppopp_wins) + ' wins in ' + str(oppopp_games) + ' games')
        return round(((2*(opp_wins/opp_games) + (oppopp_wins/oppopp_games))/3), 3)
