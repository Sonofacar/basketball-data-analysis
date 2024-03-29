import re

class team_info:

    def __init__(self, franchise_soup, soup, url):
        self.franchise_soup = franchise_soup
        self.soup = soup
        self.url = url

        self.coach_path = 'p:nth-child(4) a'
        self.executive_path = 'p:nth-child(5) a'

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

    def name(self):
        beginning = re.sub(' Roster.*$', '', self.soup.title.text)
        self.Name = re.sub('^[0-9]{4}-[0-9]{2} ', '', beginning)
        return self.Name

    def abbreviation(self):
        self.Abbreviation = self.url.split('/')[4]
        return self.Abbreviation

    def wins(self):
        self.Wins = int(self.franchise_soup.select('.left+ .right')[self.franchise_index].text)
        return self.Wins

    def losses(self):
        self.Losses = int(self.franchise_soup.select('.right:nth-child(5)')[self.franchise_index].text)
        return self.Losses

    def location(self):
        match = self.franchise_soup.select('h1+ p')[0].text
        self.Location = match.replace('\n', '').replace('Location:  ', '')
        return self.Location

    def playoff_appearance(self):
        text = self.franchise_soup.select('.right+ .left')[self.franchise_index].text
        self.Playoff_appearance = (text != '')
        return self.Playoff_appearance

    def ranking(self, In):
        self.Ranking = In
        return self.Ranking

    def generate_team_id(self, prev):
        self.Team_ID = prev + 1
        return self.Team_ID

    def team_id(self, prev):
        generate_team_id(prev)
        return self.Team_ID

    def season(self):
        self.Season = self.url.split('/')[5].replace('.html', '')
        return self.Season

    def executive_href(self):
        selection = self.soup.select(self.executive_path)
        self.executive_href = [tag.attrs['href'] for tag in selection if re.match('/executives', tag.attrs['href'])][0]
        return self.kxecutive_href

    def set_executive_id(self, In):
        self.Executive_ID = In
        return self.Executive_ID

    def executive(self):
        return self.Executive_ID

    def coach_href(self):
        selection = self.soup.select(self.coach_path)
        self.Coach_href = [tag.attrs['href'] for tag in selection if re.match('/coaches', tag.attrs['href'])][0]
        return self.Coach_href

    def set_coach_id(self, In):
        self.co_id = In
        self.Coach_ID = self.co_id
        return self.Coach_ID

    def coach(self):
        return self.Coach_ID

    def output_row(self, ranking, executive_id, coach_id, prev_id = 0):
        self.generate_team_id(prev_id)
        self.set_franchise_index()
        self.ranking(ranking)
        self.set_executive_id(executive_id)
        self.set_coach_id(coach_id)
        self.row = {'Name': [self.name()],
                    'Abbreviation': [self.abbreviation()],
                    'Wins': [self.wins()],
                    'Losses': [self.losses()],
                    'Location': [self.location()],
                    'Playoff_Appearance': [self.playoff_appearance()],
                    'League_Ranking': [self.Ranking],
                    'Team_ID': [self.Team_ID],
                    'Season': [self.season()],
                    'Executive_ID': [self.Executive_ID],
                    'Coach_ID': [self.Coach_ID]}
        return self.row
