import pandas as pd
import hockeydata.database_session.database_session as ds
import hockeydata.database_creator.database_creator as db
import hockeydata.database_queries.database_query as dq
db_path = "C:/Users/janzi/Documents/repositories/elite/database/hockey_v17_test.db"
query_path = "C:/Users/janzi/Documents/repositories/elite/powerbi/queries.json"

#connection to database is managed by class GetDatabaseSession
#which takes one parameter with the path to the existing DB
#or path where the new DB should be created in case that it does not
#already exist at a given location

session_o = ds.GetDatabaseSession(db_path=db_path)
session_o.set_up_connection()
filter = [db.Season.season.in_(["2022-2023"])]

getter = dq.DbDataGetter(db_session=session_o.session)


data_goals =  getter.get_db_query_result(query_name="goals", query_file_path=query_path)
df_goals = pd.DataFrame(data_goals)
df_goals_sum = df_goals[['player_id', 'name']].value_counts().reset_index(name='n_goals')
data_assits =  getter.get_db_query_result(query_name="assists", query_file_path=query_path)
df_assist = pd.DataFrame(data_assits)
df_assist_sum = df_assist[['player_id', 'name']].value_counts().reset_index(name='n_assits')
df_points = pd.merge(df_goals_sum, df_assist_sum, on="player_id")
df_points["p"] = df_points['n_goals'] + df_points['n_assits']
data_shifts =  getter.get_db_query_result(query_name="shifts", query_file_path=query_path)
df_shifts = pd.DataFrame(data_shifts)
df_shifts['shift_duration'] = df_shifts['shift_end'] - df_shifts["shift_start"]
df_shifts_sum = df_shifts[['id', 'shift_duration']].groupby('id').sum()
df_shifts_sum = df_shifts[['id', 'shift_duration']].groupby('id').sum()
df_points = pd.merge(df_points, df_shifts_sum, left_on="player_id", right_on="id")
df_points['min_per_point'] = ((df_points['shift_duration'] / df_points['p']).round(3) / 60).round(3)
df_points['min_per_goal'] = ((df_points['shift_duration'] / df_points['n_goals']).round(3) / 60).round(3)