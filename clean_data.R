# Libraries
library(tidyverse) |> suppressMessages()
library(RSQLite)

# Add custom functions
source("functions.R")

# Read in data
conn <- dbConnect(RSQLite::SQLite(), "bball_db")
player_games <- dbReadTable(conn, "player_games") %>%
  tibble()
team_games <- dbReadTable(conn, "team_games") %>%
  tibble() %>%
  select(!c(Win, Home, Season, Opponent_ID))
player_info <- dbReadTable(conn, "player_info") %>%
  tibble() %>%
  select(!c(
    High_School,
    College,
    Draft_Team
  )) %>%
  mutate(
    Shoots = factor(Shoots),
    Birthday = Birthday %>%
      as.Date("%b %d, %Y") %>%
      as.numeric(),
    Debut_Date = Debut_Date %>%
      as.Date("%b %d, %Y") %>%
      as.numeric()
  )
game_info <- dbReadTable(conn, "game_info") %>%
  tibble()
team_info <- dbReadTable(conn, "team_info") %>%
  tibble() %>%
  select(!c(
    Name,
    Abbreviation,
    Location,
    Coach_ID,
    Executive_ID
  ))
dbDisconnect(conn)

# Aggregate data by season
season_totals <- player_games %>%
  inner_join(
    team_games,
    by = c("Team_ID", "Game_ID"),
    suffix = c("", "_team")
  ) %>%
  inner_join(
    team_games %>% rename(Opponent_ID = Team_ID),
    by = c("Opponent_ID", "Game_ID"),
    suffix = c("", "_opponent")
  ) %>%
  mutate(
    Possessions = possessions_team_precise(
      Field_Goal_Attempts_team,
      Field_Goals_team,
      Freethrow_Attempts_team,
      Offensive_Rebounds_team,
      Defensive_Rebounds_team,
      Turnovers_team,
      Field_Goal_Attempts_opponent,
      Field_Goals_opponent,
      Freethrow_Attempts_opponent,
      Offensive_Rebounds_opponent,
      Defensive_Rebounds_opponent,
      Turnovers_opponent
    ),
    Pace = pace(Seconds_team / 60, Possessions)
  ) %>%
  group_by(Player_ID, Season) %>%
  summarize(
    Games = n(),
    Seconds = sum(Seconds),
    Threes = sum(Threes),
    Three_Attempts = sum(Three_Attempts),
    Field_Goals = sum(Field_Goals),
    Field_Goal_Attempts = sum(Field_Goal_Attempts),
    Freethrows = sum(Freethrows), 
    Freethrow_Attempts = sum(Freethrow_Attempts),
    Offensive_Rebounds = sum(Offensive_Rebounds),
    Defensive_Rebounds = sum(Defensive_Rebounds),
    Assists = sum(Assists),
    Steals = sum(Steals),
    Blocks = sum(Blocks),
    Turnovers = sum(Turnovers),
    Fouls = sum(Fouls),
    Points = sum(Points),
    PM = sum(PM),
    Seconds_team = sum(Seconds_team),
    Threes_team = sum(Threes_team),
    Three_Attempts_team = sum(Three_Attempts_team),
    Field_Goals_team = sum(Field_Goals_team),
    Field_Goal_Attempts_team = sum(Field_Goal_Attempts_team),
    Freethrows_team = sum(Freethrows_team), 
    Freethrow_Attempts_team = sum(Freethrow_Attempts_team),
    Offensive_Rebounds_team = sum(Offensive_Rebounds_team),
    Defensive_Rebounds_team = sum(Defensive_Rebounds_team),
    Assists_team = sum(Assists_team),
    Steals_team = sum(Steals_team),
    Blocks_team = sum(Blocks_team),
    Turnovers_team = sum(Turnovers_team),
    Fouls_team = sum(Fouls_team),
    Points_team = sum(Points_team),
    Seconds_opponent = sum(Seconds_opponent),
    Threes_opponent = sum(Threes_opponent),
    Three_Attempts_opponent = sum(Three_Attempts_opponent),
    Field_Goals_opponent = sum(Field_Goals_opponent),
    Field_Goal_Attempts_opponent = sum(Field_Goal_Attempts_opponent),
    Freethrows_opponent = sum(Freethrows_opponent), 
    Freethrow_Attempts_opponent = sum(Freethrow_Attempts_opponent),
    Offensive_Rebounds_opponent = sum(Offensive_Rebounds_opponent),
    Defensive_Rebounds_opponent = sum(Defensive_Rebounds_opponent),
    Assists_opponent = sum(Assists_opponent),
    Steals_opponent = sum(Steals_opponent),
    Blocks_opponent = sum(Blocks_opponent),
    Turnovers_opponent = sum(Turnovers_opponent),
    Fouls_opponent = sum(Fouls_opponent),
    Points_opponent = sum(Points_opponent),
    Possessions = sum(Possessions),
    Pace = mean(Pace),
    Team_ID = last(Team_ID),
  ) %>%
  mutate(
    # Approximate starting date of October 20
    Season_start = paste(Season, 10, 20, sep = "-") %>%
      as.Date() %>%
      as.numeric(),
    Fantasy_points = fantasy_points(
      Points,
      Threes,
      Field_Goals,
      Field_Goal_Attempts,
      Freethrow_Attempts,
      Freethrows,
      Offensive_Rebounds + Defensive_Rebounds,
      Assists,
      Steals,
      Blocks,
      Turnovers
    ),
    Usage = usage(
      Seconds / 60,
      Field_Goal_Attempts,
      Freethrow_Attempts,
      Turnovers,
      Seconds_team / 60,
      Field_Goal_Attempts_team,
      Freethrow_Attempts_team,
      Turnovers_team
    ),
    Seconds_lag_two = lag(Seconds, default = 0, order_by = Season),
    Seconds_lag_three = lag(Seconds, n = 2, default = 0, order_by = Season),
    Seconds_lag_four = lag(Seconds, n = 3, default = 0, order_by = Season),
    Seconds_lag_five = lag(Seconds, n = 4, default = 0, order_by = Season),
    Seconds_lag_six = lag(Seconds, n = 5, default = 0, order_by = Season)
  ) %>%
  ungroup() %>%
  group_by(Season) %>%
  # top_n(156, Fantasy_points) %>% # 156 corresponds to a 12 team league
  rename(Seconds_lag_one = Seconds)
