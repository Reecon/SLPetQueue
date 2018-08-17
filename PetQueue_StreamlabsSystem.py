#---------------------------
#   Import Libraries
#---------------------------
import os
import codecs
import sys
import json
import re
import time
sys.path.append(os.path.join(os.path.dirname(__file__), "lib")) #point at lib folder for classes / references

import clr
clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

#   Import your Settings class
from Settings_Module import MySettings
#---------------------------
#   [Required] Script Information
#---------------------------
ScriptName = "PetQueue"
Website = "reecon820@gmail.com"
Description = "Shows links from viewers in a html file for easy visiting"
Creator = "Reecon820"
Version = "1.1.0.0"

#---------------------------
#   Define Global Variables
#---------------------------
global SettingsFile
SettingsFile = ""
global ScriptSettings
ScriptSettings = MySettings()

global QueueHtmlPath
QueueHtmlPath = os.path.abspath(os.path.join(os.path.dirname(__file__), "Queue.html"))

global ViewerHtmlPath
ViewerHtmlPath = os.path.abspath(os.path.join(os.path.dirname(__file__), "Viewer.html"))

global Queue
Queue = []

global currentIndex
currentIndex = -1

#---------------------------
#   [Required] Initialize Data (Only called on load)
#---------------------------
def Init():

    #   Create Settings Directory
    directory = os.path.join(os.path.dirname(__file__), "Settings")
    if not os.path.exists(directory):
        os.makedirs(directory)

    #   Load settings
    global SettingsFile
    SettingsFile = os.path.join(os.path.dirname(__file__), "Settings\settings.json")
    global ScriptSettings
    ScriptSettings = MySettings(SettingsFile)

    ui = {}
    UiFilePath = os.path.join(os.path.dirname(__file__), "UI_Config.json")
    try:
        with codecs.open(UiFilePath, encoding="utf-8-sig", mode="r") as f:
            ui = json.load(f, encoding="utf-8")
    except Exception as err:
        Parent.Log(ScriptName, "{0}".format(err))

    # update ui with loaded settings
    ui['Command']['value'] = ScriptSettings.Command
    ui['CommandAlt']['value'] = ScriptSettings.CommandAlt
    ui['Cooldown']['value'] = ScriptSettings.Cooldown
    ui['Permission']['value'] = ScriptSettings.Permission
    ui['Info']['value'] = ScriptSettings.Info
    ui['RemoteCommand']['value'] = ScriptSettings.RemoteCommand
    ui['RemoteCooldown']['value'] = ScriptSettings.RemoteCooldown
    ui['RemotePermission']['value'] = ScriptSettings.RemotePermission
    ui['RemoteInfo']['value'] = ScriptSettings.RemoteInfo

    try:
        with codecs.open(UiFilePath, encoding="utf-8-sig", mode="w+") as f:
            json.dump(ui, f, encoding="utf-8", indent=4, sort_keys=True)
    except Exception as err:
        Parent.Log(ScriptName, "{0}".format(err))

    return

