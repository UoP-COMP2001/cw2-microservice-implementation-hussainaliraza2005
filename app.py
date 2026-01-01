from flask import render_template
import config
from models import Profile

# Get the application instance from config
app = config.connex_app

# Read the swagger.yml file to configure the endpoints
app.add_api(config.basedir / "swagger.yml")

@app.route("/")
def home():
    """
    A simple home page to prove the server is running.
    """
    return render_template("home.html")

if __name__ == "__main__":
 
    import logging
    from sqlalchemy.exc import OperationalError
    import os

    with app.app.app_context():
        skip_db = os.getenv("SKIP_DB_INIT", "false").lower() in ("1", "true", "yes")
        if skip_db:
            logging.info("SKIP_DB_INIT set, skipping database initialization")
        else:
            try:
                config.db.create_all()
            except OperationalError:
                logging.exception("Database initialization failed (OperationalError). Continuing without DB.")
            except Exception:
                logging.exception("Database initialization failed. Continuing without DB.")

    app.run(host="0.0.0.0", port=8000, debug=True)