from edu_lite import db, app
from edu_lite import models

with app.app_context():
    db.create_all()
    db.session.commit()
