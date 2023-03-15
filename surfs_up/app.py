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
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    
    return (
        f"Welcome to the Home of Honolulu Weather Data!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/min_avg_max_temps/01012010 (input start date in MMDDYYYY format)<br/>"
        f"/api/v1.0/min_avg_max_temps/01012010/08232017 (input start-end dates range in MMDDYYYY format)"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year."""
    
    # Calculate the date 1 year ago from last date in database.
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for the date and precipitation for the last year.
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()

    session.close()
    
    # Create dictionary with date as the key and prcp as the value and append to a list of all the records from the past year.
    last_year_precipitation = []
    
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        last_year_precipitation.append(prcp_dict)
    
    return jsonify(last_year_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    
    # Query for all the stations.
    results = session.query(Station.station).all()

    session.close()

    # Unravel results into a 1D array and convert it to a list.
    stations = list(np.ravel(results))
    
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def temperatures():
    """Return the temperature observations (tobs) for the previous year."""
    
    # Calculate the date 1 year ago from last date in database.
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the primary station for all tobs from the last year.
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()

    session.close()
    
    # Unravel results into a 1D array and convert it to a list.
    temps = list(np.ravel(results))

    # Return the results.
    return jsonify(temps=temps)

@app.route("/api/v1.0/min_avg_max_temps/<start>")
@app.route("/api/v1.0/min_avg_max_temps/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""
    
    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # Calculate TMIN, TAVG, and TMAX for dates greater than the start.
        start = dt.datetime.strptime(start, "%m%d%Y")
        
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()

        session.close()
        
        # Unravel results into a 1D array and convert it to a list.
        temps = list(np.ravel(results))
        
        return jsonify(temps)

    # Calculate TMIN, TAVG, TMAX with start and end.
    start = dt.datetime.strptime(start, "%m%d%Y")
    
    end = dt.datetime.strptime(end, "%m%d%Y")

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()

    # Unravel results into a 1D array and convert it to a list.
    temps = list(np.ravel(results))
    
    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)