from sqlalchemy import create_engine, MetaData, Table, text
from sqlalchemy.orm import sessionmaker

import database_creator.database_creator as db


DB_URL = "sqlite:///./database/hockey_v14_test.db"

engine = create_engine(DB_URL)

Session = sessionmaker(bind=engine)
session = Session()

DELETE_ORDER = [
    db.Match,
    db.Play,
    db.PlayerShift,
    db.PlayerOnIce,
    db.GoalPlay,
    db.AssistPlay,
    db.ShotPlay,
    db.MissedShotPlay,
    db.BlockedShotPlay,
    db.HitPlay,
    db.FaceoffPlay,
    db.GiveawayPlay,
    db.TakeawayPlay,
    db.PenaltyPlay,
    db.ChallengePlay,
    db.DelayedPenaltyPlay,
    db.PeriodPlay,
    db.GameStopagePlay,
    db.PlayType,
    db.ShotType,
    db.ZoneType,
    db.ShotResult,
    db.PenaltyType,
    db.DeflectionType,
    db.BlockerType,
    db.ChallengeReason,
    db.ChallengeResult,
    db.TimeZone,
    db.PeriodType,
    db.GameStopageType,
    db.BrokenPOI,
    db.BrokenPBP,
]

def delete_all_data(session):
    try:
        for table in DELETE_ORDER:
            table_name = table.__tablename__
            print(f"Deleting data from {table_name}...")
            session.query(table).delete()
        session.commit()
        print("All data deleted successfully.")
    except Exception as e:
        session.rollback()
        print("Error deleting data:", e)
    finally:
        session.close()

if __name__ == "__main__":
    delete_all_data(session)

