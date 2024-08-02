# Order of arguments:
# - Pts
# - MP
# - FGM
# - FGA
# - Threes
# - ThreePA
# - FTM
# - FTA
# - REB
# - O_REB
# - D_REB
# - AST
# - STL
# - BLK
# - TOV
# - PF
# - Poss
# - Pace
# - O_rating
# - D_rating
#
# This order remains within each section, and the
# order of sections is this:
# - player
# - team
# - opponent
# - league

usage <- function(MP, FGA, FTA, TO, team_MP, team_FGA, team_FTA, team_TO) {
	numerator <- (FGA + 0.44 * FTA + TO) * team_MP
	denominator <- (team_FGA + 0.44 * team_FTA + team_TO) * 5 * MP
	output <- numerator / denominator
	return(output)
}

possessions <- function(FGM, FGA, FTA, O_REB, D_REB, TOV, opp_FGM, opp_FGA, opp_FTA, opp_O_REB, opp_D_REB, opp_TOV) {
	team <- (FGA + 0.4 * FTA - 1.07 * (O_REB / (O_REB + opp_D_REB)) * (FGA - FGM) + TOV)
	opponent <- (opp_FGA + 0.4 * opp_FTA - 1.07 * (opp_O_REB / (opp_O_REB + D_REB)) * (opp_FGA - opp_FGM) + opp_TOV)
	output <- 0.5 * (team + opponent)
	return(output)
}

pace <- function(team_MP, team_Poss, opp_Poss) {
	output <- (240 / team_MP) * (team_Poss + opp_Poss) / 2
	return(output)
}

touches <- function(FGA, FTA, AST, TOV, team_FTA, opp_PF) {
	output <- FGA + TOV + (FTA / (team_FTA / opp_PF)) + (AST / 0.17)
	return(output)
}

points_per_possession <- function(Pts, FGA, FTA, TO) {
	output <- Pts / (FGA + 0.44 * FTA + TO)
	return(output)
}

effective_fg_pcent <- function(FGA, FGM, Threes) {
	output <- (FGM + 0.5 * Threes) / FGA
	return(output)
}

true_shooting <- function(Pts, FGA, FTA) {
	TSA <- FGA + 0.44 * FTA
	output <- Pts / (2 * TSA)
	return(output)
}

rebound_pcent <- function(MP, REB, team_MP, team_REB, opp_REB) {
	# Useful for any type of rebound percentage.
	# If calculating for offensive/defensive
	# rebound percentages, the opponent rebounds
	# must be opposite (ie. offensive rebound
	# percent: use opponent defensive rebounds).

	numerator <- REB * (team_MP / 5)
	denominator <- (team_REB + opp_REB) * MP
	output <- numerator / denominator
	return(output)
}

