import pandas
import re
from bs4 import Comment

pandas.options.mode.copy_on_write = True

class debug:

    def debug(self, title, message):
        print('[ ' + title + ' ]: ' + message)

    def debug_error(self, soup, location, field, return_type, info = '', default = None):
        if not isinstance(return_type, type):
            raise TypeError

        output = 0
        url = soup.find('link', {'rel': 'canonical'}).attrs['href']
        href = url.replace('https://www.basketball-reference.com', '')
        print('[ Error: ' + location + ' ]: Could not fill the ' + field + ' field.')
        print("\tHREF: " + href)
        if info != '':
            print("\tCONTEXT: " + info)

        if default != None:
            output = default
            return output

        if return_type == int:
            output = 0
        elif return_type == str:
            output = ''
        elif return_type == bool:
            output = False
        elif return_type == list:
            output = []
        elif return_type == None:
            output = return_type

        return output

    def error_wrap(location = '', field = '', return_type = '', info = '', default = None):
        def decorator(function):
            def wrapper(self, *args, **kwargs):
                try:
                    return function(self, *args, **kwargs)
                except:
                    return self.debug_error(self.soup, location, field, return_type, info, default)
            return wrapper
        return decorator

#done
class referee_info(debug):

    def __init__(self, soup):
        self.soup = soup

    @debug.error_wrap('referee_info', 'name', str)
    def name(self):
        self.Name = self.soup.select('h1 span')[0].text
        return self.Name

    @debug.error_wrap('referee_info', 'number', int)
    def number(self):
        self.Number = int(self.soup.find('text').text)
        return self.Number

    @debug.error_wrap('referee_info', 'birthday', str)
    def birthday(self):
        birthday_raw = [x.text for x in self.soup.select('#meta p') if 'Born:' in x.text][0]
        birthday_raw = birthday_raw.replace('Born: ', '').split(' in ')[0]
        self.Birthday = birthday_raw.replace('Born:\n', '').replace('\n', '').replace('   ', '')
        return self.Birthday

    def generate_referee_id(self, prev):
        self.Referee_ID = prev + 1
        return self.Referee_ID

    @debug.error_wrap('referee_info', 'referee_id', int)
    def referee_id(self):
        return self.Referee_ID
    
    def output_row(self, prev):
        self.generate_referee_id(prev)
        self.row = {'Name': [self.name()],
                    'Number': [self.number()],
                    'Birthday': [self.birthday()],
                    'Referee_ID': [self.referee_id()]}
        return self.row

#done
class executive_info(debug):

    def __init__(self, soup):
        self.soup = soup

    @debug.error_wrap('executive_info', 'name', str)
    def name(self):
        self.Name = self.soup.select('h1 span')[0].text
        return self.Name

    @debug.error_wrap('executive_info', 'birthday', str)
    def birthday(self):
        birthday_raw = [x.text for x in self.soup.select('#meta p') if 'Born:' in x.text][0]
        birthday_raw = birthday_raw.replace('Born: ', '').split(' in ')[0]
        self.Birthday = birthday_raw.replace('Born:\n', '').replace('\n', '').replace('   ', '')
        return self.Birthday

    @debug.error_wrap('executive_info', 'teams', str)
    def teams(self):
        teams = [x.text for x in self.soup.select('tbody th+ .left') if x.text != 'TOT']
        self.Teams = ','.join(list(set(teams)))
        return self.Teams

    def generate_executive_id(self, prev):
        self.Executive_ID = prev + 1
        return self.Executive_ID

    @debug.error_wrap('executive_info', 'executive_id', str)
    def executive_id(self):
        return self.Executive_ID

    def output_row(self, prev):
        self.generate_executive_id(prev)
        self.row = {'Name': [self.name()],
                    'Birthday': [self.birthday()],
                    'Teams': [self.teams()],
                    'Executive_ID': [self.executive_id()]}
        return self.row

#done
class coach_info(debug):

    def __init__(self, soup):
        self.soup = soup

    @debug.error_wrap('coach_info', 'name', str)
    def name(self):
        self.Name = self.soup.select('h1 span')[0].text
        return self.Name

    @debug.error_wrap('coach_info', 'birthday', str)
    def birthday(self):
        birthday_raw = [x.text for x in self.soup.select('#meta p') if 'Born:' in x.text][0]
        birthday_raw = birthday_raw.replace('Born: ', '').split(' in ')[0]
        self.Birthday = birthday_raw.replace('Born:\n', '').replace('\n', '').replace('   ', '')
        return self.Birthday

    @debug.error_wrap('coach_info', 'wins', int)
    def wins(self):
        self.Wins = int(self.soup.select('.thead .right:nth-child(6)')[0].text)
        return self.Wins

    @debug.error_wrap('coach_info', 'losses', int)
    def losses(self):
        self.Losses = int(self.soup.select('.thead .right:nth-child(7)')[0].text)
        return self.Losses

    @debug.error_wrap('coach_info', 'teams', str)
    def teams(self):
        teams = [x.text for x in self.soup.select('.right+ .left a') if x.text != 'TOT']
        self.Teams = ','.join(list(set(teams)))
        return self.Teams

    def generate_coach_id(self, prev):
        self.Coach_ID = prev + 1
        return self.Coach_ID

    @debug.error_wrap('coach_info', 'coach_id', int)
    def coach_id(self):
        return self.Coach_ID

    def output_row(self, prev):
        self.generate_coach_id(prev)
        self.row = {'Name': [self.name()],
                    'Birthday': [self.birthday()],
                    'Wins': [self.wins()],
                    'Losses': [self.losses()],
                    'Teams': [self.teams()],
                    'Coach_ID': [self.coach_id()]}
        return self.row

