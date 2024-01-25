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