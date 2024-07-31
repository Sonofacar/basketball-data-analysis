Work in progress.

This repo is for my own personal enjoyment and to showcase my skills in data analysis and webscraping.

# Web-scraping Scripts

To use,
first run the initialization script from the web-scripts directory:
```
python3 initialize_db.py
```

Then you can execute your choice of the scraping scripts (also from the web-scripts directory).
The `scrape-range.py` script requires two years as arguments (must be later than 1990) and will scrape all information in that range:
```
python3 scrape-range.py 2000 2023
```
Be warned,
this will take a *long* time as it will wait for 4 seconds between each request to Basketball-Reference.

The other is still in progress but will run similarly to get the data for a given date.

## Data Cleaning

Even if the script did everything perfectly,
there would be errors from the website.
Here are some if the errors I know of:
| Where/When                                             | What                                                         |
|--------------------------------------------------------|--------------------------------------------------------------|
| Oklahoma City Thunder, Milwaukee Bucks, April 12, 2024 | Duration: it should be 2 hours and 6 minutes, not 206 hours. |

## Ethics

All webscraping scripts run following Basketball-Reference's requested methods as specified in their robots.txt.

# Table Specifications

Once scraped, the following tables will be created in the `bball_db` sqlite database:

## game_info
| Column         | Type    | Requirements    | References           |
|----------------|---------|-----------------|----------------------|
| Home_Team_Name | Text    |                 |                      |
| Away_Team_Name | Text    |                 |                      |
| Date           | Text    |                 |                      |
| Location       | Text    |                 |                      |
| Duration       | Integer |                 |                      |
| Attendance     | Integer | Attendance >= 0 |                      |
| Game_ID        | Integer |                 |                      |
| Home_Team_ID   | Integer |                 | team_info(Team_ID)   |
| Away_Team_ID   | Integer |                 | team_info(Team_ID)   |
| Season         | Integer | Season > 1990   | season(Season)       |
| Referee_ID1    | Integer |                 | referees(Referee_ID) |
| Referee_ID2    | Integer |                 | referees(Referee_ID) |
| Referee_ID3    | Integer |                 | referees(Referee_ID) |

## playoff_game_info
| Column         | Type    | Requirements    | References           |
|----------------|---------|-----------------|----------------------|
| Home_Team_Name | Text    |                 |                      |
| Away_Team_Name | Text    |                 |                      |
| Date           | Text    |                 |                      |
| Location       | Text    |                 |                      |
| Duration       | Integer |                 |                      |
| Attendance     | Integer | Attendance >= 0 |                      |
| Game_ID        | Integer |                 |                      |
| Home_Team_ID   | Integer |                 | team_info(Team_ID)   |
| Away_Team_ID   | Integer |                 | team_info(Team_ID)   |
| Season         | Integer | Season > 1990   | season(Season)       |
| Referee_ID1    | Integer |                 | referees(Referee_ID) |
| Referee_ID2    | Integer |                 | referees(Referee_ID) |
| Referee_ID3    | Integer |                 | referees(Referee_ID) |

## team_info
| Column             | Type    | Requirements       | References               |
|--------------------|---------|--------------------|--------------------------|
| Name               | Text    |                    |                          |
| Abbreviation       | Text    |                    |                          |
| Wins               | Integer | Wins >= 0          |                          |
| Losses             | Integer | Losses >= 0        |                          |
| Location           | Text    |                    |                          |
| Playoff_Appearance | Boolean |                    |                          |
| League_Ranking     | Integer | League_Ranking > 0 |                          |
| Team_ID            | Integer |                    |                          |
| Season             | Integer | Season > 1990      | season(Season)           |
| Coach_ID           | Integer |                    | coaches(Coach_ID)        |
| Executive_ID       | Integer |                    | executives(Executive_ID) |