#---------------------------
#   [Required] Execute Data / Process messages
#---------------------------
def Execute(data):
    #   only handle messages from chat
    if data.IsChatMessage() and not Parent.IsOnCooldown(ScriptName, ScriptSettings.Command) and Parent.HasPermission(data.User, ScriptSettings.Permission, ScriptSettings.Info) and not data.IsWhisper():

        isCommand = data.GetParam(0).lower() == ScriptSettings.Command

        if not isCommand:
            alts = ScriptSettings.CommandAlt.split(" ")
            for s in alts:
                if s == data.GetParam(0).lower():
                    isCommand = True
                    break
            if not isCommand:
                return
                
        # don't add empty messages
        if not data.GetParam(1):
            return
        
        #remove command from message
        cleanMessage = data.Message.split(' ', 1)[1]
        
        jsonData = '{{"user": "{0}", "message": "{1}" }}'.format(data.User, cleanMessage)

        Queue.append(jsonData)
        if currentIndex < 0:
            global currentIndex
            currentIndex = 0
        
        Parent.BroadcastWsEvent("EVENT_PET_QUEUE", jsonData)
        Parent.AddCooldown(ScriptName, ScriptSettings.Command, ScriptSettings.Cooldown)  # Put the command on cooldown

    # handle remote whisper commands
    if data.IsWhisper() and data.IsFromTwitch() and data.GetParam(0).lower() == ScriptSettings.RemoteCommand and not Parent.IsOnCooldown(ScriptName, ScriptSettings.Command) and Parent.HasPermission(data.User, ScriptSettings.RemotePermission, ScriptSettings.RemoteInfo):
        
        commandInfo = 'show, preview, skip, show <index>, preview <index>, remove <index>, clear, info'
        
        qCommand1 = None
        qCommand2 = None
        
        if data.GetParamCount() == 1:
            Parent.SendStreamWhisper(data.User, "Missing a command: {}".format(commandInfo))
        elif data.GetParamCount() == 2:
            qCommand1 = data.GetParam(1)
        elif data.GetParamCount() == 3:
            qCommand1 = data.GetParam(1)
            qCommand2 = data.GetParam(2)
        elif data.GetParamCount() > 3:
            Parent.SendStreamWhisper(data.User, "Too many arguments: {}".format(commandInfo))
            return
        else:
            return
        
        # validate command
        if qCommand1:
            if not qCommand1 in ['show', 'preview', 'skip', 'remove', 'clear', 'info']:
                Parent.SendStreamWhisper(data.User, "{0} is not a valid command. Try one of these: {1}".format(qCommand1, commandInfo))
                return
        
        # validate index variable
        if qCommand1 in ['show', 'preview', 'remove']:
            if qCommand2:
                try:
                    qCommand2 = int(qCommand2)
                except ValueError as err:
                    Parent.SendStreamWhisper(data.User, "The 2nd param must be positive number")
                    return
                if qCommand2 < 0:
                    Parent.SendStreamWhisper(data.User, "The 2nd param must be positive number")
                    return
        
        if qCommand1 == 'show':
            ShowItem(qCommand2, data.User)
        elif qCommand1 == 'preview':
            PreviewItem(qCommand2, data.User)
        elif qCommand1 == 'skip':
            SkipItem(data.User)
        elif qCommand1 == 'remove':
            RemoveItem(qCommand2, data.User)
        elif qCommand1 == 'clear':
            ClearQueue(data.User)
        elif qCommand1 == 'info':
            SendInfo(data.User)

    return

#---------------------------
#   [Required] Tick method (Gets called during every iteration even when there is no incoming data)
#---------------------------
def Tick():
    return

#---------------------------
#   [Optional] Parse method (Allows you to create your own custom $parameters) 
#---------------------------
def Parse(parseString, userid, username, targetid, targetname, message):
    return parseString

#---------------------------
#   [Optional] Reload Settings (Called when a user clicks the Save Settings button in the Chatbot UI)
#---------------------------
def ReloadSettings(jsonData):
    # Execute json reloading here
    ScriptSettings.Reload(jsonData)
    ScriptSettings.Save(SettingsFile)
    return

#---------------------------
#   [Optional] Unload (Called when a user reloads their scripts or closes the bot / cleanup stuff)
#---------------------------
def Unload():
    return

#---------------------------
#   [Optional] ScriptToggled (Notifies you when a user disables your script or enables it)
#---------------------------
def ScriptToggled(state):
    return

def OpenQueueFile():
    os.startfile(QueueHtmlPath)
    time.sleep(2) # give it time to connect web socket
    Parent.BroadcastWsEvent('EVENT_PET_QUEUE_HISTORY', json.dumps(Queue))
    del Queue[:]
    global currentIndex
    currentIndex = -1
    return

def OpenViewerFile():
    os.startfile(ViewerHtmlPath)
    return

