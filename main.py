

from flask import Flask, request
import logging
import json
import random
from flask_ngrok import run_with_ngrok
app = Flask(__name__)
run_with_ngrok(app)
logging.basicConfig(level=logging.INFO)
cities = {
    'москва°': ['1540737/073a30c505eb5c28a6b0', '1652229/52684001c2bf9aa79998'],
    'нью-йорк': ['213044/3562c1d206829b2d1f8e', '213044/406984958b063d25d0e3'],
    'париж': ["1540737/bccf751fd44994cceda3", '1652229/4c4ae6c82fc276440024']
}

countries = {'москва': 'россия',
             'париж': 'франция',
             'нью-йорк': 'сша'}
sessionStorage = {}
@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info('Response: %r', response)
    return json.dumps(response)
def handle_dialog(res, req):
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = 'Привет! Назови своё имя!'
        sessionStorage[user_id] = {
            'first_name': None,
            'game_started': False
        }
        return
    if sessionStorage[user_id]['first_name'] is None:
        first_name = get_first_name(req)
        if first_name is None:
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
        else:
            sessionStorage[user_id]['first_name'] = first_name
            sessionStorage[user_id]['guessed_cities'] = []
            res['response']['text'] = f'Приятно познакомиться, {first_name.title()}.' \
                                      f' Я Алиса. Отгадаешь город по фото?'
            res['response']['buttons'] = [
                {
                    'title': 'Да',
                    'hide': True
                },
                {
                    'title': 'Нет',
                    'hide': True
                },
                {
                    'title': 'Помощь',
                }
            ]
    else:
        if not sessionStorage[user_id]['game_started']:
            if 'да' in req['request']['nlu']['tokens']:
                if len(sessionStorage[user_id]['guessed_cities']) == 3:
                    res['response']['text'] = 'Ты отгадал все города!'
                    res['end_session'] = True
                else:
                    sessionStorage[user_id]['game_started'] = True
                    sessionStorage[user_id]['attempt'] = 1
                    play_game(res, req)
            elif 'нет' in req['request']['nlu']['tokens']:
                res['response']['text'] = 'Ну и ладно!'
                res['end_session'] = True
            elif 'Помощь' in req['request']['nlu']['tokens']:
                res['response']['text'] = 'Эта игра называется Угадай город.\n' \
                                          'Вы должны угадать город по картинке.'
                res['response']['buttons'] = [
                 {
                     'title': 'Да',
                     'hide': True
                 },
                 {
                     'title': 'Нет',
                     'hide': True
                 },
                 {
                     'title': 'Помощь',
                 },
                 {
                     'title': 'Покажи город на карте',
                     'hide': True,
                     'url': 'https://yandex.ru/maps/?mode=search&text='
                            + sessionStorage[user_id]['guessed_cities'][-1]
                 }
                ]
            else:
                res['response']['text'] = 'Не поняла ответа! Так да или нет?'
                res['response']['buttons'] = [
                  {
                      'title': 'Да',
                      'hide': True
                  },
                  {
                      'title': 'Нет',
                      'hide': True
                  },
                  {
                      'title': 'Помощь',
                  },
                  {
                     'title': 'Покажи город на карте',
                     'hide': True,
                     'url': 'https://yandex.ru/maps/?mode=search&text='
                            + sessionStorage[user_id]['guessed_cities'][-1]
                  }
                ]
        else:
            play_game(res, req)
def play_game(res, req):
    if 'Помощь' in req['request']['nlu']['tokens']:
        res['response']['text'] = 'Эта игра называется Угадай город.\n' \
                                'Вы должны угадать город по картинке.'
    user_id = req['session']['user_id']
    attempt = sessionStorage[user_id]['attempt']
    if attempt == 1:
        city = random.choice(list(cities))
        while city in sessionStorage[user_id]['guessed_cities']:
            city = random.choice(list(cities))
        sessionStorage[user_id]['city'] = city
        sessionStorage[user_id]['country'] = countries[city]
        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['title'] = 'Что это за город?'
        res['response']['card']['image_id'] = cities[city][attempt - 1]
        res['response']['text'] = 'Тогда сыграем!'
    else:
        city = sessionStorage[user_id]['city']
        if get_city(req) == city:
            res['response']['text'] = 'Правильно! А в какой стране этот город?'
            sessionStorage[user_id]['guessed_cities'].append(city)
            sessionStorage[user_id]['game_started'] = False
            check_city(res, req)
            return
        else:
            if attempt == 3:
                res['response']['text'] = f'Вы пытались. Это {city.title()}. Сыграем ещё?'
                res['response']['buttons'] = [
                 {
                     'title': 'Да',
                     'hide': True
                 },
                 {
                     'title': 'Нет',
                     'hide': True
                 },
                 {
                     'title': 'Помощь',
                 },
                 {
                     'title': 'Покажи город на карте',
                     'hide': True,
                     'url': 'https://yandex.ru/maps/?mode=search&text=' + city
                 }
                  ]
                sessionStorage[user_id]['game_started'] = False
                sessionStorage[user_id]['guessed_cities'].append(city)
                return
            else:
                res['response']['card'] = {}
                res['response']['card']['type'] = 'BigImage'
                res['response']['card']['title'] = 'Неправильно. Вот тебе дополнительное фото'
                res['response']['card']['image_id'] = cities[city][attempt - 1]
                res['response']['text'] = 'А вот и не угадал!'
    sessionStorage[user_id]['attempt'] += 1
def get_city(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            return entity['value'].get('city', None)
def get_first_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)
def check_country(res, req):
    if 'Помощь' in req['request']['nlu']['tokens']:
        res['response']['text'] = 'Эта игра называется Угадай город.\n' \
                                'Вы должны угадать город по картинке.'
    user_id = req['session']['user_id']
    country = sessionStorage[user_id]['country']
    if get_country(req) == country:
        res['response']['text'] = 'Правильно! Сыграем ещё?'
        res['response']['buttons'] = [
            {
                'title': 'Да',
                'hide': True
            },
            {
                'title': 'Нет',
                'hide': True
            },
            {
                'title': 'Помощь',
            },
            {
                'title': 'Покажи город на карте',
                'hide': True,
                'url': 'https://yandex.ru/maps/?mode=search&text=' + city
            }
        ]
        return
    res['response']['text'] = f'Вы пытались. Это {country.title()}. Сыграем ещё?'
    res['response']['buttons'] = [
        {
            'title': 'Да',
            'hide': True
        },
        {
            'title': 'Нет',
            'hide': True
        },
        {
            'title': 'Помощь',
        },
        {
            'title': 'Покажи город на карте',
            'hide': True,
            'url': 'https://yandex.ru/maps/?mode=search&text=' + city
        }
    ]
    return
def get_country(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            return entity['value'].get('country', None)
if __name__ == '__main__':
    app.run()
