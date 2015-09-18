__author__ = 'cancobanoglu'
import math
from matrix import Matrix

DISTANCE_BETWEEN_POINT = 0.02 # 0.88 km
START_POINT_LAT = 41.35954
START_POINT_LNG = 28.49873
SCAN_AREA_AXIS = 70
SCAN_AREA_ORDINATE = 70



def distance_on_unit_sphere(lat1, long1, lat2, long2):
    # Convert latitude and longitude to
    # spherical coordinates in radians.
    degrees_to_radians = math.pi / 180.0

    # phi = 90 - latitude
    phi1 = (90.0 - lat1) * degrees_to_radians
    phi2 = (90.0 - lat2) * degrees_to_radians

    # theta = longitude
    theta1 = long1 * degrees_to_radians
    theta2 = long2 * degrees_to_radians

    # Compute spherical distance from spherical coordinates.

    # For two locations in spherical coordinates
    # (1, theta, phi) and (1, theta', phi')
    # cosine( arc length ) =
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length

    cos = (math.sin(phi1) * math.sin(phi2) * math.cos(theta1 - theta2) +
           math.cos(phi1) * math.cos(phi2))
    arc = math.acos(cos)

    # Remember to multiply arc by the radius of the earth
    # in your favorite set of units to get length.
    return arc * 6373


def create_grid_matrix(lat, lng, max_distance_lng, max_distance_lat, distance_between_points):
    # Start with longitude and float to right

    pilot_lat = lat
    pilot_lng = lng

    row_array_list = []

    while True:
        tmp_lat = pilot_lat
        tmp_lng = pilot_lng
        row_tuple_array = []
        while True:
            pos_tpl = ()
            tmp_lng = tmp_lng + distance_between_points

            pos_tpl += ('%.6f' % tmp_lng,)
            pos_tpl += ('%.6f' % tmp_lat,)

            row_tuple_array.append(pos_tpl)

            # Calculate distance starting point to the new point
            current_distance_lng = distance_on_unit_sphere(pilot_lat, pilot_lng, tmp_lat, tmp_lng)

            if (current_distance_lng > max_distance_lng):
                break

        row_array_list.append(row_tuple_array)

        current_distance_lat = distance_on_unit_sphere(lat, lng, pilot_lat - distance_between_points, pilot_lng)

        if (current_distance_lat > max_distance_lat):
            break

        pilot_lat -= distance_between_points

    matrix = Matrix.fromList(row_array_list)

    return matrix


def create_boundingbox_rect_list():
    # first two lat and long point is a randomly selected left top point of istanbul map
    # grid_matrix is tuples - which hold lat long point within it - matrix
    grid_matrix = create_grid_matrix(START_POINT_LAT, START_POINT_LNG, SCAN_AREA_AXIS, SCAN_AREA_ORDINATE, DISTANCE_BETWEEN_POINT)

    # rule of getting bounding box point values of matrix .
    # bounding box specified as 4 values, denoting west longitude, south latitude, east longitude, north latitude.
    col = grid_matrix.n
    row = grid_matrix.m

    print 'col size: ' + str(col) + ' row size :' + str(row)

    bbox_str_list = []

    for __row in (range(0, row, 1)):
        for __col in range(1, (col), 1):
            if __row == (row - 1):
                break
            str_bbox = grid_matrix[__row + 1][__col - 1][0] + ',' + \
                   grid_matrix.__getitem__(__row + 1)[__col - 1][1] + ',' + \
                   grid_matrix.__getitem__(__row)[__col][0] + ',' + grid_matrix.__getitem__(__row)[__col][1]
            bbox_str_list.append(str_bbox)

    return bbox_str_list


def create_geolocation_list():
    grid_matrix = create_grid_matrix(START_POINT_LAT, START_POINT_LNG, SCAN_AREA_AXIS, SCAN_AREA_ORDINATE, 0.02)
    print grid_matrix
    col = grid_matrix.n
    row = grid_matrix.m

    print 'col size: ' + str(col) + ' row size :' + str(row)

    geolocation_list = []

    matrix_row_list = grid_matrix.rows

    for row in matrix_row_list:
        geolocation_list.extend(row)

    return geolocation_list

create_geolocation_list()
