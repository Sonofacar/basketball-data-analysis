#!/usr/bin/Rscript

# This script needs to take data and format it as follows:
# | ...Player Data... | mu_hs | mu_hl | mu_hS | ... |
# | ................. | ..... | ..... | ..... | ... |
# Where the player data is any information desired on a player,
# and the various `mu_??` are the force of transition in this
# multi-state model:
#   ▗▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▖
#   ▐                   Healthy                   ▌
#   ▝▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▘
#         ▲                  |              |
#         |                  |              |
#         ▼                  ▼              ▼
# ▗▄▄▄▄▄▄▄▄▄▄▄▄▄▄▖    ▗▄▄▄▄▄▄▄▄▄▄▄▄▄▖ ▗▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▖
# ▐ Short injury ▌◀---▐ Long injury ▌ ▐ Season-ending injury ▌
# ▝▀▀▀▀▀▀▀▀▀▀▀▀▀▀▘    ▝▀▀▀▀▀▀▀▀▀▀▀▀▀▘ ▝▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▘
#
# A player can transition to and from the healthy state to any other,
# but they cannot transition between the various injury states.
# 
# The script will merge the data from various tables in a sqlite database,
# and compute the various force of transition values for each possible
# combination. 

# Libraries
library(RSQLite)
library(msm)

# Threshold to split short and long injuries at
# ADJUST TO CHANGE RATIO OF SHORT/LONG-TERM INJURIES
THRESHOLD=3

# Get data from SQL database
conn <- dbConnect(RSQLite::SQLite(), "../bball_db")
player_games_raw <- dbReadTable(conn, "player_games")
player_info_raw <- dbReadTable(conn, "player_info")
game_info_raw <- dbReadTable(conn, "game_info")
dbDisconnect(conn)

# Make the date column into a numeric value
game_info <- game_info_raw |>
  within({
    Date = Date |> as.Date("%b %d, %Y") |> as.numeric()
    rm(Home_Team_Name, Away_Team_Name, Referee_ID1, Referee_ID2, Referee_ID3)
  })
player_games <- player_games_raw |>
  within({
    rm(Threes, Three_Attempts, Field_Goals, Field_Goal_Attempts, Freethrows,
       Freethrow_Attempts, Offensive_Rebounds, Defensive_Rebounds, Assists,
       Steals, Blocks, Turnovers, Fouls, Points, PM, Win, Home)
  })

# Utility functions
get_player_states <- function(player_id, season, p_data_raw, g_data_raw) {
  rows <- with(p_data_raw, (Player_ID == player_id) & (Season == season))
  p_data <- p_data_raw[rows, ]
  teams <- unique(p_data[["Team_ID"]])

  if (nrow(p_data) == 0) {
    return NULL # Early exit
  }

  rows <- g_data_raw |>
    with(
      (Season == season) &
        (Home_Team_ID %in% teams | Away_Team_ID %in% teams)
    )
  g_data <- g_data_raw[rows, ]
  data <- merge(g_data, p_data, by = c("Game_ID", "Season"), all.x = TRUE) |>
    within({
      last_team <- numeric()
      drop <- numeric()
      for (i in seq_along(Seconds)) {
      }
    })
}
