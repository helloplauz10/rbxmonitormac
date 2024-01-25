# rbxmonitormac
A simple script that monitors roblox asynchronously without modifying and reading the game's client. This only works in MacOS

# Installation
```bash
python3 -m pip install rbxmonitormac
```

# Example on how to use
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
