import pandas as pd
import numpy as np

VALID_POS = ['WR', 'TE', 'RB']
TRACKING_FILE_STUB = '{}/tracking_gameId_{}.csv'
END_EVENTS = {'pass_arrived'}
INDEX_COLS = ['gameId', 'playId', 'nflId']


def get_side(df):
    """Helper to get side."""
    indx = (df['PlayResult'].abs() - df['x_diff'].abs()).abs().sort_values()
    return np.sign(df.loc[indx.index[0], 'x_diff'])


def get_relevant_plays(game_plays_df):
    """Get relevant plays."""
    game_plays_df['x_diff'] = game_plays_df['x_loc'].diff().shift(-1)

    same_team_mask = game_plays_df['possessionTeam'].shift() == game_plays_df['possessionTeam']
    large_play_mask = game_plays_df['PlayResult'] > 3
    not_ST_play = ~(game_plays_df['isSTPlay'].shift().fillna(True))
    not_penalty_play = ~game_plays_df['isPenalty']
    same_quarter_mask = game_plays_df['quarter'] == game_plays_df['quarter'].shift()

    return game_plays_df[
        same_team_mask & same_quarter_mask & not_ST_play & not_penalty_play & large_play_mask
        ]


def test_get_rel_plays():
    """Testing function."""
    mock_df = pd.DataFrame([
        ['a', 8, False, False, 1, .88],  # at beginning
        ['a', 8, False, False, 1, .88],  # yes
        ['a', 1, False, False, 1, .91],  # not long enough
        ['b', 8, False, False, 1, .86],  # possession change
        ['b', 8, False, True, 1, .85],  # quarter change next
        ['b', 8, False, False, 2, .84],  # is penalty next
        ['b', 8, False, False, 2, .83],  # yes
        ['b', 8, True, False, 2, .70],   # yes
        ['b', 8, False, True, 2, .60],  # special team is before
    ], columns=['possessionTeam', 'PlayResult', 'isSTPlay', 'isPenalty', 'quarter', 'x_loc'])
    output = get_relevant_plays(mock_df)
    expected_df = pd.DataFrame([
        ['a', 8, False, False, 1, .88, .91 - .88],
        ['b', 8, False, False, 2, .83, .7 - .83],
        ['b', 8, True, False, 2, .7, .6 - .7],
    ],
        columns=['possessionTeam', 'PlayResult', 'isSTPlay', 'isPenalty', 'quarter', 'x_loc',
                 'x_diff'],
        index=[1, 6, 7]
    )
    pd.testing.assert_frame_equal(expected_df, output)


test_get_rel_plays()


def get_dict_of_sides(tracking_df, game_plays_df):
    """Helper to get side of field for team/quarter pair."""
    # Get location of center
    rel_tracking = tracking_df[(tracking_df['playerPos'] == 'C') & (tracking_df['frame.id'] == 15)]
    # Get location of center on first moment of play
    x_pos_on_play = rel_tracking.groupby('playId')['x'].nth(0).to_frame('x_loc').reset_index()
    # Merge with game play data
    game_plays_df = game_plays_df.merge(x_pos_on_play)

    rel_plays_df = get_relevant_plays(game_plays_df)

    side_dict = rel_plays_df.groupby(['quarter', 'possessionTeam']).apply(get_side).to_dict()
    teams = tracking_df['teamAbbr'].dropna().unique()
    if len(teams) != 2:
        raise ValueError
    for i in game_plays_df['quarter'].unique():
        for t in teams:
            if (i, t) not in side_dict:
                side_dict[(i, t)] = -side_dict[(i, list(set(teams).difference({t}))[0])]
    return side_dict


def get_routes_for_game(game_id, passes_df, plays_df, home_away_dict, player_pos_dict, data_folder):
    """Function to get relevant routes for games."""
    # Get all tracking data for game, only where theres actually tracking data
    tracking_df = pd.read_csv(TRACKING_FILE_STUB.format(data_folder, game_id)).dropna(subset=['x'])
    # Get all passes for game
    game_passes_df = passes_df[passes_df['gameId'] == game_id]
    # Get all plays where there is tracking data fro
    plays_with_tracking_data = tracking_df[tracking_df['displayName'] == 'football']['playId']
    game_plays_df = plays_df[
        (plays_df['gameId'] == game_id) & plays_df['playId'].isin(plays_with_tracking_data)
    ]

    # Get relevant team abbreviations
    sub_home_away_dict = {
        'home': home_away_dict['home'][game_id],
        'away': home_away_dict['away'][game_id]
    }
    tracking_df['teamAbbr'] = tracking_df['team'].apply(sub_home_away_dict.get)
    tracking_df['playerPos'] = tracking_df['nflId'].apply(player_pos_dict.get)
    dict_of_sides = get_dict_of_sides(tracking_df, game_plays_df)

    # Get a side multiplier
    game_passes_df['mult'] = [
        dict_of_sides[p] for p in zip(game_passes_df['quarter'], game_passes_df['possessionTeam'])
    ]
    tracking_df = tracking_df.merge(
        game_passes_df[['playId', 'mult', 'possessionTeam']], how='inner', on='playId'
    )

    # Get the position of the ball when snapped, to normalize player routes
    ball_snap_mask = tracking_df['event'] == 'ball_snap'
    ball_snap = (tracking_df[ball_snap_mask].groupby('playId')['frame.id'].first()
                 .to_frame('ball_snap').reset_index())

    pass_arrived = (tracking_df[tracking_df['event'].isin(END_EVENTS)].groupby('playId')['frame.id']
                    .first().to_frame('end_events').reset_index())

    merged_tracking = tracking_df.merge(ball_snap).merge(pass_arrived)

    rel_series_mask = (
        ((merged_tracking['playerPos'] == 'C') | (merged_tracking['displayName'] == 'football')) &
        (merged_tracking['ball_snap'] == merged_tracking['frame.id'])
    )

    # Get info of centers/football at time of snap where we have locations
    filtered_df = merged_tracking[rel_series_mask].dropna(subset=['x', 'y'])
    # Sort by dir (football does not have dir, so will be last, so we get football location if poss
    ball_info = filtered_df.sort_values('dir').groupby('playId', as_index=False).last()
    ball_info = ball_info.rename(columns={'x': 'ball_x', 'y': 'ball_y'})

    relevant_tracking = merged_tracking[
        (merged_tracking['teamAbbr'] == merged_tracking['possessionTeam']) &
        (merged_tracking['playerPos'].isin(VALID_POS)) &
        (merged_tracking['frame.id'] >= merged_tracking['ball_snap']) &
        (merged_tracking['frame.id'] <= merged_tracking['end_events'])
    ].merge(ball_info[['playId', 'ball_x', 'ball_y']], how='left', on='playId')

    # Adjusted for where the ball is
    relevant_tracking['mod_y'] = relevant_tracking['y'] - relevant_tracking['ball_y']
    relevant_tracking['mod_x'] = (
        (relevant_tracking['x'] - relevant_tracking['ball_x']) * relevant_tracking['mult']
    )
    # Adjusted for towards center/sideline
    relevant_tracking['mod_mod_y'] = relevant_tracking['mod_y'].abs()
    return relevant_tracking


