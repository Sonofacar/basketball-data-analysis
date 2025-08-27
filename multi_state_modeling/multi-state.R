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
library(tidyverse) |> suppressMessages()
library(RSQLite)
library(msm)

# Threshold to split short and long injuries at
# ADJUST TO CHANGE RATIO OF SHORT/LONG-TERM INJURIES
THRESHOLD=3

# Functions used to compute force of transitions
discrete_to_continuous_safe <- function(subtotal, total) {
  if (total > 0) {
    if (subtotal == total) {
      return(NA)
    } else if (subtotal > 0) {
      return(-log(1 - subtotal / total))
    } else {
      return(0)
    }
  } else {
    return(NA)
  }
}

categorize_injuries <- function(i_vect, index, threshold) {
  if (i_vect[index] == 0) {
    return("h")
  } else {
    short <- sum(i_vect[index:(index + threshold)] == 0)
    long <- sum(i_vect[index:length(i_vect)] == 0)
    if (short > 0 | is.na(short)) {
      return("s")
    } else if (long > 0) {
      return ("l")
    } else {
      return ("S")
    }
  }
}

arbitrary_categorize_numeric <- function(i_vect, threshold) {
  output <- list(
    healthy = 0,
    short = 0,
    long = 0,
    ending = 0,
    Q = matrix(nrow = 4, ncol = 4),
    states = c()
  )

  seq <- 1
  prev <- 1
  for (i in 1:length(i_vect)) {
    if (i_vect[i] == 0) {
      # Healthy
      if (output$healthy == 0) {
        output$Q[seq, ] <- 0
        output$Q[, seq] <- 0
        output$healthy <- seq
        seq <- seq + 1
      }
      output$states[i] <- output$healthy
      current <- output$healthy
    } else {
      short <- sum(i_vect[i:(i + threshold)] == 0)
      long <- sum(i_vect[i:length(i_vect)] == 0)
      if (short > 0 | is.na(short)) {
        # Short-term injury
        if (output$short == 0) {
          output$Q[seq, ] <- 0
          output$Q[, seq] <- 0
          output$short <- seq
          seq <- seq + 1
        }
        output$states[i] <- output$short
        current <- output$short
      } else if (long > 0) {
        # Long-term injury
        if (output$long == 0) {
          output$Q[seq, ] <- 0
          output$Q[, seq] <- 0
          output$long <- seq
          seq <- seq + 1
        }
        output$states[i] <- output$long
        current <- output$long
      } else {
        # Season-ending injury
        if (output$ending == 0) {
          output$Q[seq, ] <- 0
          output$Q[, seq] <- 0
          output$ending <- seq
          seq <- seq + 1
        }
        output$states[i] <- output$ending
        current <- output$ending
      }
    }

    # Check if this is a transition
    if (prev != current) {
      output$Q[prev, current] <- 1
    }
    prev <- current
  }

  return(output)
}

compute_transitions_precise <- function(df, threshold) {
  output <- list(
    mu_hs = NA,
    mu_hs_estimate = NA,
    mu_hl = NA,
    mu_hl_estimate = NA,
    mu_hS = NA,
    mu_hS_estimate = NA,
    mu_sh = NA,
    mu_sh_estimate = NA,
    mu_ls = NA,
    mu_ls_estimate = NA
  )

  info <- arbitrary_categorize_numeric(df$Injured, threshold)
  id <- rep(1, length(info$states))

  data <- tibble(
    time = df$Date,
    state = info$states
  )

  rows <- !is.na(info$Q) %>%
    rowSums()
  cols <- !is.na(info$Q) %>%
    colSums()
  Q <- info$Q[rows, cols]

  # Check if any transitions occur at all.
  # If none, return default values.
  if (sum(rows) == 1 & sum(cols) == 1) {
    return(output)
  }

  # Try to make a model and save real values if possible
  qmat <- tryCatch(
    {
      msm(state ~ time, data = data, qmatrix = Q) %>%
        qmatrix.msm()
    },
    error = \(e) NA
  )

  output$mu_hs <- tryCatch(
    qmat[info$healthy, info$short][["estimate"]],
    error = \(e) NA
  )
  output$mu_hl <- tryCatch(
    qmat[info$healthy, info$long][["estimate"]],
    error = \(e) NA
  )
  output$mu_hS <- tryCatch(
    qmat[info$healthy, info$ending][["estimate"]],
    error = \(e) NA
  )
  output$mu_sh <- tryCatch(
    qmat[info$short, info$healthy][["estimate"]],
    error = \(e) NA
  )
  output$mu_ls <- tryCatch(
    qmat[info$long, info$short][["estimate"]],
    error = \(e) NA
  )

  qmat_estimate <- crudeinits.msm(
      state ~ time,
      data = data,
      qmatrix = Q
    ) %>%
      suppressWarnings()

  tmp <- qmat_estimate[info$healthy, info$short]
  if (length(tmp) == 1) {
    output$mu_hs_estimate <- tmp
  } else {
    output$mu_hs_estimate <- NA
  }

  tmp <- qmat_estimate[info$healthy, info$long]
  if (length(tmp) == 1) {
    output$mu_hl_estimate <- tmp
  } else {
    output$mu_hl_estimate <- NA
  }

  tmp <- qmat_estimate[info$healthy, info$ending]
  if (length(tmp) == 1) {
    output$mu_hS_estimate <- tmp
  } else {
    output$mu_hS_estimate <- NA
  }

  tmp <- qmat_estimate[info$short, info$healthy]
  if (length(tmp) == 1) {
    output$mu_sh_estimate <- tmp
  } else {
    output$mu_sh_estimate <- NA
  }

  tmp <- qmat_estimate[info$long, info$short]
  if (length(tmp) == 1) {
    output$mu_ls_estimate <- tmp
  } else {
    output$mu_ls_estimate <- NA
  }

  return(output)
}

