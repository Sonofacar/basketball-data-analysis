# Imports
import re
from bs4 import BeautifulSoup
import pandas
import sqlite3

# scraping library
from lib.get_page import page
from lib.season import season_info
from lib.game import game_data
from lib.team import team_info
from lib.player import player_info
from lib.other_info import referee_info, executive_info, coach_info
from lib.matching import *


# Initialize empty data frames
Game_Info = pandas.DataFrame({'Home_Team_Name': [],
                              'Away_Team_Name': [],
                              'Date': [],
                              'Location': [],
                              'Duration': [],
                              'Attendance': [],
                              'Game_ID': [],
                              'Home_Team_ID': [],
                              'Away_Team_ID': [],
                              'Season': [],
                              'Referee_ID1': [],
                              'Referee_ID2': [],
                              'Referee_ID3': []})
Playoff_Game_Info = pandas.DataFrame({'Home_Team_Name': [],
                                      'Away_Team_Name': [],
                                      'Date': [],
                                      'Location': [],
                                      'Duration': [],
                                      'Attendance': [],
                                      'Game_ID': [],
                                      'Home_Team_ID': [],
                                      'Away_Team_ID': [],
                                      'Season': [],
                                      'Referee_ID1': [],
                                      'Referee_ID2': [],
                                      'Referee_ID3': []})
Team_Info = pandas.DataFrame({'Name': [],
                              'Abbreviation': [],
                              'Wins': [],
                              'Losses': [],
                              'Location': [],
                              'Playoff_Appearance': [],
                              'League_Ranking': [],
                              'Team_ID': [],
                              'Season': [],
                              'Coach_ID': [],
                              'Executive_ID': []})
Team_Games = pandas.DataFrame({'Total_minutes': [],
                               'Field_Goals': [],
                               'Field_Goal_Attempts': [],
                               'Threes': [],
                               'Three_Attempts': [],
                               'Twos': [],
                               'Two_Attempts': [],
                               'Freethrows': [],
                               'Freethrow_Attempts': [],
                               'Offensive_Rebounds': [],
                               'Deffensive_Rebounds': [],
                               'Assists': [],
                               'Steals': [],
                               'Blocks': [],
                               'Turnovers': [],
                               'Fouls': [],
                               'Points': [],
                               'Win': [],
                               'Home': [],
                               'Game_ID': [],
                               'Season': [],
                               'Team_ID': [],
                               'Opponent_ID': []})
Team_Quarters = pandas.DataFrame({'Quarter': [],
                                  'Total_Minutes': [],
                                  'Field_Goals': [],
                                  'Field_Goal_Attempts': [],
                                  'Threes': [],
                                  'Three_Attempts': [],
                                  'Twos': [],
                                  'Two_Attempts': [],
                                  'Freethrows': [],
                                  'Freethrow_Attempts': [],
                                  'Offensive_Rebounds': [],
                                  'Deffensive_Rebounds': [],
                                  'Assists': [],
                                  'Steals': [],
                                  'Blocks': [],
                                  'Turnovers': [],
                                  'Fouls': [],
                                  'Points': [],
                                  'Win': [],
                                  'Home': [],
                                  'Game_ID': [],
                                  'Season': [],
                                  'Team_ID': [],
                                  'Opponent_ID': [],})
Team_Games_Playoffs = pandas.DataFrame({'Total_minutes': [],
                                        'Field_Goals': [],
                                        'Field_Goal_Attempts': [],
                                        'Threes': [],
                                        'Three_Attempts': [],
                                        'Twos': [],
                                        'Two_Attempts': [],
                                        'Freethrows': [],
                                        'Freethrow_Attempts': [],
                                        'Offensive_Rebounds': [],
                                        'Deffensive_Rebounds': [],
                                        'Assists': [],
                                        'Steals': [],
                                        'Blocks': [],
                                        'Turnovers': [],
                                        'Fouls': [],
                                        'Points': [],
                                        'Win': [],
                                        'Home': [],
                                        'Game_ID': [],
                                        'Season': [],
                                        'Team_ID': [],
                                        'Opponent_ID': []})
