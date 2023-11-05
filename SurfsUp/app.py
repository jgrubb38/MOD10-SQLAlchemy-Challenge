# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
base = automap_base()

# reflect the tables
base.prepare(autoload_with=engine)

# Save references to each table
measurement = base.classes.measurement
station = base.classes.station

# Create our session (link) from Python to the DB
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
        f"Welcome to the Climate App for Honolulu<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>YYYY-MM-DD<br/>"
        f"/api/v1.0/<start>YYYY-MM-DD/<end>YYYY-MM-DD"
    )
@app.route("/api/v1.0/precipitation")

def precipitation():

    """Return a list of dates and percipitation values from 2016-2017"""
# Query to retrieve the last 12 months of precipitation data.
# Find the most recent date in the dataset.
    latest_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]

# Calculate the date one year from the last date in data set.
    one_year_ago = dt.datetime.strptime(latest_date, '%Y-%m-%d') - dt.timedelta(days=365)

# Perform a query to retrieve the data and precipitation scores
    precipitation_data = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= '2016-08-23', measurement.date <= '2017-08-23').all()

# Create a dictionary with date as key and prcp as value.
    precipitation_analysis = {}
    for date, prcp in precipitation_data:
        precipitation_analysis[date] = prcp

    return jsonify(precipitation_analysis)

@app.route("/api/v1.0/stations")
def stations():

    """Return a list of all station names"""
    # Query all stations
    total_stations = session.query(Station.station).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(total_stations))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")

def temperature():

    """Return a list of dates and temperatures values from 2016-2017"""
# Query to retrieve the last 12 months of temperature data.
# Find the most recent date in the dataset.
    latest_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]

# Calculate the date one year from the last date in data set.
    one_year_ago = dt.datetime.strptime(latest_date, '%Y-%m-%d') - dt.timedelta(days=365)

# Perform a query to retrieve the data and temp scores
    tobs_data = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == "USC00519281").\
        filter(measurement.date >= one_year_ago).all()

# Create a dictionary with date as key and temp as value.
    temperature_analysis = {}
    for date, temp in tobs_data:
        temperature_analysis[date] = temp

    return jsonify(temperature_analysis)

@app.route("/api/v1.0/<start>")

def avg_temps(start):

 # Convert the start_date parameter to a datetime object
    start = dt.datetime.strptime(start, "%Y-%m-%d").date()

    # Query the database for temp data from start to the end date of the data
    results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >= start).all()

    # Calculate min, max, and average temperatures
    temp = [result.tobs for result in results]
    if temp:
        min_temp = min(temp)
        max_temp = max(temp)
        avg_temp = sum(temp) / len(temp)
        return jsonify({"The lowest tempature is": min_temp, "The highest tempature is": max_temp,
                         "The average tempature is": avg_temp})
    else:
        return jsonify({"error": f"The date specified {start} was not found."}), 404

@app.route("/api/v1.0/<start>/<end>")

def state_end_avg(start, end):

 # Convert the start_date parameter to a datetime object
    start= dt.datetime.strptime(start, "%Y-%m-%d").date()
    end = dt.datetime.strptime(end, "%Y-%m-%d").date()

    # Query the database for temp data from start to the end date of the data
    results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >= start, measurement.date <= end).all()

    # Calculate min, max, and average temperatures
    temp = [result.tobs for result in results]
    if temp:
        min_temp = min(temp)
        max_temp = max(temp)
        avg_temp = sum(temp) / len(temp)
        return jsonify({"The lowest tempature is": min_temp, "The highest tempature is": max_temp,
                         "The average tempature is": avg_temp})
    else:
        return jsonify({"error": f"The dates specified {start} and/or {end} was not found."}), 404

# Define main behavior
if __name__ == '__main__':
    app.run(debug=True)