from flask import *
from .db_session import create_session
from .users import User
from flask_restful import reqparse, abort, Api, Resource


def abort_if_user_not_found(user_id):
    session = create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"user {user_id} not found")


class UserResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict(
            only=('id', 'surname', 'name', 'age', 'position', 'speciality', 'email', 'address'))})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


parser = reqparse.RequestParser()
parser.add_argument('surname', required=True)
parser.add_argument('name', required=True)
parser.add_argument('age', required=True, type=int)
parser.add_argument('position', required=True)
parser.add_argument('speciality', required=True)
parser.add_argument('email', required=True)
parser.add_argument('address', required=True)
parser.add_argument('position', required=True)


class UserListResource(Resource):
    def get(self):
        session = create_session()
        user = session.query(User).all()
        return jsonify({'user': [item.to_dict(
            only=('id', 'surname', 'name')) for item in user]})

    def post(self):
        args = parser.parse_args()
        session = create_session()
        user = User(
            surname=args['surname'],
            name=args['name'],
            age=args['age'],
            position=args['position'],
            speciality=args['speciality'],
            email=args['email'],
            address=args['address'],
        )
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
