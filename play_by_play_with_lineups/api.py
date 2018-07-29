import numpy as np
import sys
import warnings

sys.path.append("..")
from play_by_play_with_lineups.thorny_data_points import BAD_DATA_POINTS, DATA_TO_DELETE
from nba_stats.ingest import get_boxscore_for_game_quarter

HOME_COLS = ['HOME_PLAYER_1', 'HOME_PLAYER_2', 'HOME_PLAYER_3', 'HOME_PLAYER_4', 'HOME_PLAYER_5']
AWAY_COLS = ['AWAY_PLAYER_1', 'AWAY_PLAYER_2', 'AWAY_PLAYER_3', 'AWAY_PLAYER_4', 'AWAY_PLAYER_5']
NEW_COLS = HOME_COLS + AWAY_COLS


def fill_up(pbp, index, player_id, cols):
    """Helper function to backfill a player being on the court"""
    index -= 1
    open_count = pbp.ix[index, cols].isnull().sum()
    while ((pbp.ix[index, 'EVENTMSGTYPE'] != 12) & (pbp.ix[index, cols].isnull().sum() > 0)
            & ((pbp.ix[index, cols] == player_id).sum() == 0)):
        pbp.ix[index, cols[open_count-1]] = player_id
        index -= 1


def get_players_on_the_court(pbp, game_id):
    """Annotate play by play data with player ids of who is on the court"""
    # Filter out all actions before the start
    start = min(pbp[pbp['EVENTMSGTYPE'] == 12]['EVENTNUM'])
    mask = pbp['EVENTNUM'] >= start
    pbp = pbp[mask].fillna(np.nan)
    # super hacky but sometimes data sucks
    if game_id in BAD_DATA_POINTS:
        bad_data_points = BAD_DATA_POINTS[game_id]
        pbp['EVENTNUM'] = pbp['EVENTNUM'].replace(bad_data_points)
    if game_id in DATA_TO_DELETE:
        delete_mask = ~pbp['EVENTNUM'].isin(DATA_TO_DELETE[game_id])
        pbp = pbp[delete_mask]
    pbp['seconds'] = pbp['PCTIMESTRING'].str.split(':').apply(lambda x: int(x[1]) + 60 * int(x[0]))
    pbp = (pbp.sort_values(['PERIOD', 'seconds', 'EVENTNUM'], ascending=[True, False, True])
               .reset_index(drop=True))

    # Go through each row and based on actions figure out who was on the court
    for index, row in pbp.iterrows():
        # As long as not start of quarter
        if row.EVENTMSGTYPE != 12:
            pbp.ix[index, NEW_COLS] = pbp.ix[index-1, NEW_COLS]
        home_open = pbp.loc[index][HOME_COLS].isnull().sum()
        away_open = pbp.loc[index][AWAY_COLS].isnull().sum()
        # EVENTMSGTYPE = 6 means foul
        # EVENTMSGACTIONTYPE =16 and 11 are events that I found to cause errors
        # EVENTMSGTYPE = 8 means substitution
        # EVENTMSGTYPE = 9 means timeout
        # EVENTMSGTYPE = 11 means
        if ((row.EVENTMSGTYPE not in [8, 9, 11, 10])
                & (not ((row.EVENTMSGTYPE == 6) & (row.EVENTMSGACTIONTYPE == 16)))
                & (not ((row.EVENTMSGTYPE == 6) & (row.EVENTMSGACTIONTYPE == 12)))
                & (not ((row.EVENTMSGTYPE == 6) & (row.EVENTMSGACTIONTYPE == 11)))
                & (not ((row.EVENTMSGTYPE == 9) & (row.EVENTMSGACTIONTYPE == 2)))):
            if row.PERSON1TYPE in [4, 5]:
                if row.PERSON1TYPE == 5:
                    if (pbp.ix[index, AWAY_COLS] == row.PLAYER1_ID).sum() < 1:
                        pbp.ix[index, AWAY_COLS[away_open-1]] = row.PLAYER1_ID
                        away_open -= 1
                        if away_open < 0:
                            #huh
                            warnings.warn('Error on game {} on play {}'.format(game_id, index))
                        fill_up(pbp, index, row.PLAYER1_ID, AWAY_COLS)
                else:
                    if (pbp.ix[index, HOME_COLS] == row.PLAYER1_ID).sum() < 1:
                        pbp.ix[index, HOME_COLS[home_open-1]] = row.PLAYER1_ID
                        home_open -= 1
                        if home_open < 0:
                            #huh
                            warnings.warn('Error on game {} on play {}'.format(game_id, index))
                        fill_up(pbp, index, row.PLAYER1_ID, HOME_COLS)
            if row.PERSON2TYPE in [4, 5]:
                if row.PERSON2TYPE == 5:
                    if (pbp.ix[index, AWAY_COLS] == row.PLAYER2_ID).sum() < 1:
                        pbp.ix[index, AWAY_COLS[away_open-1]] = row.PLAYER2_ID
                        away_open -= 1
                        if away_open < 0:
                            #huh
                            warnings.warn('Error on game {} on play {}'.format(game_id, index))
                        fill_up(pbp, index, row.PLAYER2_ID, AWAY_COLS)
                else:
                    if (pbp.ix[index, HOME_COLS] == row.PLAYER2_ID).sum() < 1:
                        pbp.ix[index, HOME_COLS[home_open-1]] = row.PLAYER2_ID
                        home_open -= 1
                        if home_open < 0:
                            #huh
                            warnings.warn('Error on game {} on play {}'.format(game_id, index))
                        fill_up(pbp, index, row.PLAYER2_ID, HOME_COLS)
            if row.PERSON3TYPE in [4, 5]:
                if row.PERSON3TYPE == 5:
                    if (pbp.ix[index, AWAY_COLS] == row.PLAYER3_ID).sum() < 1:
                        pbp.ix[index, AWAY_COLS[away_open-1]] = row.PLAYER3_ID
                        away_open -= 1
                        if away_open < 0:
                            #huh
                            warnings.warn('Error on game {} on play {}'.format(game_id, index))
                        fill_up(pbp, index, row.PLAYER3_ID, AWAY_COLS)
                else:
                    if (pbp.ix[index, HOME_COLS] == row.PLAYER3_ID).sum() < 1:
                        pbp.ix[index, HOME_COLS[home_open-1]] = row.PLAYER3_ID
                        home_open -= 1
                        if home_open < 0:
                            #huh
                            warnings.warn('Error on game {} on play {}'.format(game_id, index))
                        fill_up(pbp, index, row.PLAYER3_ID, HOME_COLS)
        elif row.EVENTMSGTYPE == 8:
            if row.PERSON1TYPE in [4, 5]:

                player1 = row.PLAYER1_ID
                player2 = row.PLAYER2_ID
                if row.PERSON1TYPE == 5:
                    if (pbp.ix[index, AWAY_COLS] == player1).sum() > 0:
                        pbp.ix[index, pbp.ix[index, AWAY_COLS][pbp.ix[index, AWAY_COLS] ==
                                                               player1].index[0]] = player2
                    else:
                        pbp.ix[index, AWAY_COLS[away_open-1]] = player2
                        away_open -= 1
                        if away_open < 0:
                            #huh
                            warnings.warn('Error on game {} on play {}'.format(game_id, index))
                        fill_up(pbp, index, player1, AWAY_COLS)
                else:
                    if (pbp.ix[index, HOME_COLS] == player1).sum() > 0:
                        pbp.ix[index, pbp.ix[index, HOME_COLS][pbp.ix[index, HOME_COLS] ==
                                                               player1].index[0]] = player2
                    else:
                        pbp.ix[index, HOME_COLS[home_open-1]] = player2
                        home_open -= 1
                        if home_open < 0:
                            #huh
                            warnings.warn('Error on game {} on play {}'.format(game_id, index))
                        fill_up(pbp, index, player1, HOME_COLS)
    return pbp


