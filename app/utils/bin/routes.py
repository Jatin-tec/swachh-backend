import googlemaps

def get_optimal_route(start, end, waypoints):
    gmaps = googlemaps.Client(key='AIzaSyB-fBkFNcH9NsY1iIoR4IIMqsLU_u0HQSU')

    # Format waypoints for Google Maps API
    formatted_waypoints = [{'lat': wp['lat'], 'lng': wp['lng']} for wp in waypoints]

    # Request directions via driving mode
    directions_result = gmaps.directions(
        origin=start,
        destination=end,
        waypoints=formatted_waypoints,
        optimize_waypoints=True,
        mode="driving"
    )

    return directions_result
