import pandas as pd

import hockeydata.database_session.database_session as ds
import hockeydata.database_creator.database_creator as db
import hockeydata.database_queries.database_query as dq

db_path = "C:/Users/janzi/Documents/repositories/elite/database/hockey_v17_test.db"
query_path = "C:/Users/janzi/Documents/repositories/elite/powerbi/queries.json"

#set up connection to db
session_o = ds.GetDatabaseSession(db_path=db_path)
session_o.set_up_connection()
filter = [db.Season.season.in_(["2022-2023"])]
#get data
getter = dq.DbDataGetter(db_session=session_o.session)
#get goals sums by player
data_goals =  getter.get_db_query_result(query_name="goals", query_file_path=query_path)
df_goals = pd.DataFrame(data_goals)
df_goals_sum = df_goals[['player_id']].value_counts().reset_index(name='n_goals')
#get assist sums by player
data_assits =  getter.get_db_query_result(query_name="assists", query_file_path=query_path)
df_assist = pd.DataFrame(data_assits)
df_assist_sum = df_assist[['player_id']].value_counts().reset_index(name='n_assits')
#get points sums
df_points = pd.merge(df_goals_sum[["player_id", "n_goals"]], df_assist_sum[["player_id", "n_assits"]], on="player_id")
df_points["points"] = df_points['n_goals'] + df_points['n_assits']
data_shifts =  getter.get_db_query_result(query_name="shifts", query_file_path=query_path)
df_shifts = pd.DataFrame(data_shifts)
df_shifts['shift_duration'] = df_shifts['shift_end'] - df_shifts["shift_start"]
df_shifts_sum = df_shifts[['id', 'shift_duration']].groupby('id').sum()
df_shifts_sum = df_shifts[['id', 'shift_duration']].groupby('id').sum()
#get minutes divided by stats
df_points = pd.merge(df_points, df_shifts_sum, left_on="player_id", right_on="id")
df_points['min_per_point'] = ((df_points['shift_duration'] / df_points['points']).round(3) / 60).round(3)
df_points['min_per_goal'] = ((df_points['shift_duration'] / df_points['n_goals']).round(3) / 60).round(3)
#add general info
data_info =  getter.get_db_query_result(query_name="player_basic_info", query_file_path=query_path)
df_info = pd.DataFrame(data_info)
df_points = pd.merge(df_points, df_info, left_on="player_id", right_on="id")
df_points = df_points.drop(columns="id").rename(columns={"country_s": "country"})
df_points 