Team_Quarters_Playoffs = pandas.DataFrame({'Quarter': [],
                                           'Total_Minutes': [],
                                           'Field_Goals': [],
                                           'Field_Goal_Attempts': [],
                                           'Threes': [],
                                           'Three_Attempts': [],
                                           'Twos': [],
                                           'Two_Attempts': [],
                                           'Freethrows': [],
                                           'Freethrow_Attempts': [],
                                           'Offensive_Rebounds': [],
                                           'Deffensive_Rebounds': [],
                                           'Assists': [],
                                           'Steals': [],
                                           'Blocks': [],
                                           'Turnovers': [],
                                           'Fouls': [],
                                           'Points': [],
                                           'Win': [],
                                           'Home': [],
                                           'Game_ID': [],
                                           'Season': [],
                                           'Team_ID': [],
                                           'Opponent_ID': []})
Player_Info = pandas.DataFrame({'Name': [],
                                'Shoots': [],
                                'Birthday': [],
                                'High_School': [],
                                'College': [],
                                'Draft_Position': [],
                                'Draft_Team': [],
                                'Draft_Year': [],
                                'Debut_Date': [],
                                'Career_Seasons': [],
                                'Teams': [],
                                'Player_ID': []})
Player_Games = pandas.DataFrame({'Minutes': [],
                                 'Field_Goals': [],
                                 'Field_Goal_Attempts': [],
                                 'Threes': [],
                                 'Three_Attempts': [],
                                 'Twos': [],
                                 'Two_Attempts': [],
                                 'Freethrows': [],
                                 'Freethrow_Attempts': [],
                                 'Offensive_Rebounds': [],
                                 'Deffensive_Rebounds': [],
                                 'Assists': [],
                                 'Steals': [],
                                 'Blocks': [],
                                 'Turnovers': [],
                                 'Fouls': [],
                                 'Points': [],
                                 'PM': [],
                                 'Injured': [],
                                 'Win': [],
                                 'Home': [],
                                 'Player_ID': [],
                                 'Game_ID': [],
                                 'Season': [],
                                 'Team_ID': [],
                                 'Opponent_ID': []})
Player_Quarters = pandas.DataFrame({'Quarter': [],
                                    'Minutes': [],
                                    'Field_Goals': [],
                                    'Field_Goal_Attempts': [],
                                    'Threes': [],
                                    'Three_Attempts': [],
                                    'Twos': [],
                                    'Two_Attempts': [],
                                    'Freethrows': [],
                                    'Freethrow_Attempts': [],
                                    'Offensive_Rebounds': [],
                                    'Deffensive_Rebounds': [],
                                    'Assists': [],
                                    'Steals': [],
                                    'Blocks': [],
                                    'Turnovers': [],
                                    'Fouls': [],
                                    'Points': [],
                                    'PM': [],
                                    'Injured': [],
                                    'Win': [],
                                    'Home': [],
                                    'Player_ID': [],
                                    'Game_ID': [],
                                    'Season': [],
                                    'Team_ID': [],
                                    'Opponent_ID': [],})
Player_Games_Playoffs = pandas.DataFrame({'Minutes': [],
                                          'Field_Goals': [],
                                          'Field_Goal_Attempts': [],
                                          'Threes': [],
                                          'Three_Attempts': [],
                                          'Twos': [],
                                          'Two_Attempts': [],
                                          'Freethrows': [],
                                          'Freethrow_Attempts': [],
                                          'Offensive_Rebounds': [],
                                          'Deffensive_Rebounds': [],
                                          'Assists': [],
                                          'Steals': [],
                                          'Blocks': [],
                                          'Turnovers': [],
                                          'Fouls': [],
                                          'Points': [],
                                          'PM': [],
                                          'Injured': [],
                                          'Win': [],
                                          'Home': [],
                                          'Player_ID': [],
                                          'Game_ID': [],
                                          'Season': [],
                                          'Team_ID': [],
                                          'Opponent_ID': []})
Player_Quarters_Playoffs = pandas.DataFrame({'Quarter': [],
                                             'Minutes': [],
                                             'Field_Goals': [],
                                             'Field_Goal_Attempts': [],
                                             'Threes': [],
                                             'Three_Attempts': [],
                                             'Twos': [],
                                             'Two_Attempts': [],
                                             'Freethrows': [],
                                             'Freethrow_Attempts': [],
                                             'Offensive_Rebounds': [],
                                             'Deffensive_Rebounds': [],
                                             'Assists': [],
                                             'Steals': [],
                                             'Blocks': [],
                                             'Turnovers': [],
                                             'Fouls': [],
                                             'Points': [],
                                             'PM': [],
                                             'Injured': [],
                                             'Win': [],
                                             'Home': [],
                                             'Player_ID': [],
                                             'Game_ID': [],
                                             'Season': [],
                                             'Team_ID': [],
                                             'Opponent_ID': []})
