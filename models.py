from config import db, ma

# Define tables/models
class Activity(db.Model):
    __tablename__ = 'Activity'
    __table_args__ = {'schema': 'CW2'}

    Activity_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Activity = db.Column(db.String(30), unique=True, nullable=False)

class FavouriteActivity(db.Model):
    __tablename__ = 'FavouriteActivity'
    __table_args__ = {'schema': 'CW2'}

    Email = db.Column(db.String(30), db.ForeignKey('CW2.Profile.Email'), primary_key=True)
    Activity_id = db.Column(db.Integer, db.ForeignKey('CW2.Activity.Activity_id'), primary_key=True)

class SavedTrail(db.Model):
    __tablename__ = 'SavedTrail'
    __table_args__ = {'schema': 'CW2'}

    Email = db.Column(db.String(30), db.ForeignKey('CW2.Profile.Email'), primary_key=True)
    Trail_id = db.Column(db.Integer, primary_key=True)
    Saved_date = db.Column(db.Date)

class Profile(db.Model):
    __tablename__ = 'Profile'
    __table_args__ = {'schema': 'CW2'}

    Email = db.Column(db.String(30), primary_key=True)
    Username = db.Column(db.String(30))
    About_me = db.Column('About me', db.String(500)) 
    Location = db.Column(db.String(50))
    Dob = db.Column(db.Date)
    Language = db.Column(db.String(30))
    Role = db.Column(db.String(5))

    favourites = db.relationship('FavouriteActivity', backref='user', lazy=True, cascade="all, delete-orphan")
    saved_trails = db.relationship('SavedTrail', backref='user', lazy=True, cascade="all, delete-orphan")


# Define Schemas
class ActivitySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Activity
        load_instance = True
        sqla_session = db.session

class FavouriteActivitySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = FavouriteActivity
        load_instance = True
        sqla_session = db.session
        include_fk = True  

class SavedTrailSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SavedTrail
        load_instance = True
        sqla_session = db.session
        include_fk = True

class ProfileSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Profile
        load_instance = True
        sqla_session = db.session
    
    favourites = ma.Nested('FavouriteActivitySchema', many=True)
    saved_trails = ma.Nested('SavedTrailSchema', many=True)


# Initialize Schemas
profile_schema = ProfileSchema()
profiles_schema = ProfileSchema(many=True)

activity_schema = ActivitySchema()
activities_schema = ActivitySchema(many=True)

fav_activity_schema = FavouriteActivitySchema()
fav_activities_schema = FavouriteActivitySchema(many=True)

saved_trail_schema = SavedTrailSchema()
saved_trails_schema = SavedTrailSchema(many=True)