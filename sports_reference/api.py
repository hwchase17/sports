from bs4 import BeautifulSoup, Comment
import numpy as np
import pandas as pd
import sqlite3


def extract_table(table_str, header_row=1, start_of_rows=2, get_url=False):
    """Extract table from html."""
    columns = [t['data-stat'] for t in table_str.findAll('tr')[header_row].findAll('th')]
    rows = [
        [r.find('th').text] +
        [t.text for t in r.findAll('td')] for r in table_str.findAll('tr')[start_of_rows:]
    ]
    df = pd.DataFrame(rows, columns=columns)
    if get_url:
        extra_rows = [[t.find('a')['href'] if t.find('a') else np.nan for t in r.findAll('td')]
                      for r in table_str.findAll('tr')[start_of_rows:]]
        extra_df = pd.DataFrame(extra_rows, columns=[c+'_url' for c in columns[1:]])
        df = pd.concat([df, extra_df], axis=1)
    return df


def find_table(soup, table_name):
    """Find html for table, even if in a comment."""
    tables = soup.findAll('table', {"id": table_name})
    if tables:
        return tables[0]
    comments = soup.findAll(text=lambda text: isinstance(text, Comment))
    table_comment = next(c for c in comments if 'id="{}"'.format(table_name) in c)
    table_soup = BeautifulSoup(str(table_comment), "lxml")
    return table_soup.findAll('table', {"id": table_name})[0]


def create_insert_table_sql(table_name, col_mappings):
    """Create sql for creating and inserting a table."""
    col_types = ', '.join([k + ' ' + v for k, v in col_mappings.items()])
    create_sql = 'CREATE TABLE {} ({})'.format(table_name, col_types)
    placeholders = ', '.join(['?' for _ in col_mappings.items()])
    insert_sql = 'INSERT INTO {} VALUES ({})'.format(table_name, placeholders)
    return create_sql, insert_sql


def save_df_to_sqlite(sqlite_db, df, cols, table_name):
    """Helper to save df to sqlite."""
    with sqlite3.connect(sqlite_db) as conn:
        cur = conn.cursor()
        create_sql, insert_sql = create_insert_table_sql(table_name, cols)
        cur.execute(create_sql)
        cur.executemany(insert_sql, df[list(cols.keys())].values)