offensive_rating <- function(Pts, MP, FGA, FGM, Threes, ThreePA, FTA,
			     FTM, AST, O_REB, TOV, team_Pts, team_MP,
			     team_FGM, team_FGA, team_Threes, team_ThreePA,
			     team_FTM, team_FTA, team_AST, team_O_REB,
			     team_TOV, opp_REB, opp_O_REB) {
	qAST <- ((MP / (team_MP / 5)) * (1.14 * ((team_AST - AST) / team_FGM))) +
		((((team_AST / team_MP) * MP * 5 - AST) / ((team_FGM / team_MP) * MP * 5 - FGM)) *
			(1 - (MP / (team_MP / 5))))
	FGM_part <- FGM * (1 - 0.5 * ((Pts - FTM) / (2 * FGA)) * qAST)
	AST_part <- 0.5 * (((team_Pts - team_FTM) - (Pts - FTM)) / (2 * (team_FGA - FGA))) * AST
	FT_part <- (1 - (1 - (FTM / FTA))^2) * 0.4 * FTA
	team_scoring_poss <- team_FGM + (1 - (1 - (team_FTM / team_FTA))^2) * team_FTA * 0.4
	team_play_pcent <- team_scoring_poss / (team_FGA + team_FTA * 0.4 + team_TOV)
	team_O_REB_pcent <- team_O_REB / (team_O_REB + (opp_REB - opp_O_REB))
	team_O_REB_weight <- ((1 - team_O_REB_pcent) * team_play_pcent) /
		((1 - team_O_REB_pcent) * team_play_pcent + team_O_REB_pcent * (1 - team_play_pcent))
	O_REB_part <- O_REB * team_O_REB_weight * team_play_pcent
	ScPoss <- (FGM_part + AST_part + FT_part) *
		(1 - (team_O_REB / team_scoring_poss) * team_O_REB_weight * team_play_pcent) + O_REB_part

	FGMxPoss <- (FGA - FGM) * (1 - 1.07 * team_O_REB_pcent)
	FTxPoss <- ((1 - (FTM / FTA))^2) * 0.4 * FTA

	TotPoss <- ScPoss + FGMxPoss + FTxPoss + TOV

	PProd_FGM_part <- 2 * (FGM + 0.5 * Threes) * (1 - 0.5 * ((Pts - FTM) / (2 * FGA)) * qAST)
	PProd_AST_part <- 2 * ((team_FGM - FGM + 0.5 * (team_Threes - Threes)) / (team_FGM - FGM)) *
		0.5 * (((team_Pts - team_FTM) - (Pts - FTM)) / (2 * (team_FGA - FGA))) * AST
	PProd_O_REB_part <- O_REB * team_O_REB_weight * team_play_pcent *
		(team_Pts / (team_FGM + (1 - (1 - (team_FTM / team_FTA))^2) * 0.4 * team_FTA))
	PProd <- (PProd_FGM_part + PProd_AST_part + FTM) *
		(1 - (team_O_REB / team_scoring_poss) * team_O_REB_weight * team_play_pcent) + PProd_O_REB_part

	ORtg <- 100 * (PProd / TotPoss)
	return(ORtg)
}

defensive_rating <- function(MP, D_REB, STL, BLK, PF, team_MP,
			     team_D_REB, team_STL, team_BLK, team_PF,
			     team_poss, opp_Pts, opp_MP, opp_FGM,
			     opp_FGA, opp_FTM, opp_FTA, opp_O_REB,
			     opp_D_REB, opp_TOV) {
	DOR_pcent <- opp_O_REB / (opp_O_REB + team_D_REB)
	DFGM_pcent <- opp_FGM / opp_FGA
	FMwt <- (DFGM_pcent * (1 - DOR_pcent)) / (DFGM_pcent * (1 - DOR_pcent) + (1 - DFGM_pcent) * DOR_pcent)
	Stops1 <- STL + BLK * FMwt * (1 - 1.07 * DOR_pcent) + D_REB * (1 - FMwt)
	Stops2 <- (((opp_FGA - opp_FGM - team_BLK) / team_MP) * FMwt * (1 - 1.07 * DOR_pcent) + ((opp_TOV - team_STL) / team_MP)) *
		MP + (PF / team_PF) * 0.4 * opp_FTA * (1 - (opp_FTM / opp_FTA))^2
	Stops <- Stops1 + Stops2

	Stop_pcent <- (Stops * opp_MP) / (team_poss * MP)

	team_Defensive_Rating <- 100 * (opp_Pts / team_poss)
	D_Pts_per_ScPoss <- opp_Pts / (opp_FGM + (1 - (1 - (opp_FTM / opp_FTA))^2) * opp_FTA * 0.4)

	DRtg <- team_Defensive_Rating + 0.2 * (100 * D_Pts_per_ScPoss * (1 - Stop_pcent) - team_Defensive_Rating)
	return(DRtg)
}

points_produced <- function(FGA, FTA, TO, O_rating) {
	output <- (FGA + 0.44 * FTA + TO) * O_rating / 100
	return(output)
}

points_allowed <- function(MP, D_rating, team_MP, team_Poss) {
	output <- (D_rating / 100) * (.2 * (MP / (team_MP / 5)) * team_Poss)
	return(output)
}

net_points <- function(MP, FGA, FTA, TO, O_rating, D_rating, team_MP, team_Poss) {
	produced <- (FGA + 0.44 * FTA + TO) * O_rating / 100
	allowed <- (D_rating / 100) * (.2 * (MP / (team_MP / 5)) * team_Poss)
	output <- produced - allowed
	return(output)
}

