import hockeydata.database_creator.database_creator as db
import database_session.database_session as ds
import hockeydata.database_queries.database_query as dq

import unicodedata

from sqlalchemy import insert


def remove_diacritics(text):
    normalized = unicodedata.normalize("NFD", text)
    without_diacritics = ''.join(
        c for c in normalized if unicodedata.category(c) != 'Mn'
    )
    return without_diacritics


DB_PATH = "./database/hockey_v15_test.db"


session_o = ds.GetDatabaseSession(db_path=DB_PATH)
session_o.set_up_connection()

query_o = dq.DbDataGetter(db_session=session_o.session)


data = query_o.get_db_query_result("nhl_elite_names")
name_dict = {tuple_[0]: tuple_[1] for tuple_ in data}

query_o = dq.DbDataGetter(db_session=session_o.session)

data = query_o.get_db_query_result("nhl_elite_names")
name_dict = {tuple_[0]: tuple_[1] for tuple_ in data}

firstnames = []
for k, v in name_dict.items():
    firstnames.append((k.split()[0], v.split()[0]))


firstnames_unique = set([combo for combo in firstnames if remove_diacritics(combo[0])!=remove_diacritics(combo[1])])


stmt = insert(db.FirstNameMapper).values([
    {'name': d[0], 'alternative_name': d[1]} for d in firstnames_unique
])
session_o.session.execute(stmt)

session_o.session.commit()