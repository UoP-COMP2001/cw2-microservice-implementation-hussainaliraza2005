from flask import abort
from config import db
from models import Activity, activity_schema, activities_schema

def read_all():
    activities = Activity.query.all()
    return activities_schema.dump(activities)

def create(activity):
    new_activity = activity_schema.load(activity, session=db.session)
    db.session.add(new_activity)
    db.session.commit()
    return activity_schema.dump(new_activity), 201