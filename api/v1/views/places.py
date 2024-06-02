#!/usr/bin/python3
"""
Routes for handling Place objects and operations
"""
from flask import jsonify, abort, request
from api.v1.views import app_views, storage
from models.place import Place


def get_json_or_abort():
    """Get JSON body from request, abort if not JSON"""
    place_json = request.get_json(silent=True)
    if place_json is None:
        abort(400, 'Not a JSON')
    return place_json


def get_object_or_abort(model, obj_id):
    """Retrieve an object by ID, abort if not found"""
    obj = storage.get(model, str(obj_id))
    if obj is None:
        abort(404)
    return obj


@app_views.route("/api/v1/places_search", methods=["POST"], strict_slashes=False)
def places_search():
    """
    Search for Place objects based on JSON criteria.
    :return: JSON response with filtered Place objects
    """
    place_json = request.get_json(silent=True)

    if place_json is None:
        place_list = [place.to_json() for place in storage.all("Place").values()]
    else:
        states = place_json.get("states", [])
        cities = place_json.get("cities", [])
        amenities = place_json.get("amenities", [])

        place_list = []
        for place in storage.all("Place").values():
            if (not states or place.city.state_id in states) and \
               (not cities or place.city_id in cities) and \
               (not amenities or all(amenity_id in place.amenities for amenity_id in amenities)):
                place_list.append(place.to_json())

    return jsonify(place_list)


@app_views.route("/cities/<city_id>/places", methods=["GET"], strict_slashes=False)
def places_by_city(city_id):
    """
    Retrieve all Place objects by city.
    :param city_id: ID of the city
    :return: JSON of all Places in the city
    """
    city_obj = get_object_or_abort("City", city_id)
    place_list = [place.to_json() for place in city_obj.places]
    return jsonify(place_list)


@app_views.route("/cities/<city_id>/places", methods=["POST"], strict_slashes=False)
def place_create(city_id):
    """
    Create a new Place object.
    :param city_id: ID of the city
    :return: Newly created Place object
    """
    place_json = get_json_or_abort()
    if "user_id" not in place_json:
        abort(400, 'Missing user_id')
    if "name" not in place_json:
        abort(400, 'Missing name')

    get_object_or_abort("User", place_json["user_id"])
    get_object_or_abort("City", city_id)

    place_json["city_id"] = city_id
    new_place = Place(**place_json)
    new_place.save()
    
    resp = jsonify(new_place.to_json())
    resp.status_code = 201
    return resp


@app_views.route("/places/<place_id>", methods=["GET"], strict_slashes=False)
def place_by_id(place_id):
    """
    Retrieve a specific Place object by ID.
    :param place_id: Place object ID
    :return: Place object with the specified ID or error
    """
    fetched_obj = get_object_or_abort("Place", place_id)
    return jsonify(fetched_obj.to_json())


@app_views.route("/places/<place_id>", methods=["PUT"], strict_slashes=False)
def place_put(place_id):
    """
    Update a specific Place object by ID.
    :param place_id: Place object ID
    :return: Updated Place object
    """
    place_json = get_json_or_abort()
    fetched_obj = get_object_or_abort("Place", place_id)

    for key, val in place_json.items():
        if key not in ["id", "created_at", "updated_at", "user_id", "city_id"]:
            setattr(fetched_obj, key, val)

    fetched_obj.save()
    return jsonify(fetched_obj.to_json())


@app_views.route("/places/<place_id>", methods=["DELETE"], strict_slashes=False)
def place_delete_by_id(place_id):
    """
    Delete a Place by ID.
    :param place_id: Place object ID
    :return: Empty dictionary with 200 status or 404 if not found
    """
    fetched_obj = get_object_or_abort("Place", place_id)
    storage.delete(fetched_obj)
    storage.save()
    return jsonify({})


if __name__ == "__main__":
    pass  # Add any necessary app initialization here
