import sqlite3
from bs4 import BeautifulSoup

# scraping library
from lib.season import season_info
from lib.game import game_data
from lib.team import team_info
from lib.player import player_info
from lib.other_info import referee_info, executive_info, coach_info
from lib.matching import *

def generate_season_href(season):
    # Going by the end year
    href = ''.join(['/leagues/NBA_', str(x), '.html'])
    return href

def get_month_page_hrefs(page_obj, season):
    soup = page_obj.get(base_url + '/leagues/NBA_' + str(season) + '_games.html')
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

def get_player_info(page_obj, href):
    url = base_url + href
    soup = page_obj.get(url)

    db = retrieve_from_sql('player_info')
    maximum_id = db['Player_ID'].max()

    info = player_info(soup, url)
    output = pandas.DataFrame(player_info.output_row(maximum_id))
    return output

def get_coach_info(page_obj, href):
    url = base_url + href
    soup = page_obj.get(url)

    db = retrieve_from_sql('coach_info')
    maximum_id = db['Coach_ID'].max()

    info = coach_info(soup, url)
    output = pandas.DataFrame(coach_info.output_row(maximum_id))
    return output

def get_executive_info(page_obj, href):
    url = base_url + href
    soup = page_obj.get(url)

    db = retrieve_from_sql('executive_info')
    maximum_id = db['Executive_ID'].max()

    info = executive_info(soup, url)
    output = pandas.DataFrame(info.output_row(maximum_id))
    return output

def get_referee_info(page_obj, href):
    url = base_url + href
    soup = page_obj.get(url)

    db = retrieve_from_sql('referee_info')
    maximum_id = db['Referee_ID'].max()

    info = referee_info(soup, url)
    output = pandas.DataFrame(info.output_row(maximum_id))
    return output

def get_team_info(page_obj, href, ranking):
    soup = page_obj.get(base_url + href)
    franchise_href = re.sub(r'[0-9]{4}.html', '', href)
    franchise_soup = page_obj.get(base_url + franchise_href)
    
    info = team_info(franchise_soup, soup, base_url + href)

    # Executive ID
    db = retrieve_from_sql('executive_info')
    matches = info.executive_match_dict()
    exec_id = match_executive(db, matches)
    if isinstance(exec_id, int):
        tmp = get_executive_info(page_obj, matches['href'])
        exec_id = tmp['Executive_ID']
        write_to_sql('executive_info', tmp)

    # Coach ID
    db = retrieve_from_sql('coach_info')
    matches = info.coach_match_dict()
    coach_id = match_executive(db, matches)
    if isinstance(coach_id, int):
        tmp = get_coach_info(page_obj, matches['href'])
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

def rankings(page_obj, season):
    url = base_url + '/leagues/NBA_' + str(season) + '_standings.html'
    soup = page_obj.get('url')
    table = soup.select('#expanded_standings > tbody')[0]
    comment = [x for x in soup.find_all(string=lambda t: isinstance(t, Comment)) if 'expanded_standings' in x][0]
    newsoup = BeautifulSoup(comment)
    ranks = {x.find(attrs = {'data-stat': 'team_name'}).text: int(x.find('th').text) for x in newsoup.find_all('tr')[2:32]}
    return ranks

def get_game_data(page_obj, href):
    url = base_url + href
    soup = page_obj.get(url)

    game = game_data(soup)

    # home_team_id
    db = retrieve_from_sql('team_info')
    matches = game.home_team_id_match_dict()
    home_id = match_team(db, matches)
    if isinstance(home_id, int):
        ranks = rankings(game.season())
        team_rank = ranks[matches['Name']]
        tmp = get_team_info(page_obj, matches['href'], team_rank)
        home_id = tmp['Team_ID']
        write_to_sql('team_info', tmp)

    # away_team_id
    db = retrieve_from_sql('team_info')
    matches = game.away_team_id_match_dict()
    away_id = match_team(db, matches)
    if isinstance(away_id, int):
        ranks = rankings(page_obj, game.season())
        team_rank = ranks[matches['Name']]
        tmp = get_team_info(page_obj, matches['href'], team_rank)
        away_id = tmp['Team_ID']
        write_to_sql('team_info', tmp)

    # referee_ids
    db = retrieve_from_sql('referee_info')
    matches = game.referee_match_dicts()
    ref_ids = match_referees(db, matches)
    for index in range(len(ref_ids)):
        if isinstance(ref_ids[index], int):
            tmp = get_referee_info(page_obj, ref_ids[index])
            ref_ids[index] = tmp['Referee_ID']
            write_to_sql('referee_info', tmp)

    # prev
    db = retrieve_from_sql('game_info')
    maximum_id = db['Game_ID'].max()

    game.generate_game_id(maximum_id)
    game.set_home_team_id(home_id)
    game.set_away_team_id(away_id)
    game.set_referee_ids(ref_ids)

    return game

def get_season_info(page_obj, href):
    url = base_url + href
    soup = page_obj.get(url)

    info = season_info(soup, url)

    # champion
    db = retrieve_from_sql('team_info')
    matches = info.champion_match_dict()
    champ_id = match_team(db, matches)
    if isinstance(champ_id, int):
        ranks = rankings(page_obj, info.season())
        team_rank = ranks[matches['Name']]
        tmp = get_team_info(page_obj, matches['href'], team_rank)
        champ_id = tmp['Team_ID']
        write_to_sql('team_info', tmp)

    # finals_mvp
    db = retrieve_from_sql('player_info')
    matches = info.finals_mvp_match_dict()
    finals_mvp = match_player(db, matches)
    if isinstance(finals_mvp, int):
        tmp = get_player_info(page_obj, matches['href'])
        finals_mvp = tmp['Player_ID']
        write_to_sql('player_info', tmp)

    # mvp
    db = retrieve_from_sql('player_info')
    matches = info.mvp_match_dict()
    mvp = match_player(db, matches)
    if isinstance(mvp, int):
        tmp = get_player_info(page_obj, matches['href'])
        mvp = tmp['Player_ID']
        write_to_sql('player_info', tmp)

    # dpoy
    db = retrieve_from_sql('player_info')
    matches = info.dpoy_match_dict()
    dpoy = match_player(db, matches)
    if isinstance(dpoy, int):
        tmp = get_player_info(page_obj, matches['href'])
        dpoy = tmp['Player_ID']
        write_to_sql('player_info', tmp)

    # mip
    db = retrieve_from_sql('player_info')
    matches = info.mip_match_dict()
    mip = match_player(db, matches)
    if isinstance(mip, int):
        tmp = get_player_info(page_obj, matches['href'])
        mip = tmp['Player_ID']
        write_to_sql('player_info', tmp)

    # sixmoty
    db = retrieve_from_sql('player_info')
    matches = info.sixmoty_match_dict()
    sixmoty = match_player(db, matches)
    if isinstance(sixmoty, int):
        tmp = get_player_info(page_obj, matches['href'])
        sixmoty = tmp['Player_ID']
        write_to_sql('player_info', tmp)

    # roty
    db = retrieve_from_sql('player_info')
    matches = info.roty_match_dict()
    roty = match_player(db, matches)
    if isinstance(roty, int):
        tmp = get_player_info(page_obj, matches['href'])
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
