# Libraries
library(tidyverse) |> suppressMessages()
library(randomForest) |> suppressMessages()
library(glmnet) |> suppressMessages()
library(ggfortify)
library(car) |> suppressMessages()

# Add custom functions
source("functions.R")

# Read in data
source("clean_data.R")

# Save seconds data to use as response variable
response <- season_totals %>%
  rename(Seconds = Seconds_lag_one) %>%
  select(c(Seconds, Season, Player_ID)) %>%
  mutate(Season = Season - 1)

# Merge Data and perform final feature engineering
data <- season_totals %>%
  inner_join(player_info , by = c("Player_ID")) %>%
  inner_join(
    team_info,
    by = c("Team_ID", "Season"),
    suffix = c("", "_team")
  ) %>%
  inner_join(response, by = c("Player_ID", "Season")) %>%
  group_by(Player_ID) %>%
  mutate(
    Win_pct = Wins / (Wins + Losses),
    Age = (Season_start - Birthday) / 365,
    Experience = (Season_start - Debut_Date) / 365,
    is_2011 = (Season == 2011),
    is_2012 = (Season == 2012),
    rolling_games_sum_2 = roll(Games, 2, sum),
    rolling_games_sum_3 = roll(Games, 3, sum),
    rolling_games_sum_4 = roll(Games, 4, sum),
    rolling_games_sum_5 = roll(Games, 5, sum),
    ewma_games_2 = ewma(Games, 2),
    ewma_games_3 = ewma(Games, 3),
    ewma_games_4 = ewma(Games, 4),
    ewma_games_5 = ewma(Games, 5),
    ewma_2 = ewma(Seconds_lag_one, 2),
    ewma_2_lag_one = lag(ewma_2, n = 1, default = 0, order_by = Season),
    ewma_2_lag_two = lag(ewma_2, n = 2, default = 0, order_by = Season),
    ewma_2_lag_three = lag(ewma_2, n = 3, default = 0, order_by = Season),
    ewma_3 = ewma(Seconds_lag_one, 3),
    ewma_3_lag_one = lag(ewma_3, n = 1, default = 0, order_by = Season), 
    ewma_3_lag_two = lag(ewma_3, n = 2, default = 0, order_by = Season), 
    ewma_3_lag_three = lag(ewma_3, n = 3, default = 0, order_by = Season), 
    ewma_4 = ewma(Seconds_lag_one, 4),
    ewma_4_lag_one = lag(ewma_4, n = 1, default = 0, order_by = Season), 
    ewma_4_lag_two = lag(ewma_4, n = 2, default = 0, order_by = Season), 
    ewma_4_lag_three = lag(ewma_4, n = 3, default = 0, order_by = Season), 
    ewma_5 = ewma(Seconds_lag_one, 5),
    ewma_5_lag_one = lag(ewma_5, n = 1, default = 0, order_by = Season), 
    ewma_5_lag_two = lag(ewma_5, n = 2, default = 0, order_by = Season), 
    ewma_5_lag_three = lag(ewma_5, n = 3, default = 0, order_by = Season), 
    rolling_var_2 = roll(Seconds_lag_one, 2, var),
    rolling_var_2_lag_one = lag(rolling_var_2, n = 1, default = 0, order_by = Season),
    rolling_var_2_lag_two = lag(rolling_var_2, n = 2, default = 0, order_by = Season),
    rolling_var_2_lag_three = lag(rolling_var_2, n = 3, default = 0, order_by = Season),
    rolling_var_3 = roll(Seconds_lag_one, 3, var),
    rolling_var_3_lag_one = lag(rolling_var_3, n = 1, default = 0, order_by = Season),
    rolling_var_3_lag_two = lag(rolling_var_3, n = 2, default = 0, order_by = Season),
    rolling_var_3_lag_three = lag(rolling_var_3, n = 3, default = 0, order_by = Season),
    rolling_var_4 = roll(Seconds_lag_one, 4, var),
    rolling_var_4_lag_one = lag(rolling_var_4, n = 1, default = 0, order_by = Season),
    rolling_var_4_lag_two = lag(rolling_var_4, n = 2, default = 0, order_by = Season),
    rolling_var_4_lag_three = lag(rolling_var_4, n = 3, default = 0, order_by = Season),
    rolling_var_5 = roll(Seconds_lag_one, 5, var),
    rolling_var_5_lag_one = lag(rolling_var_5, n = 1, default = 0, order_by = Season),
    rolling_var_5_lag_two = lag(rolling_var_5, n = 2, default = 0, order_by = Season),
    rolling_var_5_lag_three = lag(rolling_var_5, n = 3, default = 0, order_by = Season),
    rolling_sd_2 = roll(Seconds_lag_one, 2, sd),
    rolling_sd_2_lag_one = lag(rolling_sd_2, n = 1, default = 0, order_by = Season),
    rolling_sd_2_lag_two = lag(rolling_sd_2, n = 2, default = 0, order_by = Season),
    rolling_sd_2_lag_three = lag(rolling_sd_2, n = 3, default = 0, order_by = Season),
    rolling_sd_3 = roll(Seconds_lag_one, 3, sd),
    rolling_sd_3_lag_one = lag(rolling_sd_3, n = 1, default = 0, order_by = Season),
    rolling_sd_3_lag_two = lag(rolling_sd_3, n = 2, default = 0, order_by = Season),
    rolling_sd_3_lag_three = lag(rolling_sd_3, n = 3, default = 0, order_by = Season),
    rolling_sd_4 = roll(Seconds_lag_one, 4, sd),
    rolling_sd_4_lag_one = lag(rolling_sd_4, n = 1, default = 0, order_by = Season),
    rolling_sd_4_lag_two = lag(rolling_sd_4, n = 2, default = 0, order_by = Season),
    rolling_sd_4_lag_three = lag(rolling_sd_4, n = 3, default = 0, order_by = Season),
    rolling_sd_5 = roll(Seconds_lag_one, 5, sd),
    rolling_sd_5_lag_one = lag(rolling_sd_5, n = 1, default = 0, order_by = Season),
    rolling_sd_5_lag_two = lag(rolling_sd_5, n = 2, default = 0, order_by = Season),
    rolling_sd_5_lag_three = lag(rolling_sd_5, n = 3, default = 0, order_by = Season)
  ) %>%
  ungroup(Player_ID) %>%
  select(!c(
    Player_ID,
    Team_ID,
    Season_start,
    Points,
    Wins,
    Losses,
    Birthday,
    Debut_Date,
    Fantasy_points
  )) %>%
  drop_na()

