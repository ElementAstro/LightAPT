Camera API
==========

## Client Side 

We will expose the following APIs to the client for calling:

### connect
Connect to the camera by name
```
Params : device_name : str
Returns : dict | str | None
    info : infomation ahout camera containing in a dictionary
```
### disconnect
Disconnect from the connected camera
```
Params : None
Returns : dict | str | None
```
### reconnect
Reconnect to the connected camera
```
Params : None
Returns : dict | str | None
```
### scanning
Scanning the available cameras (Maybe only for ASCOM)
```
Params : None
Returns : dict | str | None
    camera : list # a list of the available cameras' names
```
### polling
Get the newest infomation about the camera
```
Params : None
Returns : dict | str | None
    info : camera information containing in a dictionary
```
### get_parameter
Get the specified parameter value of the camera
```
Params : name : str
Returns : dict | str | None
    value : the specified parameter value
```
### set_parameter
Set the parameter value of the camera
```
Params :
    name : str
    value : the parameter value
Returns : dict | str | None
```

### start_exposure
Start the exposure operation , non-blocking
```
Params : exposure : float
Returns : dict | str | None
```
### abort_exposure
Abort the current exposure operation
```
Params : None
Returns : dict | str | None
```
### get_exposure_status
Get the current exposure status of the camera
```
Params : None
Returns : dict | str | None
    status : bool whether the operation is executing
```
### get_exposure_result
Get the exposure result of the camera
```
Params : None
Returns : dict | str | None
    image : nparray
    info : dict
```
### cooling
Start or stop the cooling mode
```
Params : enable : bool
Returns : dict | str | None
```
### cooling_to
Cooling to the specified temperature
```
Params : temperature : float
Returns : dict | str | None
```
### get_cooling_status
Get the cooling status , return true if the camera is cooling
```
Params : None
Returns : dict | str | None
    status : bool
```
### get_current_temperature
Get the current temperature of the current camera
```
Params : None
Returns : dict | str | None
    temperature : float
```
### get_cooling_power
Get the current cooling power of the camera
```
Params : None
Returns : dict | str | None
    power : float
```

### get_camera_roi
Get the ROI settings of the camera frame
```
Params : None
Returns : dict
    height : int
    width : int
    start_x : int
    start_y : int
```
### get_gain
Get the current gain of the camera
```
Params : None
Returns : dict
    gain : int
```
### get_offset
Get the current offset of the camera
```
Params : None
Returns : dict
    offset : int
```
### get_binning
Get the binning mode of the camera
```
Params : None
Returns : dict
    binning : list [x,y]
```

### set_camera_roi
Set the ROI of the camera frame
```
Params : dict
    height : int
    width : int
    start_x : int
    start_y : int
Returns : dict
```
### set_gain
Set the gain of the camera
```
Params : dict
    gain : int
Returns : dict
```
### set_offset
Set the offset of the camera
```
Params : dict
    offset : int
Returns : dict
```
### set_binning
Set the binning of the camera
```
Params : dict
    binning : list [x,y]
Returns : dict
```
### call
Call some function with the function name and parameters
```
Params : dict
    name : function name
    params : function parameters
Returns : dict
```