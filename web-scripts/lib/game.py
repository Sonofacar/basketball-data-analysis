import pandas
import re

pandas.options.mode.copy_on_write = True

class game_info:

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
                            'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'PM']

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

    def playoffs(self):
        if ('NBA' in self.heading) and (':' in self.heading):
            output = True
        else:
            output = False
        return output

    def in_season_tournament(self):
        if 'In-Season' in self.heading:
            output = True
        else:
            output = False
        return output

    def home_team_name(self):
        return self.Home_Team_Name

    def away_team_name(self):
        return self.Away_Team_Name

    def date(self):
        self.Date = re.split('[a-z], ', self.soup.title.text)[1].split(' | ')[0]
        return self.Date

    def location(self):
        self.Location = self.soup.select('.scorebox_meta div')[1].text
        return self.Location

    def attendance(self):
        return self.Attendance

    def duration(self):
        return self.Duration

    def generate_game_id(self, prev):
        self.Game_ID = prev + 1
        return self.Game_ID

    def game_id(self):
        return self.Game_ID

    def home_team_href(self):
        return self.Home_Team_href

    def set_home_team_id(self, In):
        self.Home_Team_ID = In
        return self.Home_Team_ID

    def home_team_id(self):
        return self.Home_Team_ID

    def away_team_href(self):
        return self.Away_Team_href

    def set_away_team_id(self, In):
        self.Away_Team_ID = In
        return self.Away_Team_ID

    def away_team_id(self):
        return self.Away_Team_ID

    def season(self):
        self.Season = int(self.soup.select('u')[1].text.split('-')[0]) + 1
        return self.Season

    def referee_hrefs(self):
        return self.Referee_hrefs

    def set_referee_ids(self, In):
        self.Referee_IDs = In
        return self.Referee_IDs

    def referee_ids(self):
        return self.Referee_IDs

    def output_row(self):

        exists = (hasattr(self, 'Game_ID') and hasattr(self, 'Home_Team_ID') and hasattr(self, 'Away_Team_ID') and hasattr(self, 'Referee_IDs'))
        if not exists:
            print('Necessary values have not been set.')
            return 1

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
            tmp_table.loc[tmp_table.Name == 'Team Totals', 'Name'] = self.Home_Team_Name
        else:
            tmp_table.loc[tmp_table.Name == 'Team Totals', 'Name'] = self.Away_Team_Name

        tmp_table['Player_ID'] = [0] * tmp_table.shape[0]
        tmp_table['Game_ID'] = self.Game_ID
        tmp_table['Season'] = self.Season
        tmp_table['Team_ID'] = Team_ID
        tmp_table['Opponent_ID'] = Opponent_ID
        tmp_table['Injured'] = tmp_table.Name.str.contains('|'.join(self.Injured)).astype(int)

        hrefs = {x.text: x.attrs['href'] for x in raw_html.find_all('a')}
        tmp_table['href'] = tmp_table['Name'].map(hrefs)

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
        self.quarters['Quarter'] = []

        scores = [int(x.text) for x in self.soup.select('.score')]
        win = int(scores[0] > scores[1])
        home = 0
        team_id = self.Away_Team_ID
        opponent_id = self.Home_Team_ID

        raw_tables = self.soup.find_all('table')
        injured_table = self.injured_table(self.Injured_Away)
        length = len(raw_tables)

        for i in range(0, length):

            if i == int(length / 2):
                home = 1
                win = int(not win)
                injured_table = self.injured_table(self.Injured_Home)
                team_id = self.Home_Team_ID

            status = self.table_iteration(raw_tables[i], injured_table, length, i, home, win, team_id, opponent_id)

        self.total_game.loc[self.total_game['href'].isna(), 'href'] = self.total_game.loc[self.total_game['href'].isna(), 'Name'].map(self.Injured_dict)
        self.quarters.loc[self.quarters['href'].isna(), 'href'] = self.quarters.loc[self.quarters['href'].isna(), 'Name'].map(self.Injured_dict)

    def players_to_match(self):
        Teams = [self.Home_Team_Name, self.Away_Team_Name]
        tmp_table = self.total_game[~self.total_game.Name.str.contains('|'.join(Teams))]
        return tmp_table[['Name', 'href']].to_dict('records')

    def apply_matches(self, matches):
        tmp = self.total_game.loc[self.total_game['Player_ID'] == 0, 'href'].map(matches)
        self.total_game.loc[self.total_game['Player_ID'] == 0, 'Player_ID'] = tmp
        tmp = self.quarters.loc[self.quarters['Player_ID'] == 0, 'href'].map(matches)
        self.quarters.loc[self.quarters['Player_ID'] == 0, 'Player_ID'] = tmp

    def player_data(self):
        Teams = [self.Home_Team_Name, self.Away_Team_Name]
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
        Teams = [self.Home_Team_Name, self.Away_Team_Name]
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
        Teams = [self.Home_Team_Name, self.Away_Team_Name]
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
        Teams = [self.Home_Team_Name, self.Away_Team_Name]
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