delta_data <- data %>%
  mutate(
    delta_rolling_games_sum_2 = rolling_games_sum_2 - rolling_games_sum_3,
    delta_rolling_games_sum_3 = rolling_games_sum_3 - rolling_games_sum_4,
    delta_rolling_games_sum_4 = rolling_games_sum_4 - rolling_games_sum_5,
    delta_ewma_games_2 = ewma_games_2 - ewma_games_3,
    delta_ewma_games_3 = ewma_games_3 - ewma_games_4,
    delta_ewma_games_4 = ewma_games_4 - ewma_games_5,
    delta_Seconds = Seconds - Seconds_lag_one,
    delta_Seconds_lag_one = Seconds_lag_one - Seconds_lag_two,
    delta_Seconds_lag_two = Seconds_lag_two - Seconds_lag_three,
    delta_Seconds_lag_three = Seconds_lag_three - Seconds_lag_four,
    delta_Seconds_lag_four = Seconds_lag_four - Seconds_lag_five,
    delta_Seconds_lag_five = Seconds_lag_five - Seconds_lag_six,
    delta_ewma_2 = ewma_2 - ewma_2_lag_one,
    delta_ewma_2_lag_one = ewma_2_lag_one - ewma_2_lag_two,
    delta_ewma_2_lag_two = ewma_2_lag_two - ewma_2_lag_three,
    delta_ewma_3 = ewma_3 - ewma_3_lag_one,
    delta_ewma_3_lag_one = ewma_3_lag_one - ewma_3_lag_two, 
    delta_ewma_3_lag_two = ewma_3_lag_two - ewma_3_lag_three, 
    delta_ewma_4 = ewma_4 - ewma_4_lag_one,
    delta_ewma_4_lag_one = ewma_4_lag_one - ewma_4_lag_two, 
    delta_ewma_4_lag_two = ewma_4_lag_two - ewma_4_lag_three, 
    delta_ewma_5 = ewma_5 - ewma_5_lag_one,
    delta_ewma_5_lag_one = ewma_5_lag_one - ewma_5_lag_two, 
    delta_ewma_5_lag_two = ewma_5_lag_two - ewma_5_lag_three, 
    delta_rolling_var_2 = rolling_var_2 - rolling_var_2_lag_one,
    delta_rolling_var_2_lag_one = rolling_var_2_lag_one - rolling_var_2_lag_two,
    delta_rolling_var_2_lag_two = rolling_var_2_lag_two - rolling_var_2_lag_three,
    delta_rolling_var_3 = rolling_var_3 - rolling_var_3_lag_one,
    delta_rolling_var_3_lag_one = rolling_var_3_lag_one - rolling_var_3_lag_two,
    delta_rolling_var_3_lag_two = rolling_var_3_lag_two - rolling_var_3_lag_three,
    delta_rolling_var_4 = rolling_var_4 - rolling_var_4_lag_one,
    delta_rolling_var_4_lag_one = rolling_var_4_lag_one - rolling_var_4_lag_two,
    delta_rolling_var_4_lag_two = rolling_var_4_lag_two - rolling_var_4_lag_three,
    delta_rolling_var_5 = rolling_var_5 - rolling_var_5_lag_one,
    delta_rolling_var_5_lag_one = rolling_var_5_lag_one - rolling_var_5_lag_two,
    delta_rolling_var_5_lag_two = rolling_var_5_lag_two - rolling_var_5_lag_three,
    delta_rolling_sd_2 = rolling_sd_2 - rolling_sd_2_lag_one,
    delta_rolling_sd_2_lag_one = rolling_sd_2_lag_one - rolling_sd_2_lag_two,
    delta_rolling_sd_2_lag_two = rolling_sd_2_lag_two - rolling_sd_2_lag_three,
    delta_rolling_sd_3 = rolling_sd_3 - rolling_sd_3_lag_one,
    delta_rolling_sd_3_lag_one = rolling_sd_3_lag_one - rolling_sd_3_lag_two,
    delta_rolling_sd_3_lag_two = rolling_sd_3_lag_two - rolling_sd_3_lag_three,
    delta_rolling_sd_4 = rolling_sd_4 - rolling_sd_4_lag_one,
    delta_rolling_sd_4_lag_one = rolling_sd_4_lag_one - rolling_sd_4_lag_two,
    delta_rolling_sd_4_lag_two = rolling_sd_4_lag_two - rolling_sd_4_lag_three,
    delta_rolling_sd_5 = rolling_sd_5 - rolling_sd_5_lag_one,
    delta_rolling_sd_5_lag_one = rolling_sd_5_lag_one - rolling_sd_5_lag_two,
    delta_rolling_sd_5_lag_two = rolling_sd_5_lag_two - rolling_sd_5_lag_three
  ) %>%
  select(!c(
    Seconds,
    Seconds_lag_one,
    Seconds_lag_two,
    Seconds_lag_three,
    Seconds_lag_four,
    Seconds_lag_five,
    Seconds_lag_six,
    rolling_games_sum_2,
    rolling_games_sum_3,
    rolling_games_sum_4,
    rolling_games_sum_5,
    ewma_games_2,
    ewma_games_3,
    ewma_games_4,
    ewma_games_5,
    ewma_2,
    ewma_2_lag_one,
    ewma_2_lag_two,
    ewma_2_lag_three,
    ewma_3,
    ewma_3_lag_one, 
    ewma_3_lag_two, 
    ewma_3_lag_three, 
    ewma_4,
    ewma_4_lag_one, 
    ewma_4_lag_two, 
    ewma_4_lag_three, 
    ewma_5,
    ewma_5_lag_one, 
    ewma_5_lag_two, 
    ewma_5_lag_three, 
    rolling_var_2,
    rolling_var_2_lag_one,
    rolling_var_2_lag_two,
    rolling_var_2_lag_three,
    rolling_var_3,
    rolling_var_3_lag_one,
    rolling_var_3_lag_two,
    rolling_var_3_lag_three,
    rolling_var_4,
    rolling_var_4_lag_one,
    rolling_var_4_lag_two,
    rolling_var_4_lag_three,
    rolling_var_5,
    rolling_var_5_lag_one,
    rolling_var_5_lag_two,
    rolling_var_5_lag_three,
    rolling_sd_2,
    rolling_sd_2_lag_one,
    rolling_sd_2_lag_two,
    rolling_sd_2_lag_three,
    rolling_sd_3,
    rolling_sd_3_lag_one,
    rolling_sd_3_lag_two,
    rolling_sd_3_lag_three,
    rolling_sd_4,
    rolling_sd_4_lag_one,
    rolling_sd_4_lag_two,
    rolling_sd_4_lag_three,
    rolling_sd_5,
    rolling_sd_5_lag_one,
    rolling_sd_5_lag_two,
    rolling_sd_5_lag_three
  ))

