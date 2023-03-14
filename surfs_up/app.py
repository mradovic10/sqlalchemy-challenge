# Import dependencies.
import datetime as dt
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model.
Base = automap_base()
# Reflect the tables.
Base.prepare(autoload_with=engine)

# Save references to each table.
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session from Python to the DB.
session = Session(engine)

#################################################
# Flask Setup
#################################################