#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 12:54:53 2018

@author: markvonoven
"""

# import packages
import urllib3
import certifi
from bs4 import BeautifulSoup
import bs4
import pandas as pd
import datetime
from jobs import SRjobs

#settings
http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where())
today = datetime.datetime.today()
gamelog = []
translator = pd.read_csv('/Users/markvonoven/Projects/CollegeFootball/SRinput/valid_school_translation.csv')
HTTPnames = translator['HTTPname']


def GL_off_scraper(teams, years):
    """
    teams - can pass in a single team or list of teams...alternatively passing * will scrape all known teams
    years - must be a list (can be a list of one)
    """
    if teams == '*':
        schools = HTTPnames
    else:
        schools = [teams]
        
    if type(years) == list:
        years = years.sort()  
    else:
        years = [years]

    for school in schools:
        for year in years:
            #scrape the data and write the df
            url = "http://www.sports-reference.com/cfb/schools/"+school+"/"+str(year)+"/gamelog/"
            response = http.request('GET', url)
            soup = BeautifulSoup(response.data, features="html.parser")
            cnt = 0
    
            for row in soup.findAll('tr'):
                try:
                    col1=row.findAll('th')
                    Game=col1[0].string
                    col=row.findAll('td')
                    Date = col[0].get_text()
                    Loc = col[1].get_text()
                    Team = translator[translator['HTTPname'] == school]['School'].values[0]
                    Opp = col[2].get_text()
                    Result = col[3].get_text()
                    Pass_cmp = col[4].get_text()
                    Pass_att = col[5].get_text()
                    Pass_pct = col[6].get_text()
                    Pass_yds = col[7].get_text()
                    Pass_TD = col[8].get_text()
                    Rush_att = col[9].get_text()
                    Rush_yds = col[10].get_text()
                    Rush_avg = col[11].get_text()
                    Rush_TD = col[12].get_text()
                    TO_plays = col[13].get_text()
                    TO_yds = col[14].get_text()
                    TO_avg = col[15].get_text()
                    FD_pass = col[16].get_text()
                    FD_rush = col[17].get_text()
                    FD_pen = col[18].get_text()
                    FD_tot = col[19].get_text()
                    Pen_num = col[20].get_text()
                    Pen_yds = col[21].get_text()
                    Turn_fum = col[22].get_text()
                    Turn_int = col[23].get_text()
                    Turn_tot = col[24].get_text()
                    Season = year
    
                    gamelog.append([Season, Game, Date, Team, Loc, Opp, Result, Pass_cmp, Pass_att, Pass_pct, Pass_yds, Pass_TD,
                                   Rush_att, Rush_yds, Rush_avg, Rush_TD, TO_plays, TO_yds, TO_avg, FD_pass,
                                   FD_rush, FD_pen, FD_tot, Pen_num, Pen_yds, Turn_fum, Turn_int, Turn_tot])
                    cnt += 1
                except:
                    pass
            if cnt > 0:
                print("Finished writing " + str(year), school + " with " + str(cnt) + " records")
            
    GL_final=pd.DataFrame(gamelog,columns=['Season', 'Game', 'Date', 'Team', 'Loc', 'Opp', 'Result', 'Pass_cmp',
                                                  'Pass_att', 'Pass_pct', 'Pass_yds', 'Pass_TD',
                                                  'Rush_att', 'Rush_yds', 'Rush_avg', 'Rush_TD', 'TO_plays',
                                                  'TO_yds', 'TO_avg', 'FD_pass',
                                                  'FD_rush', 'FD_pen', 'FD_tot', 'Pen_num', 'Pen_yds', 'Turn_fum',
                                                  'Turn_int', 'Turn_tot'])
    GL_final['Gamecode'] = GL_final.apply(lambda x: SRjobs.gamecode(x['Date'], x['Team'], x['Opp']), axis=1)
    GL_final.set_index(['Season', 'Gamecode'], inplace=True)
    
    return GL_final

