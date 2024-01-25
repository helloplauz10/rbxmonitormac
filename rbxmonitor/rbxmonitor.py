# This script is from the project im making by making bloxstrap on mac (based on python)
import re # Used for getting the Job ID, Server IP, Place ID.
import subprocess
import threading
import typing
import getpass
import os
import sys
import enum
import psutil
import asyncio

if os.geteuid() == 0:
    print("Dont run this on root, it will confuse the getpass module. EXITING!")
    sys.exit()
if sys.platform != "darwin":
    print("This module only works in Mac OS.")
    sys.exit()
# Credits to Bloxstrap.
# https://github.com/pizzaboxer/bloxstrap/blob/main/Bloxstrap/Integrations/ActivityWatcher.cs
GameJoiningEntry = "[FLog::Output] ! Joining game" # [FLog::Output] ! Joining game 'job id' place 1234567 at machine.id
GameJoiningPrivateServerEntry = "[FLog::GameJoinUtil] GameJoinUtil::joinGamePostPrivateServer"
GameJoiningReservedServerEntry = "[FLog::GameJoinUtil] GameJoinUtil::initiateTeleportToReservedServer"
GameJoiningUDMUXEntry = "[FLog::Network] UDMUX Address = "
GameJoinedEntry = "[FLog::Network] serverId:" # [FLog::Network] serverId: ipadrr|port
GameDisconnectedEntry = "[FLog::Network] Time to disconnect replication data:"
GameTeleportingEntry = "[FLog::SingleSurfaceApp] initiateTeleport" # i dont need this
GameClientQuitted = "[FLog::Output] The monitorFunc thread exit now"
jobidpttr = r"'(\w{8}-\w{4}-\w{4}-\w{4}-\w{12})'"
gamepttr = r"place (\d+)"
serveridpttr = r"serverId: (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"

logfile = f"/Users/{getpass.getuser()}/Library/Logs/Roblox"

def getLatestLogFile():
    "Returns the latest log file from Roblox. This only finds the 'latest' and not the active. Returns 1 if the latest log file already exited or if Roblox isnt running"
    _logsinside = os.listdir(logfile)
    _filteredout = []
    #print(_logsinside)
    for i in _logsinside:
        if i.endswith(".log") and "Player" in i:
            _filteredout.append(i)
    _final = open(os.path.join(logfile,max(_filteredout,key=lambda log: os.path.getmtime(os.path.join(logfile,log)))),"r",encoding="utf-8",errors="ignore")
    #Do some checks
    if GameClientQuitted in _final.read() or not isRobloxRunning:
        return 1
    else:
        return _final
def isRobloxRunning() -> bool:
    for i in psutil.process_iter():
        if "RobloxPlayer" in i.name():
            return True
    return False
class ServerType(enum.Enum):
    "A class object for describing which type of server the player is in."
    InHome = 0 # Set after getting disconnected.
    Public = 1 # Set after the player joined if Roblox didnt say that it will go to a reserved or private place.
    Reserved = 2 # Set after joining a reserved place.
    Private = 3 # Set after joining a private place.

class Game():
    "A class object for the information of the game. This object is returned to the function."
    def __init__(self,placeid : int, jobid : str, accesscode : str = None, servertype : ServerType = None):
        self.placeid = placeid
        self.jobid = jobid
        self.accesscode = accesscode
        self.servertype = servertype
