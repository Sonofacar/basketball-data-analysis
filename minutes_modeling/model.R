# Libraries
library(tidyverse) |> suppressMessages()
library(randomForest) |> suppressMessages()
library(glmnet) |> suppressMessages()
library(ggfortify)

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
data <- player_info %>%
  inner_join(season_totals, by = c("Player_ID")) %>%
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
  mutate(delta_Seconds = Seconds - Seconds_lag_one) %>%
  select(!c(Seconds))

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
    Delta_Model = predict(delta_lm, newdata = train) + prev,
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
    Delta_Model = predict(delta_lm, newdata = train) + prev - actual,
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