## team_games
| Column              | Type    | Requirements                           | References         |
|---------------------|---------|----------------------------------------|--------------------|
| Total_minutes       | Integer | Total_minutes >= 0                     |                    |
| Field_Goals         | Integer | Default to 0, Field_Goals >= 0         |                    |
| Field_Goal_Attempts | Integer | Default to 0, Field_Goal_Attempts >= 0 |                    |
| Threes              | Integer | Default to 0, Threes >= 0              |                    |
| Three_Attempts      | Integer | Default to 0, Three_Attempts >= 0      |                    |
| Twos                | Integer | Default to 0, Twos >= 0                |                    |
| Two_Attempts        | Integer | Default to 0, Two_Attempts >= 0        |                    |
| Freethrows          | Integer | Default to 0, Freethrows >= 0          |                    |
| Freethrow_Attempts  | Integer | Default to 0, Freethrow_Attempts >= 0  |                    |
| Offensive_Rebounds  | Integer | Default to 0, Offensive_Rebounds >= 0  |                    |
| Deffensive_Rebounds | Integer | Default to 0, Deffensive_Rebounds >= 0 |                    |
| Assists             | Integer | Default to 0, Assists >= 0             |                    |
| Steals              | Integer | Default to 0, Steals >= 0              |                    |
| Blocks              | Integer | Default to 0, Blocks >= 0              |                    |
| Turnovers           | Integer | Default to 0, Turnovers >= 0           |                    |
| Fouls               | Integer | Default to 0, Fouls >= 0               |                    |
| Points              | Integer | Default to 0, Points >= 0              |                    |
| Win                 | Boolean |                                        |                    |
| Home                | Boolean |                                        |                    |
| Game_ID             | Integer |                                        | game_info(Game_ID) |
| Season              | Integer | Season > 1990                          | season(Season)     |
| Team_ID             | Integer |                                        | team_info(Team_ID) |
| Opponent_ID         | Integer |                                        | team_info(Team_ID) |

## team_quarters
| Column              | Type    | Requirements                           | References         |
|---------------------|---------|----------------------------------------|--------------------|
| Quarter             | Integer | Quarter > 0                            |                    |
| Total_Minutes       | Integer | Total_Minutes >= 0                     |                    |
| Field_Goals         | Integer | Default to 0, Field_Goals >= 0         |                    |
| Field_Goal_Attempts | Integer | Default to 0, Field_Goal_Attempts >= 0 |                    |
| Threes              | Integer | Default to 0, Threes >= 0              |                    |
| Three_Attempts      | Integer | Default to 0, Three_Attempts >= 0      |                    |
| Twos                | Integer | Default to 0, Twos >= 0                |                    |
| Two_Attempts        | Integer | Default to 0, Two_Attempts >= 0        |                    |
| Freethrows          | Integer | Default to 0, Freethrows >= 0          |                    |
| Freethrow_Attempts  | Integer | Default to 0, Freethrow_Attempts >= 0  |                    |
| Offensive_Rebounds  | Integer | Default to 0, Offensive_Rebounds >= 0  |                    |
| Deffensive_Rebounds | Integer | Default to 0, Deffensive_Rebounds >= 0 |                    |
| Assists             | Integer | Default to 0, Assists >= 0             |                    |
| Steals              | Integer | Default to 0, Steals >= 0              |                    |
| Blocks              | Integer | Default to 0, Blocks >= 0              |                    |
| Turnovers           | Integer | Default to 0, Turnovers >= 0           |                    |
| Fouls               | Integer | Default to 0, Fouls >= 0               |                    |
| Points              | Integer | Default to 0, Points >= 0              |                    |
| Win                 | Boolean |                                        |                    |
| Home                | Boolean |                                        |                    |
| Game_ID             | Integer |                                        | game_info(Game_ID) |
| Season              | Integer | Season > 1990                          | season(Season)     |
| Team_ID             | Integer |                                        | team_info(Team_ID) |
| Opponent_ID         | Integer |                                        | team_info(Team_ID) |

## team_games_playoffs
| Column              | Type    | Requirements                           | References         |
|---------------------|---------|----------------------------------------|--------------------|
| Total_minutes       | Integer | Total_minutes >= 0                     |                    |
| Field_Goals         | Integer | Default to 0, Field_Goals >= 0         |                    |
| Field_Goal_Attempts | Integer | Default to 0, Field_Goal_Attempts >= 0 |                    |
| Threes              | Integer | Default to 0, Threes >= 0              |                    |
| Three_Attempts      | Integer | Default to 0, Three_Attempts >= 0      |                    |
| Twos                | Integer | Default to 0, Twos >= 0                |                    |
| Two_Attempts        | Integer | Default to 0, Two_Attempts >= 0        |                    |
| Freethrows          | Integer | Default to 0, Freethrows >= 0          |                    |
| Freethrow_Attempts  | Integer | Default to 0, Freethrow_Attempts >= 0  |                    |
| Offensive_Rebounds  | Integer | Default to 0, Offensive_Rebounds >= 0  |                    |
| Deffensive_Rebounds | Integer | Default to 0, Deffensive_Rebounds >= 0 |                    |
| Assists             | Integer | Default to 0, Assists >= 0             |                    |
| Steals              | Integer | Default to 0, Steals >= 0              |                    |
| Blocks              | Integer | Default to 0, Blocks >= 0              |                    |
| Turnovers           | Integer | Default to 0, Turnovers >= 0           |                    |
| Fouls               | Integer | Default to 0, Fouls >= 0               |                    |
| Points              | Integer | Default to 0, Points >= 0              |                    |
| Win                 | Boolean |                                        |                    |
| Home                | Boolean |                                        |                    |
| Game_ID             | Integer |                                        | game_info(Game_ID) |
| Season              | Integer | Season > 1990                          | season(Season)     |
| Team_ID             | Integer |                                        | team_info(Team_ID) |
| Opponent_ID         | Integer |                                        | team_info(Team_ID) |

