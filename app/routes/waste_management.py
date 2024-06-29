from flask import Blueprint, request, jsonify, current_app as app
from flask_jwt_extended import jwt_required
from app.utils.jwt import get_current_user
from datetime import datetime

bp = Blueprint('waste_management', __name__, url_prefix='/waste')

@bp.route('/bins', methods=['GET'])
@jwt_required()
def get_bins():
    bins = app.db.bins.find()
    return jsonify([bin for bin in bins]), 200

@bp.route('/bins', methods=['POST'])
@jwt_required()
def add_bin():
    data = request.get_json()
    app.db.bins.insert_one(data)
    return jsonify({'msg': 'Bin added successfully'}), 201

@bp.route('/report-bin', methods=['POST'])
@jwt_required()
def report_bin():
    try:
        data = request.get_json()
        user = get_current_user()

        data['reported_by'] = user
        data['reported_at'] = datetime.now()
        data['status'] = 'pending'

        app.db.reports.insert_one(data)

        return jsonify({'msg': 'Bin reported successfully'}), 200
    except:
        return jsonify({'msg': 'Internal server error'}), 500