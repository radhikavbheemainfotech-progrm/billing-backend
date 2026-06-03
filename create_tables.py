# check_db.py
from app.database.db import engine, Base
from app.database.models import BusinessProfile

Base.metadata.create_all(bind = engine)
print("Done")

