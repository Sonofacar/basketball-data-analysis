# Script that simply contains some useful functions.
# Run in other scripts as:
# `source("functions.R")`

##################
# Advanced Stats #
##################

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
  pts = 0,
  threepm = 0,
  fga = 0,
  fgm = 0,
  fta = 0,
  ftm = 0,
  reb = 0,
  ast = 0,
  stl = 0,
  blk = 0,
  tov = 0,
  point_mapping = list()
) {
  # Check for correct inputs
  numeric_check(
    pts,
    threepm,
    fga,
    fgm,
    fta,
    ftm,
    reb,
    ast,
    stl,
    blk,
    tov
  )
  list_check(point_mapping)

  # Define default point structure and add custom changes
  points <- list(
    pts = 1,
    threepm = 1,
    fga = -1,
    fgm = 2,
    fta = -1,
    ftm = 1,
    reb = 1,
    ast = 2,
    stl = 4,
    blk = 4,
    tov = -2
  ) |>
    modifyList(point_mapping) |>
    pull_coefficient()

  (
    pts * points("pts") +
      threepm * points("threepm") +
      fga * points("fga") +
      fgm * points("fgm") +
      fta * points("fta") +
      ftm * points("ftm") +
      reb * points("reb") +
      ast * points("ast") +
      stl * points("stl") +
      blk * points("blk") +
      tov * points("tov")
  )
}

# Team possession estimation
possessions_team_simple <- function(
  fga = 0,
  fta = 0,
  oreb = 0,
  tov = 0,
  adjustment = list()
) {
  # Check if input is valid
  numeric_check(fga, fta, oreb, tov)
  list_check(adjustment)

  adjust <- list(
    fga = 0.96,
    fta = 0.44
  ) |>
    modifyList(adjustment) |>
    pull_coefficient()

  (
    fga * adjust("fga") +
      fta * adjust("fta") +
      tov -
      oreb
  )
}

# More precise, but more complex calculation of possessions
possessions_team <- function(
  fga = 0,
  fg = 0,
  fta = 0,
  oreb = 0,
  tov = 0,
  o_dreb = 0,
  adjustment = list()
) {
  # Check for valid inputs
  numeric_check(
    fga,
    fg,
    fta,
    oreb,
    tov,
    o_dreb
  )
  list_check(adjustment)

  # If these are zero, we won't be able to compute
  stopifnot((oreb + o_dreb) != 0)

  # Pull default values
  adjust <- list(
    fta = 0.4,
    reb = 1.07
  ) |>
    modifyList(adjustment) |>
    pull_coefficient()

  fga +
    fta * adjust("fta")
  (oreb / (oreb + o_dreb)) *
    adjust("reb") *
    (fga - fg) +
    tov
}

# Meta function that averages takes calculation for both teams and averages it
# out to be more precise.
possessions_team_precise <- function(
  fga = 0,
  fg = 0,
  fta = 0,
  oreb = 0,
  dreb = 0,
  tov = 0,
  o_fga = 0,
  o_fg = 0,
  o_fta = 0,
  o_oreb = 0,
  o_dreb = 0,
  o_tov = 0,
  adjustment = list()
) {
  # We don't need to check for input validity, but we do need to pass
  # adjustment list.
  mapply(
    mean,
    possessions_team(fga, fg, fta, oreb, tov, o_dreb, adjustment),
    possessions_team(o_fga, o_fg, o_fta, o_oreb, o_tov, dreb, adjustment)
  )
}

# Because there are multiple possession functions available, pace will need to
# be given the possession value from the desired form.
pace <- function(min = 0, poss = 0) {
  # Check for valid input
  numeric_check(min, poss)

  48 * 5 * poss / min
}

# Usage
usage <- function(
  mp = 0,
  fga = 0,
  fta = 0,
  tov = 0,
  t_mp = 0,
  t_fga = 0,
  t_fta = 0,
  t_tov = 0,
  adjustment = list()
) {
  # Check for valid input
  numeric_check(
    mp,
    fga,
    fta,
    tov,
    t_mp,
    t_fga,
    t_fta,
    t_tov
  )
  list_check(adjustment)

  # Pull default values
  adjust <- list(
    fta = 0.4,
    reb = 1.07
  ) |>
    modifyList(adjustment) |>
    pull_coefficient()

  # If these are zero, we won't be able to compute
  stopifnot((t_fga + t_fta * adjust("fta") + t_tov) != 0)

  (
    (
      fga +
        fta * adjust("fta") +
        tov
    ) *
      (
        t_mp /
          (mp * 5)
      ) /
      (
        t_fga +
          t_fta * adjust("fta") +
          t_tov
      )
  ) |>
    (\(.) (is.na(.) | is.nan(.)) |> ifelse(0, .))() # replace NA values with 0
}

# Pythagorean Wins, used to estimate final win percentage
pythagorean_wins <- function(t_pts = 0, o_pts = 0, adjustment = list()) {
  # Check for valid input
  numeric_check(t_pts, o_pts)
  list_check(adjustment)

  # Pull default values
  adjust <- list(exp = 14) |>
    modifyList(adjustment) |>
    pull_coefficient()

  t_pts ^ adjust("exp") /
    (
      t_pts ^ adjust("exp") +
        o_pts ^ adjust("exp")
    )
}


#######################
# Feature Engineering #
#######################

# The following function are designed to imitate a moving average from time
# series analysis and *must* be used properly. They are designed to be used
# with data that is arranged in descending order according to time, meaning the
# most recent time is first and the oldest observation is last.

# EWMA (exponentially weighted moving average), used for data manipulation
point_ewma <- function(x, n = length(x), weight = 2 / (n + 1)) {
  x[!is.na(x)] |>
    (\(v) {
      min(length(v), n) |>
        (\(m) {
          if ((m - 1) > 0) {
            weight * v[1] + (1 - weight) * point_ewma(v[-1], m - 1, weight)
          } else {
            weight * v[1]
          }
        })()
    })()
}

ewma <- function(x, n, weight = 2 / (n + 1), by = c()) {
  # Determine if we need to sort values
  (\(v) {
    if (length(v) == length(by)) {
      v[order(by, decreasing = TRUE)]
    } else {
      x
    }
  })(x) |>
    (\(v) {
      sapply(
        seq_along(v) |> rev(), # We look at the values in descending order
        \(i) point_ewma(v[i:(i + n - 1)], n, weight)
      ) |>
        rev()
    })() |>
    (\(v) {
      if (length(v) == length(by)) {
        v[seq_along(v)[order(by, decreasing = TRUE)] |> order()]
      } else {
        v
      }
    })()
}

# Apply a function to the past n occurances of the provided vector
roll <- function(x, n, func, by = c()) {
  # Sort values in order of time
  (\(v) {
    if (length(v) == length(by)) {
      v[order(by, decreasing = TRUE)]
    } else {
      x
    }
  })(x) |>
    (\(v) {
      sapply(
        seq_along(v),
        \(i) v[i:(i + n - 1)]
      ) |>
        apply(2, \(w) mean(w[!is.na(w)]))
    })() |>
    # Undo sorting of values by time
    (\(v) {
      if (length(v) == length(by)) {
        v[seq_along(v)[order(by, decreasing = TRUE)] |> order()]
      } else {
        v
      }
    })() |>
    # Replace all NAs with 0
    (\(v) is.na(v) |> ifelse(0, v))()
}
