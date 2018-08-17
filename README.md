# PetQueue

Intended as a queue for people to post pictures of their pets, this can of course be used for any sort of link or even just message queue.

## Installation

* Donwload the [latest release](https://github.com/Reecon/SLPetQueue/releases/latest)
* Import zip into bot
* Right-click script and select `Insert API Key`

## Usage

You can use this queue in two ways. Through the `Queue.html` page or remote controled by your mods (or other viewers) with the `Viewer.html`.

__Note:__ I would recommend using only one method, based on how easily accessible the manual queue is for you during your streams.

### Queue.hmtl

Open the HTML file by clicking the `Open Queue` button in the `Core` section of the script's settings UI. It will start listening for incoming events
and display the messages and links in a list.

You can open the links individually or all at once with the `open all` button in the top left corner.

To remove individual entries, you can click the `remove` button for that entry. Or you can empty the entire list with the `clear q` button in the top right corner.

__Note:__ You have to allow popups for this site for the `open all` button to work.

__Note:__ Removing item here, will not remove them from the remote controlled queue.

__Note:__ Opening the HTML file will clear the internal queue for remote control.

### Viewer.html

In the `Remote` section of the script settings, you can find the options for the remote control feature. This is inteded to be used by your moderators or other viewers via whispers in situations where you can't go through the manual list by yourself.

To open the HTML file expand the `Remote` section and click the `Open Viewer` button.
The page you see will handle logic and has this nice easy-on-the-eyes color so you can chroma-key it out easily in your streaming software.

Add your browser window as a `Window Capture` to your streaming software and add a chroma-key filter for `rgb(0,255,0)`. Additionaly crop the window capture in a way that you can't see the control elements of your browser, to make the window invisible when no images are shown. Of course feel free to edit the `Viewer.html`
file to change the background however you want.

Links will opened in new tabs of your browser window, and automatically closed after 15 seconds. If the message contained multiple links, all of them will be openend in succession with the same 15 second delay.

Viewers with the neccessary privileges are now able to use the following whisper commands to control the queue.
All commands have to be preceeded by the chosen `Remote Command` (`!q` by default).

Command | Param | Description
------- | ----- | -----------
show |  | Opens the next link in the queue, if one is available. Moves current pointer to the next position. Responds in a whisper with the item that will be shown on screen and the next item on the list.
show | index | Opens the link at the given index of the queue, without advancing the current position. Responds in a whisper with the item that will be shown on screen.
preview | | Responds in a whisper with the index, username and message of the queue item that will be shown next.
preview | index | Responds in a whisper with the index, username and message of the queue item at the given index.
skip | | Will skip the next item in the list for and respond in a whisper with information about the skipped item and the next item in line.
remove | index | Will remove the item at the given index and respond in a whisper with information about the removed item.
info | | Responds in a whisper with the length of the queue and the current position of the pointer.
clear | | Deletes the entire queue!

__Note:__ All indices are starting at `0`. For example `!q preview 0` gives information about the first element of the queue.

__Note:__ You have to allow popups for this site for so the page can open the links.

__Note:__ Removing items here will not remove them from the manual queue.
