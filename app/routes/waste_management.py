from flask import Blueprint, request, jsonify, current_app as app
from flask_jwt_extended import jwt_required
from app.utils.jwt import get_current_user
from datetime import datetime
from ..services.report_service import serialize_report
from ..services.model import make_prediction
from ..utils.bin.bin_utils import add_bin, get_filled_bins
from ..utils.bin.routes import get_optimal_route
from bson import ObjectId
import pandas as pd
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
    
    # Log the waypoints and start/end coordinates
    logging.info(f"Start: {start}")
    logging.info(f"End: {end}")
    logging.info(f"Waypoints: {waypoints}")

    route = get_optimal_route(start, end, waypoints)
    return jsonify(route), 200


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

    scaler_level = app.scaler_level
    scaler_features = app.scaler_features

    model = app.model

    # Predict for 6 upcoming days
    dates_to_predict = pd.date_range(start=date_str, periods=6, freq='D')

    predictions = []
    current_level = float(initial_level)

    # Initialize rolling statistics and lag features (with example values)
    rolling_mean = current_level
    rolling_std = 0
    level_lag_1 = current_level
    level_lag_2 = current_level

    for i, dt in enumerate(dates_to_predict):
        prediction_value, rolling_mean, rolling_std, level_lag_1, level_lag_2 = make_prediction(
            dt.strftime('%d/%m/%Y'), model, scaler_level, scaler_features, current_level, 
            rolling_mean, rolling_std, level_lag_1, level_lag_2)
        
        current_level = prediction_value  # Use predicted value as the next day's input level
        predictions.append({
            'date': dt.strftime('%d/%m/%Y'),
            'predicted_level': float(prediction_value)
        })

    return jsonify(predictions), 200