## team_quarters_playoffs
| Column              | Type    | Requirements                           | References         |
|---------------------|---------|----------------------------------------|--------------------|
| Quarter             | Integer | Quarter > 0                            |                    |
| Total_Minutes       | Integer | Total_Minutes >= 0                     |                    |
| Field_Goals         | Integer | Default to 0, Field_Goals >= 0         |                    |
| Field_Goal_Attempts | Integer | Default to 0, Field_Goal_Attempts >= 0 |                    |
| Threes              | Integer | Default to 0, Threes >= 0              |                    |
| Three_Attempts      | Integer | Default to 0, Three_Attempts >= 0      |                    |
| Twos                | Integer | Default to 0, Twos >= 0                |                    |
| Two_Attempts        | Integer | Default to 0, Two_Attempts >= 0        |                    |
| Freethrows          | Integer | Default to 0, Freethrows >= 0          |                    |
| Freethrow_Attempts  | Integer | Default to 0, Freethrow_Attempts >= 0  |                    |
| Offensive_Rebounds  | Integer | Default to 0, Offensive_Rebounds >= 0  |                    |
| Deffensive_Rebounds | Integer | Default to 0, Deffensive_Rebounds >= 0 |                    |
| Assists             | Integer | Default to 0, Assists >= 0             |                    |
| Steals              | Integer | Default to 0, Steals >= 0              |                    |
| Blocks              | Integer | Default to 0, Blocks >= 0              |                    |
| Turnovers           | Integer | Default to 0, Turnovers >= 0           |                    |
| Fouls               | Integer | Default to 0, Fouls >= 0               |                    |
| Points              | Integer | Default to 0, Points >= 0              |                    |
| Win                 | Boolean |                                        |                    |
| Home                | Boolean |                                        |                    |
| Game_ID             | Integer |                                        | game_info(Game_ID) |
| Season              | Integer | Season > 1990                          | season(Season)     |
| Team_ID             | Integer |                                        | team_info(Team_ID) |
| Opponent_ID         | Integer |                                        | team_info(Team_ID) |

## player_info
| Column         | Type    | Requirements      | References |
|----------------|---------|-------------------|------------|
| Name           | Text    |                   |            |
| Shoots         | Text    | Either 'L' or 'R' |            |
| Birthday       | Text    |                   |            |
| High_School    | Boolean |                   |            |
| College        | Boolean |                   |            |
| Draft_Position | Integer | Default to 0      |            |
| Draft_Team     | Text    |                   |            |
| Draft_Year     | Integer | Default to 0      |            |
| Debut_Date     | Text    |                   |            |
| Career_Seasons | Integer | Default to 0      |            |
| Teams          | Text    |                   |            |
| Player_ID      | Integer |                   |            |

## player_games
| Column              | Type    | Requirements                           | References             |
|---------------------|---------|----------------------------------------|------------------------|
| Minutes             | Integer | Default to 0, Minutes >= 0             |                        |
| Field_Goals         | Integer | Default to 0, Field_Goals >= 0         |                        |
| Field_Goal_Attempts | Integer | Default to 0, Field_Goal_Attempts >= 0 |                        |
| Threes              | Integer | Default to 0, Threes >= 0              |                        |
| Three_Attempts      | Integer | Default to 0, Three_Attempts >= 0      |                        |
| Twos                | Integer | Default to 0, Twos >= 0                |                        |
| Two_Attempts        | Integer | Default to 0, Two_Attempts >= 0        |                        |
| Freethrows          | Integer | Default to 0, Freethrows >= 0          |                        |
| Freethrow_Attempts  | Integer | Default to 0, Freethrow_Attempts >= 0  |                        |
| Offensive_Rebounds  | Integer | Default to 0, Offensive_Rebounds >= 0  |                        |
| Deffensive_Rebounds | Integer | Default to 0, Deffensive_Rebounds >= 0 |                        |
| Assists             | Integer | Default to 0, Assists >= 0             |                        |
| Steals              | Integer | Default to 0, Steals >= 0              |                        |
| Blocks              | Integer | Default to 0, Blocks >= 0              |                        |
| Turnovers           | Integer | Default to 0, Turnovers >= 0           |                        |
| Fouls               | Integer | Default to 0, Fouls >= 0               |                        |
| Points              | Integer | Default to 0, Points >= 0              |                        |
| PM                  | Integer | Default to 0                           |                        |
| Injured             | Boolean |                                        |                        |
| Win                 | Boolean |                                        |                        |
| Home                | Boolean |                                        |                        |
| Player_ID           | Integer |                                        | player_info(Player_ID) |
| Game_ID             | Integer |                                        | game_info(Game_ID)     |
| Season              | Integer | Season > 1990                          | season(Season)         |
| Team_ID             | Integer |                                        | team_info(Team_ID)     |
| Opponent_ID         | Integer |                                        | team_info(Team_ID)     |

