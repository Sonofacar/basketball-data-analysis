import debug

class referee_info:

    def __init__(self, soup):
        self.soup = soup

    @debug.error_wrap('referee_info', 'name', str)
    def name(self):
        self.Name = self.soup.select('h1 span')[0].text
        return self.Name

    @debug.error_wrap('referee_info', 'number', int)
    def number(self):
        try:
            self.Number = int(self.soup.find('text').text)
        except:
            self.Number = 0
        return self.Number

    @debug.error_wrap('referee_info', 'birthday', str)
    def birthday(self):
        try:
            birthday_raw = [x.text for x in self.soup.select('#meta p') if 'Born:' in x.text][0]
        except:
            self.Birthday = ''
        else:
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

class executive_info:

    def __init__(self, soup):
        self.soup = soup

    @debug.error_wrap('executive_info', 'name', str)
    def name(self):
        self.Name = self.soup.select('h1 span')[0].text
        return self.Name

    @debug.error_wrap('executive_info', 'birthday', str)
    def birthday(self):
        try:
            birthday_raw = [x.text for x in self.soup.select('#meta p') if 'Born:' in x.text][0]
        except:
            self.Birthday = ''
        else:
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

class coach_info:

    def __init__(self, soup):
        self.soup = soup

    @debug.error_wrap('coach_info', 'name', str)
    def name(self):
        self.Name = self.soup.select('h1 span')[0].text
        return self.Name

    @debug.error_wrap('coach_info', 'birthday', str)
    def birthday(self):
        try:
            self.Birthday = [x.text for x in self.soup.select('#meta p') if 'Born:' in x.text][0].replace('Born: ', '').split(' in ')[0].replace('Born:\n', '').replace('\n', '').replace('   ', '')
        except:
            self.Birthday = ''
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

