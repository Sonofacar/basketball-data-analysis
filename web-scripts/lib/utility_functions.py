import sqlite3
import re
import pandas
from bs4 import BeautifulSoup, Comment

# scraping library
from lib.season import season_info
from lib.game import game_data
from lib.team import team_info
from lib.player import player_info
from lib.other_info import referee_info, executive_info, coach_info
from lib.matching import *

base_url = 'https://www.basketball-reference.com'
db_name = '../bball_db'

def generate_season_href(season):
    # Going by the end year
    href = ''.join(['/leagues/NBA_', str(season), '.html'])
    return href

def get_month_page_hrefs(page_obj, season):
    soup = page_obj.get('/leagues/NBA_' + str(season) + '_games.html', False)
    selection = soup.select('.filter a')
    return [x.attrs['href'] for x in selection]

def get_game_hrefs(soup):
    selection = soup.select('.center a')
    return [x.attrs['href'] for x in selection]

def write_to_sql(table_name, data_frame):
    conn = sqlite3.Connection(db_name)
    print('Writing: ' + table_name)
    data_frame.to_sql(name = table_name, con = conn, if_exists = 'append', index = False)
    conn.close()

def retrieve_from_sql(table_name):
    conn = sqlite3.Connection(db_name)
    df = pandas.read_sql('SELECT * FROM ' + table_name, conn)
    conn.close()
    return df

def should_we_write(table_name, data_frame):
    if table_name == 'seasons':
        tmp = retrieve_from_sql(table_name)
        if len(tmp.loc[tmp['Season'] == data_frame['Season'].item()]) == 0:
            return True
        else:
            return False

    if table_name == 'game_info':
        cols = ['Home_Team_Name', 'Away_Team_Name', 'Date']
        tmp = retrieve_from_sql(table_name)
        merge = tmp.merge(data_frame, 'outer', on = cols, indicator = True)
        if len(merge[merge['_merge'] == 'both']) == 0:
            return True
        else:
            return False

    return True

def get_player_info(page_obj, href):
    soup = page_obj.get(href, True)

    db = retrieve_from_sql('player_info')
    maximum_id = db['Player_ID'].max()

    info = player_info(soup)
    output = pandas.DataFrame(info.output_row(maximum_id))
    return output

def get_coach_info(page_obj, href):
    soup = page_obj.get(href, True)

    db = retrieve_from_sql('coach_info')
    maximum_id = db['Coach_ID'].max()

    info = coach_info(soup)
    output = pandas.DataFrame(info.output_row(maximum_id))
    return output

def get_executive_info(page_obj, href):
    soup = page_obj.get(href, True)

    db = retrieve_from_sql('executive_info')
    maximum_id = db['Executive_ID'].max()

    info = executive_info(soup)
    output = pandas.DataFrame(info.output_row(maximum_id))
    return output

def get_referee_info(page_obj, href):
    soup = page_obj.get(href, True)

    db = retrieve_from_sql('referee_info')
    maximum_id = db['Referee_ID'].max()

    info = referee_info(soup)
    output = pandas.DataFrame(info.output_row(maximum_id))
    return output

def get_team_info(page_obj, href, ranking):
    soup = page_obj.get(href, True)
    franchise_href = re.sub(r'[0-9]{4}.html', '', href)
    franchise_soup = page_obj.get(franchise_href, False)
    
    info = team_info(franchise_soup, soup, base_url + href)

    # Executive ID
    db = retrieve_from_sql('executive_info')
    matches = info.executive_match_dict()
    exec_id = match_executive(db, matches)
    if not isinstance(exec_id, int):
        tmp = get_executive_info(page_obj, matches['href'])
        exec_id = tmp['Executive_ID'].item()
        write_to_sql('executive_info', tmp)

    # Coach ID
    db = retrieve_from_sql('coach_info')
    matches = info.coach_match_dict()
    coach_id = match_executive(db, matches)
    if not isinstance(coach_id, int):
        tmp = get_coach_info(page_obj, matches['href'])
        coach_id = tmp['Coach_ID'].item()
        write_to_sql('coach_info', tmp)

    # Previous ID
    db = retrieve_from_sql('team_info')
    maximum_team_id = db['Team_ID'].max()

    if pandas.isna(maximum_team_id):
        maximum_team_id = 0

    output = pandas.DataFrame(info.output_row(ranking,
                                              exec_id,
                                              coach_id,
                                              maximum_team_id))
    return output

def rankings(page_obj, season):
    href = '/leagues/NBA_' + str(season) + '_standings.html'
    soup = page_obj.get(href, False)
    comment = [x for x in soup.find_all(string=lambda t: isinstance(t, Comment)) if 'expanded_standings' in x][0]
    newsoup = BeautifulSoup(comment, features="lxml")
    ranks = {x.find(attrs = {'data-stat': 'team_name'}).text: int(x.find('th').text) for x in newsoup.find_all('tr')[2:32]}
    return ranks

def get_player_id_mapping(page_obj, df):
    tmp = df.loc[~df['href'].isna(),:].loc[df['Player_ID'] == 0,['Name', 'href']]
    to_get = [[x[0], x[1]] for x in tmp.values]

    mapping = {}

    for name, href in to_get:
        player_df = get_player_info(page_obj, href)
        write_to_sql('player_info', player_df)
        mapping.update({name: player_df['Player_ID'].item()})

    return mapping

