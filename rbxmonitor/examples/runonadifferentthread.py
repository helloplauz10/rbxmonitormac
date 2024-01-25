# A simple script that monitors Roblox on a different thread to disable blocking.
import rbxmonitor

monitor = rbxmonitor.MonitorSession()
@monitor.joinedPrivateServer(142823291)
def joinedprivatemm2(info : rbxmonitor.Game):
    print("Player joined a private server")

monitor.runOnDiffThread()
print("look!")