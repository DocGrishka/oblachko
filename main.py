from flask import Flask, render_template, redirect, request, abort, jsonify, make_response
from flask_wtf import *
from wtforms.validators import *
from wtforms import *
from wtforms.fields.html5 import EmailField
from data.db_session import global_init
from data.db_session import create_session
from data.users import User
from data.jobs import Jobs
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from requests import get
from api_files.geo_api import search_topo_coord_and_name, draw_image, get_spn_ll, find_topo
from flask_restful import Api
from data import users_resourse, jobs_resoursce

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
global_init('db/mars_exploers.db')
api = Api(app)
url = 'http://127.0.0.1:80/'

if __name__ == '__main__':
    # для списка объектов
    api.add_resource(users_resourse.UserListResource, '/api/v2/user')
    api.add_resource(jobs_resoursce.JobsListResource, '/api/v2/jobs')

    # для одного объекта
    api.add_resource(users_resourse.UserResource, '/api/v2/users/<int:user_id>')
    api.add_resource(jobs_resoursce.JobsResource, '/api/v2/job/<int:jobs_id>')
    app.run(port=80, host='127.0.0.1')
