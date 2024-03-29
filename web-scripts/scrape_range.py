# Imports
import sys
import pandas

pandas.options.mode.copy_on_write = True

# scraping library
import lib.get_page
from lib.utility_functions import *


# Other Variables
page = lib.get_page.page()
id_cache = {}


# Main script
beginning = int(sys.argv[1])
end = int(sys.argv[2])
seasons = range(beginning, end + 1)

for i in seasons:
    # Season Info
    season_href = generate_season_href(i)
    Seasons = get_season_info(page, season_href, id_cache)

    if should_we_write('seasons', Seasons):
        write_to_sql('seasons', Seasons)

    # Get game hrefs
    month_hrefs = get_month_page_hrefs(page, i)

    for j in month_hrefs:
        soup = page.get(j, id_cache)
        game_hrefs = [x.attrs['href'] for x in soup.select('.center a')]

        for k in game_hrefs:
            game = get_game_data(page, k, id_cache)
            game_info = pandas.DataFrame(game.output_row())

            if (not should_we_write('game_info', game_info)) or (not should_we_write('playoffs_game_info', game_info)):
                continue

            result = game.get_data()

            if game.playoffs():
                write_to_sql('playoff_game_info', pandas.DataFrame(game.output_row()))
                write_to_sql('player_games_playoffs', game.player_data())
                write_to_sql('player_quarters_playoffs', game.player_data_quarter())
                write_to_sql('team_games_playoffs', game.team_data())
                write_to_sql('team_quarters_playoffs', game.team_data_quarter())
            else:
                write_to_sql('game_info', pandas.DataFrame(game.output_row()))
                write_to_sql('player_games', game.player_data())
                write_to_sql('player_quarters', game.player_data_quarter())
                write_to_sql('team_games', game.team_data())
                write_to_sql('team_quarters', game.team_data_quarter())
