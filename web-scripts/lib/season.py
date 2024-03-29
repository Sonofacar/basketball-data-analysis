from bs4 import BeautifulSoup, Comment

class season_info:

    def __init__(self, soup):
        self.soup = soup

    def header(self):
        for line in self.soup.select('#meta p'):
            if 'League Champion' in line.text:
                self.champion_name = line.find('a').text
                self.champion_href = line.find('a').attrs['href']

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

    def season(self):
        self.Season = int(self.soup.select('h1 span')[0].text.split('-')[0]) + 1
        return self.Season

    def games(self):
        team_totals = [int(x.text) for x in self.soup.select('#per_game-team tbody .left+ .right')]
        self.Games = sum(team_totals)
        return self.Games

    def teams(self):
        teams = self.soup.select('#per_game-team a')
        self.Teams = len(teams)
        return self.Teams

    def champion_href(self):
        return self.champion_href

    def set_champion(self, In):
        self.Champion = In
        return self.Champion

    def champion(self):
        return self.Champion

    def finals_mvp_href(self, playoffs_soup):
        selection = [x.find('a') for x in playoffs_soup.select('#meta p') if 'Finals MVP' in x.text][0]
        self.Finals_MVP_href = selection.attrs['href']
        return self.Finals_MVP_href

    def set_finals_mvp(self, In):
        self.Finals_MVP = In
        return self.Finals_MVP

    def finals_mvp(self):
        return self.Finals_MVP

    def mvp_href(self):
        return self.MVP_href

    def set_mvp(self, In):
        self.MVP = In
        return self.MVP

    def mvp(self):
        return self.MVP

    def dpoy_href(self):
        return self.DPOY_href

    def set_dpoy(self, In):
        self.DPOY = In
        return self.DPOY

    def dpoy(self):
        return self.DPOY

    def mip_href(self):
        return self.MIP_href

    def set_mip(self, In):
        self.MIP = In
        return self.MIP

    def mip(self):
        return self.MIP

    def sixmoty_href(self):
        return self.SixMOTY_href

    def set_sixmoty(self, In):
        self.SixMOTY = In
        return self.SixMOTY

    def sixmoty(self):
        return self.SixMOTY

    def roty_href(self):
        return self.ROTY_href

    def set_roty(self, In):
        self.ROTY = In
        return self.ROTY

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
