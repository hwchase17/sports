import cgi
import json

import pandas as pd
import requests as _requests
from .constants import HEADER_DATA, BASE_URL


def fetch_from_nba_stats_api(url_modifier, api_params):
    """Pull from nba stats api given url modifier and api params."""
    pull_url = cgi.urlparse.urljoin(BASE_URL, url_modifier)
    response = _requests.get(pull_url, params=api_params, headers=HEADER_DATA)
    data = json.loads(response.content)
    df = pd.DataFrame(data['resultSets'][0]['rowSet'], columns=data['resultSets'][0]['headers'])
    return df


def get_all_games_for_year(yr_string):
    """Get all games for a given year."""
    url_modifier = 'leaguegamelog'
    api_params = {
        'LeagueID': '00',
        'Season': yr_string,
        'PlayerOrTeam': 'T',
        'Direction': 'DESC',
        'SeasonType': 'Regular Season',
        'Sorter': 'FGM'
    }
    return fetch_from_nba_stats_api(url_modifier, api_params)


def get_play_by_play_for_game(game_id):
    """Get raw play by play data for a given game id."""
    url_modifier = 'playbyplayv2'
    api_params = {
        'GameID': game_id,
        'StartPeriod': 0,
        'EndPeriod': 0
    }
    return fetch_from_nba_stats_api(url_modifier, api_params)


def get_boxscore_for_game_quarter(game_id, period):
    """Get boxscore stats for a specific period of a game."""
    url_modifier = 'boxscoretraditionalv2'
    api_params = {
        'GameID': game_id,
        'StartPeriod': period,
        'EndPeriod': period,
        'StartRange': 0,
        'EndRange': 0,
        'RangeType': 1
    }
    return fetch_from_nba_stats_api(url_modifier, api_params)


def get_shot_log(year, player_id):
    """Get shot log for a player for a given year."""
    url_modifier = 'shotchartdetail'
    api_params = {
        'DateFrom': '',
        'DateTo': '',
        'GameSegment': '',
        'LastNGames': 0,
        'LeagueID': "00",
        'Location': '',
        'Month': 0,
        'OpponentTeamID': 0,
        'Outcome': '',
        'Period': 0,
        'PlayerID': player_id,
        'Season': year,
        'SeasonSegment': '',
        'SeasonType': "Regular Season",
        'TeamID': 0,
        'VsConference': '',
        'VsDivision': '',
        'GameID': '',
        'PlayerPosition': '',
        'RookieYear': '',
        'ContextMeasure': 'FGA'
    }
    return fetch_from_nba_stats_api(url_modifier, api_params)


def get_players_for_season(season):
    """Get data for all players given a season"""
    url_modifier = "commonallplayers"
    api_params = {
        'IsOnlyCurrentSeason': "1",
        'LeagueID': '00',
        'Season': season
    }
    return fetch_from_nba_stats_api(url_modifier, api_params)


def get_player_info(player_id):
    url_modifier = 'commonplayerinfo'
    api_params = {'PlayerID': player_id}
    return fetch_from_nba_stats_api(url_modifier, api_params)
