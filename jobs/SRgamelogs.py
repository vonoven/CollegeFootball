#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 16:02:46 2018

@author: markvonoven
"""

import pandas as pd
import math

GL_offense_mstr = pd.read_csv('/Users/markvonoven/Projects/CollegeFootball/SRinput/current/GL_offense.csv')
GL_offense_mstr.set_index('Season', inplace=True)
GL_offense_mstr['Date'] = pd.to_datetime(GL_offense_mstr['Date'])
GL_offense_mstr.sort_values(by=['Date'])

GL_defense_mstr = pd.read_csv('/Users/markvonoven/Projects/CollegeFootball/SRinput/current/GL_defense.csv')
GL_defense_mstr.set_index('Season', inplace=True)
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