#done
class player_info(debug):
    
    def __init__(self, soup):
        self.soup = soup
        self.hand_dict = {'Left': 'L', 'Right': 'R'}

    @debug.error_wrap('player_info', 'header', None, info = 'This may affect the shoots, birthday, draft, debut, college, and highschool fields.')
    def header(self):
        for i in range(1,20):
            string = 'p:nth-child(' + str(i) + ')'

            try:
                text = self.soup.select(string)[0].text.replace('\n', '')
                text = text.replace('\t', '')
                text = text.replace('            ', '')
                text = text.replace('    ', '')
            except:
                break

            if 'Sports Reference' in text:
                break

            if 'Shoots:' in text:
                self.Shoots = self.hand_dict[text.split('Shoots:')[1]]

            if 'Born:' in text:
                self.Birthday = text.replace('Born: ', '').split('in')[0].replace(',', ', ')

            if 'Draft:' in text:
                parts = re.split('\(|\)', text)
                self.Draft_position = int(re.findall('[0-9]{1,2}', parts[1].split(', ')[1])[0])
                self.Draft_team = parts[0].replace('  ', '').replace('Draft:', '').split(',')[0]
                self.Draft_year = int(re.findall('[0-9]{4}', parts[2])[0])

            if 'NBA Debut:' in text:
                self.Debut_date = text.replace('NBA Debut: ', '')

            if 'College:' in text:
                self.College = 1

            if 'High School:' in text:
                self.High_school = 1

    @debug.error_wrap('player_info', 'name', str)
    def name(self):
        self.Name = self.soup.select('h1 span')[0].text
        return self.Name

    @debug.error_wrap('player_info', 'shoots', str, default = 'R')
    def shoots(self):
        return self.Shoots

    @debug.error_wrap('player_info', 'birthday', str)
    def birthday(self):
        return self.Birthday

    @debug.error_wrap('player_info', 'high_school', int)
    def high_school(self):
        return self.High_school

    @debug.error_wrap('player_info', 'college', int)
    def college(self):
        return self.College

    @debug.error_wrap('player_info', 'draft_position', int)
    def draft_position(self):
        return self.Draft_position

    @debug.error_wrap('player_info', 'draft_team', str)
    def draft_team(self):
        return self.Draft_team

    @debug.error_wrap('player_info', 'draft_year', int)
    def draft_year(self):
        return self.Draft_year

    @debug.error_wrap('player_info', 'debut_date', str)
    def debut_date(self):
        return self.Debut_date

    @debug.error_wrap('player_info', 'career_seasons', str)
    def career_seasons(self):
        ages = self.soup.select('#per_game .full_table th+ .center')
        self.Career_seasons = len(ages)
        return self.Career_seasons

    @debug.error_wrap('player_info', 'teams', str)
    def teams(self):
        teams = [x.text for x in self.soup.select('#per_game tbody .center+ .left') if x.text != 'TOT']
        self.Teams = ','.join(list(set(teams)))
        return self.Teams

    def generate_player_id(self, prev):
        self.Player_ID = prev + 1
        return self.Player_ID

    @debug.error_wrap('player_info', 'player_id', int)
    def player_id(self):
        return self.Player_ID

    def output_row(self, prev_id):
        self.generate_player_id(prev_id)
        self.header()
        self.career_seasons()
        self.teams()
        self.row = {'Name': [self.name()],
                    'Shoots': [self.shoots()],
                    'Birthday': [self.birthday()],
                    'High_School': [self.high_school()],
                    'College': [self.college()],
                    'Draft_Position': [self.draft_position()],
                    'Draft_Team': [self.draft_team()],
                    'Draft_Year': [self.draft_year()],
                    'Debut_Date': [self.debut_date()],
                    'Career_Seasons': [self.career_seasons()],
                    'Teams': [self.teams()],
                    'Player_ID': [self.player_id()]}
        return self.row

