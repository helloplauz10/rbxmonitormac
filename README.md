# rbxmonitormac
A simple object oriented script that monitors roblox asynchronously without modifying and reading the game's client. This only works in MacOS

# Installation
```bash
python3 -m pip install macrbxmonitor
```

# Getting Started
Here are some examples on what can you do with this module.

Get the Info:
```python
# Get the Place ID, Job ID and the type of the server
import rbxmonitor

monitor = rbxmonitor.MonitorSession()
@monitor.joinedGame()
async def joined(info : rbxmonitor.Game):
  print(f"Player joined. Place ID: {info.placeid} Job ID: {info.jobid} Server Type: {info.servertype}")
  "do actions"

@monitor.disconnected()
async def disconnect():
  print("Player left the game")
  "do actions"

monitor.run()
```
Monitor the player if it joins a game or disconnect.
```python
# A simple script that monitors the player once he joins and disconnects
import rbxmonitor

monitor = rbxmonitor.MonitorSession()

@monitor.joinedGame()
def joinedgame(info : rbxmonitor.Game):
    print("Player joined a game.")
    print("Place ID:",info.placeid)
    print("Job ID:",info.jobid)
    print("Server",info.servertype)
@monitor.joinedGame(142823291) # This will execute if the player (you) joined the place id you provided
def joinedmm2(info : rbxmonitor.Game):
    print("Player joined MM2")
    print("Job ID:",info.jobid)
    print("Server:",info.servertype)
@monitor.disconnected()
def disconnected():
    print("Player disconencted")

monitor.run()
```

Run on a different thread to not block anything else from executing.
```python
# A simple script that monitors Roblox on a different thread to disable blocking.
import rbxmonitor

monitor = rbxmonitor.MonitorSession()
@monitor.joinedPrivateServer(142823291)
def joinedprivatemm2(info : rbxmonitor.Game):
    print("Player joined a private server")

monitor.runOnDiffThread()
print("look!")
```

Do a http request to get the name of the place id you joined
```python
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
```
