from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from geoalchemy2 import WKTElement
from shapely.geometry import asPoint, asPolygon

import requests
from api_urls import *
from models import *

from map_grid_creator import *

__author__ = 'cancobanoglu'

DB_SETTINGS = dict(
    db_name='poi',
    db_user='postgres',
    db_password='1234',
    db_host='localhost',
    db_port=5432
)


def engine_factory():
    settings = DB_SETTINGS
    postgresql_path = 'postgresql://%s:%s@%s:%s/%s' % (
        settings['db_user'],
        settings['db_password'],
        settings['db_host'],
        settings['db_port'],
        settings['db_name']
    )
    return create_engine(postgresql_path)


engine = engine_factory()
Session = scoped_session(sessionmaker(bind=engine))
Base.metadata.create_all(engine)

# establish conversation between database
_session = Session()


# return _session
def get_session():
    return _session


# '180', 'geo!41.078414,29.012468'
def do_request_for_reverse_isoline(range, destionation_point):
    request_url = build_isoline_url(range, destionation_point)
    response = requests.get(request_url)
    data = response.json()
    return data


def build_isochrone_polygon(range, destionation_point):
    data = do_request_for_reverse_isoline(range, destionation_point)
    shape_data = data['response']['isoline'][0]['component'][0]['shape']
    polygon = build_polygon(shape_data)
    return polygon


def create_isoline(poi=TagPlaces):
    str_lat = str(poi.lat)
    str_lng = str(poi.lng)
    # 3 minutes isoline polgon
    polygon_3min = build_isochrone_polygon(180, str_lat + "," + str_lng)
    geo_3min_pol = wkt_element(polygon_3min)
    # 5 minutes isoline polygon
    polygon_5min = build_isochrone_polygon(300, str_lat + "," + str_lng)
    geo_5min_pol = wkt_element(polygon_5min)
    # 10 minutes isoline polygon
    polygon_10min = build_isochrone_polygon(600, str_lat + "," + str_lng)
    geo_10min_pol = wkt_element(polygon_10min)
    # Isochrone object creation
    isochrone_polygon = PoiIsochrones(type=PoiType.PLACES, here_id=poi.here_id, geom_3min_isoline=geo_3min_pol,
                                      geom_5min_isoline=geo_5min_pol, geom_10min_isoline=geo_10min_pol)

    q = _session.query(PoiIsochrones).filter(PoiIsochrones.here_id == poi.here_id)
    global one

    try:
        one = q.one()

        if one == None:
            _session.add(isochrone_polygon)
        else:
            isochrone_polygon.id = one.id
            _session.merge(isochrone_polygon)
    except:
        _session.add(isochrone_polygon)
        pass

    _session.commit()


def build_polygon(shape_data):
    point_list = [None] * len(shape_data)
    counter = 0

    for point in shape_data:
        lat_lng = [float(coord) for coord in point.split(",")]
        point_list.insert(counter, lat_lng)
        counter += 1

    point_list = [x for x in point_list if x is not None]

    p = asPolygon(point_list)

    return p


def start_fetching_pois():
    request_url = build_places_url('41.078360,29.012938')
    response = requests.get(request_url)
    data = response.json()
    results = data['results']
    items = results['items']
    next_page_url = results['next']

    for i in items:
        create_place(i)


def wkt_element(object):
    return WKTElement('SRID=4326; ' + object.wkt)


def fetch_pois_by_next(next_url):
    response = requests.get(next_url)
    data = response.json()


def find_nearest_places_x_min_walking_away(p):
    isochrones = _session.query(PoiIsochrones).filter(PoiIsochrones.geom_3min_isoline.contains(p)).all()
    print isochrones[0].here_id


def test_point_within_three_min_distance():
    test_point = WKTElement('Point(41.076305 29.014334)')
    print test_point.wkt
    find_nearest_places_x_min_walking_away(test_point)


def create_input_for_multi_reverse_geocoding(poi_type=PoiType):
    '''
    First fetch pois from db by type, then generate a input for multi reverse geocoding of HERE api.
        - id=0001&prox=41.077797,29.013208,1000
        - id=0002&prox=41.022435, 29.058573,250
    '''

    request_url = build_multi_reverse_geocoding_url()
    print request_url

    input_body = ''
    template_format = 'id=%s&prox=%s,%s,500'

    if poi_type == PoiType.PLACES:
        places_list = _session.query(TagPlaces).all()

        for poi in places_list:
            input_body += template_format % (str(poi.id), str(poi.lat), str(poi.lng))
            input_body += '\n'

        headers = {'Content-Type': 'text/plain'}
        response = requests.post(request_url, data=input_body, headers=headers)
        data = response.json()

        response_data = data['Response']
        item_list = response_data['Item']

        for item in item_list:
            item_result_list = item['Result']
            for item_result in item_result_list:
                create_poi_nearest_routes(item_result, item['ItemId'])


