import sqlite3
import json
import re
import os
import pandas
from bs4 import BeautifulSoup, Comment

# scraping library
from lib.get_info import *
from lib.get_page import page

base_url = 'https://www.basketball-reference.com'
db_name = '../bball_db'
id_cache_file = '../id_cache.json'

def read_id_cache_dict():
    output = {}
    if os.path.isfile(id_cache_file):
        with open(id_cache_file, 'r') as file:
            output = json.load(file)
    return output

def save_id_cache_dict(id_cache):
    if os.path.isfile(id_cache_file):
        os.remove(id_cache_file)

    with open(id_cache_file, 'w+') as file:
        json.dump(id_cache, file)

def id_cache_wrap(function):
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except:
            if isinstance(args[-1], dict):
                cache = args[-1]
                save_id_cache_dict(cache)
            elif isinstance(kwargs['id_cache_dict']):
                cache = kwargs['id_cache_dict']
                save_id_cache_dict(cache)
            else:
                debug.debug('  Error   ', 'Could not write out id cache.')
            raise
    return wrapper

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
    debug.debug(' Writing  ', 'to ' + table_name)
    data_frame.to_sql(name = table_name, con = conn, if_exists = 'append', index = False)
    conn.close()

def retrieve_from_sql(table_name):
    conn = sqlite3.Connection(db_name)
    df = pandas.read_sql('SELECT * FROM ' + table_name, conn)
    conn.close()
    return df

def should_we_write(table_name, data_frame):
    tmp = retrieve_from_sql(table_name)

    if table_name == 'seasons':
        if len(tmp.loc[tmp['Season'] == data_frame['Season'].item()]) == 0:
            return True
        else:
            return False

    if table_name == 'game_info':
        cols = ['Home_Team_Name', 'Away_Team_Name', 'Date']
        merge = tmp.merge(data_frame, 'outer', on = cols, indicator = True)
        if len(merge[merge['_merge'] == 'both']) == 0:
            return True
        else:
            return False

    if table_name == 'playoff_game_info':
        cols = ['Home_Team_Name', 'Away_Team_Name', 'Date']
        merge = tmp.merge(data_frame, 'outer', on = cols, indicator = True)
        if len(merge[merge['_merge'] == 'both']) == 0:
            return True
        else:
            return False

    if table_name == 'team_info':
        cols = ['Name', 'Season']
        merge = tmp.merge(data_frame, 'outer', on = cols, indicator = True)
        if len(merge[merge['_merge'] == 'both']) == 0:
            return True
        else:
            return False

    return True

@id_cache_wrap
def get_player_info(page_obj, href, id_cache_dict):
    soup = page_obj.get(href, False)

    db = retrieve_from_sql('player_info')

    if len(db) == 0:
        maximum_id = 0
    else:
        maximum_id = db['Player_ID'].max()

    id_cache_dict.update({href: maximum_id + 1})

    info = player_info(soup)
    output = pandas.DataFrame(info.output_row(maximum_id))
    return output

@id_cache_wrap
def get_coach_info(page_obj, href, id_cache_dict):
    soup = page_obj.get(href, False)

    db = retrieve_from_sql('coach_info')

    if len(db) == 0:
        maximum_id = 0
    else:
        maximum_id = db['Coach_ID'].max()

    id_cache_dict.update({href: maximum_id + 1})

    info = coach_info(soup)
    output = pandas.DataFrame(info.output_row(maximum_id))
    return output

@id_cache_wrap
def get_executive_info(page_obj, href, id_cache_dict):
    soup = page_obj.get(href, False)

    db = retrieve_from_sql('executive_info')

    if len(db) == 0:
        maximum_id = 0
    else:
        maximum_id = db['Executive_ID'].max()

    id_cache_dict.update({href: maximum_id + 1})

    info = executive_info(soup)
    output = pandas.DataFrame(info.output_row(maximum_id))
    return output

@id_cache_wrap
def get_referee_info(page_obj, href, id_cache_dict):
    soup = page_obj.get(href, False)

    db = retrieve_from_sql('referee_info')

    if len(db) == 0:
        maximum_id = 0
    else:
        maximum_id = db['Referee_ID'].max()

    id_cache_dict.update({href: maximum_id + 1})

    info = referee_info(soup)
    output = pandas.DataFrame(info.output_row(maximum_id))
    return output

@id_cache_wrap
def get_team_info(page_obj, href, rank_obj, id_cache_dict):
    soup = page_obj.get(href, False)
    franchise_href = re.sub(r'[0-9]{4}.html', '', href)
    franchise_soup = page_obj.get(franchise_href, True)

    if franchise_soup.find('body').text.strip() == '':
        franchise_href = franchise_soup.find('script').text.strip().split('"')[1]
        franchise_soup = page_obj.get(franchise_href, True)
    
    info = team_info(franchise_soup, soup)

    info.get_hrefs()

    # Executive ID
    try:
        exec_id = id_cache_dict[info.executive_href()]
    except:
        tmp = get_executive_info(page_obj, info.executive_href(), id_cache_dict)
        exec_id = tmp['Executive_ID'].item()
        write_to_sql('executive_info', tmp)

    # Coach ID
    try:
        coach_id = id_cache_dict[info.coach_href()]
    except:
        tmp = get_coach_info(page_obj, info.coach_href(), id_cache_dict)
        coach_id = tmp['Coach_ID'].item()
        write_to_sql('coach_info', tmp)

    # Previous ID
    db = retrieve_from_sql('team_info')
    maximum_team_id = db['Team_ID'].max()

    if pandas.isna(maximum_team_id):
        maximum_team_id = 0

    id_cache_dict.update({href: maximum_team_id + 1})
    ranking = rank_obj[info.name()]

    output = pandas.DataFrame(info.output_row(ranking,
                                              exec_id,
                                              coach_id,
                                              maximum_team_id))
    return output

