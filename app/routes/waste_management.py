from flask import Blueprint, request, jsonify, current_app as app
from flask_jwt_extended import jwt_required
from app.utils.jwt import get_current_user
from datetime import datetime
from ..services.report_service import serialize_report
from ..services.model import predict_future_bin_levels
from ..utils.bin.bin_utils import add_bin, get_filled_bins
from ..utils.bin.routes import get_optimal_route
from bson import ObjectId
import pandas as pd
import math
import logging

bp = Blueprint('waste_management', __name__, url_prefix='/waste')


@bp.route('/bins', methods=['POST'])
@jwt_required()
def new_bin():
    data = request.get_json()
    result = add_bin(data)
    return jsonify({'msg': 'Bin added successfully', 'id': str(result.inserted_id)}), 200


@bp.route('/bins/filled', methods=['GET'])
@jwt_required()
def get_full_bins():
    bins = get_filled_bins()
    serialized_bins = [serialize_report(bin) for bin in bins]  # Ensure to serialize ObjectId
    return jsonify(serialized_bins), 200


@bp.route('/bins/route', methods=['GET'])
@jwt_required()
def get_route():
    bins = get_filled_bins()
    waypoints = [bin['coordinates'] for bin in bins]
    
    start_lat = float(request.args.get('start_lat'))
    start_lng = float(request.args.get('start_lng'))
    start = {'lat': start_lat, 'lng': start_lng}
    
    end_lat = float(request.args.get('end_lat', start_lat))
    end_lng = float(request.args.get('end_lng', start_lng))
    end = {'lat': end_lat, 'lng': end_lng}
    
    route = get_optimal_route(start, end, waypoints)
    return jsonify({'routes': route}), 200


@bp.route('/report-bin', methods=['POST', 'GET'])
@jwt_required()
def report_bin():
    if request.method == 'GET':
        report_id = request.args.get('id')
        report = app.db.reports.find_one({'_id': ObjectId(report_id)})
        if not report:
            return jsonify({'msg': 'Report not found'}), 404

        return jsonify({
            'msg': 'Report retrieved successfully', 
            'report': serialize_report(report)
            }), 200
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            user = get_current_user()

            data['reported_by'] = user
            data['reported_at'] = datetime.now()
            data['status'] = 'Pending'

            report_id = app.db.reports.insert_one(data).inserted_id
            print(report_id)
            
            return jsonify({
                'msg': 'Bin reported successfully',
                'report': {
                    'report_id': str(report_id),
                    'reported_by': data.get('reported_by'),
                    'status': data.get('status')
                }
                }), 200
        except:
            return jsonify({'msg': 'Internal server error'}), 500
    
    return jsonify({'msg': 'Method not allowed'}), 405

def serialize_report(report):
    """Helper function to serialize MongoDB reports"""
    report['_id'] = str(report['_id'])
    return report


@bp.route('/reports', methods=['GET', 'PATCH'])
@jwt_required()
def get_reports():
    if request.method == 'PATCH':
        try:
            data = request.get_json()
            id = request.args.get('id')

            report = app.db.reports.find_one({'_id': ObjectId(id)})
            if not report:
                return jsonify({'msg': 'Report not found'}), 404
            
            app.db.reports.update_one({'_id': ObjectId(id)}, {'$set': {'status': data.get('status')}})
            return jsonify({
                'msg': 'Report updated successfully',
                'report': serialize_report({
                    '_id': str(report['_id']),
                    'bin_id': report.get('bin_id'),
                    'reported_by': report.get('reported_by'),
                    'reported_at': report.get('reported_at'),
                    'description': report.get('description'),
                    'image': report.get('image'),
                    'location': report.get('location'),
                    'status': data.get('status')
                })
            }), 200
        except:
            return jsonify({'msg': 'Internal server error'}), 500
    reports = app.db.reports.find().sort('reported_at', -1)
    return jsonify([serialize_report(report) for report in reports]), 200


@bp.route('/predict', methods=['POST'])
@jwt_required()
def predict():
    data = request.json
    date_str = data['date']
    initial_level = data['level']

    print(f"Predicting for {date_str} with initial level {initial_level}")

    scaler_level = app.scaler_level
    scaler_features = app.scaler_features

    model = app.model

    # Predict for 6 upcoming days
    predictions = predict_future_bin_levels(
        float(initial_level), 
        date_str, 
        6, 
        model, 
        scaler_level, 
        scaler_features
    )

    res = []
    predictions = [math.fabs(level) for level in predictions]
    for prediction in predictions:
        res.append({
            'date': date_str,
            'level': prediction
        })
        date_str = pd.to_datetime(date_str) + pd.Timedelta(days=1)
        date_str = date_str.strftime('%Y-%m-%d')

    return jsonify(res), 200