# Split data into training and test sets
train <- data %>%
  filter(Season < 2023)
test <- data %>%
  filter(Season >= 2023)
delta_train <- delta_data %>%
  filter(Season < 2023)
delta_test <- delta_data %>%
  filter(Season >= 2023)

# Random Forest
forest <- randomForest(Seconds ~ ., data = train, ntree = 1000)
summary(forest)

# Visualize partial regression plots for each variable
lm(Seconds ~ ., data = train) %>%
  avPlots()

# Do the same thing for the delta model
lm(delta_Seconds ~ ., data = delta_train) %>%
  avPlots()

# There is odd clustering happening in these variables:
# - Minutes_team
# - Threes_team
# - Twos_team
# - Freethrows_team
# - Points_team
# - Minutes_opponent
# - Threes_opponent
# - Twos_opponent
# - Freethrows_opponent
# - Points_opponent

# We'll just drop these variables because they cause problems even if we take
# these points out.
train <- train %>%
  select(!c(
    Minutes_team,
    Threes_team,
    Twos_team,
    Freethrows_team,
    Points_team,
    Minutes_opponent,
    Threes_opponent,
    Twos_opponent,
    Freethrows_opponent,
    Points_opponent
  ))
delta_train <- delta_train %>%
  select(!c(
    Minutes_team,
    Threes_team,
    Twos_team,
    Freethrows_team,
    Points_team,
    Minutes_opponent,
    Threes_opponent,
    Twos_opponent,
    Freethrows_opponent,
    Points_opponent
  ))

