# Libraries
library(tidyverse) |> suppressMessages()
library(RSQLite)
library(randomForest) |> suppressMessages()

# Add custom functions
source("functions.R")

# Get data from SQL database
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

# Get the transitions table
transitions <- read_csv("transitions-3.csv") %>%
  mutate(
    Season = Season - 1 # Adjust season so we are looking at upcoming season
  )

# Arrange game data into season totals
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
    Seconds_lag_three = lag(Seconds, n = 2, default = 0, order_by = Season)
  ) %>%
    select(!c(
      Games,
      Injured
    ))
  

# Merge Data and perform final feature engineering
data <- transitions %>%
  inner_join(player_info, by = "Player_ID") %>%
  inner_join(season_totals, by = c("Player_ID", "Season")) %>%
  inner_join(
    team_info,
    by = c("Team_ID", "Season"),
    suffix = c("", "_team")
  ) %>%
  group_by(Season) %>%
  top_n(182, Fantasy_points) %>% # 182 corresponds to a 14 team league
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
  ))

# Show how many observations are available for each outcome variable
for (col in transitions[-c(1, 2)] %>% colnames()) {
  na <- data[[col]] |> is.na()
  z <- data[[col]] == 0
  x <- nrow(data) - sum(na | z)
  paste(col, x, sep = ": ") |> paste("\n") |> cat()
}

# Split data into train and test sets
train <- data %>%
  filter(Season < 2023)
test <- data %>%
  filter(Season >= 2023)

# Train a random forest model as a baseline
response_indices <- 2:16
forests <- list()
i <- 1
for (col in train[response_indices] %>% colnames()) {
  # Filter data for model
  df <- train[-response_indices[-i]] %>%
    drop_na(all_of(col))

  # Make the model
  formula <- paste(col, "~", ".") %>%
    as.formula()
  model <- randomForest(formula, data = df)

  # Add it to the list of models
  forests[[col]] <- model

  # Iterate to next column integer
  i <- i + 1
}

# Train models for all the force of transition values:
models <- list()
i <- 1
for (col in train[response_indices] %>% colnames()) {
  # Filter data for model
  df <- train[-response_indices[-i]] %>%
    drop_na(all_of(col))

  # Make the basic models
  full_formula <- paste(col, "~", ".") %>%
    as.formula()
  full_model <- lm(full_formula, data = df)
  base_formula <- paste(col, "~", "1") %>%
    as.formula()
  base_model <- lm(base_formula, data = df)

  # Stepwise variable selection
  refined_model <- step(
    full_model,
    direction = "both",
    scope = list(lower = base_model, upper = full_model),
    k = log(nrow(train))
  )

  vars <- refined_model$call$formula %>%
    as.character() %>%
    .[[3]]

  # Add to the model list
  models[[col]] <- list(
    name = col,
    full = full_model,
    refined = refined_model,
    selected_vars = vars
  )

  # Iterate to next column integer
  i <- i + 1
}

# Now we'll compare these to the random forest models
model_comparison <- tibble(
  variable = character(),
  random_forest = numeric(),
  full_linear = numeric(),
  selected_linear = numeric()
)
i <- 1
for (col in train[response_indices] %>% colnames()) {
  # Filter data for model
  df <- train[-response_indices[-i]] %>%
    drop_na(all_of(col))

  # Make predictions
  forest_predictions <- predict(
    forests[[col]],
    newdata = df
  )
  forest_rmse <- (forest_predictions - df[[col]])^2 %>%
    mean() %>%
    sqrt()
  full_predictions <- predict(
    models[[col]]$full,
    newdata = df
  )
  full_rmse <- (full_predictions - df[[col]])^2 %>%
    mean() %>%
    sqrt()
  selected_predictions <- predict(
    models[[col]]$refined,
    newdata = df
  )
  selected_rmse <- (selected_predictions - df[[col]])^2 %>%
    mean() %>%
    sqrt()

  # Save to the dataframe
  model_comparison <- model_comparison %>%
    add_row(
      variable = col,
      random_forest = forest_rmse,
      full_linear = full_rmse,
      selected_linear = selected_rmse
    )

  # Iterate to next column integer
  i <- i + 1
}
# # A tibble: 15 × 4
#    variable       random_forest full_linear selected_linear
#    <chr>                  <dbl>       <dbl>           <dbl>
#  1 mu_hs               1.11e+10    2.24e+10        2.26e+10
#  2 mu_hl             Inf         Inf             Inf
#  3 mu_hS               6.99e+52    8.51e+52        9.75e+52
#  4 mu_sh             Inf         Inf             Inf
#  5 mu_ls               3.32e+18    7.99e+18        8.34e+18
#  6 mu_hs_estimate      5.04e- 3    1.15e- 2        1.16e- 2
#  7 mu_hl_estimate      3.59e- 3    7.59e- 3        7.73e- 3
#  8 mu_hS_estimate      2.52e- 2    4.45e- 2        4.69e- 2
#  9 mu_sh_estimate      8.53e- 2    1.97e- 1        1.98e- 1
# 10 mu_ls_estimate      1.06e- 1    2.34e- 1        2.36e- 1
# 11 mu_hs_approx        1.17e- 2    2.67e- 2        2.68e- 2
# 12 mu_hl_approx        7.22e- 3    1.47e- 2        1.47e- 2
# 13 mu_hS_approx        1.13e- 2    2.25e- 2        2.27e- 2
# 14 mu_sh_approx        1.40e- 1    3.36e- 1        3.39e- 1
# 15 mu_ls_approx        1.02e- 1    2.39e- 1        2.47e- 1

# These models seem to have a very hard time explaining much variation at all.
# The linear models don't perform much worse than the random forest, and they
# all had an R^2 less than 0.07, which needs to be more to be useful. However,
# it may be interesting to see how it does with a transformation of the response
# variable or using a logistic regression. For the time being, I'll just take
# note of what variables were commonly selected in the various models.
for (item in models) {
  name <- item$name
  vars <- item$selected_vars

  paste(name, ":", vars, "\n") %>%
    cat()
}
# mu_hs : Assists
# mu_hl : *Ignored*
# mu_hS : Draft_Year
# mu_sh : *Ignored*
# mu_ls : 1
# mu_hs_estimate : Season + Points + Games_played + Seconds_lag_two + Age
# mu_hl_estimate : Draft_Year
# mu_hS_estimate : 1
# mu_sh_estimate : Seconds_lag_two + Age + Seconds
# mu_ls_estimate : Assists + Turnovers
# mu_hs_approx : Season + Points + Games_played + Season_start + Seconds_lag_two + Age
# mu_hl_approx : Season + Games_played
# mu_hS_approx : Games_played
# mu_sh_approx : Season + Experience
# mu_ls_approx : 1

# Likely, the best next step if I decide would be to attempt to fully model
# the markov chain rather than do this pseudo modeling.