def rankings(page_obj, href):
    soup = page_obj.get(href, True)
    comment = [x for x in soup.find_all(string=lambda t: isinstance(t, Comment)) if 'expanded_standings' in x][0]
    newsoup = BeautifulSoup(comment, features="lxml")
    ranks = {x.find(attrs = {'data-stat': 'team_name'}).text: int(x.find('th').text) for x in newsoup.find_all('tr')[2:32]}
    return ranks

@id_cache_wrap
def find_remaining_players(page_obj, row_dicts, id_cache_dict):
    output = {}

    for row in row_dicts:
        info = get_player_info(page_obj, row['href'], id_cache_dict)
        output.update({row['href']: info['Player_ID'].item()})
        write_to_sql('player_info', info)

    return output

@id_cache_wrap
def get_game_data(page_obj, href, counter, id_cache_dict):
    soup = page_obj.get(href, False)

    game = game_data(soup)

    debug.debug(' New Game ', href + ' ' + counter)

    # home_team_id
    try:
        home_id = id_cache_dict[game.home_team_href()]
    except:
        ranks = rankings(page_obj, '/leagues/NBA_' + str(game.season()) + '_standings.html')
        tmp = get_team_info(page_obj, game.home_team_href(), ranks, id_cache_dict)
        home_id = tmp['Team_ID'].item()
        if should_we_write('team_info', tmp):
            write_to_sql('team_info', tmp)

    # away_team_id
    try:
        away_id = id_cache_dict[game.away_team_href()]
    except:
        ranks = rankings(page_obj, '/leagues/NBA_' + str(game.season()) + '_standings.html')
        tmp = get_team_info(page_obj, game.away_team_href(), ranks, id_cache_dict)
        away_id = tmp['Team_ID'].item()
        if should_we_write('team_info', tmp):
            write_to_sql('team_info', tmp)

    # referee_ids
    ref_ids = []
    for ref_href in game.referee_hrefs():
        try:
            ref_ids.append(id_cache_dict[ref_href])
        except:
            tmp = get_referee_info(page_obj, ref_href, id_cache_dict)
            ref_ids.append(tmp['Referee_ID'].item())
            write_to_sql('referee_info', tmp)

    # prev
    if game.playoffs():
        db = retrieve_from_sql('playoff_game_info')
    else:
        db = retrieve_from_sql('game_info')

    if len(db) == 0:
        maximum_id = 0
    else:
        maximum_id = db['Game_ID'].max()

    game.generate_game_id(maximum_id)
    game.set_home_team_id(home_id)
    game.set_away_team_id(away_id)
    game.set_referee_ids(ref_ids)

    return game

@id_cache_wrap
def get_season_info(page_obj, href, id_cache_dict):
    soup = page_obj.get(href, False)

    info = season_info(soup)

    info.header()
    info.awards()

    debug.debug('New Season', '!!!!!!! ' + str(info.season()) + ' !!!!!!!')

    # champion
    try:
        champ_id = id_cache_dict[info.champion_href()]
    except:
        ranks = rankings(page_obj, '/leagues/NBA_' + str(info.season()) + '_standings.html')
        tmp = get_team_info(page_obj, info.champion_href(), ranks, id_cache_dict)
        champ_id = tmp['Team_ID'].item()
        if should_we_write('team_info', tmp):
            write_to_sql('team_info', tmp)

    # finals_mvp
    playoffs_soup = page_obj.get('/playoffs/NBA_' + str(info.season()) + '.html', False)
    try:
        finals_mvp = id_cache_dict[info.finals_mvp_href(playoffs_soup)]
    except:
        tmp = get_player_info(page_obj, info.finals_mvp_href(playoffs_soup), id_cache_dict)
        finals_mvp = tmp['Player_ID'].item()
        write_to_sql('player_info', tmp)

    # mvp
    try:
        mvp = id_cache_dict[info.mvp_href()]
    except:
        tmp = get_player_info(page_obj, info.mvp_href(), id_cache_dict)
        mvp = tmp['Player_ID'].item()
        write_to_sql('player_info', tmp)

    # dpoy
    try:
        dpoy = id_cache_dict[info.dpoy_href()]
    except:
        tmp = get_player_info(page_obj, info.dpoy_href(), id_cache_dict)
        dpoy = tmp['Player_ID'].item()
        write_to_sql('player_info', tmp)

    # mip
    try:
        mip = id_cache_dict[info.mip_href()]
    except:
        tmp = get_player_info(page_obj, info.mip_href(), id_cache_dict)
        mip = tmp['Player_ID'].item()
        write_to_sql('player_info', tmp)

    # sixmoty
    try:
        sixmoty = id_cache_dict[info.sixmoty_href()]
    except:
        tmp = get_player_info(page_obj, info.sixmoty_href(), id_cache_dict)
        sixmoty = tmp['Player_ID'].item()
        write_to_sql('player_info', tmp)

    # roty
    try:
        roty = id_cache_dict[info.roty_href()]
    except:
        tmp = get_player_info(page_obj, info.roty_href(), id_cache_dict)
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
