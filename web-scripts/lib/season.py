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
        self.mvp_href = players[0].attrs['href']

        # ROTY
        self.roty_name = players[1].text
        self.roty_href = players[1].attrs['href']

        # DPOY
        self.dpoy_name = players[2].text
        self.dpoy_href = players[2].attrs['href']

        # MIP
        self.mip_name = players[3].text
        self.mip_href = players[3].attrs['href']

        # SixMOTY
        self.sixmoty_name = players[4].text
        self.sixmoty_href = players[4].attrs['href']

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

    def champion_match_dict(self):
        if not hasattr(self, 'champion_name'):
            self.header()
        self.champion_matches = {'Name': self.champion_name,
                                 'Season': self.season(),
                                 'href': self.champion_href}
        return self.champion_matches

    def set_champion(self, In):
        self.Champion = In
        return self.Champion

    def champion(self):
        return self.Champion

    def finals_mvp_url(self):
        href = self.soup.select('.drophover a')[0].attrs['href']
        return 'https://www.basketball-reference.com' + href

    def finals_mvp_info(self, playoffs_soup):
        selection = [x.find('a') for x in playoffs_soup.select('#meta p') if 'Finals MVP' in x.text][0]
        self.finals_mvp_name = selection.text
        self.finals_mvp_href = selection.attrs['href']

    def finals_mvp_match_dict(self, playoffs_soup):
        if not hasattr(self, 'finals_mvp_name'):
            self.finals_mvp_info(playoffs_soup)
        self.finals_mvp_matches = {'Name': self.finals_mvp_name,
                                   'Season': self.season(),
                                   'href': self.finals_mvp_href}
        return self.finals_mvp_matches

    def set_finals_mvp(self, In):
        self.Finals_MVP = In
        return self.Finals_MVP

    def finals_mvp(self):
        return self.Finals_MVP

    def mvp_match_dict(self):
        if not hasattr(self, 'mvp_name'):
            self.awards()
        self.mvp_matches = {'Name': self.mvp_name,
                            'Season': self.season(),
                            'href': self.mvp_href}
        return self.mvp_matches

    def set_mvp(self, In):
        self.MVP = In
        return self.MVP

    def mvp(self):
        return self.MVP

    def dpoy_match_dict(self):
        if not hasattr(self, 'dpoy_name'):
            self.awards()
        self.dpoy_matches = {'Name': self.dpoy_name,
                             'Season': self.season(),
                             'href': self.dpoy_href}
        return self.dpoy_matches

    def set_dpoy(self, In):
        self.DPOY = In
        return self.DPOY

    def dpoy(self):
        return self.DPOY

    def mip_match_dict(self):
        if not hasattr(self, 'mip_name'):
            self.awards()
        self.mip_matches = {'Name': self.mip_name,
                            'Season': self.season(),
                            'href': self.mip_href}
        return self.mip_matches

    def set_mip(self, In):
        self.MIP = In
        return self.MIP

    def mip(self):
        return self.MIP

    def sixmoty_match_dict(self):
        if not hasattr(self, 'sixmoty_name'):
            self.awards()
        self.sixmoty_matches = {'Name': self.sixmoty_name,
                                'Season': self.season(),
                                'href': self.sixmoty_href}
        return self.sixmoty_matches

    def set_sixmoty(self, In):
        self.SixMOTY = In
        return self.SixMOTY

    def sixmoty(self):
        return self.SixMOTY

    def roty_match_dict(self):
        if not hasattr(self, 'roty_name'):
            self.awards()
        self.roty_matches = {'Name': self.roty_name,
                             'Season': self.season(),
                             'href': self.roty_href}
        return self.roty_matches

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
