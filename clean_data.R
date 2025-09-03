# Libraries
library(tidyverse) |> suppressMessages()
library(RSQLite)

# Add custom functions
source("functions.R")

# Read in data
conn <- dbConnect(RSQLite::SQLite(), "bball_db")
player_games <- dbReadTable(conn, "player_games") %>%
  tibble() %>%
  filter(Injured != 1) %>%
  select(!c(Injured))
team_games <- dbReadTable(conn, "team_games") %>%
  tibble() %>%
  select(!c(Win, Home, Season, Opponent_ID))
player_info <- dbReadTable(conn, "player_info") %>%
  tibble() %>%
  select(!c(
    Name,
    High_School,
    College,
    Career_Seasons,
    Draft_Team,
    Teams
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
      Two_Attempts_team,
      Twos_team,
      Freethrow_Attempts_team,
      Offensive_Rebounds_team,
      Deffensive_Rebounds_team,
      Turnovers_team,
      Two_Attempts_opponent,
      Twos_opponent,
      Freethrow_Attempts_opponent,
      Offensive_Rebounds_opponent,
      Deffensive_Rebounds_opponent,
      Turnovers_opponent
    ),
    Pace = pace(Total_minutes, Possessions)
  ) %>%
  group_by(Player_ID, Season) %>%
  summarize(
    Games = n(),
    Seconds = sum(Seconds),
    Threes = sum(Threes),
    Three_Attempts = sum(Three_Attempts),
    Twos = sum(Twos),
    Two_Attempts = sum(Two_Attempts),
    Freethrows = sum(Freethrows), 
    Freethrow_Attempts = sum(Freethrow_Attempts),
    Offensive_Rebounds = sum(Offensive_Rebounds),
    Deffensive_Rebounds = sum(Deffensive_Rebounds),
    Assists = sum(Assists),
    Steals = sum(Steals),
    Blocks = sum(Blocks),
    Turnovers = sum(Turnovers),
    Fouls = sum(Fouls),
    Points = sum(Points),
    PM = sum(PM),
    Minutes_team = sum(Total_minutes),
    Threes_team = sum(Threes_team),
    Three_Attempts_team = sum(Three_Attempts_team),
    Twos_team = sum(Twos_team),
    Two_Attempts_team = sum(Two_Attempts_team),
    Freethrows_team = sum(Freethrows_team), 
    Freethrow_Attempts_team = sum(Freethrow_Attempts_team),
    Offensive_Rebounds_team = sum(Offensive_Rebounds_team),
    Deffensive_Rebounds_team = sum(Deffensive_Rebounds_team),
    Assists_team = sum(Assists_team),
    Steals_team = sum(Steals_team),
    Blocks_team = sum(Blocks_team),
    Turnovers_team = sum(Turnovers_team),
    Fouls_team = sum(Fouls_team),
    Points_team = sum(Points_team),
    Minutes_opponent = sum(Total_minutes_opponent),
    Threes_opponent = sum(Threes_opponent),
    Three_Attempts_opponent = sum(Three_Attempts_opponent),
    Twos_opponent = sum(Twos_opponent),
    Two_Attempts_opponent = sum(Two_Attempts_opponent),
    Freethrows_opponent = sum(Freethrows_opponent), 
    Freethrow_Attempts_opponent = sum(Freethrow_Attempts_opponent),
    Offensive_Rebounds_opponent = sum(Offensive_Rebounds_opponent),
    Deffensive_Rebounds_opponent = sum(Deffensive_Rebounds_opponent),
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
      Twos,
      Two_Attempts,
      Freethrow_Attempts,
      Freethrows,
      Offensive_Rebounds + Deffensive_Rebounds,
      Assists,
      Steals,
      Blocks,
      Turnovers
    ),
    Usage = usage(
      Seconds / 60,
      Two_Attempts,
      Freethrow_Attempts,
      Turnovers,
      Minutes_team,
      Two_Attempts_team,
      Freethrow_Attempts_team,
      Turnovers_team
    ),
    Seconds_lag_two = lag(Seconds, default = 0, order_by = Season),
    Seconds_lag_three = lag(Seconds, n = 2, default = 0, order_by = Season)
  ) %>%
  group_by(Season) %>%
  top_n(156, Fantasy_points) %>% # 156 corresponds to a 12 team league
  rename(Seconds_lag_one = Seconds)
