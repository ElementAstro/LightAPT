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

# Functions

### Http Request
The following functions are called by http request

+ start_phd2 / stop_phd2 
start or stop the phd2 instance
```
Args : path : str # the full path to the PHD2 executable
Returns : {
    "message" : str # if the PHD2 server is started or stopped successfully , the message will be None
}
```

+ scan_server / connect_server / disconnect_server
after started the server , maybe we nned to find where the server is listening on , so call scan_server() , this is for the windows users or the desktop users.
```
Args: range : list # the range of the port we need to scan
Returns: {
    "list" : [port] # a list of ports , None if there are no server listening on
}
```
After we know the port of the server , we should set up the connection first . call connect_server()
```
Args : port : int # the port of the server , default is 4400
Returns: {
    "message" : str # the message of the operation , None if succeeded
```
disconnect_server()
```
Args : None
Returns: {
    "message" : str # the message of the operation , None if succeeded
}
```
reconnect_server()
```
Args : None
Returns: {
    "message" : str # the message of the operation , None if succeeded
}
```

+ get_proflies / get_current_profile / set_profile / generate_profile
Due to the limitation of the interface provided by the server, we cannot directly provide the configuration file.
```
get_profiles()
Args : None
Returns : {
    "list" : a list of the profiles dicts available on the server , if there is no profile available , just return an empty list
}
Example : [{
    "id":profile_id,
    "name":"profile_name",
    "camera":{"name":"Simulator","connected":true},
    "mount":{"name":"On Camera","connected":true},
    "aux_mount":{"name":"Simulator","connected":true},
    "AO":{"name":"AO-Simulator","connected":false},
    "rotator":{"name":"Rotator Simulator .NET (ASCOM)","connected":false
}]
```
Sometimes we also need to get the currently loaded configuration file.
```
get_current_profile()
Args : None
Returns : {
    "id":profile_id,  # the current loaded profile
    "name":"profile_name",
    "camera":{"name":"Simulator","connected":true},
    "mount":{"name":"On Camera","connected":true},
    "aux_mount":{"name":"Simulator","connected":true},
    "AO":{"name":"AO-Simulator","connected":false},
    "rotator":{"name":"Rotator Simulator .NET (ASCOM)","connected":false
}
```
After we get the relevant information of all configuration files, the user can decide which to connect to.
```
set_profile()
Args : profile_id : int # the ID of the profile , the same as the above
Returns : {
    "message" : str # None if the operation is successful
}
```
But sometimes, there will be no required configuration file. At this time, we need to generate a configuration file that conforms to the format, and then let the server read it.
```
generate_profile()
Args : {
    "id" : int # The default is to add one to the existing quantity
    "name" : str # The name of the profile , should be specified by the user
    "camera" : str # The name of the camera driver , Users should choose, not fill in
    "mount" : str # The name of the mount driver , Users should choose, not fill in
    I'm not sure whether other devices need to write. If so, the format is the same.
}
```

+ connect_device / disconnect_device / reconnect_device
After we confirm the configuration file, we can connect the device
```
connect_device()
Args : None
Returns : {
    "message" : None if the operation succeeded
}
```
However, we do not rule out the need to disconnect from the device, such as when the server stops
```
disconnect_device()
Args : None
Returns : {
    "message" : None if the operation succeeded
}
```
Encapsulation of connected devices and disconnected devices.
```
reconnect_device()
Args : None
Returns : {
    "message" : None if the operation succeeded
}
```

### Webscoket Interface
These are the interface functions of Websocket.

#### Calibration Interface
After the device is connected successfully, we will start calibration, which is the key step for successful star guidance
+ start calibration / stop_calibration / clear_calibration_data / flip_calibration_data

Start calibration
```
start_calibration()
```
Stop calibration
```
stop_calibration()
```
Clear calibration data
```
clear_calibration_data()
Args : None
Returns : {
    "message" : str # None if the operation is successful
}
```
Flip the calibration data
```
flip_calibration_data()
Args : None
Returns : {
    "message" : str # None if the operation is successful
}
```

#### Guiding Interface

+ start_guiding / stop_guiding / pause_guiding / resume_guiding
```
start_guiding()
Args : {
    "pixel" : float # maximum guide distance for guiding to be considered stable or "in-range"
    "time" : int # minimum time to be in-range before considering guiding to be stable
    "timeout" : int # time limit before settling is considered to have failed
    "recalibration" : bool # whether to restart the calibration before guiding
}
Returns : {
    "message" : str # None if the operation is successful
}
```
Stop guiding star
```
stop_guiding()
Args : None
Returns : {
    "message" : str # None if the operation is successful
}
```
Stop guiding star but do not stop cyclic exposure.
```
pause_guiding()
Args : None
Returns : {
    "message" : str # None if the operation is successful
}
```
Just to be symmetrical with the above function.
```
resume_guiding()
Args : None
Returns : {
    "message" : str # None if the operation is successful
}
```

##### Dither
Dithering is to eliminate the horizontal lines in the image. It should be dithered once after several pictures are taken. It is necessary to set the dithering range and stable conditions
```
dither()
Args : {
    "pixel" : float # maximum guide distance for guiding to be considered stable or "in-range"
    "time" : int # minimum time to be in-range before considering guiding to be stable
    "timeout" : int # time limit before settling is considered to have failed
    "raonly" : bool # whether the dither will only be on the RA axis
    "amount" : int # amount in pixels
}
Returns : {
    "message" : str
}
```

#### Image 

We need to obtain real-time images from the server, but there seems to be a small problem with this function of PHD2.

+ start_looping / stop_looping
  
Cycle exposure to obtain real-time image for star point selection
```
start_looping()
Args : None
Returns : {
    "message" : str # None if the operation is successful
}
```

Abort the looping operation
```
stop_looping()
Args : None
Returns : {
    "message" : str # None if the operation is successful
}
```

+ get_image / save_image

Get real-time images
```
get_image()
Args : None
Returns : {
    "frame" : int # frame number
    "width" : int # width in pixels
    "height" : int # height in pixels
    "image" : str # a base64 encoded image
    "star_position" : list # The position of the star is locked , [x,y]
}
```

Save the image to the specified folder
```
save_image()
Args : None
Returns : {
    "path" : str # the full path to the image
}
```