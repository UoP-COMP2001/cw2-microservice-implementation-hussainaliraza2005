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
    1. Authenticates against University API
    2. Creates profile in local DB if valid
    """
    # Get data from the request body
    email = body.get("Email")
    password = body.get("Password")

 
    # We send the email/password to the University's API to verify identity
    auth_url = "https://web.socem.plymouth.ac.uk/COMP2001/auth/api/users"
    credentials = {"email": email, "password": password}
    
    try:
        response = requests.post(auth_url, json=credentials)
        
        # If the University API returns anything other than 200 OK, reject
        if response.status_code != 200:
            abort(401, "Authentication failed. Password incorrect or user not registered.")
            
        # The API specifically returns ["Verified", True] on success
        response_json = response.json()
        if response_json != ["Verified", "True"]:
             abort(401, "Authentication failed. Credentials rejected.")

    except requests.exceptions.RequestException:
        # If the university server is unreachable
        abort(503, "Authentication Service Unavailable")
    # ----------------------------

    # Check if profile already exists in our local database
    existing_profile = Profile.query.filter(Profile.Email == email).one_or_none()
    if existing_profile is not None:
        abort(409, f"Profile with email {email} already exists")

    # Create new profile in local database
    new_profile = profile_schema.load(body, session=db.session)
    db.session.add(new_profile)
    db.session.commit()
    
    return profile_schema.dump(new_profile), 201

def read_one(email):
    """
    Responds to GET /profiles/{email}
    """
    profile = Profile.query.filter(Profile.Email == email).one_or_none()
    if profile is not None:
        return profile_schema.dump(profile)
    else:
        abort(404, f"Profile with email {email} not found")

def update(email, body):
    """
    Responds to PUT /profiles/{email}
    """
    existing_profile = Profile.query.filter(Profile.Email == email).one_or_none()
    if existing_profile:
        # Load the updated data
        update_profile = profile_schema.load(body, session=db.session)
        
        # Update the fields
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
    """
    Responds to DELETE /profiles/{email}
    """
    existing_profile = Profile.query.filter(Profile.Email == email).one_or_none()
    if existing_profile:
        db.session.delete(existing_profile)
        db.session.commit()
        return make_response(f"Profile {email} successfully deleted", 200)
    else:
        abort(404, f"Profile with email {email} not found")



def read_user_activities(email):
    """
    GET /profiles/{email}/activities
    Returns the list of activities that this specific user likes.
    """
    # Check if user exists
    user = Profile.query.filter(Profile.Email == email).one_or_none()
    if not user:
        abort(404, f"Person not found for Id: {email}")

    # Join tables to get actual activity details
    results = db.session.query(Activity).join(FavouriteActivity).filter(FavouriteActivity.Email == email).all()
    return activities_schema.dump(results)

def add_activity(email, body):
    """
    POST /profiles/{email}/activities
    Links a user to an activity.
    """
    activity_id = body.get('Activity_id')

    # Check if user exists
    user = Profile.query.filter(Profile.Email == email).one_or_none()
    if not user:
        abort(404, f"Person not found for Id: {email}")
    
    # Check if the activity type exists (e.g. Hiking)
    activity = Activity.query.filter(Activity.Activity_id == activity_id).one_or_none()
    if not activity:
        abort(404, f"Activity not found for Id: {activity_id}")

    # Create the link in the database
    new_fav = FavouriteActivity(Email=email, Activity_id=activity_id)
    db.session.add(new_fav)
    db.session.commit()
    
    return "Activity added", 201

# Saved Trails Functions 
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