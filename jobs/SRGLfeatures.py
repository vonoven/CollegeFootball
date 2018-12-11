#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 12:45:21 2018

@author: markvonoven
"""

import pandas as pd

GLstats = pd.read_csv('/Users/markvonoven/Projects/CollegeFootball/SRoutput/past_games_w_GLstats.csv')
GLstats.set_index(['Season', 'Gamecode'], inplace=True)
GLstats['Date'] = pd.to_datetime(GLstats['Date'])
GLstats = GLstats.sort_values(by=['Date'])

def offensive_strategy(team, date):
    # Calulating offensive strategy going into each played game...for future games it will give IndexError
    # because GLstats doesn't have future game stats, so instead it needs to find the last game we have in GLstats
    try:  # simple stat pull for past games
        Pass_att = GLstats[GLstats['Team'] == team][GLstats[GLstats['Team'] == team]['Date'] == date].iloc[0]['Team_Off_Pass_att']
        Rush_att = GLstats[GLstats['Team'] == team][GLstats[GLstats['Team'] == team]['Date'] == date].iloc[0]['Team_Off_Rush_att']
    except IndexError:  # this is for future games, which uses the last known game stats
        try:
            laststatdate = max(GLstats[GLstats['Team'] == team]['Date'])
            Pass_att = GLstats[GLstats['Team'] == team][GLstats[GLstats['Team'] == team]['Date'] == laststatdate].iloc[0]['Team_Off_Pass_att']
            Rush_att = GLstats[GLstats['Team'] == team][GLstats[GLstats['Team'] == team]['Date'] == laststatdate].iloc[0]['Team_Off_Rush_att']
        except ValueError:  # this future game team has no past stats, return balanced offensive strategy
            return 1
    if (Pass_att == 0):
        return 0
    elif (Rush_att == 0):
        return 1
    else:
        off_strat = (Pass_att / Rush_att)   
        return round(off_strat, 3)
    
def defensive_strength(team, date):
    # Calulating defensive strength going into each played game...for future games it will give IndexError
    # because GLstats doesn't have future game stats, so instead it needs to find the last game we have in GLstats
    try:  # simple stat pull for past games
        Pass_yds = GLstats[GLstats['Team'] == team][GLstats[GLstats['Team'] == team]['Date'] == date].iloc[0]['Team_Def_Pass_yds']
        Rush_yds = GLstats[GLstats['Team'] == team][GLstats[GLstats['Team'] == team]['Date'] == date].iloc[0]['Team_Def_Rush_yds']
    except IndexError:  # this is for future games, which uses the last known game stats
        try:
            laststatdate = max(GLstats[GLstats['Team'] == team]['Date'])
            Pass_yds = GLstats[GLstats['Team'] == team][GLstats[GLstats['Team'] == team]['Date'] == laststatdate].iloc[0]['Team_Def_Pass_yds']
            Rush_yds = GLstats[GLstats['Team'] == team][GLstats[GLstats['Team'] == team]['Date'] == laststatdate].iloc[0]['Team_Def_Rush_yds']
        except ValueError:  # this future game team has no past stats, return balanced defensive strength
            return 1
    if (Pass_yds == 0):
        return 0
    elif (Rush_yds == 0):
        return 1
    else:
        def_strength = (Pass_yds / Rush_yds)
        return round(def_strength, 3)
    
def apply_features(orig_df):
    new_df = orig_df.copy()
    new_df['Team_OffStrat'] = new_df.apply(lambda x: offensive_strategy(x['Team'], x['Date']), axis=1)
    print('Added Team_OffStrat')
    new_df['Opp_OffStrat'] = new_df.apply(lambda x: offensive_strategy(x['Opp'], x['Date']), axis=1)
    print('Added Opp_OffStrat')
    new_df['Team_DefStren'] = new_df.apply(lambda x: defensive_strength(x['Team'], x['Date']), axis=1)
    print('Added Team_DefStren')
    new_df['Opp_DefStren'] = new_df.apply(lambda x: defensive_strength(x['Opp'], x['Date']), axis=1)
    print('Added Opp_DefStren')
    return new_df