class MonitorSession():
    "A class object used monitoring Roblox."
    def __init__(self):
        self.running : bool = False
        self.runningOnDiffThread : bool = False
        self._thread : threading.Thread
        self.placeid : int = 0
        self.jobid : str = ""
        self.serverip : str = ""
        self.servertype : ServerType = ServerType.InHome
        self._functions : dict = {"Joined": [], "JoinedPublic": [], "JoinedReserved": [], "JoinedPrivate": [], "JoinedPlaceId": [], "Disconnected": [], "ClientQuit": []} # For joined, joinedreserved, joined private, disconnect : {func1,func2} For JoinedPlaceId: {[func1,12345],[func2,54321]}
    def _understandString(self, logtxt):
        """Dont use this function plz.
        Joining Private Server: PrivateServerEntry > Joining Game
        Joining Public: Joining Game
        Joining Reserved: Teleport > ReservedServerEntry > Disconnect > Joining Game
        """
        # Go with checking Reserved first
        if GameJoiningReservedServerEntry in logtxt:
            self.servertype = ServerType.Reserved
            #print("Reserved")
        elif GameJoiningPrivateServerEntry in logtxt:
            self.servertype = ServerType.Private
            #print("Private")
        elif GameJoiningEntry in logtxt:
            global returnedGameObj
            #print("chomp chomp walang pasok")
            self.jobid = re.search(jobidpttr,logtxt).group(1)
            self.placeid = re.search(gamepttr,logtxt).group(1)
            returnedGameObj = Game(self.placeid,self.jobid,servertype=self.servertype)
            #print(self.servertype)
            if self.servertype == ServerType.Reserved:
                returnedGameObj.servertype = ServerType.Reserved
                for i in self._functions["JoinedReserved"]:
                    #print("late ako natulog kasi walang pasok")
                    if i[1] == self.placeid:
                        asyncio.run(i[0](returnedGameObj))
                    elif not i[1]:
                        asyncio.run(i[0](returnedGameObj))
            elif self.servertype == ServerType.Private:
                returnedGameObj.servertype = ServerType.Private
                for i in self._functions["JoinedPrivate"]:
                    #print("late ako natulog kasi walang pasok")
                    if i[1] == self.placeid:
                        asyncio.run(i[0](returnedGameObj))
                    elif not i[1]:
                        asyncio.run(i[0](returnedGameObj))
            else:
                returnedGameObj.servertype = ServerType.Public
                for i in self._functions["JoinedPublic"]:
                    #print("late ako natulog kasi walang pasok")
                    #print(returnedGameObj.servertype)
                    if i[1] == self.placeid:
                        asyncio.run(i[0](returnedGameObj))
                        
                    elif not i[1]:
                        asyncio.run(i[0](returnedGameObj))
            #print(returnedGameObj.servertype)
            for i in self._functions["Joined"]:
                #print("late ako natulog kasi walang pasok")
                if i[1] == self.placeid:
                    asyncio.run(i[0](returnedGameObj))
                elif not i[1]:
                    asyncio.run(i[0](returnedGameObj))
            #print(self.placeid,self.jobid)
        elif GameJoinedEntry in logtxt:
            self.serverip = re.search(serveridpttr,logtxt).group(1)
            #print(self.serverip)
        elif GameDisconnectedEntry in logtxt:
            #print("Disconnected")
            #print("late ako natulog kasi walang pasok")
            if self.servertype != ServerType.Reserved:
                self.jobid = ""
                self.placeid = 0
                self.serverip = ""
                self.servertype = ServerType.InHome
                for i in self._functions["Disconnected"]:
                    asyncio.run(i())
        elif GameClientQuitted in logtxt:
            #print("late ako natulog kasi walang pasok")
            for i in self._functions["ClientQuit"]:
                asyncio.run(i())
            self.running = False
            self.runningOnDiffThread = False
    def joinedGame(self,placeid : int = None):
        """A decorator for calling a function that will execute once you join a game or the place id you joined.
        Example:
        @monitor.joinedGame()
        async def joined(g):
            print('Joined Game')
        @monitor.joinedGame(142823291)
        async def joined(g):
            print('Joined MM2')
        """
        def whatever(func,placeid : int = None):
            self._functions["Joined"].append([func,placeid])
        return whatever
    def joinedPublicPlace(self,placeid : int = None):
        """A decorator for calling a function that will execute once you joined a public server. If Roblox's log didnt say that you joined a reserved place or a private one, the monitor expect that we joined a public one.
        Example:
        @monitor.joinedPublicPlace()
        async def joined(g):
            print(f'Joined a Public Place. Place ID: {g.placeid} Job ID: {g.jobid}')

        """
        def whatever(func):
            self._functions["JoinedPublic"].append([func,placeid])
        return whatever
    def joinedReservedPlace(self,placeid : int = None):
        """A decorator for calling a function that will execute once you join a reserved place. This will be executed once you joined the game after Roblox requested a join to a Reserved Place. This is useful for games with lobby systems like TRD, Bedwars, etc.
        Example:
        @monitor.joinedReservedPlace()
        async def joined(g):
            print('Joined a Reserved Place')
        """
        def whatever(func):
            self._functions["JoinedReserved"].append([func,placeid])
        return whatever
    def joinedPrivateServer(self,placeid : int = None):
        """A decorator for calling a function that will execute once you join a private server..
        Example:
        @monitor.joinedPrivateServer()
        async def joined(g):
            print('Joined a Private Server')
        """
        def whatever(func):
            self._functions["JoinedPrivate"].append([func,placeid])
        return whatever
    def disconnected(self):
        """A decorator for calling a function that will execute once you disconnected.
        Example:
        @monitor.disconected()
        async def byebye():
            print('Disconnected')
        """
        def whatever(func):
            self._functions["Disconnected"].append(func)
        return whatever
    def clientquit(self):
        """A decorator for calling a function that will execute once Roblox quit.
        Example:
        @monitor.clientquit()
        async def quit():
            print('Roblox Quitted, exiting')
            exit()
        """
        def whatever(func):
            self._functions["ClientQuit"].append(func)
        return whatever
    def run(self):
        "Monitor Roblox in a loop."
        _latest = getLatestLogFile()
        if _latest == 1:
            raise Exception("Roblox is not running")
        else:
            print(f"Monitoring {_latest.name}")
            self.running = True
            _tailstream = subprocess.Popen(["tail","-f",_latest.name],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            while self.running:
                #print("late ako natulog kasi walang pasok")
                self._understandString(_tailstream.stdout.readline().decode("utf-8",errors="ignore"))
    def stop(self):
        "A shorcut for setting runningOnDiffThread and running to False"
        self.runningOnDiffThread = False
        self.running = False
    def runOnDiffThread(self):
        "Monitor Roblox in a different thread."
        self.runningOnDiffThread = True
        self._thread = threading.Thread(target=self.run)
        self._thread.start()
        return self._thread
if __name__ == "__main__":
    print(isRobloxRunning())
    test = MonitorSession()
    #test.run()
    @test.joinedPublicPlace()
    async def lol(g):
        print(f"public {g.placeid} {g.jobid}")
    @test.joinedReservedPlace()
    async def uwu(g):
        print(f"reserved {g.placeid} {g.jobid}")
    @test.joinedPrivateServer()
    async def owo(g):
        print(f"priv {g.placeid} {g.jobid}")
    @test.joinedGame()
    async def lol(g):
        print(f"game {g.placeid} {g.jobid} {g.servertype}")
    @test.disconnected()
    async def O_O():
        print(f"disconnect")
    @test.clientquit()
    async def cute():
        print("bye")
    test.runOnDiffThread()
    #test._functions["JoinedPlaceId"][0][0]()