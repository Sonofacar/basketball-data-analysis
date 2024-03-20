# Imports
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


# Functions
def generate_season_hrefs(start, end):
    # Going by the end year
    hrefs = [''.join(['/leagues/NBA_', str(x), '.html']) for x in range(start, end + 1)]
    return hrefs

def get_month_page_hrefs(soup):
    selection = soup.select('.filter a')
    return [x.attrs['href'] for x in selection]

def get_game_hrefs(soup):
    selection = soup.select('.center a')
    return [x.attrs['href'] for x in selection]

def write_to_sql(db_name, table_name, data_frame):
    conn = sqlite3.Connection(db_name)
    data_frame.to_sql(name = table_name, con = conn)
    conn.close()

def retrieve_from_sql(db_name, table_name):
    conn = sqlite3.Connection(db_name)
    df = pandas.read_sql('SELECT * FROM ' + table_name, conn)
    conn.close()
    return df


# Other Variables
base_url = 'https://www.basketball-reference.com'
db_name = 'bball_db'