#done
class team_info(debug):

    def __init__(self, franchise_soup, soup, url):
        self.franchise_soup = franchise_soup
        self.soup = soup
        self.url = url

    @debug.error_wrap('team_info', 'get_hrefs', None, info = 'May affect linking up to coach and executive ids.')
    def get_hrefs(self):
        for x in self.soup.select('#meta div a'):

            if 'coaches' in x.attrs['href']:
                self.Coach_href = x.attrs['href']

            if 'executives' in x.attrs['href']:
                self.Executive_href = x.attrs['href']

    def set_franchise_index(self):
        # Needed for:
        # - wins
        # - losses
        # - playoff_appearance
        year = self.url.split('/')[5].replace('.html', '')
        season_text = str(int(year) - 1) + '-' + year[2:4]
        seasons_list = self.franchise_soup.select('th.left')
        self.franchise_index = int([i for i, x in enumerate(seasons_list) if x.text == season_text][0])
        return self.franchise_index

    @debug.error_wrap('team_info', 'name', str)
    def name(self):
        beginning = re.sub(' Roster.*$', '', self.soup.title.text)
        self.Name = re.sub('^[0-9]{4}-[0-9]{2} ', '', beginning)
        return self.Name

    @debug.error_wrap('team_info', 'abbreviation', str)
    def abbreviation(self):
        self.Abbreviation = self.url.split('/')[4]
        return self.Abbreviation

    @debug.error_wrap('team_info', 'wins', int)
    def wins(self):
        self.Wins = int(self.franchise_soup.select('.left+ .right')[self.franchise_index].text)
        return self.Wins

    @debug.error_wrap('team_info', 'losses', int)
    def losses(self):
        self.Losses = int(self.franchise_soup.select('.right:nth-child(5)')[self.franchise_index].text)
        return self.Losses

    @debug.error_wrap('team_info', 'location', str)
    def location(self):
        match = self.franchise_soup.select('h1+ p')[0].text
        self.Location = match.replace('\n', '').replace('Location:  ', '')
        return self.Location

    @debug.error_wrap('team_info', 'playoff_appearance', bool)
    def playoff_appearance(self):
        text = self.franchise_soup.select('.right+ .left')[self.franchise_index].text
        self.Playoff_appearance = text != ''
        return self.Playoff_appearance

    def set_ranking(self, In):
        self.Ranking = In
        return self.Ranking

    @debug.error_wrap('team_info', 'league_ranking', int)
    def ranking(self):
        return self.Ranking

    def generate_team_id(self, prev):
        self.Team_ID = prev + 1
        return self.Team_ID

    @debug.error_wrap('team_info', 'team_id', int)
    def team_id(self):
        return self.Team_ID

    @debug.error_wrap('team_info', 'season', int)
    def season(self):
        self.Season = int(self.url.split('/')[5].replace('.html', ''))
        return self.Season

    def executive_href(self):
        return self.Executive_href

    def set_executive_id(self, In):
        self.Executive_ID = In
        return self.Executive_ID

    @debug.error_wrap('team_info', 'executive_id', int)
    def executive(self):
        return self.Executive_ID

    def coach_href(self):
        return self.Coach_href

    def set_coach_id(self, In):
        self.co_id = In
        self.Coach_ID = self.co_id
        return self.Coach_ID

    @debug.error_wrap('team_info', 'coach_id', int)
    def coach(self):
        return self.Coach_ID

    def output_row(self, ranking, executive_id, coach_id, prev_id = 0):
        self.generate_team_id(prev_id)
        self.set_franchise_index()
        self.set_ranking(ranking)
        self.set_executive_id(executive_id)
        self.set_coach_id(coach_id)
        self.row = {'Name': [self.name()],
                    'Abbreviation': [self.abbreviation()],
                    'Wins': [self.wins()],
                    'Losses': [self.losses()],
                    'Location': [self.location()],
                    'Playoff_Appearance': [self.playoff_appearance()],
                    'League_Ranking': [self.Ranking],
                    'Team_ID': [self.team_id()],
                    'Season': [self.season()],
                    'Executive_ID': [self.executive()],
                    'Coach_ID': [self.coach()]}
        return self.row

