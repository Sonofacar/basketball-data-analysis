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
data_modifications <- function(df) {
  df %>%
    group_by(Player_ID) %>%
    mutate(
      Win_pct = Wins / (Wins + Losses),
      Age = (Season_start - Birthday) / 365,
      Experience = (Season_start - Debut_Date) / 365,
      is_2011 = (Season == 2011),
      is_2012 = (Season == 2012),
      games_lag_one = lag(Games, n = 1, default = 0, order_by = Season),
      games_lag_two = lag(Games, n = 2, default = 0, order_by = Season),
      games_lag_three = lag(Games, n = 3, default = 0, order_by = Season),
      games_lag_four = lag(Games, n = 4, default = 0, order_by = Season),
      games_lag_five = lag(Games, n = 5, default = 0, order_by = Season),
      rolling_games_sum_2 = roll(Games, 2, sum),
      rolling_games_sum_2_lag_one = lag(
        rolling_games_sum_2,
        n = 1,
        default = 0,
        order_by = Season
      ),
      rolling_games_sum_2_lag_two = lag(
        rolling_games_sum_2,
        n = 2,
        default = 0,
        order_by = Season
      ),
      rolling_games_sum_2_lag_three = lag(
        rolling_games_sum_2,
        n = 3,
        default = 0,
        order_by = Season
      ),
      rolling_games_sum_3 = roll(Games, 3, sum),
      rolling_games_sum_3_lag_one = lag(
        rolling_games_sum_3,
        n = 1,
        default = 0,
        order_by = Season
      ),
      rolling_games_sum_3_lag_two = lag(
        rolling_games_sum_3,
        n = 2,
        default = 0,
        order_by = Season
      ),
      rolling_games_sum_3_lag_three = lag(
        rolling_games_sum_3,
        n = 3,
        default = 0,
        order_by = Season
      ),
      rolling_games_sum_4 = roll(Games, 4, sum),
      rolling_games_sum_4_lag_one = lag(
        rolling_games_sum_4,
        n = 1,
        default = 0,
        order_by = Season
      ),
      rolling_games_sum_4_lag_two = lag(
        rolling_games_sum_4,
        n = 2,
        default = 0,
        order_by = Season
      ),
      rolling_games_sum_4_lag_three = lag(
        rolling_games_sum_4,
        n = 3,
        default = 0,
        order_by = Season
      ),
      rolling_games_sum_5 = roll(Games, 5, sum),
      rolling_games_sum_5_lag_one = lag(
        rolling_games_sum_5,
        n = 1,
        default = 0,
        order_by = Season
      ),
      rolling_games_sum_5_lag_two = lag(
        rolling_games_sum_5,
        n = 2,
        default = 0,
        order_by = Season
      ),
      rolling_games_sum_5_lag_three = lag(
        rolling_games_sum_5,
        n = 3,
        default = 0,
        order_by = Season
      ),
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
}

delta_modifications <- function(df) {
  df %>%
    mutate(
      delta_games_lag_one = games_lag_one - games_lag_two,
      delta_games_lag_two = games_lag_two - games_lag_three,
      delta_games_lag_three = games_lag_three - games_lag_four,
      delta_games_lag_four = games_lag_four - games_lag_five,
      delta_rolling_games_sum_2_lag_one = `-`(
        rolling_games_sum_2,
        rolling_games_sum_2_lag_one
      ),
      delta_rolling_games_sum_2_lag_two = `-`(
        rolling_games_sum_2_lag_one,
        rolling_games_sum_2_lag_two
      ),
      delta_rolling_games_sum_2_lag_three = `-`(
        rolling_games_sum_2_lag_two,
        rolling_games_sum_2_lag_three
      ),
      delta_rolling_games_sum_3_lag_one = `-`(
        rolling_games_sum_3,
        rolling_games_sum_3_lag_one
      ),
      delta_rolling_games_sum_3_lag_two = `-`(
        rolling_games_sum_3_lag_one,
        rolling_games_sum_3_lag_two
      ),
      delta_rolling_games_sum_3_lag_three = `-`(
        rolling_games_sum_3_lag_two,
        rolling_games_sum_3_lag_three
      ),
      delta_rolling_games_sum_4_lag_one = `-`(
        rolling_games_sum_4,
        rolling_games_sum_4_lag_one
      ),
      delta_rolling_games_sum_4_lag_two = `-`(
        rolling_games_sum_4_lag_one,
        rolling_games_sum_4_lag_two
      ),
      delta_rolling_games_sum_4_lag_three = `-`(
        rolling_games_sum_4_lag_two,
        rolling_games_sum_4_lag_three
      ),
      delta_rolling_games_sum_5_lag_one = `-`(
        rolling_games_sum_5,
        rolling_games_sum_5_lag_one
      ),
      delta_rolling_games_sum_5_lag_two = `-`(
        rolling_games_sum_5_lag_one,
        rolling_games_sum_5_lag_two
      ),
      delta_rolling_games_sum_5_lag_three = `-`(
        rolling_games_sum_5_lag_two,
        rolling_games_sum_5_lag_three
      ),
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
      games_lag_one,
      games_lag_two,
      games_lag_three,
      games_lag_four,
      games_lag_five,
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
}

data <- season_totals %>%
  inner_join(player_info , by = c("Player_ID")) %>%
  select(!Name) %>%
  inner_join(
    team_info,
    by = c("Team_ID", "Season"),
    suffix = c("", "_team")
  ) %>%
  inner_join(response, by = c("Player_ID", "Season")) %>%
  data_modifications() %>%
  select(!Player_ID)

delta_data <- data %>%
  delta_modifications()

# Split data into training and test sets
train <- data %>%
  filter(Season < (max(Season) - 1))
test <- data %>%
  filter(Season >= (max(Season) - 1))
delta_train <- delta_data %>%
  filter(Season < (max(Season) - 1))
delta_test <- delta_data %>%
  filter(Season >= (max(Season) - 1))

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
# - Seconds_team
# - Threes_team
# - Twos_team
# - Freethrows_team
# - Points_team
# - Seconds_opponent
# - Threes_opponent
# - Twos_opponent
# - Freethrows_opponent
# - Points_opponent

# We'll just drop these variables because they cause problems even if we take
# these points out.
train <- train %>%
  select(!c(
    Seconds_team,
    Threes_team,
    Twos_team,
    Freethrows_team,
    Points_team,
    Seconds_opponent,
    Threes_opponent,
    Twos_opponent,
    Freethrows_opponent,
    Points_opponent
  ))
delta_train <- delta_train %>%
  select(!c(
    Seconds_team,
    Threes_team,
    Twos_team,
    Freethrows_team,
    Points_team,
    Seconds_opponent,
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

# Output predictions and SE for this upcoming season
season_totals %>%
  inner_join(player_info , by = c("Player_ID")) %>%
  inner_join(
    team_info,
    by = c("Team_ID", "Season"),
    suffix = c("", "_team")
  ) %>%
  data_modifications() %>%
  ungroup() %>%
  # filter(Season == 2022) %>%
  filter(Season == max(Season)) %>%
  (\(df)
    predict(final_linear, df, se.fit = TRUE) %>%
      (\(l)
        tibble(
          Player_ID = df$Player_ID,
          Seconds = l$fit,
          Seconds_SE = l$se.fit
        )
      )()
  )() %>%
  write_csv(
    max(season_totals$Season) %>%
      `+`(1) %>%
      paste("minutes-predictions.csv", sep = "-")
  )

output %>%
  inner_join(player_info, by = "Player_ID") %>%
  select(Name, Seconds) %>%
  arrange(desc(Seconds)) %>%
  View()

season_totals %>%
  inner_join(player_info , by = c("Player_ID")) %>%
  inner_join(
    team_info,
    by = c("Team_ID", "Season"),
    suffix = c("", "_team")
  ) %>%
  data_modifications() %>%
  left_join(response, by = c("Player_ID", "Season")) %>%
  filter(Season == 2024) %>%
  (\(df) mutate(df, pred = predict(final_linear, df)))() %>%
  select(Player_ID, Seconds, pred) %>%
  ggplot() +
    geom_density(aes(x = pred), fill = "green", alpha = 0.5) +
    geom_density(aes(x = Seconds), fill = "blue", alpha = 0.5)

# 2024
#      ewma_4      Seconds_lag_one      ewma_2        ewma_games_5
# Min.   :    0   Min.   :     0   Min.   :     0   Min.   : 0.3333
# 1st Qu.: 4800   1st Qu.: 11999   1st Qu.:  7999   1st Qu.:12.3333
# Median :20924   Median : 52311   Median : 34874   Median :21.3333
# Mean   :24546   Mean   : 61364   Mean   : 40909   Mean   :18.5875
# 3rd Qu.:42659   3rd Qu.:106647   3rd Qu.: 71098   3rd Qu.:25.6667
# Max.   :71726   Max.   :179314   Max.   :119543   Max.   :28.3333
#     Games        ewma_games_2     Seconds_lag_three     Usage
# Min.   : 1.00   Min.   : 0.6667   Min.   :     0    Min.   :0.0000
# 1st Qu.:37.00   1st Qu.:24.6667   1st Qu.:     0    1st Qu.:0.1374
# Median :64.00   Median :42.6667   Median : 42372    Median :0.1696
# Mean   :55.76   Mean   :37.1750   Mean   : 53769    Mean   :0.1784
# 3rd Qu.:77.00   3rd Qu.:51.3333   3rd Qu.:101444    3rd Qu.:0.2142
# Max.   :85.00   Max.   :56.6667   Max.   :171257    Max.   :0.6373
#    Win_pct       rolling_sd_3_lag_three
# Min.   :0.1707   Min.   :    0
# 1st Qu.:0.3293   1st Qu.:    0
# Median :0.5610   Median : 7741
# Mean   :0.4903   Mean   :14806
# 3rd Qu.:0.5976   3rd Qu.:24380
# Max.   :0.7805   Max.   :80165

# 2023 (upper 1/4)
#     Seconds           ewma_4       Seconds_lag_one      ewma_2
# Min.   :120113   Min.   : 40889   Min.   : 17905   Min.   : 43165
# 1st Qu.:128805   1st Qu.: 72914   1st Qu.:103466   1st Qu.: 98587
# Median :137578   Median : 83473   Median :125792   Median :114407
# Mean   :139144   Mean   : 80789   Mean   :119277   Mean   :110146
# 3rd Qu.:146167   3rd Qu.: 92445   3rd Qu.:145040   3rd Qu.:128139
# Max.   :177782   Max.   :111170   Max.   :171257   Max.   :153678
#  ewma_games_5       Games        ewma_games_2   Seconds_lag_three
# Min.   :20.67   Min.   :14.00   Min.   :26.44   Min.   :     0
# 1st Qu.:36.19   1st Qu.:62.00   1st Qu.:57.00   1st Qu.: 34360
# Median :39.44   Median :70.00   Median :62.67   Median :100902
# Mean   :38.21   Mean   :66.22   Mean   :60.29   Mean   : 82499
# 3rd Qu.:42.11   3rd Qu.:76.00   3rd Qu.:67.00   3rd Qu.:124164
# Max.   :45.78   Max.   :82.00   Max.   :73.11   Max.   :153385
#     Usage            Win_pct       rolling_sd_3_lag_three
# Min.   :0.09951   Min.   :0.2439   Min.   :    0
# 1st Qu.:0.18492   1st Qu.:0.4268   1st Qu.:    0
# Median :0.21914   Median :0.5610   Median :16172
# Mean   :0.22584   Mean   :0.5166   Mean   :25770
# 3rd Qu.:0.27183   3rd Qu.:0.6220   3rd Qu.:49312
# Max.   :0.37402   Max.   :0.7805   Max.   :89942

# 2023
#      ewma_4      Seconds_lag_one      ewma_2        ewma_games_5
# Min.   :    0   Min.   :     0   Min.   :     0   Min.   : 0.3333
# 1st Qu.:11482   1st Qu.: 28704   1st Qu.: 19136   1st Qu.:16.6667
# Median :28566   Median : 71416   Median : 47611   Median :22.6667
# Mean   :29188   Mean   : 72971   Mean   : 48647   Mean   :20.1162
# 3rd Qu.:46576   3rd Qu.:116439   3rd Qu.: 77626   3rd Qu.:25.3333
# Max.   :71113   Max.   :177782   Max.   :118521   Max.   :27.6667
#     Games        ewma_games_2     Seconds_lag_three     Usage
# Min.   : 1.00   Min.   : 0.6667   Min.   :     0    Min.   :0.0000
# 1st Qu.:50.00   1st Qu.:33.3333   1st Qu.:     0    1st Qu.:0.1454
# Median :68.00   Median :45.3333   Median : 49106    Median :0.1794
# Mean   :60.35   Mean   :40.2324   Mean   : 52720    Mean   :0.1861
# 3rd Qu.:76.00   3rd Qu.:50.6667   3rd Qu.: 93559    3rd Qu.:0.2123
# Max.   :83.00   Max.   :55.3333   Max.   :160015    Max.   :0.3825
#    Win_pct       rolling_sd_3_lag_three
# Min.   :0.2073   Min.   :    0
# 1st Qu.:0.4268   1st Qu.:    0
# Median :0.5122   Median : 8138
# Mean   :0.4983   Mean   :16436
# 3rd Qu.:0.5732   3rd Qu.:26237
# Max.   :0.7073   Max.   :83394