def ShowItem(index, user):
    if index != None:
        if index < len(Queue):
            item = json.loads(Queue[index])
            Parent.BroadcastWsEvent('EVENT_SHOW_QUEUE_ITEM', '{0}'.format(json.dumps(GetLinksFromItem(index))))
            Parent.SendStreamWhisper(user, "Showing link from item: [{0}] {1}: {2}".format(index, item['user'], item['message']))
        else:
            Parent.SendStreamWhisper(user, "Queue is only {} items long".format(len(Queue)))
    else:
        if currentIndex < len(Queue):
            item = json.loads(Queue[currentIndex])
            Parent.BroadcastWsEvent('EVENT_SHOW_QUEUE_ITEM', '{0}'.format(json.dumps(GetLinksFromItem(currentIndex))))
            Parent.SendStreamWhisper(user, "Showing link from item: [{0}] {1}: {2}".format(currentIndex,item['user'],item['message']))
            time.sleep(1)

            oldIndex = currentIndex
            
            global currentIndex
            currentIndex = oldIndex + 1

            if len(Queue) > currentIndex:
                item = json.loads(Queue[currentIndex])
                Parent.SendStreamWhisper(user, "Next item is: [{0}] {1}: {2}".format(currentIndex, item['user'], item['message']))
            else:
                Parent.SendStreamWhisper(user, "This was the last item in the queue!")

    return

def PreviewItem(index, user):
    if index != None:
        if index < len(Queue):
            item = json.loads(Queue[index])
            Parent.SendStreamWhisper(user, "Item at position [{0}] would be: {1}: {2}".format(index, item['user'], item['message']))
        else:
            Parent.SendStreamWhisper(user, "Queue only has {} item(s)".format(len(Queue)))
    else:
        item = json.loads(Queue[currentIndex])
        Parent.SendStreamWhisper(user, "Next item would be: [{0}] {1}: {2}".format(currentIndex, item['user'], item['message']))
    return

def SkipItem(user):
    if len(Queue) > currentIndex:
        item = json.loads(Queue[currentIndex])
        Parent.SendStreamWhisper(user, "Skipping item: [{0}] {1}: {2}".format(currentIndex, item['user'],item['message']))
        time.sleep(1)
        
        oldIndex = currentIndex

        global currentIndex
        currentIndex = oldIndex + 1

        if len(Queue) > currentIndex:
            item = json.loads(Queue[currentIndex])
            Parent.SendStreamWhisper(user, "Next item is: [{0}] {1}: {2}".format(currentIndex, item['user'], item['message']))
        else:
            Parent.SendStreamWhisper(user, "This was the last item in the queue!")
    else:
        Parent.SendStreamWhisper(user, "No more items in the Queue")
    return

def RemoveItem(index, user):
    if index != None:
        if index < len(Queue):
            item = json.loads(Queue[index])
            Parent.SendStreamWhisper(user, "Removing item: [{0}] {1}: {2}".format(index, item['user'], item['message']))
            del Queue[index]

            # if an element before the current index was removed, point to the old element again
            if index < currentIndex:
                oldIndex = currentIndex
                global currentIndex
                currentIndex = oldIndex - 1
            
            # if the current index is now out of bounds, set it to the last element
            if currentIndex >= len(Queue):
                global currentIndex
                currentIndex = len(Queue) - 1
        else:
            Parent.SendStreamWhisper(user, "Queue only has {} item(s)".format(len(Queue)))
    else:
        Parent.SendStreamWhisper(user, "Please provide the index of the item you want to remove.")
        
    return

def ClearQueue(user):
    Parent.SendStreamWhisper(user, "Clearing the entire queue, I hope you knew what you were doing Kappa")
    del Queue[:]
    global currentIndex
    currentIndex = -1
    return

def SendInfo(user):
    Parent.SendStreamWhisper(user, "The queue has {0} item(s). The next item to be shown is at index {1}".format(len(Queue), currentIndex))
    return


def GetLinksFromItem(index):
    item = json.loads(Queue[index])
    originalMessage = item['message']

    results = re.findall(r'(https?://[^\s]+)', originalMessage)
    links = {'links': results}
    return links