#done
class season_info(debug):

    def __init__(self, soup):
        self.soup = soup

    @debug.error_wrap('season_info', 'header', None, info = 'This will affect the champion team.')
    def header(self):
        for line in self.soup.select('#meta p'):
            if 'League Champion' in line.text:
                self.Champion_href = line.find('a').attrs['href']

    @debug.error_wrap('season_info', 'awards', None, info = 'This will affect just about all awards outside of the champion and finals mvp.')
    def awards(self):
        comment = [x for x in self.soup.find_all(string=lambda t: isinstance(t, Comment)) if 'award' in x][0]
        new_soup = BeautifulSoup(comment.replace('\n', ''), features = 'lxml')
        players = [x for x in new_soup.select('#all_awards a') if x.text != '']
        
        # MVP
        self.mvp_name = players[0].text
        self.MVP_href = players[0].attrs['href']

        # ROTY
        self.roty_name = players[1].text
        self.ROTY_href = players[1].attrs['href']

        # DPOY
        self.dpoy_name = players[2].text
        self.DPOY_href = players[2].attrs['href']

        # MIP
        self.mip_name = players[3].text
        self.MIP_href = players[3].attrs['href']

        # SixMOTY
        self.sixmoty_name = players[4].text
        self.SixMOTY_href = players[4].attrs['href']

    @debug.error_wrap('season_info', 'season', str)
    def season(self):
        self.Season = int(self.soup.select('h1 span')[0].text.split('-')[0]) + 1
        return self.Season

    @debug.error_wrap('season_info', 'games', int)
    def games(self):
        team_totals = [int(x.text) for x in self.soup.select('#per_game-team tbody .left+ .right')]
        self.Games = sum(team_totals)
        return self.Games

    @debug.error_wrap('season_info', 'teams', int)
    def teams(self):
        teams = self.soup.select('#per_game-team a')
        self.Teams = len(teams)
        return self.Teams

    def champion_href(self):
        return self.Champion_href

    def set_champion(self, In):
        self.Champion = In
        return self.Champion

    @debug.error_wrap('season_info', 'champion', int)
    def champion(self):
        return self.Champion

    def finals_mvp_href(self, playoffs_soup):
        selection = [x.find('a') for x in playoffs_soup.select('#meta p') if 'Finals MVP' in x.text][0]
        self.Finals_MVP_href = selection.attrs['href']
        return self.Finals_MVP_href

    def set_finals_mvp(self, In):
        self.Finals_MVP = In
        return self.Finals_MVP

    @debug.error_wrap('season_info', 'finals_mvp', int)
    def finals_mvp(self):
        return self.Finals_MVP

    def mvp_href(self):
        return self.MVP_href

    def set_mvp(self, In):
        self.MVP = In
        return self.MVP

    @debug.error_wrap('season_info', 'mvp', int)
    def mvp(self):
        return self.MVP

    def dpoy_href(self):
        return self.DPOY_href

    def set_dpoy(self, In):
        self.DPOY = In
        return self.DPOY

    @debug.error_wrap('season_info', 'dpoy', int)
    def dpoy(self):
        return self.DPOY

    def mip_href(self):
        return self.MIP_href

    def set_mip(self, In):
        self.MIP = In
        return self.MIP

    @debug.error_wrap('season_info', 'mip', int)
    def mip(self):
        return self.MIP

    def sixmoty_href(self):
        return self.SixMOTY_href

    def set_sixmoty(self, In):
        self.SixMOTY = In
        return self.SixMOTY

    @debug.error_wrap('season_info', 'sixmoty', int)
    def sixmoty(self):
        return self.SixMOTY

    def roty_href(self):
        return self.ROTY_href

    def set_roty(self, In):
        self.ROTY = In
        return self.ROTY

    @debug.error_wrap('season_info', 'roty', int)
    def roty(self):
        return self.ROTY

    def output_row(self, champion, finals_mvp, mvp, dpoy, mip, sixmoty, roty):
        self.set_champion(champion)
        self.set_finals_mvp(finals_mvp)
        self.set_mvp(mvp)
        self.set_dpoy(dpoy)
        self.set_mip(mip)
        self.set_sixmoty(sixmoty)
        self.set_roty(roty)
        self.row = {'Season': [self.season()],
                    'Games': [self.games()],
                    'Teams': [self.teams()],
                    'Champion': [self.champion()],
                    'Finals_MVP': [self.finals_mvp()],
                    'MVP': [self.mvp()],
                    'DPOY': [self.dpoy()],
                    'MIP': [self.mip()],
                    'SixMOTY': [self.sixmoty()],
                    'ROTY': [self.roty()]}
        return self.row

