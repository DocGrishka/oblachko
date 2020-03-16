from flask import *
from .db_session import create_session
from .jobs import Jobs
from flask_restful import reqparse, abort, Api, Resource
import datetime


def abort_if_jobs_not_found(jobs_id):
    session = create_session()
    jobs = session.query(Jobs).get(jobs_id)
    if not jobs:
        abort(404, message=f"jobs {jobs_id} not found")


class JobsResource(Resource):
    def get(self, jobs_id):
        abort_if_jobs_not_found(jobs_id)
        session = create_session()
        jobs = session.query(Jobs).get(jobs_id)
        return jsonify({'jobs': jobs.to_dict(
            only=('id', 'team_leader', 'job', 'work_size', 'collaborators', 'speciality', 'is_finished'))})

    def delete(self, jobs_id):
        abort_if_jobs_not_found(jobs_id)
        session = create_session()
        jobs = session.query(Jobs).get(jobs_id)
        session.delete(jobs)
        session.commit()
        return jsonify({'success': 'OK'})


parser = reqparse.RequestParser()
parser.add_argument('team_leader', required=True, type=int)
parser.add_argument('job', required=True)
parser.add_argument('work_size', required=True, type=int)
parser.add_argument('collaborators', required=True)
parser.add_argument('speciality', required=True)
parser.add_argument('is_finished', required=True)


class JobsListResource(Resource):
    def get(self):
        session = create_session()
        jobs = session.query(Jobs).all()
        return jsonify({'jobs': [item.to_dict(
            only=('id', 'team_leader', 'job', 'is_finished')) for item in jobs]})

    def post(self):
        args = parser.parse_args()
        session = create_session()
        jobs = Jobs(
            team_leader=args['team_leader'],
            job=args['job'],
            work_size=args['work_size'],
            collaborators=args['collaborators'],
            speciality=args['speciality'],
            is_finished=True if args['is_finished'] == 'True' else False,
        )
        session.add(jobs)
        session.commit()
        return jsonify({'success': 'OK'})
