__author__ = 'cancobanoglu'

HERE_APP_ACCESS = dict(
    app_id="kvTMp5y2JFGERc9pWR6o",
    app_code="PBy3H_B24TMLr03MECgKFQ"
)

HERE_ROUTING_URL = dict(

    # http://isoline.route.cit.api.here.com/routing/7.2/calculateisoline.json
    # ?app_id={YOUR_APP_ID}
    # &app_code={YOUR_APP_CODE}
    # &mode=fastest;car;traffic:disabled
    # &rangetype=time
    # &destination=geo!52.51578,13.37749
    # &range=600

    base_url='http://isoline.route.cit.api.here.com/routing',
    version='7.2',
    action="calculateisoline.json",
    mode='fastest;pedestrian;traffic:disabled',
    rangetype='time',
)


def build_isoline_url(range, destination):
    here_routing_endpoint = HERE_ROUTING_URL
    access_codes = HERE_APP_ACCESS

    request_url = '%s/%s/%s%s%s%s%s%s%s' % (
        here_routing_endpoint['base_url'],
        here_routing_endpoint['version'],
        here_routing_endpoint['action'],
        '?app_id=' + access_codes['app_id'],
        '&app_code=' + access_codes['app_code'],
        '&mode=' + here_routing_endpoint['mode'],
        '&rangetype=' + here_routing_endpoint['rangetype'],
        '&destination=%s' % (destination),
        "&range={0}".format(range)
    )

    return request_url


HERE_PLACES_API = dict(

    # http://places.cit.api.here.com/places/v1/discover/explore
    # ?app_id={YOUR_APP_ID}
    # &app_code={YOUR_APP_CODE}
    # &at=52.50449,13.39091
    # &pretty

    places_api_url='http://places.cit.api.here.com/places',
    version='v1',
    action='discover/explore',
    scantype='in',
    radius='7000'  # meters
)


def build_discover_places_url(bounding_box, *cat):
    places_api = HERE_PLACES_API
    access_codes = HERE_APP_ACCESS

    request_url = '%s/%s/%s%s%s%s%s' % (
        places_api['places_api_url'],
        places_api['version'],
        places_api['action'],
        '?app_id=' + access_codes['app_id'],
        '&app_code=' + access_codes['app_code'],
        '&in=' + bounding_box,
        '&size=2000'
    )

    if cat is not None:
        request_url += '&cat=' + str(cat[0])

    return request_url


def build_places_url(center_point):
    places_api = HERE_PLACES_API
    access_codes = HERE_APP_ACCESS

    request_url = '%s/%s/%s%s%s%s' % (
        places_api['places_api_url'],
        places_api['version'],
        places_api['action'],
        '?app_id=' + access_codes['app_id'],
        '&app_code=' + access_codes['app_code'],
        '&in=' + center_point + ';r=' + places_api['radius']
    )

    return request_url


HERE_PT_STOPS_API = dict(

    # http://places.cit.api.here.com/places/v1/browse/pt-stops?
    # at=41.03685%2C28.87139%3Br%3D1
    # &app_id=3XcPbZb1LRDI614kGvUU&app_code=t6N5N_77PbY8PFROAwZJpA
    # &size=1000

    pt_stops_api_cit_url='http://places.cit.api.here.com/places/v1/browse/pt-stops',
    pt_stops_api_url='http://places.api.here.com/places/v1/browse/pt-stops',
    size='2000',
)


def build_pt_stops_url(center_point):
    stops_api = HERE_PT_STOPS_API
    access_codes = HERE_APP_ACCESS

    request_url = '%s?%s%s%s%s' % (
        stops_api['pt_stops_api_url'],
        'at=' + center_point,
        '&app_id=' + access_codes['app_id'],
        '&app_code=' + access_codes['app_code'],
        '&size=' + stops_api['size']
    )

    return request_url


# The reversegeocode endpoint allows client applications to either retrieve street address
# information corresponding to a given coordinate and radius or to retrieve area information for a
# given coordinate

HERE_REVERSE_GEOCODING_API = dict(

    # http://reverse.geocoder.cit.api.here.com/6.2/reversegeocode.xml
    # ?app_id={YOUR_APP_ID}
    # &app_code={YOUR_APP_CODE}
    # &gen=9
    # &prox=50.112,8.683,100
    # &mode=retrieveAddresses

    reverse_geocode_api_url='http://reverse.geocoder.cit.api.here.com/6.2',
    single_action='reversegeocode.json',
    multi_action='multi-reversegeocode.json',
    gen='9',
    within='500',
    mode='retrieveAddresses',
    maxresults='8'
)


def build_multi_reverse_geocoding_url():
    reverse_geocode_api = HERE_REVERSE_GEOCODING_API
    access_codes = HERE_APP_ACCESS

    action = reverse_geocode_api['multi_action']

    request_url = '%s/%s?%s&%s&%s&%s&%s' % (
        reverse_geocode_api['reverse_geocode_api_url'],
        action,
        'app_id=' + access_codes['app_id'],
        'app_code=' + access_codes['app_code'],
        'gen=' + reverse_geocode_api['gen'],
        'mode=' + reverse_geocode_api['mode'],
        'maxresults=' + reverse_geocode_api['maxresults']
    )

    return request_url


def build_reverse_geocoding_url(center_point):
    reverse_geocode_api = HERE_REVERSE_GEOCODING_API
    access_codes = HERE_APP_ACCESS

    action = reverse_geocode_api['single_action']

    request_url = '%s/%s?%s&%s&%s&%s&%s' % (
        reverse_geocode_api['reverse_geocode_api_url'],
        action,
        'app_id=' + access_codes['app_id'],
        'app_code=' + access_codes['app_code'],
        'gen=' + reverse_geocode_api['gen'],
        'prox=' + center_point + ',' + reverse_geocode_api['within'],
        'mode=' + reverse_geocode_api['mode']
    )

    return request_url


print build_reverse_geocoding_url('41.022435,29.058573')
