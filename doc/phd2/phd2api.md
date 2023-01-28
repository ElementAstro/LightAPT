PHD2 Client API for LightAPT
============================

# Working methods

PHD2 is a standalone software , so we can just set up a socket connection with it and read/write messages .Because the PHD2 is asynchronous so the socket should keep alive until disconnect from the server , may be just in a thread.

# How to start 

First , we need to get all of the profiles had already existing in PHD2 server side.

`-> get_profiles`

Next , we should choose a specific profile to start device and connect . 

`-> set_connected False` Make sure that before changing the profile , the devices are not connected.

`-> set_profile profile` Send the id of the profile 

`-> set_connected True` Then you can setup the connection to the device

Then , we may do different things like guiding or calibrating . All of these commands should work not crashing . For example , if you are calibrating the telescope , do not send guiding command during calibration . 

`-> guide`

# About the wrapper API

Not like other devices , when you execute `connect` command , this will just connect to the PHD2 server and you can use `scanning` to look for the available server in a range of different ports.

After connection setup successfully , you can call `get_profiles` method to get the list of profiles available in the server , then choose one of them to connect `set_profile`

After the devices are all connected , you can run `start_guiding` or `start_calibrating`.

About the dither function , this should be called while PHD2 is in guiding mode.Pay attention to that if the guider is settling , please do not call dither command.