# From here, let's make models and select variables.
#
# Note: we start from a base model and largely do forward selection because
# the computation would take a long time otherwise. Along the same vein,
# using BIC instead of AIC tremendously helps in computation and outputs
# a simpler model.
full_linear <- lm(Seconds ~ .^2, data = train)
base_linear <- lm(Seconds ~ 1, data = train)
final_linear <- step(
  base_linear,
  scope = list(upper = full_linear, lower = base_linear),
  k = log(nrow(train)),
  direction = "both"
)
full_delta <- lm(delta_Seconds ~ .^2, data = delta_train)
base_delta <- lm(delta_Seconds ~ 1, data = delta_train)
final_delta <- step(
  base_delta,
  scope = list(upper = full_delta, lower = base_delta),
  k = log(nrow(delta_train)),
  direction = "both"
)

# Compare RMSE of final models
tibble(actual = test$Seconds, prev = test$Seconds_lag_one) %>%
  mutate(
    Linear_Model = predict(final_linear, newdata = test),
    Delta_Model = predict(final_delta, newdata = delta_test) + prev,
    Random_forest = predict(forest, newdata = test)
  ) %>%
  summarize(
    Linear_RMSE = mean((actual - Linear_Model)^2) %>% sqrt(),
    Delta_RMSE = mean((actual - Delta_Model)^2) %>% sqrt(),
    RF_RMSE = mean((actual - Random_forest)^2) %>% sqrt()
  )

tibble(actual = test$Seconds, prev = test$Seconds_lag_one) %>%
  mutate(
    Linear_Model = predict(final_linear, newdata = test) - actual,
    Delta_Model = predict(final_delta, newdata = delta_test) + prev - actual,
    Random_forest = predict(forest, newdata = test) - actual
  ) %>%
  select(!c(actual, prev)) %>%
  (\(df)
    tibble(
      "model" = colnames(df),
      "min" = apply(df, 2, min) / 60,
      "1%" = apply(df, 2, \(.) quantile(., probs = 0.01)) / 60,
      "25%" = apply(df, 2, \(.) quantile(., probs = 0.25)) / 60,
      "mean" = apply(df, 2, mean) / 60,
      "median" = apply(df, 2, median) / 60,
      "75%" = apply(df, 2, \(.) quantile(., probs = 0.75)) / 60,
      "99%" = apply(df, 2, \(.) quantile(., probs = 0.99)) / 60,
      "max" = apply(df, 2, max) / 60,
      "sd" = apply(df, 2, sd) / 60
    )
  )()