def apply_player_id_mapping(game_obj, mapping):
    game_obj.total_game.loc[game_obj.total_game['Player_ID'] == 0, 'Player_ID'] = game_obj.total_game['Name'].map(mapping)
    game_obj.quarters.loc[game_obj.quarters['Player_ID'] == 0, 'Player_ID'] = game_obj.quarters['Name'].map(mapping)

def get_game_data(page_obj, href):
    soup = page_obj.get(href, False)

    game = game_data(soup)

    print()
    print('############')
    print('# New Game #')
    print('############')
    print()

    # home_team_id
    db = retrieve_from_sql('team_info')
    matches = game.home_team_id_match_dict()
    home_id = match_team(db, matches)
    if not isinstance(home_id, int):
        ranks = rankings(page_obj, game.season())
        team_rank = ranks[matches['Name']]
        tmp = get_team_info(page_obj, matches['href'], team_rank)
        home_id = tmp['Team_ID'].item()
        write_to_sql('team_info', tmp)

    # away_team_id
    db = retrieve_from_sql('team_info')
    matches = game.away_team_id_match_dict()
    away_id = match_team(db, matches)
    if not isinstance(away_id, int):
        ranks = rankings(page_obj, game.season())
        team_rank = ranks[matches['Name']]
        tmp = get_team_info(page_obj, matches['href'], team_rank)
        away_id = tmp['Team_ID'].item()
        write_to_sql('team_info', tmp)

    # referee_ids
    db = retrieve_from_sql('referee_info')
    matches = game.referee_ids_match_dicts()
    ref_ids = match_referees(db, matches)
    for index in range(len(ref_ids)):
        if not isinstance(ref_ids[index], int):
            tmp = get_referee_info(page_obj, ref_ids[index])
            ref_ids[index] = tmp['Referee_ID'].item()
            write_to_sql('referee_info', tmp)

    # prev
    db = retrieve_from_sql('game_info')
    maximum_id = db['Game_ID'].max()

    if pandas.isna(maximum_id):
        maximum_id = 0

    game.generate_game_id(maximum_id)
    game.set_home_team_id(home_id)
    game.set_away_team_id(away_id)
    game.set_referee_ids(ref_ids)

    return game

def get_season_info(page_obj, href):
    soup = page_obj.get(href, False)

    info = season_info(soup)

    print()
    print()
    print('##############')
    print('##############')
    print('#### ' + str(info.season()) + ' ####')
    print('##############')
    print('##############')
    print()

    # champion
    db = retrieve_from_sql('team_info')
    matches = info.champion_match_dict()
    champ_id = match_team(db, matches)
    if not isinstance(champ_id, int):
        ranks = rankings(page_obj, info.season())
        team_rank = ranks[matches['Name']]
        tmp = get_team_info(page_obj, matches['href'], team_rank)
        champ_id = tmp['Team_ID'].item()
        write_to_sql('team_info', tmp)

    # finals_mvp
    db = retrieve_from_sql('player_info')
    playoffs_soup = page_obj.get('/playoffs/NBA_' + str(info.season()) + '.html', False)
    matches = info.finals_mvp_match_dict(playoffs_soup)
    finals_mvp = match_player(db, matches)
    if not isinstance(finals_mvp, int):
        tmp = get_player_info(page_obj, matches['href'])
        finals_mvp = tmp['Player_ID'].item()
        write_to_sql('player_info', tmp)

    # mvp
    db = retrieve_from_sql('player_info')
    matches = info.mvp_match_dict()
    mvp = match_player(db, matches)
    if not isinstance(mvp, int):
        tmp = get_player_info(page_obj, matches['href'])
        mvp = tmp['Player_ID'].item()
        write_to_sql('player_info', tmp)

    # dpoy
    db = retrieve_from_sql('player_info')
    matches = info.dpoy_match_dict()
    dpoy = match_player(db, matches)
    if not isinstance(dpoy, int):
        tmp = get_player_info(page_obj, matches['href'])
        dpoy = tmp['Player_ID'].item()
        write_to_sql('player_info', tmp)

    # mip
    db = retrieve_from_sql('player_info')
    matches = info.mip_match_dict()
    mip = match_player(db, matches)
    if not isinstance(mip, int):
        tmp = get_player_info(page_obj, matches['href'])
        mip = tmp['Player_ID'].item()
        write_to_sql('player_info', tmp)

    # sixmoty
    db = retrieve_from_sql('player_info')
    matches = info.sixmoty_match_dict()
    sixmoty = match_player(db, matches)
    if not isinstance(sixmoty, int):
        tmp = get_player_info(page_obj, matches['href'])
        sixmoty = tmp['Player_ID'].item()
        write_to_sql('player_info', tmp)

    # roty
    db = retrieve_from_sql('player_info')
    matches = info.roty_match_dict()
    roty = match_player(db, matches)
    if not isinstance(roty, int):
        tmp = get_player_info(page_obj, matches['href'])
        roty = tmp['Player_ID'].item()
        write_to_sql('player_info', tmp)

    output = pandas.DataFrame(info.output_row(champ_id,
                                              finals_mvp,
                                              mvp,
                                              dpoy,
                                              mip,
                                              sixmoty,
                                              roty))

    return output
