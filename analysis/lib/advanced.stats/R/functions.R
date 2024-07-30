usage <- function(player_FGA, player_FTA, player_TO, player_MP, team_FGA, team_FTA, team_TO, team_MP)
{
	numerator <- (player_FGA + 0.44*player_FTA + player_TO) * team_MP
	denominator <- (team_FGA + 0.44*team_FTA + team_TO) * 5*player_MP
	output <- numerator/denominator
	return(output)
}

possessions <- function(FGA, FTA, ORB, FG, TOV, opponent_FGA, opponent_FTA, opponent_ORB, opponent_FG, opponent_TOV)
{
	team <- ( FGA + 0.4*FTA - 1.07*( ORB / ( ORB + opponent_DRB ) ) * ( FGA - FG ) + TOV )
	opponent <- ( opponent_FGA + 0.4 * opponent_FTA - 1.07 * ( opponent_ORB / ( opponent_ORB + DRB ) ) * ( opponent_FGA - opponent_FG ) + opponent_TOV )
	output <- 0.5 * ( team + opponent )
	return(output)
}

pace <- function(Team_MP, Team_Poss, opponent_Poss)
{
	output <- (240 / Team_MP) * ( Team_Poss + opponent_Poss ) / 2
	return(output)
}

touches <- function(AST, TOV, FGA, FTA, team_FTA, opponent_PF)
{
	output <- FGA + TOV + ( FTA / (team_FTA / opponent_PF) ) + ( AST/0.17 )
	return(output)
}

points_per_possession <- function(Pts, FGA, FTA, TO)
{
	output <- PTS / ( FGA + 0.44*FTA + TO )
	return(output)
}

effective_fg_pcent <- function(FG, ThreeP, FGA)
{
	output <- (FG + 0.5*ThreeP) / FGA
	return(output)
}

true_shooting <- function(points, FGA, FTA)
{
	TSA <- FGA + 0.44*FTA
	output <- points / (2 * TSA)
	return(output)
}

rebound_pcent <- function(player_RB, player_MP, team_RB, team_MP, opponent_RB)
{
	# Useful for any type of rebound percentage.
	# If calculating for offensive/defensive 
	# rebound percentages, the opponent rebounds
	# must be opposite (ie. offensive rebound 
	# percent: use opponent defensive rebounds).

	numerator <- player_RB * (team_MP / 5)
	denominator <-  (team_RB + opponent_RB) * player_MP
	output <- numerator / denominator
	return(output)
}

offensive_rating <- function(MP, AST, ORB, FGA, FGM, FTA, FTM, 
				    ThreePA, ThreePM, TOV, PTS, team_MP,
				    team_AST, team_ORB, team_FGA, team_FGM,
				    team_FTA, team_FTM, team_ThreePA,
				    team_ThreePM, team_TOV, team_PTS ,
				    opp_RB, opp_ORB) 
{
	qAST <- ( ( MP / (team_MP/5) ) * ( 1.14*( (team_AST - AST) / team_FGM ) ) ) + 
		( ( ( (team_AST / team_MP) * MP * 5 - AST ) / ( (team_FGM / team_MP) * MP * 5 - FGM ) ) * 
		 ( 1 - ( MP / (team_MP/5) ) ) )
	FG_part <- FGM * ( 1 - 0.5*( (PTS - FTM) / (2*FGA) ) * qAST )
	AST_part <- 0.5*( ( (team_PTS - team_FTM) - (PTS - FTM) ) / ( 2*(team_FGA - FGA) ) ) * AST
	FT_part <- ( 1 - ( 1 - (FTM/FTA) )^2 ) * 0.4 * FTA
	team_scoring_poss <- team_FGM + ( 1 - ( 1 - (team_FTM / team_FTA) )^2 ) * team_FTA * 0.4
	team_play_pcent <- team_scoring_poss / ( team_FGA + team_FTA * 0.4 + team_TOV )
	team_ORB_pcent <- team_ORB / ( team_ORB + (opp_RB - opp_ORB) )
	team_ORB_weight <- ( (1 - team_ORB_pcent) * team_play_pcent ) /
	       	( (1 - team_ORB_pcent) * team_play_pcent + team_ORB_pcent * (1 - team_play_pcent) )
	ORB_part <- ORB * team_ORB_weight * team_play_pcent
	ScPoss = ( FG_part + AST_part + FT_part ) *
	       	( 1 - (team_ORB / team_scoring_poss) * team_ORB_weight * team_play_pcent ) + ORB_part

	FGxPoss <- (FGA - FGM) * ( 1 - 1.07*team_ORB_pcent )
	FTxPoss <- ( ( 1 - (FTM / FTA) )^2 ) * 0.4 * FTA

	TotPoss <- ScPoss + FGxPoss + FTxPoss + TOV

	PProd_FG_part <- 2*( FGM + 0.5*ThreePM ) * ( 1 - 0.5*( (PTS - FTM) / (2*FGA) ) * qAST )
	PProd_AST_part <- 2*( ( team_FGM - FGM + 0.5*( team_ThreePM - ThreePM ) ) / (team_FGM - FGM) ) * 
		0.5 * ( ( (team_PTS - team_FTM) - (PTS - FTM) ) / ( 2*(team_FGA - FGA) ) ) * AST
	PProd_ORB_part <- ORB * team_ORB_weight * team_play_pcent * 
		( team_PTS / ( team_FGM + ( 1 - ( 1 - (team_FTM / team_FTA) )^2 ) * 0.4 * team_FTA ) )
	PProd <- ( PProd_FG_part + PProd_AST_part + FTM ) * 
		( 1 - (team_ORB / team_scoring_poss) * team_ORB_weight * team_play_pcent ) + PProd_ORB_part

	ORtg <- 100*( PProd / TotPoss )
	return( ORtg )
}

