# activities.py
from config import db
from models import Activity, activities_schema, activity_schema
from flask import abort

def read_all():
    """
    GET /activities
    Returns all available activity types (Hiking, Running, etc.)
    """
    activities = Activity.query.all()
    return activities_schema.dump(activities)

def create(body):
    """
    POST /activities
    Creates a new activity type (e.g., 'Kayaking')
    """
    # Check if it already exists
    existing = Activity.query.filter(Activity.Activity == body.get('Activity')).one_or_none()

    if existing:
        abort(409, f"Activity {body.get('Activity')} already exists")

    new_activity = activity_schema.load(body, session=db.session)
    db.session.add(new_activity)
    db.session.commit()

    return activity_schema.dump(new_activity), 201