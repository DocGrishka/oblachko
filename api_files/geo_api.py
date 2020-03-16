import requests
import math


def search_topo_coord_and_name(town_name):
    geo_params = {'apikey': geo_api_key, 'geocode': town_name, 'format': 'json'}
    response = requests.get(geo_api_server, params=geo_params)
    check(response)
    json_response = response.json()
    point = json_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
    name = json_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']["metaDataProperty"][
        "GeocoderMetaData"][
        'text']
    coord1 = list(map(float, point.split()))
    return {'coord': coord1, 'name': name}


def find_topo(town_name):
    geo_params = {'apikey': geo_api_key, 'geocode': town_name, 'format': 'json'}
    response = requests.get(geo_api_server, params=geo_params)
    check(response)
    json_response = response.json()
    toponym = json_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
    return toponym


def lonlat_distance(a, b):
    degree_to_meters_factor = 111 * 1000  # 111 километров в метрах
    a_lon, a_lat = a
    b_lon, b_lat = b

    # Берем среднюю по широте точку и считаем коэффициент для нее.
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)

    # Вычисляем смещения в метрах по вертикали и горизонтали.
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    # Вычисляем расстояние между точками.
    distance = math.sqrt(dx * dx + dy * dy)
    return distance


def search_org(x, y):
    geo_params = {'apikey': geo_api_key, 'geocode': f'{x},{y}', 'format': 'json'}
    response = requests.get(geo_api_server, params=geo_params)
    check(response)
    json_response = response.json()
    name = json_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']["metaDataProperty"][
        "GeocoderMetaData"][
        'text']
    search_params = {
        "apikey": search_api_key,
        "text": name,
        "lang": "ru_RU",
        "ll": f'{x},{y}',
        "spn": '0.5,0.5',
        "type": "biz"
    }
    response = requests.get(search_api_server, params=search_params)
    check(response)


def check(response):
    if not response:
        print("Ошибка выполнения запроса!")
        print(response.content)
        print("Http статус:", response.status_code, "(", response.reason, ")")


def draw_image(coord, typ, spn):
    map_request = f"http://static-maps.yandex.ru/1.x/?ll={','.join(map(str, coord))}&l={typ}&spn={spn}"
    response = requests.get(map_request)
    check(response)
    map_file = "./static/img/map.png"
    with open(map_file, "wb") as file:
        file.write(response.content)


def get_spn_ll(toponym):
    spn = (float(toponym['boundedBy']['Envelope']['upperCorner'].split()[0]) - float(
        toponym['boundedBy']['Envelope']['lowerCorner'].split()[0])) * 0.3, (float(
        toponym['boundedBy']['Envelope']['upperCorner'].split()[1]) - float(
        toponym['boundedBy']['Envelope']['lowerCorner'].split()[1])) * 0.3
    return f"{spn[0]},{spn[1]}"


search_api_server = "https://search-maps.yandex.ru/v1/"
geo_api_server = 'https://geocode-maps.yandex.ru/1.x/'
map_api_server = "http://static-maps.yandex.ru/1.x/"
geo_api_key = "40d1649f-0493-4b70-98ba-98533de7710b"
search_api_key = 'dda3ddba-c9ea-4ead-9010-f43fbc15c6e3'
