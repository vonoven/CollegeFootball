#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 16:02:46 2018

@author: markvonoven
"""

import pandas as pd
import math
from jobs import SRfeatures

GL_offense_mstr = pd.read_csv('/Users/markvonoven/Projects/CollegeFootball/SRinput/current/GL_offense.csv')
GL_offense_mstr.set_index(['Season', 'Gamecode'], inplace=True)
GL_offense_mstr['Date'] = pd.to_datetime(GL_offense_mstr['Date'])
GL_offense_mstr.sort_values(by=['Date'])

GL_defense_mstr = pd.read_csv('/Users/markvonoven/Projects/CollegeFootball/SRinput/current/GL_defense.csv')
GL_defense_mstr.set_index(['Season', 'Gamecode'], inplace=True)
GL_defense_mstr['Date'] = pd.to_datetime(GL_defense_mstr['Date'])
GL_defense_mstr.sort_values(by=['Date'])

def get_GL_team_sumstat_STD(stat, team, date, season, OD):
    if OD == 'O':
        try:
            team_df = GL_offense_mstr[GL_offense_mstr['Team'] == team].loc[season]
            if isinstance(team_df, pd.core.series.Series):
                return 0
            else:
                date = pd.Timestamp(date.date())  #strip the time
                team_df = team_df[team_df['Date'] < date]
                return team_df[stat].sum()
        except KeyError:
            return 0
    elif OD == 'D':
        try:
            team_df = GL_defense_mstr[GL_defense_mstr['Team'] == team].loc[season]
            if isinstance(team_df, pd.core.series.Series):
                return 0
            else:
                date = pd.Timestamp(date.date())  #strip the time
                team_df = team_df[team_df['Date'] < date]
                return team_df[stat].sum()
        except KeyError:
            return 0
    else:
        return 0

def get_GL_team_meanstat_STD(stat, team, date, season, OD):
    if OD == 'O':
        try:
            team_df = GL_offense_mstr[GL_offense_mstr['Team'] == team].loc[season]
            if isinstance(team_df, pd.core.series.Series):
                return 0
            else:
                date = pd.Timestamp(date.date())  #strip the time
                team_df = team_df[team_df['Date'] < date]
            if math.isnan(team_df[stat].mean()):
                return 0
            else:
                return team_df[stat].mean()
        except KeyError:
            return 0
    elif OD == 'D':
        try:
            team_df = GL_defense_mstr[GL_defense_mstr['Team'] == team].loc[season]
            if isinstance(team_df, pd.core.series.Series):
                return 0
            else:
                date = pd.Timestamp(date.date())  #strip the time
                team_df = team_df[team_df['Date'] < date]
            if math.isnan(team_df[stat].mean()):
                return 0
            else:
                return team_df[stat].mean()
        except KeyError:
            return 0
    else:
        return 0

def add_GLstats(past_games):
# =============================================================================
#     sum_stats = ['Pass_cmp', 'Pass_att', 'Pass_yds', 'Pass_TD', 'Rush_att', 'Rush_yds', 
#              'Rush_TD', 'TO_plays', 'TO_yds', 'FD_pass', 'FD_rush', 'FD_pen', 
#              'FD_tot', 'Pen_num', 'Pen_yds', 'Turn_fum', 'Turn_int', 'Turn_tot']
#     mean_stats = ['Pass_pct', 'Rush_avg', 'TO_avg']
# =============================================================================
    temp_df = past_games.copy()
    sum_stats = ['Pass_att', 'Pass_yds', 'Rush_att', 'Rush_yds']
    mean_stats = ['Pass_pct', 'Rush_avg']
    for stat in sum_stats:
        temp_df['Team_Off_' + stat] = temp_df.apply(lambda x: 
                                            get_GL_team_sumstat_STD(stat, x['Team'], 
                                                                                x['Date'], SRfeatures.get_season_yr(x['Date']), 'O'), axis=1)
    print('Updated Team_Off_sumstats')
    for stat in mean_stats:
        temp_df['Team_Off_' + stat] = temp_df.apply(lambda x: 
                                            get_GL_team_meanstat_STD(stat, x['Team'], 
                                                                                x['Date'], SRfeatures.get_season_yr(x['Date']), 'O'), axis=1)
    print('Updated Team_Off_meanstats')
    for stat in sum_stats:
        temp_df['Team_Def_' + stat] = temp_df.apply(lambda x: 
                                            get_GL_team_sumstat_STD(stat, x['Team'], 
                                                                                x['Date'], SRfeatures.get_season_yr(x['Date']), 'D'), axis=1)
    print('Updated Team_Def_sumstats')
    for stat in mean_stats:
        temp_df['Team_Def_' + stat] = temp_df.apply(lambda x: 
                                            get_GL_team_meanstat_STD(stat, x['Team'], 
                                                                                x['Date'], SRfeatures.get_season_yr(x['Date']), 'D'), axis=1)
    print('Updated Team_Def_meanstats')
    
    temp_df.to_csv('/Users/markvonoven/Projects/CollegeFootball/SRoutput/past_games_w_GLstats.csv')
    print('Finished updating the GLstats for the new past_games')
    
    return temp_df