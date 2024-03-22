def match_referees(referee_info_df, match_dictionaries):
    df_copy = referee_info_df
    output = []
    for match in match_dictionaries:
        for key, value in match.items():
            if key == 'href':
                output.append(match['href'])
                continue

            if int(value) == value:
                df_copy = df_copy.query(key + ' == ' + str(value))
            else:
                df_copy = df_copy.query(key + ' == "' + value + '"')

            if len(df_copy) == 1:
                output.append(df_copy['Referee_ID'])
                continue

    return output

def match_executive(executive_info_df, match_dictionary):
    df_copy = executive_info_df
    for key, value in match_dictionary.items():
        if key == 'href':
            continue

        if int(value) == value:
            df_copy = df_copy.query(key + ' == ' + str(value))
        else:
            df_copy = df_copy.query(key + ' == "' + value + '"')

        if len(df_copy) == 1:
            return df_copy['Executive_ID']
        if len(df_copy) == 0:
            return 'No match found'

    return 'Multiple matches, further querying is needed'

def match_coach(coach_info_df, match_dictionary):
    df_copy = coach_info_df
    for key, value in match_dictionary.items():
        if key == 'href':
            continue

        if int(value) == value:
            df_copy = df_copy.query(key + ' == ' + str(value))
        else:
            df_copy = df_copy.query(key + ' == "' + value + '"')

        if len(df_copy) == 1:
            return df_copy['Coach_ID']
        if len(df_copy) == 0:
            return 'No match found'

    return 'Multiple matches, further querying is needed'

def match_player(player_info_df, match_dictionary):
    df_copy = player_info_df
    for key, value in match_dictionary.items():
        if key == 'href':
            continue

        if key == 'Season':
            df_copy.loc[(df_copy['Draft_Year'] + df_copy['Career_Seasons'] >= value) & (df_copy['Draft_Year'] < value),]

        if int(value) == value:
            df_copy = df_copy.query(key + ' == ' + str(value))
        else:
            df_copy = df_copy.query(key + ' == "' + value + '"')

        if len(df_copy) == 1:
            return df_copy['Player_ID']
        if len(df_copy) == 0:
            return 'No match found'

    return 'Multiple matches, further querying is needed'

def match_team(team_info_df, match_dictionary):
    df_copy = team_info_df
    for key, value in match_dictionary.items():
        if key == 'href':
            continue

        if int(value) == value:
            df_copy = df_copy.query(key + ' == ' + str(value))
        else:
            df_copy = df_copy.query(key + ' == "' + value + '"')

        if len(df_copy) == 1:
            return df_copy['Team_ID']
        if len(df_copy) == 0:
            return 'No match found'

    return 'Multiple matches, further querying is needed'
