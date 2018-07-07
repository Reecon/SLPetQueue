#---------------------------
#   Import Libraries
#---------------------------
import os
import codecs
import sys
import json
import re
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
Version = "1.0.0.0"

#---------------------------
#   Define Global Variables
#---------------------------
global SettingsFile
SettingsFile = ""
global ScriptSettings
ScriptSettings = MySettings()

global QueueHtmlPath
QueueHtmlPath = os.path.abspath(os.path.join(os.path.dirname(__file__), "Queue.html"))

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
    ui['Cooldown']['value'] = ScriptSettings.Cooldown
    ui['Permission']['value'] = ScriptSettings.Permission
    ui['Info']['value'] = ScriptSettings.Info

    try:
        with codecs.open(UiFilePath, encoding="utf-8-sig", mode="w+") as f:
            json.dump(ui, f, encoding="utf-8", indent=4, sort_keys=True)
    except Exception as err:
        Parent.Log(ScriptName, "{0}".format(err))

    # read client id for api access from file
    try:
        with codecs.open(os.path.join(os.path.dirname(__file__), "clientid.conf"), mode='r', encoding='utf-8-sig') as f:
            global ClientID
            ClientID = f.readline()
    except Exception as err:
        Parent.Log(ScriptName, "{0}".format(err))

    return

#---------------------------
#   [Required] Execute Data / Process messages
#---------------------------
def Execute(data):
    #   only handle messages from chat
    if data.IsChatMessage() and data.GetParam(0).lower() == ScriptSettings.Command and not Parent.IsOnCooldown(ScriptName, ScriptSettings.Command) and Parent.HasPermission(data.User, ScriptSettings.Permission, ScriptSettings.Info):

        # check if target was given
        if data.GetParam(1):
            target = data.GetParam(1)
        else:
            return
        
        cleanMessage = data.Message[len(ScriptSettings.Command):].strip()
        
        jsonData = '{{"user": "{0}", "message": "{1}" }}'.format(data.User, cleanMessage)
        
        Parent.BroadcastWsEvent("EVENT_PET_QUEUE", jsonData)
        Parent.AddCooldown(ScriptName, ScriptSettings.Command, ScriptSettings.Cooldown)  # Put the command on cooldown

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
    return

