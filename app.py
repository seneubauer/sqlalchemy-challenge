# import dependencies
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect the database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect = True)

# save the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# flask setup
app = Flask(__name__)

# flask routes

@app.route("/")
def homepage():
    return (
        f"Available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # open the session
    session = Session(engine)
    
    # retrieve the query results
    results = session.query(Measurement.date, Measurement.prcp).all()
    
    # close the session
    session.close()
    
    # assemble the dictionary
    myDict = {}
    for row in results:
        myDict[row[0]] = row[1]
    
    # return the query results as a jsonified dictionary
    return jsonify(myDict)

@app.route("/api/v1.0/stations")
def stations():
    
    # open the session
    session = Session(engine)
    
    # retrieve the query results
    results = session.query(Station.station).all()
    
    # close the session
    session.close()
    
    # return the jsonified query results 
    return jsonify(list(np.ravel(results)))

@app.route("/api/v1.0/tobs")
def temperature():
    
    # open the session
    session = Session(engine)
    
    # run the queries
    latest = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    previousYear = f"{int(latest.split('-')[0]) - 1}-{latest.split('-')[1]}-{latest.split('-')[2]}"
    
    activeStation = session.query(*[Station.id, Station.station, func.count(Measurement.station)])\
                                .join(Station, Station.station == Measurement.station)\
                                .group_by(Station.station)\
                                .order_by(func.count(Measurement.station).desc()).first()
    stationName = activeStation[1]
    
    results = session.query(Measurement.tobs)\
                                .filter(Measurement.date >= previousYear)\
                                .filter(Measurement.station == stationName).all()
    
    # close the session
    session.close()
    
    return jsonify(list(np.ravel(results)))

@app.route("/api/v1.0/<start>")
def stats_one(start):
    
    # open the session
    session = Session(engine)
    
    # run the query
    results = session.query(*[func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)])\
                                .filter(Measurement.date >= start).all()
    
    # close the session
    session.close()
    
    return jsonify(list(np.ravel(results)))

@app.route("/api/v1.0/<start>/<end>")
def stats_two(start, end):
    
    # open the session
    session = Session(engine)
    
    # run the query
    results = session.query(*[func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)])\
                                .filter(Measurement.date >= start)\
                                .filter(Measurement.date <= end).all()
    
    # close the session
    session.close()
    
    return jsonify(list(np.ravel(results)))

# run flask
if __name__ == "__main__":
    app.run(debug = True)