#!/usr/bin/Rscript

# This script needs to take data and format it as follows:
# | ...Player Data... | mu_hs | mu_hl | mu_hS | ... |
# | ................. | ..... | ..... | ..... | ... |
# Where the player data is any information desired on a player,
# and the various `mu_??` are the force of transition in this
# multi-state model:
#   ▗▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▖
#   ▐                   Healthy (1)               ▌
#   ▝▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▘
#         ▲                  ▲              |
#         |                  |              |
#         ▼                  ▼              ▼
# ▗▄▄▄▄▄▄▄▄▄▄▄▄▄▄▖    ▗▄▄▄▄▄▄▄▄▄▄▄▄▄▖ ▗▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▖
# ▐ Short injury ▌    ▐ Long injury ▌ ▐ Season-ending injury ▌
# ▐     (2)      ▌    ▐     (3)     ▌ ▐         (4)          ▌
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

# Add custom functions
source("functions.R")

# Threshold to split short and long injuries at
# ADJUST TO CHANGE RATIO OF SHORT/LONG-TERM INJURIES
SHORT_THRESHOLD=3

# Threshold of missed games at end of season to dictate as season-ending injury
LONG_THRESHOLD=20

# Get data from SQL database
conn <- dbConnect(RSQLite::SQLite(), "../bball_db")
team_games_raw <- dbReadTable(conn, "team_games")
player_games_raw <- dbReadTable(conn, "player_games")
player_info_raw <- dbReadTable(conn, "player_info")
game_info_raw <- dbReadTable(conn, "game_info")
dbDisconnect(conn)

# Make the date column into a numeric value
game_info <- game_info_raw |>
  within({
    Date <- Date |> as.Date("%b %d, %Y") |> as.numeric()
  })
player_games <- player_games_raw
player_info <- player_info_raw |>
  within({
    Birthday <- Birthday |> as.Date("%b %d, %Y") |> as.numeric()
    Debut_Date <- Debut_Date |> as.Date("%b %d, %Y") |> as.numeric()
  })
team_games <- team_games_raw
opponent_games <- team_games_raw |>
  within({
    Opponent_ID <- Team_ID
    rm(Team_ID)
  })

#####################
# Utility functions #
#####################

