class referee_info:

    def __init__(self, soup, url):
        self.soup = soup
        self.url = url

    def name(self):
        self.Name = self.soup.select('h1 span')[0].text
        return self.Name

    def number(self):
        self.Number = self.soup.find('text').text
        return self.Number

    def birthday(self):
        try:
            self.Birthday = [x.text for x in self.soup.select('#meta p') if 'Born:' in x.text][0].replace('Born: ', '').split(' in ')[0].replace('Born:\n', '').replace('\n', '').replace('   ', '')
        except:
            self.Birthday = ''
        return self.Birthday

    def generate_referee_id(self, prev):
        self.Referee_ID = prev + 1
        return self.Referee_ID

    def referee_id(self):
        return self.Referee_ID
    
    def output_row(self, prev):
        self.generate_referee_id(prev)
        self.row = {'Name': [self.name()],
                  'Number': [self.number()],
                  'Birthday': [self.birthday()],
                  'Referee_ID': [self.referee_id()]}
        return self.row

def match_referee(referee_info_df, match_dictionary):
    df_copy = referee_info_df
    for key, value in match_dictionary.items():
        if key == 'href':
            continue

        if int(value) == value:
            df_copy = df_copy.query(key + ' == ' + str(value))
        else:
            df_copy = df_copy.query(key + ' == "' + value + '"')

        if len(df_copy) == 1:
            return df_copy['Referee_ID']
        if len(df_copy) == 0:
            return 'No match found'

    return 'Multiple matches, further querying is needed'

class executive_info:

    def __init__(self, soup, url):
        self.soup = soup
        self.url = url

    def name(self):
        self.Name = self.soup.select('h1 span')[0].text
        return self.Name

    def birthday(self):
        try:
            self.Birthday = [x.text for x in self.soup.select('#meta p') if 'Born:' in x.text][0].replace('Born: ', '').split(' in ')[0].replace('Born:\n', '').replace('\n', '').replace('   ', '')
        except:
            self.Birthday = ''
        return self.Birthday

    def teams(self):
        teams = [x.text for x in self.soup.select('tbody th+ .left') if x.text != 'TOT']
        self.Teams = ','.join(list(set(teams)))
        return self.Teams

    def generate_executive_id(self, prev):
        self.Executive_ID = prev + 1
        return self.Executive_ID

    def executive_id(self):
        return self.Executive_ID

    def output_row(self, prev):
        self.generate_executive_id(prev)
        self.row = {'Name': [self.name()],
                    'Birthday': [self.birthday()],
                    'Teams': [self.teams()],
                    'Executive_ID': [self.executive_id()]}
        return self.row

def match_executive(executive_info_df, match_dictionary):
    df_copy = executive_info_df
    for key, value in match_dictionary.items():
        if key == 'href':
            continue

        if int(value) == value:
            df_copy = df_copy.query(key + ' == ' + str(value))
        else:
            df_copy = df_copy.query(key + ' == "' + value + '"')

        if len(df_copy) == 1:
            return df_copy['Executive_ID']
        if len(df_copy) == 0:
            return 'No match found'

    return 'Multiple matches, further querying is needed'

class coach_info:

    def __init__(self, soup, url):
        self.soup = soup
        self.url = url

    def name(self):
        self.Name = self.soup.select('h1 span')[0].text
        return self.Name

    def birthday(self):
        try:
            self.Birthday = [x.text for x in self.soup.select('#meta p') if 'Born:' in x.text][0].replace('Born: ', '').split(' in ')[0].replace('Born:\n', '').replace('\n', '').replace('   ', '')
        except:
            self.Birthday = ''
        return self.Birthday

    def wins(self):
        self.Wins = int(self.soup.select('.thead .right:nth-child(6)')[0].text)
        return self.Wins

    def losses(self):
        self.Losses = int(self.soup.select('.thead .right:nth-child(7)')[0].text)
        return self.Losses

    def teams(self):
        teams = [x.text for x in self.soup.select('.right+ .left a') if x.text != 'TOT']
        self.Teams = ','.join(list(set(teams)))
        return self.Teams

    def generate_coach_id(self, prev):
        self.Coach_ID = prev + 1
        return self.Coach_ID

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

def match_coach(coach_info_df, match_dictionary):
    df_copy = coach_info_df
    for key, value in match_dictionary.items():
        if key == 'href':
            continue

        if int(value) == value:
            df_copy = df_copy.query(key + ' == ' + str(value))
        else:
            df_copy = df_copy.query(key + ' == "' + value + '"')

        if len(df_copy) == 1:
            return df_copy['Coach_ID']
        if len(df_copy) == 0:
            return 'No match found'

    return 'Multiple matches, further querying is needed'
