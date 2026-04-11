#!/usr/bin/Rscript

# This script needs to take data and format it as follows:
# | ...Player Data... | mu_hs | mu_hl | mu_hS | ... |
# | ................. | ..... | ..... | ..... | ... |
# Where the player data is any information desired on a player,
# and the various `mu_??` are the force of transition in this
# multi-state model:
#   ▗▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▖
#   ▐                   Healthy (0)               ▌
#   ▝▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▘
#         ▲                  ▲              |
#         |                  |              |
#         ▼                  ▼              ▼
# ▗▄▄▄▄▄▄▄▄▄▄▄▄▄▄▖    ▗▄▄▄▄▄▄▄▄▄▄▄▄▄▖ ▗▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▖
# ▐ Short injury ▌    ▐ Long injury ▌ ▐ Season-ending injury ▌
# ▐     (1)      ▌    ▐     (2)     ▌ ▐         (3)          ▌
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
SHORT_THRESHOLD=3

# Threshold of missed games at end of season to dictate as season-ending injury
LONG_THRESHOLD=20

# Get data from SQL database
conn <- dbConnect(RSQLite::SQLite(), "../bball_db")
player_games_raw <- dbReadTable(conn, "player_games")
player_info_raw <- dbReadTable(conn, "player_info")
game_info_raw <- dbReadTable(conn, "game_info")
dbDisconnect(conn)

# Make the date column into a numeric value
game_info <- game_info_raw |>
  within({
    Date <- Date |> as.Date("%b %d, %Y") |> as.numeric()
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
    return(NULL) # Early exit
  }

  rows <- g_data_raw |>
    with(
      (Season == season) &
        (Home_Team_ID %in% teams | Away_Team_ID %in% teams)
    )
  g_data <- g_data_raw[rows, ]
  merge(g_data, p_data, by = c("Game_ID", "Season"), all.x = TRUE) |>
    (\(df) df[order(df$Date), ])() |> # Guarantee the proper order
    (\(df) { # Filter out unneeded rows
       last_team <- df$Team_ID[!is.na(df$Team_ID)][1]
       keep <- logical()
       for (i in seq_along(df$Seconds)) {
         if (!last_team %in% c(df[i, "Home_Team_ID"], df[i, "Away_Team_ID"])) {
           if (!is.na(df[i, "Seconds"])) {
             last_team <- df[i, "Team_ID"]
           } else {
             keep[i] <- FALSE
             next
           }
         }
         keep[i] <- TRUE
       }
       df[keep, ]
    })() |>
    within({ # Dictate states
      State <- length(Seconds) |> numeric()
      Seconds[is.na(Seconds)] <- 0
      for (i in seq_along(Seconds) |> rev()) {
        if (Seconds[i] > 0) {
          State[i] <- 0
        } else if (i != length(Seconds) & State[i + 1] != 0) {
          State[i] <- State[i + 1] # Copy previous if needed
        } else if (sum(Seconds[max(0, i - SHORT_THRESHOLD):i] > 0) > 0) {
          State[i] <- 1 # Short-term if under threshold
        } else if (i == length(Seconds) &
                   (sum(Seconds[max(0, i - LONG_THRESHOLD):i] > 0) > 0)) {
          State[i] <- 3 # Season-ending if at the end and over threshold
        } else {
          State[i] <- 2 # Otherwise, long-term
        }
      }
      rm(i)
    })
}
