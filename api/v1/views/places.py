#!/usr/bin/python3
"""
New endpoint to retrieve Place objects depending on JSON in request body
"""

from flask import jsonify, request, abort
from models import storage
from models.place import Place
from models.state import State
from models.city import City
from models.amenity import Amenity
from api.v1.views import app_views

@app_views.route('/places_search', methods=['POST'], strict_slashes=False)
def places_search():
    """
    Retrieves all Place objects depending on the JSON in the body
    of the request.
    """
    # Parse request JSON
    if not request.is_json:
        abort(400, "Not a JSON")
    search_params = request.get_json()

    if not search_params:
        # Return all Place objects if JSON body is empty
        places = storage.all(Place).values()
        return jsonify([place.to_dict() for place in places])

    places = set()

    # Handle states and cities
    state_ids = search_params.get('states', [])
    city_ids = search_params.get('cities', [])

    if state_ids:
        for state_id in state_ids:
            state = storage.get(State, state_id)
            if state:
                for city in state.cities:
                    for place in city.places:
                        places.add(place)

    if city_ids:
        for city_id in city_ids:
            city = storage.get(City, city_id)
            if city:
                for place in city.places:
                    places.add(place)

    if not state_ids and not city_ids:
        # If no state or city is provided, return all Place objects
        places = storage.all(Place).values()

    # Handle amenities filtering
    amenity_ids = search_params.get('amenities', [])
    if amenity_ids:
        amenity_ids = set(amenity_ids)
        places = {place for place in places if amenity_ids.issubset({amenity.id for amenity in place.amenities})}

    # Return the list of Place objects
    return jsonify([place.to_dict() for place in places])