offensive_win_shares <- function(Pts_Prod, team_Pace, League_Pace, League_PPP, League_PPG) {
	# League_PPP is league points per possession
	Marg_Off <- Pts_Prod - 0.92 * League_PPP * Off_Poss
	Marg_Pts_per_win <- 0.32 * League_PPG * (team_Pace / League_Pace)
	output <- Marg_Off / Marg_Pts_per_win
	return(output)
}

defensive_win_shares <- function(MP, D_rating, team_MP, team_Pace, team_Def_Poss,
				 League_Pace, League_PPP, League_PPG) {
	# League_PPP is league points per possession
	Marg_Def <- (MP / team_MP) * team_Def_Poss * (1.08 * League_PPP - (D_rating / 100))
	Marg_Pts_per_win <- 0.32 * League_PPG * (team_Pace / League_Pace)
	output <- Marg_Def / Marg_Pts_per_win
	return(output)
}

win_shares <- function(MP, Pts_Prod, D_rating, Off_Poss, team_MP, team_Pace,
		       team_Def_Poss, League_Pace, League_PPP, League_PPG) {
	# League_PPP is league points per possession
	Marg_Pts_per_win <- 0.32 * League_PPG * (team_Pace / League_Pace)
	Marg_Def <- (MP / team_MP) * team_Def_Poss * (1.08 * League_PPP - (D_rating / 100))
	Marg_Off <- Pts_Prod - 0.92 * League_PPP * Off_Poss
	output <- (Marg_Off + Marg_Def) / Marg_Pts_per_win
	return(output)
}

espn_fantasy <- function(Pts, FGM, FGA, Threes, FTM, FTA, REB, AST, STL, BLK, TOV) {
	# Point = 1
	# 3PM = 1
	# FGA = -1
	# FGM = 2
	# FTA = -1
	# FTM = 1
	# REB = 1
	# AST = 2
	# STL = 4
	# BLK = 4
	# TOV = -2
	shots <- Pts + Threes - FGA + 2 * FGM - FTA + FTM
	others <- REB + 2 * AST + 4 * STL + 4 * BLK - 2 * TOV
	output <- shots + others
	return(output)
}

win_score <- function(Pts, FGA, FTA, REB, STL, AST, BLK, TOV, PF) {
	output <- Pts + REB + STL + 0.5 * AST + 0.5 * BLK - FGA - TOV - 0.5 * FTA - 0.5 * PF
	return(output)
}

player_impact_estimate <- function(Pts, FGM, FGA, FTM, FTA, AST, STL,
				   BLK, D_REB, O_REB, TO, PF, team_Pts,
				   team_FGA, team_FGM, team_FTA, team_FTM,
				   team_AST, team_STL, team_BLK, team_D_REB,
				   team_O_REB, team_TO, team_PF) {
	numerator <- Pts + FGM + FTM - FGA - FTA + D_REB + O_REB / 2 + AST + STL + BLK / 2 - PF - TO
	denominator <- (team_Pts + team_FGM + team_FTM - team_FGA - team_FTA + team_D_REB +
		team_O_REB / 2 + team_AST + team_STL + team_BLK / 2 - team_PF - team_TO)
	output <- numerator / denominator
	return(output)
}

approximate_value <- function(Pts, FGM, FGA, FTM, FTA, REB, AST, STL, BLK, TOV) {
	Credits <- Pts + REB + AST + STL + BLK - (FGA - FGM) - (FTA - FTM) - TOV
	output <- Credits^(3 / 4) / 21
	return(output)
}

game_score <- function(Pts, FGM, FGA, FTM, FTA, O_REB, D_REB, AST, STL, BLK, TOV, PF) {
	output <- Pts + 0.4 * FGM + 0.7 * O_REB + 0.3 * D_REB + STL + 0.7 * AST +
		0.7 * BLK - 0.7 * FGA - 0.4 * (FTA - FTM) - 0.4 * PF - TOV
	return(output)
}

points_gained <- function() {
}

box_pm <- function() {
}
