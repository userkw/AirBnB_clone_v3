#!/usr/bin/python3
"""
View for Place objects that handles all default RESTful API actions
"""
from models import storage
from models.place import Place
from models.state import State
from models.city import City
from models.amenity import Amenity
from api.v1.views import app_views
from flask import abort, jsonify, request

@app_views.route('/places_search', methods=['POST'], strict_slashes=False)
def places_search():
    """
    Retrieves all Place objects depending on the JSON in the body
    of the request.
    """
    if not request.get_json():
        abort(400, "Not a JSON")
    
    data = request.get_json()
    states = data.get('states', [])
    cities = data.get('cities', [])
    amenities = data.get('amenities', [])

    # Initialize a list to store the final places
    all_places = []

    if not states and not cities:
        all_places = list(storage.all(Place).values())
    else:
        # Get all Place objects related to states
        if states:
            for state_id in states:
                state = storage.get(State, state_id)
                if state:
                    for city in state.cities:
                        all_places.extend(city.places)
        
        # Get all Place objects related to cities
        if cities:
            for city_id in cities:
                city = storage.get(City, city_id)
                if city and city not in all_places:
                    all_places.extend(city.places)

    # Remove duplicates
    all_places = list(set(all_places))

    # Filter places by amenities
    if amenities:
        amenity_objs = [storage.get(Amenity, amenity_id) for amenity_id in amenities]
        all_places = [place for place in all_places if all(amenity in place.amenities for amenity in amenity_objs)]

    # Convert Place objects to list of dictionaries
    result = [place.to_dict() for place in all_places]

    return jsonify(result)