defensive_rating <- function(MP, STL, BLK, DRB, PF, team_poss, team_MP,
			     team_STL, team_BLK, team_DRB, team_PF, opp_MP,
			     opp_FGA, opp_FGM, opp_FTA, opp_FTM, opp_ORB,
			     opp_DRB, opp_TOV, opp_PTS)
{
	DOR_pcent <- opp_ORB / ( opp_ORB + team_DRB )
	DFG_pcent <- opp_FGM / opp_FGA
	FMwt <- ( DFG_pcent * (1 - DOR_pcent) ) / ( DFG_pcent * (1 - DOR_pcent)  + (1 - DFG_pcent) * DOR_pcent )
	Stops1 <- STL + BLK * FMwt * ( 1 - 1.07*DOR_pcent ) + DRB * (1 - FMwt)
	Stops2 <- ( ( ( opp_FGA - opp_FGM - team_BLK ) / team_MP ) * FMwt * ( 1 - 1.07*DOR_pcent ) + ( (opp_TOV - team_STL) / team_MP ) ) *
		MP + (PF / team_PF) * 0.4 * opp_FTA * ( 1 - (opp_FTM / opp_FTA) )^2
	Stops <- Stops1 + Stops2

	Stop_pcent <- ( Stops * opp_MP ) / ( team_poss * MP )

	team_Defensive_Rating <- 100*( opp_PTS / team_poss )
	D_Pts_per_ScPoss <- opp_PTS / ( opp_FGM + ( 1 - ( 1 - (opp_FTM / opp_FTA) )^2 ) * opp_FTA * 0.4 )

	DRtg <- team_Defensive_Rating + 0.2*( 100 * D_Pts_per_ScPoss * (1 - Stop_pcent) - team_Defensive_Rating )
	return(DRtg)
}

points_produced <- function(FGA, FTA, TO, O_rating)
{
	output <- ( FGA + 0.44*FTA + TO ) * O_rating / 100
	return(output)
}

offensive_win_shares <- function(Pts_Prod, Off_Poss, team_Pace, League_Pace, League_PPP, League_PPG)
{
	# Leauge_PPP is league points per possession
	Marg_Off <- Pts_Prod - 0.92*League_PPP * Off_Poss
	Marg_Pts_per_win <- 0.32*League_PPG * (team_Pace / League_Pace)
	output <- Marg_Off / Marg_Pts_per_win
	return(output)
}

defensive_win_shares <- function(MP, D_rating, team_MP, team_Pace, team_Def_Poss,
				 League_Pace, League_PPP, League_PPG )
{
	# Leauge_PPP is league points per possession
	Marg_Def <- (MP / team_MP) * team_Def_Poss * ( 1.08*League_PPP - (D_rating / 100) )
	Marg_Pts_per_win <- 0.32 * League_PPG * (team_Pace / League_Pace)
	output <- Marg_Def / Marg_Pts_per_win
	return(output)
}

win_shares <- function(MP, Pts_Prod, D_rating, Off_Poss, team_MP, team_Pace,
		       team_Def_Poss, League_Pace, League_PPP, League_PPG)
{
	# Leauge_PPP is league points per possession
	Marg_Pts_per_win <- 0.32 * League_PPG * (team_Pace / League_Pace)
	Marg_Def <- (MP / team_MP) * team_Def_Poss * ( 1.08*League_PPP - (D_rating / 100) )
	Marg_Off <- Pts_Prod - 0.92*League_PPP * Off_Poss
	output <- ( Marg_Off + Marg_Def ) / Marg_Pts_per_win
	return(output)
}

espn_fantasy <- function(Pts, Threes, FGA, FGM, FTA, FTM, REB, AST, STL, BLK, TOV)
{
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
	shots <- Pts + Threes - FGA + 2*FGM - FTA + FTM
	others <- REB + 2*AST + 4*STL + 4*BLK - 2*TOV
	output <- shots + others
	return(output)
}

win_score <- function(Pts, REB, STL, AST, BLK, TOV, PF, FGA, FTA)
{
	output <- Pts + REB + STL + 0.5*AST + 0.5*BLK - FGA - TOV - 0.5*FTA - 0.5*PF
	return(output)
}

player_impact_estimate <- function(PTS, AST, STL, BLK, Def_REB, Off_REB, FGA,
				   FGM, FTA, FTM, PF, TO, team_PTS, team_AST,
				   team_STL, team_BLK, team_Def_REB, team_Off_REB,
				   team_FGA, team_FGM, team_FTA, team_FTM,
				   team_PF, team_TO)
{
	numerator <- PTS + FGM + FTM – FGA – FTA + Def_REB + Off_REB/2 + AST + STL + BLK/2 – PF – TO
	denominator <- (team_PTS + team_FGM + team_FTM – team_FGA – team_FTA + team_Def_REB + 
			team_Off_REB/2 + team_AST + team_STL + team_BLK/2 – team_PF – team_TO)
	output <- numerator / denominator
	return(output)
}

approximate_value <- function(Pts, REB, AST, STL, BLK, TOV, FGA, FGM, FTA, FTM)
{
	Credits <- Pts + REB + AST + STL + BLK - (FGA - FGM) - (FTA - FTM) - TOV)
	output <- Credits^(3/4) / 21
	return(output)
}

game_score <- function(Pts, Off_REB, Def_REB, AST, STL, BLK, TOV, FGA, FGM, FTA, FTM)
{
	output <- Pts + 0.4*FGM + 0.7*Off_REB + 0.3*Def_REB + STLs + 0.7*AST +
		0.7*BLK -  0.7*FGA - 0.4*(FTA - FTM) – 0.4*PF - TOV
	return(output)
}

points_gained <- function()
{
}

box_pm <- function()
{
}

