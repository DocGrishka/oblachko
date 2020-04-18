from flask import Flask, request
import logging
import json
import random
from flask_ngrok import run_with_ngrok
app = Flask(__name__)
run_with_ngrok(app)
logging.basicConfig(level=logging.INFO)
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
    if req['session']['new']:
        res['response']['text'] = 'Привет! Введите запрос в формате <Переведите слово: "слово"> или ' \
                                  '<Переведи слово: "слово"> и я верну перевод.'
        return
    if 'переведите слово:' in req['request']['original_utterance'].lower() \
            or 'переведи слово:' in req['request']['original_utterance'].lower():
        params = {
            "key": 'trnsl.1.1.20200327T204712Z.1e49d3a0c4a100cd.bc3ab5e8db99fd7bec26e7e84092e4b5aceb054d',
            "text": req['request']['original_utterance'].split()[-1],
            "lang": 'ru-en'
        }
        response = requests.get("https://translate.yandex.net/api/v1.5/tr.json/translate", params=params)
        res['response']['text'] = ' '.join(response.json()["text"])
if __name__ == '__main__':
    app.run()
