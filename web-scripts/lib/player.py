import re

class player_info:
    
    def __init__(self, soup, url):
        self.soup = soup
        self.url = url
        self.hand_dict = {'Left': 'L', 'Right': 'R'}

    def header(self):
        self.Shoots = ''
        self.Birthday = ''
        self.Draft_position = 0
        self.Draft_team = ''
        self.Draft_year = 0
        self.Debut_date = ''
        self.High_school = 0
        self.College = 0

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

    def name(self):
        self.Name = self.soup.select('h1 span')[0].text
        return self.Name

    def shoots(self):
        if not hasattr(self, 'Shoots'):
            self.Shoots = ''
        return self.Shoots

    def birthday(self):
        if not hasattr(self, 'Birthday'):
            self.Birthday = ''
        return self.Birthday

    def high_school(self):
        if not hasattr(self, 'High_school'):
            self.High_school = 0
        return self.High_school

    def college(self):
        if not hasattr(self, 'College'):
            self.College = 0
        return self.College

    def draft_position(self):
        if not hasattr(self, 'Draft_position'):
            self.Draft_position = 0
        return self.Draft_position

    def draft_team(self):
        if not hasattr(self, 'Draft_team'):
            self.Draft_team = ''
        return self.Draft_team

    def draft_year(self):
        if not hasattr(self, 'Draft_year'):
            self.Draft_year = 0
        return self.Draft_year

    def debut_date(self):
        if not hasattr(self, 'Debut_date'):
            self.Debut_date = ''
        return self.Debut_date

    def career_seasons(self):
        ages = self.soup.select('#per_game .full_table th+ .center')
        self.Career_seasons = len(ages)
        return self.Career_seasons

    def teams(self):
        teams = [x.text for x in self.soup.select('#per_game tbody .center+ .left') if x.text != 'TOT']
        self.Teams = ','.join(list(set(teams)))
        return self.Teams

    def generate_player_id(self, prev):
        self.Player_ID = prev + 1
        return self.Player_ID

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

def match_player(player_info_df, match_dictionary):
    df_copy = player_info_df
    for key, value in match_dictionary.items():
        if key == 'href':
            continue

        if key == 'Season':
            df_copy.loc[(df_copy['Draft_Year'] + df_copy['Career_Seasons'] >= value) & (df_copy['Draft_Year'] < value),]

        if int(value) == value:
            df_copy = df_copy.query(key + ' == ' + str(value))
        else:
            df_copy = df_copy.query(key + ' == "' + value + '"')

        if len(df_copy) == 1:
            return df_copy['Player_ID']
        if len(df_copy) == 0:
            return 'No match found'

    return 'Multiple matches, further querying is needed'
