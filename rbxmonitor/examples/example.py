# Get the Place ID, Job ID and the type of the server
import rbxmonitort

monitor = rbxmonitort.MonitorSession()
@monitor.joinedGame()
async def joined(info : rbxmonitort.Game):
  print(f"Player joined. Place ID: {info.placeid} Job ID: {info.jobid} Server Type: {info.servertype}")
  "do actions"

@monitor.disconnected()
async def disconnect():
  print("Player left the game")
  "do actions"

monitor.run()