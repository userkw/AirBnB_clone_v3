#!/usr/bin/python3
"""State objects that handle all default RESTful API actions"""
import os
from api.v1.views import app_views
from models import storage
from models.amenity import Amenity
from models.place import Place
from flask import abort, request, jsonify

db_mode = os.getenv("HBNB_TYPE_STORAGE")


@app_views.route("/places/<place_id>/amenities", strict_slashes=False,
                 methods=["GET"])
def place_amenities(place_id):
    """Retrieve place amenities"""
    amenities_list = []
    place = storage.get(Place, place_id)
    if not place:
        abort(404)  # Corrected status code to 404
    if db_mode == "db":
        amenities = place.amenities
        for amenity in amenities:
            amenities_list.append(amenity.to_dict())
    else:
        amenities_list = place.amenity_ids
    return jsonify(amenities_list)


@app_views.route("/places/<place_id>/amenities/<amenity_id>",
                 strict_slashes=False,
                 methods=["DELETE"])
def delete_amenity(place_id, amenity_id):
    """Delete an amenity by ID"""
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    amenity = storage.get(Amenity, amenity_id)
    if not amenity:
        abort(404)
    if db_mode == "db":
        place_amenities = place.amenities
    else:
        place_amenities = place.amenities_id

    for amenity_obj in place_amenities:
        if amenity_obj.id == amenity_id:
            place_amenities.remove(amenity_obj)  # Remove the amenity
            place.save()  # Save the updated Place
            return jsonify({}), 200  # Corrected status code to 200
    abort(404)  # Raise 404 if amenity not found


@app_views.route("/places/<place_id>/amenities/<amenity_id>",
                 strict_slashes=False,
                 methods=["POST"])
def link_amenity(place_id, amenity_id):
    """Link Amenity to a Place"""
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    amenity = storage.get(Amenity, amenity_id)
    if not amenity:
        abort(404)
    if db_mode == "db":
        place_amenities = place.amenities
    else:
        place_amenities = place.amenities_id

    if amenity not in place_amenities:
        place_amenities.append(amenity)
        return jsonify(amenity.to_dict()), 201  # Corrected status code to 201
    return jsonify(amenity.to_dict()), 200  # Corrected status code to 200
