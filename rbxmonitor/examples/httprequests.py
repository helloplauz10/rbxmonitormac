# A script that gets the name of the place id you joined. This uses asyncio and requests
# This will get the name of the game.

import aiohttp
import rbxmonitor
import json

monitor = rbxmonitor.MonitorSession()

async def getReq(session : aiohttp.ClientSession, url : str):
    async with session.get(url=url) as response:
        return await response.text()
async def getNameOfPlaceId(placeid : int):
    async with aiohttp.ClientSession() as session:
        universeid = json.loads(await getReq(session,f"https://apis.roblox.com/universes/v1/places/{placeid}/universe"))
        name = json.loads(await getReq(session,f"https://games.roblox.com/v1/games?universeIds={universeid['universeId']}"))["data"][0]["name"]
        return name
@monitor.joinedGame()
async def joined(info : rbxmonitor.Game):
    name = await getNameOfPlaceId(info.placeid)
    print(name)
monitor.run()