compute_transitions <- function(df, threshold) {
  c <- 1
  prev <- categorize_injuries(df$Injured, c, threshold)
  h <- 0
  s <- 0
  l <- 0
  hs <- 0
  hl <- 0
  hS <- 0
  sh <- 0
  ls <- 0
  for (i in seq(length(df$Injured))[-1]) {
    current <- categorize_injuries(df$Injured, i, threshold)
    if (prev == "h") {
      h <- h + 1
      if (current == "h") {
      } else if (current == "s") {
        hs <- hs + 1
      } else if (current == "l") {
        hl <- hl + 1
      } else {
        hS <- hS + 1
      }
    } else if (prev == "s") {
      s <- s + 1
      if (current == "h") { sh <- sh + 1 }
    } else if (prev == "l") {
      l <- l + 1
      if (current == "s") { ls <- ls + 1 }
    }
    prev <- current
  }
  list(mu_hs = discrete_to_continuous_safe(hs, h),
       mu_hl = discrete_to_continuous_safe(hl, h),
       mu_hS = discrete_to_continuous_safe(hS, h),
       mu_sh = discrete_to_continuous_safe(sh, s),
       mu_ls = discrete_to_continuous_safe(ls, l)) %>%
  return()
}

# Get data from SQL database
conn <- dbConnect(RSQLite::SQLite(), "../bball_db")
player_games <- dbReadTable(conn, "player_games") %>% tibble()
player_info <- dbReadTable(conn, "player_info") %>% tibble()
game_info <- dbReadTable(conn, "game_info") %>% tibble()
dbDisconnect(conn)

# Make the date column into a numeric value
game_info <- game_info %>%
  mutate(Date = Date %>% as.Date("%b %d, %Y") %>% as.numeric())

# Setting up the output table
output <- tibble(
  Player_ID = integer(),
  Season = integer(),
  mu_hs = double(),
  mu_hl = double(),
  mu_hS = double(),
  mu_sh = double(),
  mu_ls = double(),
  mu_hs_estimate = double(),
  mu_hl_estimate = double(),
  mu_hS_estimate = double(),
  mu_sh_estimate = double(),
  mu_ls_estimate = double(),
  mu_hs_approx = double(),
  mu_hl_approx = double(),
  mu_hS_approx = double(),
  mu_sh_approx = double(),
  mu_ls_approx = double()
)

# I need to perform this action for each player each season:
for (id in unique(player_info$Player_ID)) {
  tmp_player <- player_games %>% filter(Player_ID == id)
  for (season in unique(tmp_player$Season)) {
    tmp_player_season <- tmp_player %>% filter(Season == season)
    panel_data <- inner_join(
      tmp_player_season,
      game_info[c("Game_ID", "Date")],
      by = "Game_ID"
    ) %>%
      mutate(Date = Date - min(Date))

    # Now we find the force of transition
    approx <- compute_transitions(panel_data, THRESHOLD)
    transitions <- compute_transitions_precise(panel_data, THRESHOLD)
    output <- output %>% 
      add_row(
        Player_ID = id,
        Season = season,
        mu_hs = transitions$mu_hs,
        mu_hl = transitions$mu_hl,
        mu_hS = transitions$mu_hS,
        mu_sh = transitions$mu_sh,
        mu_ls = transitions$mu_ls,
        mu_hs_estimate = transitions$mu_hs_estimate,
        mu_hl_estimate = transitions$mu_hl_estimate,
        mu_hS_estimate = transitions$mu_hS_estimate,
        mu_sh_estimate = transitions$mu_sh_estimate,
        mu_ls_estimate = transitions$mu_ls_estimate,
        mu_hs_approx = approx$mu_hs,
        mu_hl_approx = approx$mu_hl,
        mu_hS_approx = approx$mu_hS,
        mu_sh_approx = approx$mu_sh,
        mu_ls_approx = approx$mu_ls
      )
  }
}

write_csv(output, "transitions.csv")
