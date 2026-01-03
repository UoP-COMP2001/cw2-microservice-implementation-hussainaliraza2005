import requests
from flask import abort, make_response
from config import db
from models import Profile, profile_schema, profiles_schema
from models import FavouriteActivity, Activity, activities_schema 
from models import SavedTrail, saved_trail_schema, saved_trails_schema


def read_all():
    """
    Responds to GET /profiles
    Returns all profiles
    """
    profiles = Profile.query.all()
    return profiles_schema.dump(profiles)

def create(body):
    """
    Responds to POST /profiles
    """
    email = body.get("Email")
    password = body.get("Password")

    # Authenticate with University API
    auth_url = "https://web.socem.plymouth.ac.uk/COMP2001/auth/api/users"
    credentials = {"email": email, "password": password}
    
    try:
        response = requests.post(auth_url, json=credentials)
        if response.status_code != 200:
            abort(401, "Authentication failed. Password incorrect or user not registered.")
        response_json = response.json()
        if response_json != ["Verified", True]:
             abort(401, "Authentication failed. Credentials rejected.")
    except requests.exceptions.RequestException:
        abort(503, "Authentication Service Unavailable")

    # Check local DB
    existing_profile = Profile.query.filter(Profile.Email == email).one_or_none()
    if existing_profile is not None:
        abort(409, f"Profile with email {email} already exists")

    new_profile = profile_schema.load(body, session=db.session)
    db.session.add(new_profile)
    db.session.commit()
    return profile_schema.dump(new_profile), 201

def read_one(email):
    profile = Profile.query.filter(Profile.Email == email).one_or_none()
    if profile is not None:
        return profile_schema.dump(profile)
    else:
        abort(404, f"Profile with email {email} not found")

def update(email, body):
    existing_profile = Profile.query.filter(Profile.Email == email).one_or_none()
    if existing_profile:
        update_profile = profile_schema.load(body, session=db.session)
        existing_profile.Username = update_profile.Username
        existing_profile.About_me = update_profile.About_me
        existing_profile.Location = update_profile.Location
        existing_profile.Dob = update_profile.Dob
        existing_profile.Language = update_profile.Language
        existing_profile.Password = update_profile.Password
        existing_profile.Role = update_profile.Role
        db.session.merge(existing_profile)
        db.session.commit()
        return profile_schema.dump(existing_profile), 200
    else:
        abort(404, f"Profile with email {email} not found")

def delete(email):
    existing_profile = Profile.query.filter(Profile.Email == email).one_or_none()
    if existing_profile:
        db.session.delete(existing_profile)
        db.session.commit()
        return make_response(f"Profile {email} successfully deleted", 200)
    else:
        abort(404, f"Profile with email {email} not found")

def read_user_activities(email):
    user = Profile.query.filter(Profile.Email == email).one_or_none()
    if not user:
        abort(404, f"Person not found for Id: {email}")
    results = db.session.query(Activity).join(FavouriteActivity).filter(FavouriteActivity.Email == email).all()
    return activities_schema.dump(results)

def add_activity(email, body):
    activity_id = body.get('Activity_id')
    user = Profile.query.filter(Profile.Email == email).one_or_none()
    if not user:
        abort(404, f"Person not found for Id: {email}")
    activity = Activity.query.filter(Activity.Activity_id == activity_id).one_or_none()
    if not activity:
        abort(404, f"Activity not found for Id: {activity_id}")
    new_fav = FavouriteActivity(Email=email, Activity_id=activity_id)
    db.session.add(new_fav)
    db.session.commit()
    return "Activity added", 201

# --- NEW: Saved Trails Functions ---
def read_saved_trails(email):
    """
    GET /profiles/{email}/trails
    """
    user = Profile.query.filter(Profile.Email == email).one_or_none()
    if not user:
        abort(404, f"User not found: {email}")

    saved = SavedTrail.query.filter(SavedTrail.Email == email).all()
    return saved_trails_schema.dump(saved)

def add_saved_trail(email, body):
    """
    POST /profiles/{email}/trails
    """
    trail_id = body.get('Trail_id')
    user = Profile.query.filter(Profile.Email == email).one_or_none()
    if not user:
        abort(404, f"User not found: {email}")

    existing = SavedTrail.query.filter_by(Email=email, Trail_id=trail_id).one_or_none()
    if existing:
        abort(409, f"Trail {trail_id} is already saved by this user")

    new_save = SavedTrail(Email=email, Trail_id=trail_id)
    db.session.add(new_save)
    db.session.commit()
    return saved_trail_schema.dump(new_save), 201