# Script that simply contains some useful functions.
# Run in other scripts as:
# `source("functions.R")`

# Utility function to pull a coefficient from a list
pull_coefficient <- function(l = list()) {
  \(column) l[[column]]
}

# Utility function to check inputs that should be numbers
numeric_check <- function(...) {
  c(...) |>
    is.numeric() |>
    stopifnot()
}

# Utility function to check that input is a list
list_check <- function(l) {
  l |>
    is.list() |>
    stopifnot()
}

# Fantasy points following the ESPN base line points system
fantasy_points <- function(
  PTS = 0,
  threePM = 0,
  FGA = 0,
  FGM = 0,
  FTA = 0,
  FTM = 0,
  REB = 0,
  AST = 0,
  STL = 0,
  BLK = 0,
  TOV = 0,
  point_mapping = list()
) {
  # Check for correct inputs
  numeric_check(
    PTS,
    threePM,
    FGA,
    FGM,
    FTA,
    FTM,
    REB,
    AST,
    STL,
    BLK,
    TOV
  )
  list_check(point_mapping)

  # Define default point structure and add custom changes
  points <- list(
    PTS = 1,
    threePM = 1,
    FGA = -1,
    FGM = 2,
    FTA = -1,
    FTM = 1,
    REB = 1,
    AST = 2,
    STL = 4,
    BLK = 4,
    TOV = -2
  ) |>
    modifyList(point_mapping) |>
    pull_coefficient()

  (
    PTS * points("PTS") +
    threePM * points("threePM") +
    FGA * points("FGA") +
    FGM * points("FGM") +
    FTA * points("FTA") +
    FTM * points("FTM") +
    REB * points("REB") +
    AST * points("AST") +
    STL * points("STL") +
    BLK * points("BLK") +
    TOV * points("TOV")
  )
}

# Team possession estimation
possessions_team_simple <- function(
  FGA = 0,
  FTA = 0,
  OREB = 0,
  TOV = 0,
  adjustment = list()
) {
  # Check if input is valid
  numeric_check(FGA, FTA, OREB, TOV)
  list_check(adjustment)

  adjust <- list(
    FGA = 0.96,
    FTA = 0.44
  ) |>
    modifyList(adjustment) |>
    pull_coefficient()

  (
    FGA * adjust("FGA") +
    FTA * adjust("FTA") +
    TOV -
    OREB
  )
}

# More precise, but more complex calculation of possessions
possessions_team <- function(
  FGA = 0,
  FG = 0,
  FTA = 0,
  OREB = 0,
  TOV = 0,
  O_DREB = 0,
  adjustment = list()
) {
  # Check for valid inputs
  numeric_check(
    FGA,
    FG,
    FTA,
    OREB,
    TOV,
    O_DREB
  )
  list_check(adjustment)

  # If these are zero, we won't be able to compute
  (
    (OREB + O_DREB) != 0
  ) |>
    stopifnot()

  # Pull default values
  adjust <- list(
    FTA = 0.4,
    REB = 1.07
  ) |>
    modifyList(adjustment) |>
    pull_coefficient()

  FGA +
  FTA * adjust("FTA")
  (OREB/(OREB + O_DREB)) * adjust("REB") *
  (FGA - FG) +
  TOV
}

# Meta function that averages takes calculation for both teams and averages it
# out to be more precise.
possessions_team_precise <- function(
  FGA = 0,
  FG = 0,
  FTA = 0,
  OREB = 0,
  DREB = 0,
  TOV = 0,
  O_FGA = 0,
  O_FG = 0,
  O_FTA = 0,
  O_OREB = 0,
  O_DREB = 0,
  O_TOV = 0,
  adjustment = list()
) {
  # We don't need to check for input validity, but we do need to pass
  # adjustment list.
  mapply(
    mean,
    possessions_team(FGA, FG, FTA, OREB, TOV, O_DREB, adjustment),
    possessions_team(O_FGA, O_FG, O_FTA, O_OREB, O_TOV, DREB, adjustment)
  )
}
