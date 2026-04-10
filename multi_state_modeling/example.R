###########
# Library #
###########

library(msm)

#################
# Simulate data #
#################

set.seed(123)

# Simulate observation times
n_ind <- 50
obs_per_ind <- 6

data_list <- list()

for (i in 1:n_ind) {
  times <- cumsum(runif(obs_per_ind, 0.5, 2))  # irregular intervals
  
  # Fake observed states (noisy version of true states)
  states <- sample(1:2, obs_per_ind, replace = TRUE, prob = c(0.7, 0.3))
  
  data_list[[i]] <- data.frame(
    id = i,
    time = times,
    state_obs = states
  )
}

data <- do.call(rbind, data_list)
# data[300, "state_obs"] <- 3

#######################################
# Set intensity and emission matrices #
#######################################

Q <- matrix(c(
  0, 0.2,   # Active → Desisted
  0.3, 0    # Desisted → Active
), byrow = TRUE, nrow = 2)

rownames(Q) <- colnames(Q) <- c("Active", "Desisted")

E <- matrix(c(
  0.85, 0.10,  # True Active observed as A/D
  0.10, 0.80   # True Desisted
), byrow = TRUE, nrow = 2)

rownames(E) <- colnames(E) <- c("Active", "Desisted")

################
# Create model #
################

model <- msm(
  state_obs ~ time,
  subject = id,
  data = data,
  qmatrix = Q,
  ematrix = E,
  control = list(maxit = 1000)
)

qmatrix.msm(model)
ematrix.msm(model)
sojourn.msm(model)

###############
# Predictions #
###############

# Most likely true states (Viterbi)
hidden_states <- viterbi.msm(model)

head(hidden_states)

# Total Length of Stay
totlos.msm(model, t = 100)

# READ THIS:
# The general idea of this approach would be to model individual players,
# potentially just looking at the past `n` years. We would end by computing the
# modeled number of games played with `totlos.msm` and taking the ratio between
# games played and games injured. From there, we could try to model changes in
# this ratio by looking at past data.
# 
# Another approach might be to store values in the Q matrix to use elsewhere.
# One example would be to model the probability of a player playing in a game,
# giving a more granular level of minutes played modeling.
