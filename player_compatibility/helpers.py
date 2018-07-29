import numpy as np
import pandas as pd
import tqdm as tqdm

PT_SERIES = pd.Series({
    'Above the Break 3': 3,
    'Backcourt': 3,
    'In The Paint (Non-RA)': 2,
    'Left Corner 3': 3,
    'Mid-Range': 2,
    'Restricted Area': 2,
    'Right Corner 3': 3
})


logit_func = lambda x: 1./(1 + np.exp(-x))


def get_base_series(index):
    """Get series with basic lineup to score."""
    base = pd.Series(0, index=index)
    base['int'] = 1
    base['defGuard'] = 2
    base['defForward'] = 2
    base['defCenter'] = 1
    base['offGuard'] = 2
    base['offForward'] = 2
    base['offCenter'] = 1
    return base


def score_series(eval_series, loc_coefs, pct_coefs):
    """Helper function to get expected points for a lineup."""
    eval_loc = (loc_coefs * eval_series).sum(axis=1).apply(np.exp)
    eval_loc = eval_loc/sum(eval_loc)
    eval_pct = (pct_coefs * eval_series).sum(axis=1).apply(logit_func)
    return (eval_loc * eval_pct * PT_SERIES).sum()


def create_series_for_shooter(shooter_id, player_pos_dict, index):
    """Create base series with shooter id as the shooter."""
    shooter_pos = player_pos_dict[shooter_id]
    eval_series = get_base_series(index)
    eval_series['shoot{}'.format(shooter_pos)] = 1
    eval_series['off{}'.format(shooter_pos)] -= 1
    eval_series['shoot{}'.format(shooter_id)] = 1
    return eval_series


def create_series_for_pair(shooter_id, off_id, player_pos_dict, index):
    shooter_pos = player_pos_dict[shooter_id]
    off_pos = player_pos_dict[off_id]
    eval_series = get_base_series(index)
    eval_series['shoot{}'.format(shooter_pos)] = 1
    eval_series['off{}'.format(shooter_pos)] -= 1
    eval_series['shoot{}'.format(shooter_id)] = 1
    eval_series['off{}'.format(off_id)] = 1
    if (off_pos == 'Center') & (shooter_pos == 'Center'):
        eval_series['offForward'] -= 1
        eval_series['offCenter'] += 1
    return eval_series


def get_matrix_of_compatibility(player_pos_dict, loc_coefs, pct_coefs, player_id_to_name):
    """Get matrix of player compatibility."""
    all_scores = []
    index = pct_coefs.columns
    for shooter_id in tqdm.tqdm(player_pos_dict.keys()):
        player_scores = {}
        player_shoot_series = create_series_for_shooter(shooter_id, player_pos_dict, index)
        player_off_score = score_series(player_shoot_series, loc_coefs, pct_coefs)
        for player in player_pos_dict.keys():
            pair_name = player_id_to_name[player]
            pair_series = create_series_for_pair(shooter_id, player, player_pos_dict, index)
            player_scores[pair_name] = score_series(pair_series, loc_coefs,
                                                                    pct_coefs)
        player_name = player_id_to_name[shooter_id]
        off_compat = pd.Series(player_scores, name=player_name) - player_off_score
        all_scores.append(off_compat)
    return pd.concat(all_scores, axis=1)