class game_info(debug):

    def __init__(self, soup):
        self.soup = soup

        self.teams = self.soup.select('.scorebox strong a')

        self.Home_Team_Name = self.teams[1].text
        self.Home_Team_href = self.teams[1].attrs['href']
        self.Away_Team_Name = self.teams[0].text
        self.Away_Team_href = self.teams[0].attrs['href']

        self.heading = self.soup.select('h1')[0].text

        self.Attendance = 0
        self.Duration = 0
        self.Injured = []
        self.Injured_dict = {}

        self.tmp_columns = ['Name', 'MP', 'FG', 'FGA', 'FGp', '3P', '3PA',
                            '3Pp', 'FT', 'FTA', 'FTp', 'ORB', 'DRB', 'TRB',
                            'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'GmSc',
                            'PM']

        self.empty_df = pandas.DataFrame({'Name': [],
                                          'MP': [],
                                          'FG': [],
                                          'FGA': [],
                                          'FGp': [],
                                          '3P': [],
                                          '3PA': [],
                                          '3Pp': [],
                                          'FT': [],
                                          'FTA': [],
                                          'FTp': [],
                                          'ORB': [],
                                          'DRB': [],
                                          'TRB': [],
                                          'AST': [],
                                          'STL': [],
                                          'BLK': [],
                                          'TOV': [],
                                          'PF': [],
                                          'PTS': [],
                                          'PM': []})

        self.empty_df = self.empty_df.astype({'Name': object,
                                              'MP': int,
                                              'FG': int,
                                              'FGA': int,
                                              'FGp': float,
                                              '3P': int,
                                              '3PA': int,
                                              '3Pp': float,
                                              'FT': int,
                                              'FTA': int,
                                              'FTp': float,
                                              'ORB': int,
                                              'DRB': int,
                                              'TRB': int,
                                              'AST': int,
                                              'STL': int,
                                              'BLK': int,
                                              'TOV': int,
                                              'PF': int,
                                              'PTS': int,
                                              'PM': int})

        for line in self.soup.select('#content > div')[-2].find_all('div'):

            if 'Attendance' in line.text:
                self.Attendance = int(line.contents[1].replace(',', ''))

            if 'Time of Game' in line.text:
                selection = line.contents[1].split(':')
                hours = int(selection[0])
                minutes = int(selection[1])
                self.Duration = hours * 60 + minutes

            if 'Officials' in line.text:
                selection = line.select('a')
                self.Referee_Names = [tag.text for tag in selection]
                self.Referee_hrefs = [tag.attrs['href'] for tag in selection]

            if 'Inactive' in line.text:
                do_not_catch = [',', 'Inactive:']
                injured_children = [x.text.strip() for x in list(line.children) if (x.text.strip() not in do_not_catch) and not (re.match(r'[A-Z]{3}', x.text.strip()))]
                injured = line.find_all('a')
                self.Injured = [x.text for x in injured]
                #self.Injured_hrefs = [x.attrs['href'] for x in injured]
                self.Injured_dict = {x.text.strip(): x.attrs['href'] for x in injured}

        homeness = 0
        self.Injured_Away = []
        #self.Injured_Away_hrefs = []
        self.Injured_Home = []
        #self.Injured_Home_hrefs = []
        iteration = 0

        exists = 'injured_children' in locals()
        if not exists:
            injured_children = ['', '']

        tmp = injured_children[iteration]

        while (tmp != '') and (tmp != 'None'):
            self.Injured_Away.append(tmp)
            #self.Injured_Away_hrefs.append(self.Injured_hrefs[iteration])
            iteration += 1
            tmp = injured_children[iteration]

        while (tmp != '') and (tmp != 'None'):
            self.Injured_Home.append(tmp)
            #self.Injured_Home_hrefs.append(self.Injured_hrefs[iteration])
            iteration += 1
            tmp = injured_children[iteration]

    @debug.error_wrap('game_info', 'playoffs', bool, info = 'Not sure about game type; regular season is assumed.')
    def playoffs(self):
        if ('NBA' in self.heading) and (':' in self.heading):
            output = True
        else:
            output = False
        return output

    @debug.error_wrap('game_info', 'in_season_tournament', bool, info = 'As said previously, not sure about game type; regular season is assumed.')
    def in_season_tournament(self):
        if 'In-Season' in self.heading:
            output = True
        else:
            output = False
        return output

    @debug.error_wrap('game_info', 'home_team_name', str)
    def home_team_name(self):
        return self.Home_Team_Name

    @debug.error_wrap('game_info', 'away_team_name', str)
    def away_team_name(self):
        return self.Away_Team_Name

    @debug.error_wrap('game_info', 'date', str)
    def date(self):
        self.Date = re.split('[a-z], ', self.soup.title.text)[1].split(' | ')[0]
        return self.Date

    @debug.error_wrap('game_info', 'location', str)
    def location(self):
        self.Location = self.soup.select('.scorebox_meta div')[1].text
        return self.Location

    @debug.error_wrap('game_info', 'attendance', int)
    def attendance(self):
        return self.Attendance

    @debug.error_wrap('game_info', 'duration', int)
    def duration(self):
        return self.Duration

    def generate_game_id(self, prev):
        self.Game_ID = prev + 1
        return self.Game_ID

    @debug.error_wrap('game_info', 'game_id', int, info = 'It simply has not been set yet.')
    def game_id(self):
        return self.Game_ID

    def home_team_href(self):
        return self.Home_Team_href

    def set_home_team_id(self, In):
        self.Home_Team_ID = In
        return self.Home_Team_ID

    @debug.error_wrap('game_info', 'home_team_id', int, info = 'This field has not been linked yet')
    def home_team_id(self):
        return self.Home_Team_ID

    def away_team_href(self):
        return self.Away_Team_href

    def set_away_team_id(self, In):
        self.Away_Team_ID = In
        return self.Away_Team_ID

    @debug.error_wrap('game_info', 'away_team_id', int, info = 'This field has not been linked yet')
    def away_team_id(self):
        return self.Away_Team_ID

    @debug.error_wrap('game_info', 'season', int)
    def season(self):
        self.Season = int(self.soup.select('u')[1].text.split('-')[0]) + 1
        return self.Season

    def referee_hrefs(self):
        return self.Referee_hrefs

    def set_referee_ids(self, In):
        self.Referee_IDs = In
        return self.Referee_IDs

    @debug.error_wrap('game_info', 'referee_ids', list, default = [0, 0, 0], info = 'This field has not been linked yet')
    def referee_ids(self):
        return self.Referee_IDs

    def output_row(self):
        self.row = {
            'Home_Team_Name': [self.home_team_name()],
            'Away_Team_Name': [self.away_team_name()],
            'Date': [self.date()],
            'Location': [self.location()],
            'Duration': [self.duration()],
            'Attendance': [self.attendance()],
            'Game_ID': [self.game_id()],
            'Home_Team_ID': [self.home_team_id()],
            'Away_Team_ID': [self.away_team_id()],
            'Season': [self.season()],
            'Referee_ID1': [self.referee_ids()[0]],
            'Referee_ID2': [self.referee_ids()[1]],
            'Referee_ID3': [self.referee_ids()[2]]}
        
        return self.row

