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
    2. Creates profile in local DB (without saving password)
    """
    # Get data from the request body
    email = body.get("Email")
    password = body.get("Password")

    # LSEP: AUTHENTICATION CHECK 
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
    

    # Check if profile already exists in our local database
    existing_profile = Profile.query.filter(Profile.Email == email).one_or_none()
    if existing_profile is not None:
        abort(409, f"Profile with email {email} already exists")

    # Create new profile Manually to ensure Password is NOT saved
    new_profile = Profile(
        Email=email,
        Username=body.get('Username'),
        Location=body.get('Location'),
        Dob=body.get('Dob'),
        Language=body.get('Language'),
        About_me=body.get('About_me'),
        Role=body.get('Role', 'User')
        # Password is NOT added here.
    )

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
        # We manually update fields. 
        # We do NOT use schema.load here because the incoming body might have 
        # a password, but our model does not.
        
        existing_profile.Username = body.get('Username', existing_profile.Username)
        existing_profile.About_me = body.get('About_me', existing_profile.About_me)
        existing_profile.Location = body.get('Location', existing_profile.Location)
        existing_profile.Dob = body.get('Dob', existing_profile.Dob)
        existing_profile.Language = body.get('Language', existing_profile.Language)
        existing_profile.Role = body.get('Role', existing_profile.Role)
        
         
        # (Do not allow updating the password locally since it is not stored, this is to improve security as mentioned in external authenticaion in documentation)
        
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

# Activity Functions 

def read_user_activities(email):
    """
    GET /profiles/{email}/activities
    """
    user = Profile.query.filter(Profile.Email == email).one_or_none()
    if not user:
        abort(404, f"Person not found for Id: {email}")

    # Join tables to get actual activity details
    results = db.session.query(Activity).join(FavouriteActivity).filter(FavouriteActivity.Email == email).all()
    return activities_schema.dump(results)

def add_activity(email, body):
    """
    POST /profiles/{email}/activities
    """
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