def create_poi_nearest_routes(item_data, item_id):
    location_data = item_data['Location']
    nav_location_data = location_data['NavigationPosition'][0]
    pos_lat = nav_location_data['Latitude']
    pos_lng = nav_location_data['Longitude']
    address_data = location_data['Address']
    address_label = address_data['Label']
    if not address_data.get('Street'):
        address_street = address_data.get('District')
    else:
        address_street = address_data.get('Street')
    map_reference_data = location_data['MapReference']
    side_of_street = map_reference_data['SideOfStreet']

    nearest_route = PoiNearestRoutes(type='PLACES', poi_here_id=item_id, distance=item_data['Distance'],
                                     pos_lat=pos_lat, pos_lng=pos_lng, address_label=address_label,
                                     street_label=address_street, mapref_sideofstreet=side_of_street)

    _session.add(nearest_route)
    _session.commit()


def create_place(item):
    position = item['position']
    lat = position[0]
    lng = position[1]
    # Geography data
    loc_el = WKTElement(asPoint(position).wkt)
    poi = TagPlaces(here_id=item['id'], name=item['title'], category=item['category']['title'], lat=lat, lng=lng,
                    location=loc_el)

    try:
        q = _session.query(TagPlaces).filter(TagPlaces.here_id == item['id'])
        one = q.one()

        if one == None:
            _session.add(poi)
        else:
            poi.id = one.id
            _session.merge(poi)
    except:
        _session.add(poi)
        pass

    _session.commit()
    # create_isoline(poi)


def create_pt_stop(item):
    position = item['position']
    lat = position[0]
    lng = position[1]
    # Geography data
    loc_el = WKTElement(asPoint(position).wkt)

    stop = TagPtStops(here_id=item['id'], name=item['title'], vicinity=item.get('vicinity'), location=loc_el, lat=lat,
                      lng=lng)

    try:
        q = _session.query(TagPtStops).filter(TagPtStops.here_id == item['id'])
        one = q.one()

        if one == None:
            _session.add(stop)
            _session.commit()
        else:
            stop.id = one.id
            # _session.merge(stop)
    except:
        _session.add(stop)
        _session.commit()
        pass


def explore_all_places(*cat):
    bbox_list = create_boundingbox_rect_list()
    print 'processing for : ' + cat[0]

    for box in bbox_list:
        try:
            request_url = build_discover_places_url(box, *cat)
            data = do_get_request_return_response(request_url)
            create_explored_place_data(data)
        except Exception, err:
            print 'Error: %s' % str(err)
            print 'Latest bbox position :' + str(box)


def fetch_all_pt_stops():
    geolocation_list = create_geolocation_list()

    for geolocation in geolocation_list:
        lat = geolocation[1]
        lng = geolocation[0]

        request_url = build_pt_stops_url(lat + ',' + lng)
        data = do_get_request_return_response(request_url)
        create_pt_stops_data(data)


def do_get_request_return_response(url):
    response = requests.get(url)
    global data
    try:
        data = response.json()
    except:
        print "error on do_get_request_return_response"
        print data
        print url
        raise Exception('hata aldin firlatiyorum')

    return data


def create_explored_place_data(data):
    results = data.get('results')

    global items
    global next

    try:
        if results is None:
            items = data['items']
            next = data.get('next')
        else:
            items = results['items']
            next = results.get('next')
    except:
        print 'Error : ' + str(data)
        raise

    items_len = items.__len__()

    if items_len == 0:
        return

    for item in items:
        create_place(item)

    if next is not None:
        create_explored_place_data(do_get_request_return_response(next))


def create_pt_stops_data(data):
    results = data.get('results')

    next = results.get('next')
    items = results.get('items')

    items_len = items.__len__()
    if items_len == 0:
        return

    for item in items:
        create_pt_stop(item)


# test_point_within_three_min_distance()
# start_fetching_pois()
cat = {
    # 'restaurant',
    # 'coffee-tea',
    # 'snacks-fast-food'
    'going-out',
    'sights-museums',
    # 'transport',
    # 'airport',
    'accommodation',
    # 'shopping',
    # 'leisure-outdoor',
    # 'administrative-areas-buildings',
    #'natural-geographical',
    # 'atm-bank-exchange',
    # 'toilet-rest-area',
    # 'hospital-health-care-facility',
}

# for c in cat:
#     explore_all_places(c)

# fetch_all_pt_stops()
# create_input_for_multi_reverse_geocoding(PoiType.PLACES)
