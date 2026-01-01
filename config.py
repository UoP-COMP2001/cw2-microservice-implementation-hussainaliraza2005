import pathlib
import connexion
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


basedir = pathlib.Path(__file__).parent.resolve()
connex_app = connexion.App(__name__, specification_dir=basedir)

app = connex_app.app


app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mssql+pyodbc://HRaza:Jhlk89i04@dist-6-505.uopnet.plymouth.ac.uk/COMP2001_HRaza?driver=ODBC+Driver+17+for+SQL+Server"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)
ma = Marshmallow(app)