from flask import Flask, request
import logging
import json
import requests

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)


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

    logging.info('Request: %r', response)

    return json.dumps(response)


def handle_dialog(res, req):

    if req['session']['new']:

        res['response']['text'] = 'Привет! Я умею переводить! Напиши: "Переведи ' \
                                  '%слово или фразу, которое надо перевести%"'

        return

    if req['request']['nlu']['tokens'][0].lower() == 'переведи':
        res['response']['text'] = translate(
            " ".join(req['request']['original_utterance'].split(' ')[1:])
        )
    else:
        res['response']['text'] = 'Я тебя не поняла. Напиши: "Переведи ' \
                                  '%слово или фразу, которое надо перевести%"'


def translate(text):

    url = 'https://translate.yandex.net/api/v1.5/tr.json/translate'

    parameters = {
        "key": "trnsl.1.1.20190317T135934Z.8156cdd912a0a2f0.669070ab2fe6ead9aa5b9e0e94033726cea7bd21",
        "text": text,
        "lang": "ru-en"
    }

    response = requests.get(url, parameters).json()

    return response['text'][0]


if __name__ == '__main__':
    app.run()
