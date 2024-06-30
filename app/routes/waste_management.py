from flask import Blueprint, request, jsonify, current_app as app
from flask_jwt_extended import jwt_required
from app.utils.jwt import get_current_user
from datetime import datetime
from ..services.report_service import serialize_report
from ..services.model import make_prediction
from bson import ObjectId
import pandas as pd

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

    scaler_level = app.scaler_level
    scaler_features = app.scaler_features

    model = app.model

    # Example of predicting for a time series (adjust as per your requirement)
    dates_to_predict = pd.date_range(start=date_str, periods=7, freq='D')  # Predict for 5 days

    predictions = []
    for dt in dates_to_predict:
        prediction_value = make_prediction(dt.strftime('%d/%m/%Y'), model, scaler_level, scaler_features)
        predictions.append({
            'date': dt.strftime('%d/%m/%Y'),
            'predicted_level': float(prediction_value)
        })

    return jsonify(predictions), 200
