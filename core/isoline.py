from fetcher import *
from sqlalchemy.orm import load_only

__author__ = 'merve'


def read_pois_without_isochrone_from_db():

    isochrone_id_list_inner_query = get_session().query(PoiIsochrones).options(load_only("here_id").defer("id"))

    pois_do_not_have_isochrone = get_session().query(TagPlaces).filter(~TagPlaces.here_id.in_(isochrone_id_list_inner_query)).all()

    for poi in pois_do_not_have_isochrone:
        create_isoline(poi)

read_pois_without_isochrone_from_db()