get_player_states <- function(player_id, season, p_data_raw, g_data_raw) {
  rows <- with(p_data_raw, (Player_ID == player_id) & (Season == season))
  p_data <- p_data_raw[rows, ] |>
    within({
      rm(Threes, Three_Attempts, Field_Goals, Field_Goal_Attempts, Freethrows,
         Freethrow_Attempts, Offensive_Rebounds, Defensive_Rebounds, Assists,
         Steals, Blocks, Turnovers, Fouls, Points, PM, Win, Home, Opponent_ID)
    })
  teams <- unique(p_data[["Team_ID"]])

  if (nrow(p_data) == 0) {
    return(NULL) # Early exit
  }

  rows <- g_data_raw |>
    with(
      (Season == season) &
        (Home_Team_ID %in% teams | Away_Team_ID %in% teams)
    )
  g_data <- g_data_raw[rows, ] |>
    within({
      rm(Home_Team_Name, Away_Team_Name, Location, Duration, Attendance,
         Referee_ID1, Referee_ID2, Referee_ID3)
    })
  merge(g_data, p_data, by = c("Game_ID", "Season"), all.x = TRUE) |>
    (\(df) df[order(df$Date), ])() |> # Guarantee the proper order
    (\(df) { # Filter out unneeded rows
       last_team <- df$Team_ID[!is.na(df$Team_ID)][1]
       last_date <- 0
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
    (\(df) df[order(df$Seconds), ])() |>    # Move all played games to top
    (\(df) df[!duplicated(df$Date), ])() |> # Drop all duplicated rows
    (\(df) df[order(df$Date), ])() |>       # Set back to order
    within({ # Dictate states
      State <- 0
      Seconds[is.na(Seconds)] <- 0
      for (i in seq_along(Seconds) |> rev()) {
        if (Seconds[i] > 0) {
          State[i] <- 1
          next
        } else if (i != length(Seconds) & State[i + 1] != 1) {
          State[i] <- State[i + 1] # Copy next state if needed
          State[i + 1] <- ifelse(State[i + 1] == 4, NA, State[i + 1])
        } else if (any(Seconds[max(0, i - SHORT_THRESHOLD):i] > 0)) {
          State[i] <- 2 # Short-term if under threshold
        } else if (i == length(Seconds) &
                   any(Seconds[max(0, i - LONG_THRESHOLD):i] > 0)) {
          State[i] <- 4 # Season-ending if at the end and over threshold
        } else {
          State[i] <- 3 # Otherwise, long-term
        }
        Team_ID[i] <- Team_ID[i + 1] # Team ID is always their next team
      }
      rm(i)
    }) |>
    (\(df) df[!is.na(df$State), ])() |>
    (\(df) df[df$State != 0, ])() |>
    within({ # Clean up team identification
      Team_ID[State == 4] <- Team_ID[State == 1] |>
        unique() |>
        rev() |>
        (\(.) .[1])()
      Player_ID <- player_id
      Home <- (Team_ID == Home_Team_ID) & (!is.na(Team_ID))
      Away <- (Team_ID == Away_Team_ID) & (!is.na(Team_ID))
      Opponent_ID <- NA
      Opponent_ID[Away] <- Home_Team_ID[Away]
      Opponent_ID[Home] <- Away_Team_ID[Home]
      rm(Home_Team_ID, Away_Team_ID, Home, Away)
    })
}


#################
# Cleaning Data #
#################

data_raw <- data.frame()
for (id in unique(player_info[["Player_ID"]])) {
  tmp_games_df <- player_games[player_games$Player_ID == id, ]
  for (year in unique(tmp_games_df[["Season"]])) {
    data_raw <- get_player_states(id, year, tmp_games_df, game_info) |>
      within({
        ID <- paste(id, year, sep = "_")
        Player_ID <- id
        Season <- year
      }) |>
      (\(df) { # drop all rows if only one row
         if (nrow(df) > 1) df else df[-1, ]
      })() |>
      rbind(data_raw, make.row.names = FALSE)
  }
}

data <- data_raw |>
  (\(df) df[c(1, 8, 9, 11, 10, 12, 3, 2, 4, 5, 6, 7)])() |>
  merge(player_info[c(2, 3, 6, 8:10)], by = "Player_ID", all.x = TRUE) |>
  merge(player_games[2:20], by = c("Player_ID", "Game_ID"), all.x = TRUE) |>
  merge(
    team_games[c(1:16, 18, 20)],
    by = c("Team_ID", "Game_ID"),
    all.x = TRUE,
    suffixes = c("", "_team")
  ) |>
  merge(
    opponent_games[c(1:15, 18, 20)],
    by = c("Opponent_ID", "Game_ID"),
    all.x = TRUE,
    suffixes = c("", "_opponent")
  ) |>
  (\(df) df[order(df$Date), ])() |> # Order by ID -> Date
  (\(df) df[order(df$ID), ])() |>
  within({ # Remove IDs after merging
    rm(Game_ID, Player_ID, Team_ID, Opponent_ID)
  })


##################
# Creating model #
##################

Q <- matrix(c(
    0, 1, 1, 1,
    1, 0, 0, 0,
    1, 0, 0, 0,
    0, 0, 0, 0
  ), byrow = TRUE, nrow = 4)
colnames(Q) <- rownames(Q) <- c("Healthy", "Short", "Long", "Season-end")

m <- msm(
  State ~ Date,
  data = data,
  subject = ID,
  qmatrix = Q,
  gen.inits = TRUE,
  control = list(fnscale = 50) # Raise value if running into overflow errors
)
