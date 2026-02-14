import aiohttp, asyncio
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("nasa_iss", json_response=True)

class ISSPosition:
    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude

async def _get_iss_location() -> ISSPosition:
    # Fetches the current location of the International Space Station (ISS) from the Open Notify API.
    url = "http://api.open-notify.org/iss-now.json"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            json_response = await response.json()
            return ISSPosition(**json_response["iss_position"])

@mcp.tool()
async def get_international_space_station_location() -> dict:
    # Async wrapper for fetching NASA ISS Location that awaits the coroutine.
    pos = await _get_iss_location()
    return {"latitude": pos.latitude, "longitude": pos.longitude}

if __name__ == "__main__":
    mcp.run(transport="stdio")