## player_quarters
| Column              | Type    | Requirements                           | References             |
|---------------------|---------|----------------------------------------|------------------------|
| Quarter             | Integer | Quarter > 0                            |                        |
| Minutes             | Integer | Default to 0, Minutes >= 0             |                        |
| Field_Goals         | Integer | Default to 0, Field_Goals >= 0         |                        |
| Field_Goal_Attempts | Integer | Default to 0, Field_Goal_Attempts >= 0 |                        |
| Threes              | Integer | Default to 0, Threes >= 0              |                        |
| Three_Attempts      | Integer | Default to 0, Three_Attempts >= 0      |                        |
| Twos                | Integer | Default to 0, Twos >= 0                |                        |
| Two_Attempts        | Integer | Default to 0, Two_Attempts >= 0        |                        |
| Freethrows          | Integer | Default to 0, Freethrows >= 0          |                        |
| Freethrow_Attempts  | Integer | Default to 0, Freethrow_Attempts >= 0  |                        |
| Offensive_Rebounds  | Integer | Default to 0, Offensive_Rebounds >= 0  |                        |
| Deffensive_Rebounds | Integer | Default to 0, Deffensive_Rebounds >= 0 |                        |
| Assists             | Integer | Default to 0, Assists >= 0             |                        |
| Steals              | Integer | Default to 0, Steals >= 0              |                        |
| Blocks              | Integer | Default to 0, Blocks >= 0              |                        |
| Turnovers           | Integer | Default to 0, Turnovers >= 0           |                        |
| Fouls               | Integer | Default to 0, Fouls >= 0               |                        |
| Points              | Integer | Default to 0, Points >= 0              |                        |
| PM                  | Integer | Default to 0                           |                        |
| Injured             | Boolean |                                        |                        |
| Win                 | Boolean |                                        |                        |
| Home                | Boolean |                                        |                        |
| Player_ID           | Integer |                                        | player_info(Player_ID) |
| Game_ID             | Integer |                                        | game_info(Game_ID)     |
| Season              | Integer | Season > 1990                          | season(Season)         |
| Team_ID             | Integer |                                        | team_info(Team_ID)     |
| Opponent_ID         | Integer |                                        | team_info(Team_ID)     |

## player_games_playoffs
| Column              | Type    | Requirements                           | References             |
|---------------------|---------|----------------------------------------|------------------------|
| Minutes             | Integer | Default to 0, Minutes >= 0             |                        |
| Field_Goals         | Integer | Default to 0, Field_Goals >= 0         |                        |
| Field_Goal_Attempts | Integer | Default to 0, Field_Goal_Attempts >= 0 |                        |
| Threes              | Integer | Default to 0, Threes >= 0              |                        |
| Three_Attempts      | Integer | Default to 0, Three_Attempts >= 0      |                        |
| Twos                | Integer | Default to 0, Twos >= 0                |                        |
| Two_Attempts        | Integer | Default to 0, Two_Attempts >= 0        |                        |
| Freethrows          | Integer | Default to 0, Freethrows >= 0          |                        |
| Freethrow_Attempts  | Integer | Default to 0, Freethrow_Attempts >= 0  |                        |
| Offensive_Rebounds  | Integer | Default to 0, Offensive_Rebounds >= 0  |                        |
| Deffensive_Rebounds | Integer | Default to 0, Deffensive_Rebounds >= 0 |                        |
| Assists             | Integer | Default to 0, Assists >= 0             |                        |
| Steals              | Integer | Default to 0, Steals >= 0              |                        |
| Blocks              | Integer | Default to 0, Blocks >= 0              |                        |
| Turnovers           | Integer | Default to 0, Turnovers >= 0           |                        |
| Fouls               | Integer | Default to 0, Fouls >= 0               |                        |
| Points              | Integer | Default to 0, Points >= 0              |                        |
| PM                  | Integer | Default to 0                           |                        |
| Injured             | Boolean |                                        |                        |
| Win                 | Boolean |                                        |                        |
| Home                | Boolean |                                        |                        |
| Player_ID           | Integer |                                        | player_info(Player_ID) |
| Game_ID             | Integer |                                        | game_info(Game_ID)     |
| Season              | Integer | Season > 1990                          | season(Season)         |
| Team_ID             | Integer |                                        | team_info(Team_ID)     |
| Opponent_ID         | Integer |                                        | team_info(Team_ID)     |

