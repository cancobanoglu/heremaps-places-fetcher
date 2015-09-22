__author__ = 'cancobanoglu'

from sqlalchemy import Column, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry

Base = declarative_base()


class PoiType():
    PT_STOPS = "STOP"
    PLACES = "PLACE"


class TimeDistance():
    MIN_3 = 0
    MIN_5 = 1
    MIN_10 = 2


class TagPtStops(Base):
    __tablename__ = 'poi_pt_stop'

    id = Column(Integer, primary_key=True)
    here_id = Column(String, unique=True)
    lat = Column(Float)
    lng = Column(Float)
    location = Column(Geometry('POINT'))
    name = Column(String)
    vicinity = Column(String)


class TagPlaces(Base):
    __tablename__ = 'poi_place'

    id = Column(Integer, primary_key=True)
    here_id = Column(String, unique=True)
    lat = Column(Float)
    lng = Column(Float)
    location = Column(Geometry('POINT'))
    name = Column(String)
    category = Column(String)


class PoiIsochrones(Base):
    __tablename__ = 'isochone_poi'

    id = Column(Integer, primary_key=True)
    type = Column(String)
    here_id = Column(String, unique=True)
    geom_3min_isoline = Column(Geometry('POLYGON'))
    geom_5min_isoline = Column(Geometry('POLYGON'))
    geom_10min_isoline = Column(Geometry('POLYGON'))


class PoiNearestRoutes(Base):
    __tablename__ = 'poi_nearest_route'

    id = Column(Integer, primary_key=True)
    type = Column(String)
    poi_here_id = Column(String)
    distance = Column(Float)
    address_label = Column(String)
    pos_lat = Column(Float)
    pos_lng = Column(Float)
    street_label = Column(String)  # Cadde, Sokak
    mapref_sideofstreet = Column(String)  # left, right, neither
