import unidecode
from textdistance.algorithms import hamming, levenshtein
from collections import defaultdict
import itertools
import pandas as pd

def clean_name(ser):
    return ser.apply(unidecode.unidecode).str.replace('-', ' ').str.replace(r'[^0-9a-zA-Z ]+', '').str.lower()


suffixes = ('sr', 'jr', 'ii', 'iii', 'iv')

def preprocessing(df):
    name_splits = df['clean_name'].str.split(' ').values
    df['clean_first_name'] = [split[0] for split in name_splits]
    df['clean_last_name'] = [split[-1]  if split[-1] not in suffixes else split[-2] for split in name_splits]
    df['suffix'] = [split[-1]  if split[-1] in suffixes else '' for split in name_splits]
    df['basic_name'] = [' '.join(split) if split[-1] not in suffixes else ' '.join(split[:-1]) for split in name_splits]
    return df



def get_buckets(df):
    buckets = defaultdict(list)
    for _, row in df.iterrows():
        buckets[f'LAST-{row["clean_last_name"]}'].append(row['uuid'])
        buckets[f'FIRST-{row["clean_first_name"]}'].append(row['uuid'])
    return buckets


def get_pairs(buckets_1, buckets_2):
    pairs = []
    all_keys = set(buckets_1.keys()).union(buckets_2.keys())
    for key in all_keys:
        pairs.extend(list(itertools.product(buckets_1[key], buckets_2[key])))
    return set(pairs)


def same_start(str1, str2):
    same = 0
    for i in range(min(len(str1), len(str2))):
        if str1[i] == str2[i]:
            same +=1
        else: 
            return same
    return same

def create_features(feature_df):
    features = []
    
    for column in ['basic_name','clean_first_name', 'clean_last_name', 'start_year', 'end_year', 'suffix']:
        feat_col = f'{column}___equality'
        feature_df[feat_col] = feature_df[f'{column}_1'] == feature_df[f'{column}_2'] 
        features.append(feat_col)

    feature_df['same_times'] = feature_df['start_year___equality'] & feature_df['end_year___equality']
    features.append('same_times')

    for column in ['start_year', 'end_year']:
        feat_col = f'{column}___difference'
        feature_df[feat_col] = feature_df[f'{column}_1'] - feature_df[f'{column}_2'] 
        features.append(feat_col)

    for column in ['basic_name', 'clean_first_name', 'clean_last_name']:
        feat_col = f'{column}___hamming'
        feature_df[feat_col] = [hamming(str1, str2) for str1, str2 in feature_df[[f'{column}_1', f'{column}_2']].values]
        features.append(feat_col)

    for column in ['basic_name', 'clean_first_name', 'clean_last_name']:
        feat_col = f'{column}___levenshtein'
        feature_df[feat_col] = [levenshtein(str1, str2) for str1, str2 in feature_df[[f'{column}_1', f'{column}_2']].values]
        features.append(feat_col)

    for column in ['basic_name', 'clean_first_name', 'clean_last_name']:
        for suffix in ['1', '2']:
            feat_col = f'{column}_{suffix}___length'
            feature_df[feat_col] = feature_df[f'{column}_{suffix}'].str.len()
            features.append(feat_col)

    min_hamming_1 = feature_df.groupby('uuid_1')['basic_name___hamming'].min().to_frame('min_hamming_1').reset_index()
    min_hamming_2 = feature_df.groupby('uuid_2')['basic_name___hamming'].min().to_frame('min_hamming_2').reset_index()
    feature_df = feature_df.merge(min_hamming_1).merge(min_hamming_2)
    features.append('min_hamming_1')
    features.append('min_hamming_2')

    min_hamming_1 = feature_df[feature_df['same_times'] == 1].groupby('uuid_1')['basic_name___hamming'].min().to_frame('min_hamming_1_same_times').reset_index()
    min_hamming_2 = feature_df[feature_df['same_times'] == 1].groupby('uuid_2')['basic_name___hamming'].min().to_frame('min_hamming_2_same_times').reset_index()
    feature_df = feature_df.merge(min_hamming_1, how='left').merge(min_hamming_2, how='left').fillna(100)
    features.append('min_hamming_1_same_times')
    features.append('min_hamming_2_same_times')

    feature_df['same_first_initial'] = feature_df['clean_first_name_1'].str[0] == feature_df['clean_first_name_2'].str[0]
    features.append('same_first_initial')

    feature_df['before_merger'] = feature_df['start_year_1'] < 1977
    features.append('before_merger')
    feature_df['hamming_diff'] = feature_df['basic_name___hamming'] * 2 - feature_df['min_hamming_1'] - feature_df['min_hamming_2']
    features.append('hamming_diff')
    feature_df['hamming_diff_same_times'] = feature_df['basic_name___hamming'] * 2 - feature_df['min_hamming_1_same_times'] - feature_df['min_hamming_2_same_times']
    features.append('hamming_diff_same_times')
    feature_df['name_match'] = feature_df['clean_first_name___equality'] & feature_df['clean_last_name___equality']
    features.append('name_match')
    
    feature_df['name_subset'] = [a in b or b in a for a,b in feature_df[['clean_name_1', 'clean_name_2']].values]

    features.append('name_subset')
    
    return feature_df, features


def get_label_df(initial_pos_labels, pair_df):
    pos_label_df = pd.DataFrame(initial_pos_labels, columns=['uuid_1', 'uuid_2'])
    pos_label_df['target'] = 1
    neg_labels_df = pd.concat([
        pair_df[pair_df['uuid_1'].isin(pos_label_df['uuid_1'])],
        pair_df[pair_df['uuid_2'].isin(pos_label_df['uuid_2'])],
    ])
    neg_labels_df['target'] = 0
    label_df = pd.concat([pos_label_df, neg_labels_df]).drop_duplicates(keep='first',subset=['uuid_1', 'uuid_2'])
    return label_df
