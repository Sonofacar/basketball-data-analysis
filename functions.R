# Script that simply contains some useful functions.
# Run in other scripts as:
# `source("functions.R")`

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
  c(
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
  ) |>
    is.numeric() |>
    stopifnot()
  point_mapping |>
    is.list() |>
    stopifnot()

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
    (\(l) (
      \(column) l[[column]])
    )()

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
