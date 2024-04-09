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

base_url = 'https://www.basketball-reference.com'
db_name = '../bball_db'

def error(href, Type):
    print('Error: with ' + Type + ' page at ' + kwargs['href'])
    with open('../error_log.csv', 'a') as file:
        file.write(Type + ',' + kwargs['href'])

def log_dec():

    def decorator(function):

        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except:
                if len(args) == 0:
                    error(kwargs['href'], function.__name__)
                else:
                    error(args[1], function.__name__)
        return wrapper

    return decorator

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

@log_dec()
def get_player_info(page_obj, href, id_cache_dict):
    soup = page_obj.get(href, True)

    db = retrieve_from_sql('player_info')

    if len(db) == 0:
        maximum_id = 0
    else:
        maximum_id = db['Player_ID'].max()

    id_cache_dict.update({href: maximum_id})

    info = player_info(soup)
    output = pandas.DataFrame(info.output_row(maximum_id))
    return output

@log_dec()
def get_coach_info(page_obj, href, id_cache_dict):
    soup = page_obj.get(href, True)

    db = retrieve_from_sql('coach_info')

    if len(db) == 0:
        maximum_id = 0
    else:
        maximum_id = db['Coach_ID'].max()

    id_cache_dict.update({href: maximum_id})

    info = coach_info(soup)
    output = pandas.DataFrame(info.output_row(maximum_id))
    return output

@log_dec()
def get_executive_info(page_obj, href, id_cache_dict):
    soup = page_obj.get(href, True)

    db = retrieve_from_sql('executive_info')

    if len(db) == 0:
        maximum_id = 0
    else:
        maximum_id = db['Executive_ID'].max()

    id_cache_dict.update({href: maximum_id})

    info = executive_info(soup)
    output = pandas.DataFrame(info.output_row(maximum_id))
    return output

@log_dec()
def get_referee_info(page_obj, href, id_cache_dict):
    soup = page_obj.get(href, True)

    db = retrieve_from_sql('referee_info')

    if len(db) == 0:
        maximum_id = 0
    else:
        maximum_id = db['Referee_ID'].max()

    id_cache_dict.update({href: maximum_id})

    info = referee_info(soup)
    output = pandas.DataFrame(info.output_row(maximum_id))
    return output

@log_dec()
def get_team_info(page_obj, href, rank_obj, id_cache_dict):
    soup = page_obj.get(href, True)
    franchise_href = re.sub(r'[0-9]{4}.html', '', href)
    franchise_soup = page_obj.get(franchise_href, False)

    if franchise_soup.find('body').text.strip() == '':
        franchise_href = franchise_soup.find('script').text.strip().split('"')[1]
        franchise_soup = page_obj.get(franchise_href, False)
    
    info = team_info(franchise_soup, soup, base_url + href)

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

    ranking = rank_obj[info.name()]

    output = pandas.DataFrame(info.output_row(ranking,
                                              exec_id,
                                              coach_id,
                                              maximum_team_id))
    return output

@log_dec()
def rankings(page_obj, href):
    soup = page_obj.get(href, True)
    comment = [x for x in soup.find_all(string=lambda t: isinstance(t, Comment)) if 'expanded_standings' in x][0]
    newsoup = BeautifulSoup(comment, features="lxml")
    ranks = {x.find(attrs = {'data-stat': 'team_name'}).text: int(x.find('th').text) for x in newsoup.find_all('tr')[2:32]}
    return ranks

def find_remaining_players(page_obj, id_cache_dict, row_dicts):
    output = {}

    for row in row_dicts:
        info = get_player_info(page_obj, row['href'], id_cache_dict)
        output.update({row['href']: info['Player_ID'].item()})
        write_to_sql('player_info', info)

    return output

@log_dec()
def get_game_data(page_obj, href, id_cache_dict):
    soup = page_obj.get(href, False)

    game = game_data(soup)

    print()
    print('############')
    print('# New Game #')
    print('############')
    print()

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

@log_dec()
def get_season_info(page_obj, href, id_cache_dict):
    soup = page_obj.get(href, False)

    info = season_info(soup)

    info.header()
    info.awards()

    print()
    print()
    print('##############')
    print('##############')
    print('#### ' + str(info.season()) + ' ####')
    print('##############')
    print('##############')
    print()

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
