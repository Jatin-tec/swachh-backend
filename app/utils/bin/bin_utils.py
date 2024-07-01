from bson import ObjectId
from flask import current_app as app

def add_bin(data):
    bin_data = {
        "address": data.get("address"),
        "fill_status": data.get("fill_status"),
        "coordinates": data.get("coordinates")  # Latitude and Longitude
    }
    return app.db.bins.insert_one(bin_data)

def get_filled_bins():
    return app.db.bins.find({"fill_status": "100"}).sort("address", 1)