class game_data(game_info):

    def player_to_seconds(self, series):
        series.loc[series == 0] = '0:0'
        minutes = [int(str(x).split(':')[0]) for x in list(series)]
        seconds = [int(str(x).split(':')[1]) for x in list(series)]
        output = [(minutes[i] * 60) + seconds[i] for i in range(len(minutes))]
        return pandas.Series(output, dtype = 'int')

    def clean_table(self, table):
        table.columns = self.tmp_columns
        new_table = table.drop(table[table['Name'] == 'Reserves'].index)
        new_table = new_table.fillna(0)
        new_table = new_table.replace('Did Not Play', 0)
        new_table = new_table.replace('Did Not Dress', 0)
        new_table = new_table.replace('Not With Team', 0)
        new_table = new_table.replace('Player Suspended', 0)
        return new_table

    def injured_table(self, names):
        length = len(names)
        output = pandas.DataFrame({x: [0] * length for x in self.tmp_columns})
        output['Name'] = names
        output['href'] = output['Name'].map(self.Injured_dict)
        return output

    def table_iteration(self, raw_html, injured_table, total_iters, iter, Home, Win, Team_ID, Opponent_ID):
        class iteration:
            advanced_table = int((total_iters / 2) - 1)

        match int(iter % (total_iters / 2)):

            # Totals
            case 0:
                Iteration_type = 'Totals'

            # Normal Quarters
            case 1 | 2 | 4 | 5:
                Iteration_type = 'Quarter'

            # Halves and advanced stats
            case 3 | 6 | iteration.advanced_table:
                return 1

            # Overtimes
            case _:
                Iteration_type = 'Overtime'

        tmp_table = pandas.DataFrame(columns = self.tmp_columns)
        tmp_table = pandas.read_html(str(raw_html))[0]
        tmp_table = self.clean_table(tmp_table)
        tmp_table = pandas.concat([tmp_table, injured_table], ignore_index = True)

        if tmp_table.loc[tmp_table.MP == 0].shape[0] == tmp_table.shape[0]:
            return 1

        tmp_table['Win'] = Win
        tmp_table['Home'] = Home

        if Home == 1:
            tmp_table.loc[tmp_table.Name == 'Team Totals', 'Name'] = self.home_team_name()
        else:
            tmp_table.loc[tmp_table.Name == 'Team Totals', 'Name'] = self.away_team_name()

        tmp_table['Player_ID'] = [0] * tmp_table.shape[0]
        tmp_table['Game_ID'] = self.game_id()
        tmp_table['Season'] = self.season()
        tmp_table['Team_ID'] = Team_ID
        tmp_table['Opponent_ID'] = Opponent_ID
        tmp_table['Injured'] = tmp_table.Name.str.contains('|'.join(self.Injured)).astype(int)

        hrefs = {x.text: x.attrs['href'] for x in raw_html.find_all('a')}
        tmp_table.loc[tmp_table['href'].isna(), 'href'] = tmp_table.loc[tmp_table['href'].isna(), 'Name'].map(hrefs)

        match Iteration_type:

            # Totals
            case 'Totals':
                self.total_game = pandas.concat([self.total_game, tmp_table], ignore_index = True)

            # Normal Quarters
            case 'Quarter':
                quarter = [int(x.replace('q', '')) for x in raw_html.attrs['id'].split('-') if 'q' in x][0]
                tmp_table['Quarter'] = quarter
                self.quarters = pandas.concat([self.quarters, tmp_table], ignore_index = True)

            # Overtimes
            case 'Overtime':
                quarter = [int(x.replace('ot', '')) for x in raw_html.attrs['id'].split('-') if 'ot' in x][0] + 4
                tmp_table['Quarter'] = quarter
                self.quarters = pandas.concat([self.quarters, tmp_table], ignore_index = True)

        return 0

    def get_data(self):
        self.total_game = self.empty_df
        self.quarters = self.empty_df

        self.total_game['href'] = []
        self.quarters['href'] = []
        self.total_game['Injured'] = []
        self.quarters['Injured'] = []
        self.total_game['Win'] = []
        self.quarters['Win'] = []
        self.total_game['Home'] = []
        self.quarters['Home'] = []
        self.total_game['Player_ID'] = []
        self.quarters['Player_ID'] = []
        self.total_game['Game_ID'] = []
        self.quarters['Game_ID'] = []
        self.total_game['Season'] = []
        self.quarters['Season'] = []
        self.total_game['Team_ID'] = []
        self.quarters['Team_ID'] = []
        self.total_game['Opponent_ID'] = []
        self.quarters['Opponent_ID'] = []
        self.quarters['Quarter'] = []

        scores = [int(x.text) for x in self.soup.select('.score')]
        win = int(scores[0] > scores[1])
        home = 0
        team_id = self.away_team_id()
        opponent_id = self.home_team_id()

        raw_tables = self.soup.find_all('table')
        injured_table = self.injured_table(self.Injured_Away)
        length = len(raw_tables)

        for i in range(0, length):

            if i == int(length / 2):
                home = 1
                win = int(not win)
                injured_table = self.injured_table(self.Injured_Home)
                team_id = self.home_team_id()
                opponent_id = self.away_team_id()

            status = self.table_iteration(raw_tables[i], injured_table, length, i, home, win, team_id, opponent_id)

        self.total_game.loc[self.total_game['href'].isna(), 'href'] = self.total_game.loc[self.total_game['href'].isna(), 'Name'].map(self.Injured_dict)
        self.quarters.loc[self.quarters['href'].isna(), 'href'] = self.quarters.loc[self.quarters['href'].isna(), 'Name'].map(self.Injured_dict)

    def players_to_match(self):
        Teams = [self.home_team_name(), self.away_team_name()]
        tmp_table = self.total_game[~self.total_game.Name.str.contains('|'.join(Teams))]
        return tmp_table.loc[tmp_table['Player_ID'] == 0, ['Name', 'href']].to_dict('records')

    def apply_matches(self, matches):
        tmp = self.total_game.loc[self.total_game['Player_ID'] == 0,:]['href'].map(matches).fillna(0)
        self.total_game.loc[self.total_game['Player_ID'] == 0, 'Player_ID'] = tmp
        tmp = self.quarters.loc[self.quarters['Player_ID'] == 0,:]['href'].map(matches).fillna(0)
        self.quarters.loc[self.quarters['Player_ID'] == 0, 'Player_ID'] = tmp

    def player_data(self):
        Teams = [self.home_team_name(), self.away_team_name()]
        tmp_table = self.total_game[~self.total_game.Name.str.contains('|'.join(Teams))].reset_index(drop = True)
        output = {'Seconds': self.player_to_seconds(tmp_table['MP']),
                  'Field_Goals': tmp_table['FG'],
                  'Field_Goal_Attempts': tmp_table['FGA'],
                  'Threes': tmp_table['3P'],
                  'Three_Attempts': tmp_table['3PA'],
                  'Twos': tmp_table['FG'],
                  'Two_Attempts': tmp_table['FGA'],
                  'Freethrows': tmp_table['FT'],
                  'Freethrow_Attempts': tmp_table['FTA'],
                  'Offensive_Rebounds': tmp_table['ORB'],
                  'Deffensive_Rebounds': tmp_table['DRB'],
                  'Assists': tmp_table['AST'],
                  'Steals': tmp_table['STL'],
                  'Blocks': tmp_table['BLK'],
                  'Turnovers': tmp_table['TOV'],
                  'Fouls': tmp_table['PF'],
                  'Points': tmp_table['PTS'],
                  'PM': tmp_table['PM'],
                  'Injured': tmp_table['Injured'],
                  'Win': tmp_table['Win'],
                  'Home': tmp_table['Home'],
                  'Player_ID': tmp_table['Player_ID'],
                  'Game_ID': tmp_table['Game_ID'],
                  'Season': tmp_table['Season'],
                  'Team_ID': tmp_table['Team_ID'],
                  'Opponent_ID': tmp_table['Opponent_ID']}
        return pandas.DataFrame(output)

    def player_data_quarter(self):
        Teams = [self.home_team_name(), self.away_team_name()]
        tmp_table = self.quarters[~self.quarters.Name.str.contains('|'.join(Teams))].reset_index(drop = True)
        output = {'Quarter': tmp_table.Quarter,
                  'Seconds': self.player_to_seconds(tmp_table['MP']),
                  'Field_Goals': tmp_table['FG'],
                  'Field_Goal_Attempts': tmp_table['FGA'],
                  'Threes': tmp_table['3P'],
                  'Three_Attempts': tmp_table['3PA'],
                  'Twos': tmp_table['FG'],
                  'Two_Attempts': tmp_table['FGA'],
                  'Freethrows': tmp_table['FT'],
                  'Freethrow_Attempts': tmp_table['FTA'],
                  'Offensive_Rebounds': tmp_table['ORB'],
                  'Deffensive_Rebounds': tmp_table['DRB'],
                  'Assists': tmp_table['AST'],
                  'Steals': tmp_table['STL'],
                  'Blocks': tmp_table['BLK'],
                  'Turnovers': tmp_table['TOV'],
                  'Fouls': tmp_table['PF'],
                  'Points': tmp_table['PTS'],
                  'PM': tmp_table['PM'],
                  'Injured': tmp_table['Injured'],
                  'Win': tmp_table['Win'],
                  'Home': tmp_table['Home'],
                  'Player_ID': tmp_table['Player_ID'],
                  'Game_ID': tmp_table['Game_ID'],
                  'Season': tmp_table['Season'],
                  'Team_ID': tmp_table['Team_ID'],
                  'Opponent_ID': tmp_table['Opponent_ID']}
        return pandas.DataFrame(output)

    def team_data(self):
        Teams = [self.home_team_name(), self.away_team_name()]
        tmp_table = self.total_game[self.total_game.Name.str.contains('|'.join(Teams))]
        output = {'Total_Minutes': tmp_table['MP'],
                  'Field_Goals': tmp_table['FG'],
                  'Field_Goal_Attempts': tmp_table['FGA'],
                  'Threes': tmp_table['3P'],
                  'Three_Attempts': tmp_table['3PA'],
                  'Twos': tmp_table['FG'],
                  'Two_Attempts': tmp_table['FGA'],
                  'Freethrows': tmp_table['FT'],
                  'Freethrow_Attempts': tmp_table['FTA'],
                  'Offensive_Rebounds': tmp_table['ORB'],
                  'Deffensive_Rebounds': tmp_table['DRB'],
                  'Assists': tmp_table['AST'],
                  'Steals': tmp_table['STL'],
                  'Blocks': tmp_table['BLK'],
                  'Turnovers': tmp_table['TOV'],
                  'Fouls': tmp_table['PF'],
                  'Points': tmp_table['PTS'],
                  'Win': tmp_table['Win'],
                  'Home': tmp_table['Home'],
                  'Game_ID': tmp_table['Game_ID'],
                  'Season': tmp_table['Season'],
                  'Team_ID': tmp_table['Team_ID'],
                  'Opponent_ID': tmp_table['Opponent_ID']}
        return pandas.DataFrame(output)

    def team_data_quarter(self):
        Teams = [self.home_team_name(), self.away_team_name()]
        tmp_table = self.quarters[self.quarters.Name.str.contains('|'.join(Teams))]
        output = {'Quarter': tmp_table.Quarter,
                  'Total_Minutes': tmp_table['MP'],
                  'Field_Goals': tmp_table['FG'],
                  'Field_Goal_Attempts': tmp_table['FGA'],
                  'Threes': tmp_table['3P'],
                  'Three_Attempts': tmp_table['3PA'],
                  'Twos': tmp_table['FG'],
                  'Two_Attempts': tmp_table['FGA'],
                  'Freethrows': tmp_table['FT'],
                  'Freethrow_Attempts': tmp_table['FTA'],
                  'Offensive_Rebounds': tmp_table['ORB'],
                  'Deffensive_Rebounds': tmp_table['DRB'],
                  'Assists': tmp_table['AST'],
                  'Steals': tmp_table['STL'],
                  'Blocks': tmp_table['BLK'],
                  'Turnovers': tmp_table['TOV'],
                  'Fouls': tmp_table['PF'],
                  'Points': tmp_table['PTS'],
                  'Win': tmp_table['Win'],
                  'Home': tmp_table['Home'],
                  'Game_ID': tmp_table['Game_ID'],
                  'Season': tmp_table['Season'],
                  'Team_ID': tmp_table['Team_ID'],
                  'Opponent_ID': tmp_table['Opponent_ID']}
        return pandas.DataFrame(output)

