from logging import debug
from os import name, stat
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import numpy as np

engine = create_engine("sqlite:///hawaii.sqlite?check_same_thread=False")
Base = automap_base()
Base.prepare(engine, reflect=True)
Station = Base.classes.station
Measurement = Base.classes.measurement
session = Session(engine)

app = Flask(__name__)

@app.route("/")
def home():
    return (
        f"Welcome to the API<br/>"
        f"Here are the available routes:<br/>"
        f"/api/v1.0/precipitation<br/>" 
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def prcp(): 
    
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > one_year_ago).all()
    

    precip = []
    for date, perc in results:
        precip.append({
            "date": date,
            "prcp": perc
        })
    
    return jsonify(precip) 


@app.route("/api/v1.0/stations")
def stations():
    
    los = session.query(Station.station, Station.name).all()
    

    list_of_stations = []
    for l, name in los:
        list_of_stations.append({
            "Station": l,
            "Name": name
        })

    
    return jsonify(list_of_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    tot_obs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date > one_year_ago).all()   
    

    total_obs = []
    for date, ob in tot_obs:
        total_obs.append({
            "Date": date,
            "Total Obs": ob
    })
    
    return jsonify(total_obs) 

@app.route("/api/v1.0/date/<start>")
@app.route("/api/v1.0/date/<start>/<end>")
def stats(start=None, end=None): 
    
    sd = [func.min(Measurement.tobs), 
          func.max(Measurement.tobs), 
          func.avg(Measurement.tobs)]
    
    if not end:
        # start=dt.datetime.strptime(start, "%Y%m%d")
        results = session.query(*sd).filter(Measurement.date >= start).all() 
        temps = list(np.ravel(results))
    
    else:
        results = session.query(*sd).filter(Measurement.date >= start, Measurement.date <= end).all() 
        temps = list(np.ravel(results))
    
    temps.append(start)

    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)