## player_quarters_playoffs
| Column              | Type    | Requirements                           | References             |
|---------------------|---------|----------------------------------------|------------------------|
| Quarter             | Integer | Quarter > 0                            |                        |
| Minutes             | Integer | Default to 0, Minutes >= 0             |                        |
| Field_Goals         | Integer | Default to 0, Field_Goals >= 0         |                        |
| Field_Goal_Attempts | Integer | Default to 0, Field_Goal_Attempts >= 0 |                        |
| Threes              | Integer | Default to 0, Threes >= 0              |                        |
| Three_Attempts      | Integer | Default to 0, Three_Attempts >= 0      |                        |
| Twos                | Integer | Default to 0, Twos >= 0                |                        |
| Two_Attempts        | Integer | Default to 0, Two_Attempts >= 0        |                        |
| Freethrows          | Integer | Default to 0, Freethrows >= 0          |                        |
| Freethrow_Attempts  | Integer | Default to 0, Freethrow_Attempts >= 0  |                        |
| Offensive_Rebounds  | Integer | Default to 0, Offensive_Rebounds >= 0  |                        |
| Deffensive_Rebounds | Integer | Default to 0, Deffensive_Rebounds >= 0 |                        |
| Assists             | Integer | Default to 0, Assists >= 0             |                        |
| Steals              | Integer | Default to 0, Steals >= 0              |                        |
| Blocks              | Integer | Default to 0, Blocks >= 0              |                        |
| Turnovers           | Integer | Default to 0, Turnovers >= 0           |                        |
| Fouls               | Integer | Default to 0, Fouls >= 0               |                        |
| Points              | Integer | Default to 0, Points >= 0              |                        |
| PM                  | Integer | Default to 0                           |                        |
| Injured             | Boolean |                                        |                        |
| Win                 | Boolean |                                        |                        |
| Home                | Boolean |                                        |                        |
| Player_ID           | Integer |                                        | player_info(Player_ID) |
| Game_ID             | Integer |                                        | game_info(Game_ID)     |
| Season              | Integer | Season > 1990                          | season(Season)         |
| Team_ID             | Integer |                                        | team_info(Team_ID)     |
| Opponent_ID         | Integer |                                        | team_info(Team_ID)     |

## seasons
| Column     | Type    | Requirements  | References             |
|------------|---------|---------------|------------------------|
| Season     | Integer | Season > 1990 |                        |
| Games      | Integer |               |                        |
| Teams      | Integer |               |                        |
| Champion   | Integer |               | team_info(Team_ID)     |
| Finals_MVP | Integer |               | player_info(Player_ID) |
| MVP        | Integer |               | player_info(Player_ID) |
| DPOY       | Integer |               | player_info(Player_ID) |
| MIP        | Integer |               | player_info(Player_ID) |
| SixMOTY    | Integer |               | player_info(Player_ID) |
| ROTY       | Integer |               | player_info(Player_ID) |

## referee_info
| Column     | Type    | Requirements | References |
|------------|---------|--------------|------------|
| Name       | Text    |              |            |
| Number     | Integer |              |            |
| Birthday   | Text    |              |            |
| Referee_ID | Integer |              |            |

## executive_info
| Column       | Type    | Requirements | References |
|--------------|---------|--------------|------------|
| Name         | Text    |              |            |
| Birthday     | Text    |              |            |
| Teams        | Text    |              |            |
| Executive_ID | Integer |              |            |

## coach_info
| Column   | Type    | Requirements | References |
|----------|---------|--------------|------------|
| Name     | Text    |              |            |
| Birthday | Text    |              |            |
| Wins     | Integer | Wins >= 0    |            |
| Losses   | Integer | Losses >= 0  |            |
| Teams    | Text    |              |            |
| Coach_ID | Integer |              |            |