def feature_route(df):
    """Get features like x, y, and direction for each time step."""
    df['start_x'] = df['mod_x'].shift()
    df['start_y'] = df['mod_mod_y'].shift()
    df['delta_x'] = df['mod_x'] - df['start_x']
    df['delta_y'] = df['mod_mod_y'] - df['start_y']
    return df[['start_x', 'start_y', 'delta_x', 'delta_y']]


def assign_direction(df):
    """Assign one of nine directions"""
    df['cat_dir'] = np.nan
    mask1 = (df['delta_x'] >= 0) & (df['delta_y'] >= 0)
    mask2 = (df['delta_x'] >= 0) & (df['delta_y'] < 0)
    mask3 = (df['delta_x'] < 0) & (df['delta_y'] >= 0)
    mask4 = (df['delta_x'] < 0) & (df['delta_y'] < 0)
    mask5 = (df['delta_x'] > 0) & (df['delta_y'].abs() * 3 < df['delta_x'].abs())
    mask6 = (df['delta_x'] < 0) & (df['delta_y'].abs() * 3 < df['delta_x'].abs())
    mask7 = (df['delta_y'] > 0) & (df['delta_x'].abs() * 3 < df['delta_y'].abs())
    mask8 = (df['delta_y'] < 0) & (df['delta_x'].abs() * 3 < df['delta_y'].abs())
    mask9 = df['delta_x'] ** 2 + df['delta_y'] ** 2 < .02 ** 2
    df.loc[mask1, 'cat_dir'] = 1
    df.loc[mask2, 'cat_dir'] = 2
    df.loc[mask3, 'cat_dir'] = 3
    df.loc[mask4, 'cat_dir'] = 4
    df.loc[mask5, 'cat_dir'] = 5
    df.loc[mask6, 'cat_dir'] = 6
    df.loc[mask7, 'cat_dir'] = 7
    df.loc[mask8, 'cat_dir'] = 8
    df.loc[mask9, 'cat_dir'] = 9
    df['cat_dir'] = pd.Categorical(df['cat_dir'], categories=range(1, 10))
    return df


def get_route_df(all_routes_df):
    """Get route df."""
    all_routes_df_start = all_routes_df[
        ['frame.id', 'gameId', 'playId', 'nflId', 'mod_x', 'mod_mod_y']]

    all_routes_df_start['frame.id'] += 1

    all_routes_df_start = all_routes_df_start.rename(
        columns={'mod_x': 'start_x', 'mod_mod_y': 'start_y'})

    df = all_routes_df.merge(all_routes_df_start)
    df['delta_x'] = df['mod_x'] - df['start_x']
    df['delta_y'] = df['mod_mod_y'] - df['start_y']
    cols_to_return = ['start_x', 'start_y', 'delta_x', 'delta_y', 'frame.id']
    return df.set_index(['gameId', 'playId', 'nflId'])[cols_to_return]


def group_to_matrix(df, max_len):
    """Helper function to go from df to np_array"""
    # One hot encode the columns
    df = df.join(pd.get_dummies(df['cat_dir']))
    # Drop columns we don't want to be a feature
    df = df.drop(INDEX_COLS + ['cat_dir', 'frame.id'], 1)
    if df.shape[0] > max_len:
        # If you want to toss all paths that go longer than max_len, uncomment line below
        # return np.nan
        # if df is too long, cut it off
        df = df.iloc[:max_len]
    if df.shape[0] < max_len:
        # If not
        missing_n = max_len - df.shape[0]
        index = [df.index[0] for _ in range(missing_n)]
        df = pd.concat([
            pd.DataFrame(0, columns=df.columns, index=index),
            df
        ])

    return df.T.values


def load_df_to_np_matrix(file_path, max_len=80):
    """Load file and get in the right dimensions."""
    df = pd.read_msgpack(file_path)
    # Dropna only relevant if you are tossing long time series
    res = df.groupby(INDEX_COLS).apply(group_to_matrix, max_len).dropna()
    return np.concatenate([np.expand_dims(arr, axis=-1) for arr in list(res.values)], axis=-1)
