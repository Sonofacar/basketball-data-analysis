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
  mutate(
    Win_pct = Wins / (Wins + Losses),
    Age = (Season_start - Birthday) / 365,
    Experience = (Season_start - Debut_Date) / 365
  ) %>%
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
    delta_Seconds = Seconds - Seconds_lag_one,
    delta_Seconds_lag_one = Seconds_lag_one - Seconds_lag_two,
    delta_Seconds_lag_two = Seconds_lag_two - Seconds_lag_three
  ) %>%
  select(!c(Seconds, Seconds_lag_one, Seconds_lag_two, Seconds_lag_three))

# Split data into training and test sets
train <- data %>%
  filter(Season < 2023)
test <- data %>%
  filter(Season >= 2023)
delta_train <- delta_data %>%
  filter(Season < 2023)
delta_test <- delta_data %>%
  filter(Season >= 2023)

# Try that with all interactions
full_lm <- lm(Seconds ~ .^2, data = train)
full_poisson <- glm(Seconds ~ ., data = train, family = poisson())
delta_lm <- lm(delta_Seconds ~ .^2, data = delta_train)

# Complete Linear model
autoplot(full_lm)
summary(full_lm)

# Linear model of change in seconds
autoplot(delta_lm)
summary(delta_lm)

# Complete Poisson model
autoplot(full_poisson)
summary(full_poisson)
(1 - full_poisson$deviance / full_poisson$null.deviance) %>%
  print()

# Scale coefficient to transpose all Seconds values below 1 before the exponent,
# leaving some wiggle room for future outliers.
m <- 1.1 * max(train$Seconds)
g <- \(.) exp(./m)
g_inv <- \(.) log(.) %>% `*`(m)

# Complete transposed Linear model
transposed_lm <- lm(g(Seconds) ~ .^2, data = train)
autoplot(transposed_lm)
summary(transposed_lm)

# Random Forest
forest <- randomForest(Seconds ~ ., data = train, ntree = 1000)
summary(forest)

tibble(actual = train$Seconds, prev = train$Seconds_lag_one) %>%
  mutate(
    Linear_Model = predict(full_lm, newdata = train),
    Transposed_Model = predict(transposed_lm, newdata = train) %>% g_inv(),
    Poisson_Model = predict(full_poisson, newdata = train),
    Delta_Model = predict(delta_lm, newdata = delta_train) + prev,
    Random_forest = predict(forest, newdata = train)
  ) %>%
  summarize(
    Linear_RMSE = mean((actual - Linear_Model)^2) %>% sqrt(),
    Transposed_RMSE = mean((actual - Transposed_Model)^2) %>% sqrt(),
    Poisson_RMSE = mean((actual - Poisson_Model)^2) %>% sqrt(),
    Delta_RMSE = mean((actual - Delta_Model)^2) %>% sqrt(),
    RF_RMSE = mean((actual - Random_forest)^2) %>% sqrt()
  )

tibble(actual = train$Seconds, prev = train$Seconds_lag_one) %>%
  mutate(
    Linear_Model = predict(full_lm, newdata = train) - actual,
    Transposed_Model = predict(transposed_lm, newdata = train) %>% g_inv() - actual,
    Poisson_Model = predict(full_poisson, newdata = train) - actual,
    Delta_Model = predict(delta_lm, newdata = delta_train) + prev - actual,
    Random_forest = predict(forest, newdata = train) - actual
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

# While the linear model is not as good as the transposed model, it performs
# adequately. In the interest of using a simple model, we will continue with
# that model. We may also try the delta model in the future; it seems to do
# slightly worse but might have a more sound approach.

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
# the computation would take a long time otherwise.
full_linear <- lm(Seconds ~ .^2, data = train)
base_linear <- lm(Seconds ~ 1, data = train)
final_linear <- step(
  base_linear,
  scope = list(upper = full_linear, lower = base_linear),
  direction = "both"
)
full_delta <- lm(delta_Seconds ~ .^2, data = delta_train)
base_delta <- lm(delta_Seconds ~ 1, data = delta_train)
final_delta <- step(
  base_delta,
  scope = list(upper = full_delta, lower = base_delta),
  direction = "both"
)