def patch_play_by_play(pbp, game_id):
    """Patch play by play data that has nans for player ids by looking at boxscore stats."""
    away_team = pbp.ix[pbp.PERSON1TYPE == 5, 'PLAYER1_TEAM_ID'].unique()[0]
    home_team = pbp.ix[pbp.PERSON1TYPE == 4, 'PLAYER1_TEAM_ID'].unique()[0]
    # See if any player cols are Null
    col_counts = pbp[NEW_COLS].isnull().sum()
    for index, col in enumerate(col_counts):
        if col > (pbp['EVENTMSGTYPE'] == 12).sum():
            for period in pbp.ix[pbp[NEW_COLS[index]].isnull() & (pbp.EVENTMSGTYPE != 12),
                                 'PERIOD'].unique():
                team = away_team
                team_cols = AWAY_COLS
                if index < 5:
                    team = home_team
                    team_cols = HOME_COLS
                start_index = min(pbp.ix[(pbp.PERIOD == period), :].index)+1
                boxscore_df = get_boxscore_for_game_quarter(game_id, period)
                mins = '5:00'
                if (period == 6) & (game_id == '0021701054'):
                    mins = '4:58'
                if period < 5:
                    mins = '12:00'
                played_all = boxscore_df.ix[(boxscore_df.MIN == mins) & (boxscore_df.TEAM_ID == team)]
                missing_player = np.nan
                for player_id in played_all.PLAYER_ID:
                    if player_id not in list(pbp.ix[start_index, team_cols]):
                        missing_player = player_id
                if not np.isnan(missing_player):
                    pbp.ix[(pbp.PERIOD == period) & (pbp.EVENTMSGTYPE != 12),
                           NEW_COLS[index]] = missing_player
                else:
                    raise warnings.warn('Error - need to fix minutes: ' + str(game_id))
    col_counts = pbp[NEW_COLS].isnull().sum()
    if sum(col_counts) != (pbp.EVENTMSGTYPE == 12).sum() * 10:
        warnings.warn('Error - need to fix minutes: ' + str(game_id))
    return pbp