Seasons = pandas.DataFrame({'Season': [],
                            'Games': [],
                            'Teams': [],
                            'Champion': [],
                            'Finals_MVP': [],
                            'MVP': [],
                            'DPOY': [],
                            'MIP': [],
                            'SixMOTY': [],
                            'ROTY': [],
                            'COTY': []})
Referee_Info = pandas.DataFrame({'Name': [],
                                 'Number': [],
                                 'Birthday': [],
                                 'Referee_ID': []})
Executive_Info = pandas.DataFrame({'Name': [],
                                   'Birthday': [],
                                   'Teams': [],
                                   'Executive_ID': []})
Coach_Info = pandas.DataFrame({'Name': [],
                               'Birthday': [],
                               'Wins': [],
                               'Losses': [],
                               'Teams': [],
                               'Coach_ID': []})


# Other Variables
base_url = 'https://www.basketball-reference.com'
db_name = 'bball_db'


# Functions
def generate_season_hrefs(start, end):
    # Going by the end year
    hrefs = [''.join(['/leagues/NBA_', str(x), '.html']) for x in range(start, end + 1)]
    return hrefs

def get_month_page_hrefs(season):
    soup = page.get(base_url + '/leagues/NBA_' + str(season) + '_games.html')
    selection = soup.select('.filter a')
    return [x.attrs['href'] for x in selection]

def get_game_hrefs(soup):
    selection = soup.select('.center a')
    return [x.attrs['href'] for x in selection]

def write_to_sql(table_name, data_frame):
    conn = sqlite3.Connection(db_name)
    data_frame.to_sql(name = table_name, con = conn, if_exists = 'append')
    conn.close()

def retrieve_from_sql(table_name):
    conn = sqlite3.Connection(db_name)
    df = pandas.read_sql('SELECT * FROM ' + table_name, conn)
    conn.close()
    return df

def get_player_info(href):
    url = base_url + href
    soup = page.get(url)

    db = retrieve_from_sql('player_info')
    maximum_id = db['Player_ID'].max()

    info = player_info(soup, url)
    output = pandas.DataFrame(player_info.output_row(maximum_id))
    return output

def get_coach_info(href):
    url = base_url + href
    soup = page.get(url)

    db = retrieve_from_sql('coach_info')
    maximum_id = db['Coach_ID'].max()

    info = coach_info(soup, url)
    output = pandas.DataFrame(coach_info.output_row(maximum_id))
    return output

def get_executive_info(href):
    url = base_url + href
    soup = page.get(url)

    db = retrieve_from_sql('executive_info')
    maximum_id = db['Executive_ID'].max()

    info = executive_info(soup, url)
    output = pandas.DataFrame(info.output_row(maximum_id))
    return output

def get_referee_info(href):
    url = base_url + href
    soup = page.get(url)

    db = retrieve_from_sql('referee_info')
    maximum_id = db['Referee_ID'].max()

    info = referee_info(soup, url)
    output = pandas.DataFrame(info.output_row(maximum_id))
    return output

def get_team_info(href, ranking):
    soup = page.get(base_url + href)
    franchise_href = re.sub(r'[0-9]{4}.html', '', href)
    franchise_soup = page.get(base_url + franchise_href)
    
    info = team_info(franchise_soup, soup, base_url + href)

    # Executive ID
    db = retrieve_from_sql('executive_info')
    matches = info.executive_match_dict()
    exec_id = match_executive(db, matches)
    if isinstance(exec_id, int):
        tmp = get_executive_info(matches['href'])
        exec_id = tmp['Executive_ID']
        write_to_sql('executive_info', tmp)

    # Coach ID
    db = retrieve_from_sql('coach_info')
    matches = info.coach_match_dict()
    coach_id = match_executive(db, matches)
    if isinstance(coach_id, int):
        tmp = get_coach_info(matches['href'])
        coach_id = tmp['Coach_ID']
        write_to_sql('coach_info', tmp)

    # Previous ID
    db = retrieve_from_sql('team_info')
    maximum_team_id = db['Team_ID'].max()

    output = pandas.DataFrame(info.output_row(ranking,
                                              exec_id,
                                              coach_id,
                                              maximum_team_id))
    return output

def rankings(season):
    url = base_url + '/leagues/NBA_' + str(season) + '_standings.html'
    soup = page.get('url')
    table = soup.select('#expanded_standings > tbody')[0]
    rows = table.find_all('tr')
    ranks = {x.find(data-stat = 'team_name'): int(x.find(data-stat = 'ranker').text) for x in rows}
    return ranks

