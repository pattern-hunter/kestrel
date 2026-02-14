from geopy.geocoders import Nominatim
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("geocoding", json_response=True)

@mcp.tool()
def convert_lat_long_to_city(latitude: float, longitude: float) -> str:
    geolocator = Nominatim(user_agent="kestrel")
    coordinates = f"{latitude}, {longitude}"
    location = geolocator.reverse(coordinates, exactly_one=True)
    if location and 'address' in location.raw:
        address = location.raw['address']
        # Extract relevant information like city, town, or state
        city = address.get('city', '') or address.get('town', '') or address.get('village', '')
        state = address.get('state', '')
        country = address.get('country', '')
        return f"{city}, {state}, {country}".strip(', ')
    else:
        return "Unknown"
    

if __name__ == "__main__":
    mcp.run(transport="stdio")