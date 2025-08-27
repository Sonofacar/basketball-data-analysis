# Libraries
library(tidyverse) |> suppressMessages()
library(RSQLite)
library(randomForest)

# Add custom functions
source("functions.R")

# Read in data
conn <- dbConnect(RSQLite::SQLite(), "bball_db")
player_games <- dbReadTable(conn, "player_games") %>%
  tibble()
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
  group_by(Player_ID, Season) %>%
  summarize(
    Games = n_distinct(Game_ID),
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
    PM = mean(PM),
    Injured = sum(Injured),
    Team_ID = last(Team_ID)
  ) %>%
  mutate(
    Games_played = Games - Injured,
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
    Seconds_lag_two = lag(Seconds, default = 0, order_by = Season),
    Seconds_lag_three = lag(Seconds, n = 2, default = 0, order_by = Season),
  ) %>%
  rename(Seconds_lag_one = Seconds) %>%
  select(!c(
    Games,
    Injured
  ))

# Save seconds data to use as response variable
response <- season_totals %>%
  rename(Seconds = Seconds_lag_one) %>%
  select(c(Seconds, Season, Player_ID)) %>%
  mutate(Season = Season - 1)

# Merge Data and perform final feature engineering
data <- player_info %>%
  inner_join(season_totals, by = c("Player_ID")) %>%
  inner_join(
    team_info,
    by = c("Team_ID", "Season"),
    suffix = c("", "_team")
  ) %>%
  inner_join(response, by = c("Player_ID", "Season")) %>%
  select(!c(Player_ID, Team_ID)) %>%
  mutate(
    Win_pct = Wins / (Wins + Losses),
    Age = (Season_start - Birthday) / 365,
    Experience = (Season_start - Debut_Date) / 365
  ) %>%
  select(!c(
    Wins,
    Losses,
    Birthday,
    Debut_Date
  )) %>%
  drop_na()

train <- data
test <- data

# Make a random forest model to act as a baseline
model <- randomForest(Seconds ~ ., data = train, ntree = 250)