def get_game_data(href):
    url = base_url + href
    soup = page.get(url)

    game = game_data(soup)

    # home_team_id
    db = retrieve_from_sql('team_info')
    matches = game.home_team_id_match_dict()
    home_id = match_team(db, matches)
    if isinstance(home_id, int):
        ranks = rankings(game.season())
        team_rank = ranks[matches['Name']]
        tmp = get_team_info(matches['href'], team_rank)
        home_id = tmp['Team_ID']
        write_to_sql('team_info', tmp)

    # away_team_id
    db = retrieve_from_sql('team_info')
    matches = game.away_team_id_match_dict()
    away_id = match_team(db, matches)
    if isinstance(away_id, int):
        ranks = rankings(game.season())
        team_rank = ranks[matches['Name']]
        tmp = get_team_info(matches['href'], team_rank)
        away_id = tmp['Team_ID']
        write_to_sql('team_info', tmp)

    # referee_ids
    db = retrieve_from_sql('referee_info')
    matches = game.referee_match_dicts()
    ref_ids = match_referees(db, matches)
    for index in range(len(ref_ids)):
        if isinstance(ref_ids[index], int):
            tmp = get_referee_info(ref_ids[index])
            ref_ids[index] = tmp['Referee_ID']
            write_to_sql('referee_info', tmp)

    # prev
    db = retrieve_from_sql('game_info')
    maximum_id = db['Game_ID'].max()

    output = [pandas.DataFrame(game.output_row(maximum_id,
                                              home_id,
                                              away_id,
                                              ref_ids))]
    output.append(game.player_data())
    output.append(game.player_data_quarter())
    output.append(game.team_data())
    output.append(game.team_data_quarter())

    return output

def get_season_info(href):
    url = base_url + href
    soup = page.get(url)

    info = season_info(soup, url)

    # champion
    db = retrieve_from_sql('team_info')
    matches = info.champion_match_dict()
    champ_id = match_team(db, matches)
    if isinstance(champ_id, int):
        ranks = rankings(info.season())
        team_rank = ranks[matches['Name']]
        tmp = get_team_info(matches['href'], team_rank)
        champ_id = tmp['Team_ID']
        write_to_sql('team_info', tmp)

    # finals_mvp
    db = retrieve_from_sql('player_info')
    matches = info.finals_mvp_match_dict()
    finals_mvp = match_player(db, matches)
    if isinstance(finals_mvp, int):
        tmp = get_player_info(matches['href'])
        finals_mvp = tmp['Player_ID']
        write_to_sql('player_info', tmp)

    # mvp
    db = retrieve_from_sql('player_info')
    matches = info.mvp_match_dict()
    mvp = match_player(db, matches)
    if isinstance(mvp, int):
        tmp = get_player_info(matches['href'])
        mvp = tmp['Player_ID']
        write_to_sql('player_info', tmp)

    # dpoy
    db = retrieve_from_sql('player_info')
    matches = info.dpoy_match_dict()
    dpoy = match_player(db, matches)
    if isinstance(dpoy, int):
        tmp = get_player_info(matches['href'])
        dpoy = tmp['Player_ID']
        write_to_sql('player_info', tmp)

    # mip
    db = retrieve_from_sql('player_info')
    matches = info.mip_match_dict()
    mip = match_player(db, matches)
    if isinstance(mip, int):
        tmp = get_player_info(matches['href'])
        mip = tmp['Player_ID']
        write_to_sql('player_info', tmp)

    # sixmoty
    db = retrieve_from_sql('player_info')
    matches = info.sixmoty_match_dict()
    sixmoty = match_player(db, matches)
    if isinstance(sixmoty, int):
        tmp = get_player_info(matches['href'])
        sixmoty = tmp['Player_ID']
        write_to_sql('player_info', tmp)

    # roty
    db = retrieve_from_sql('player_info')
    matches = info.roty_match_dict()
    roty = match_player(db, matches)
    if isinstance(roty, int):
        tmp = get_player_info(matches['href'])
        roty = tmp['Player_ID']
        write_to_sql('player_info', tmp)

    output = pandas.DataFrame(info.output_row(champ_id,
                                              finals_mvp,
                                              mvp,
                                              dpoy,
                                              mip,
                                              sixmoty,
                                              roty))

    return output
