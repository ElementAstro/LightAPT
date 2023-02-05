Focuser API
===========

## Client Side 

We will expose the following APIs to the client for calling:

### connect
Connect to the focuser by name
```
Params : device_name : str
Returns : dict | str | None
    info : infomation ahout focuser containing in a dictionary
```
### disconnect
Disconnect from the connected focuser
```
Params : None
Returns : dict | str | None
```
### reconnect
Reconnect to the connected focuser
```
Params : None
Returns : dict | str | None
```
### scanning
Scanning the available focusers (Maybe only for ASCOM)
```
Params : None
Returns : dict | str | None
    focuser : list # a list of the available focusers' names
```
### polling
Get the newest infomation about the focuser
```
Params : None
Returns : dict | str | None
    info : focuser information containing in a dictionary
```
### get_parameter
Get the specified parameter value of the focuser
```
Params : name : str
Returns : dict | str | None
    value : the specified parameter value
```
### set_parameter
Set the parameter value of the focuser
```
Params :
    name : str
    value : the parameter value
Returns : dict | str | None
```

### move_to
Move to a specific position
```
Params : dict
    position : int
Returns : dict | str | None
```
### move_step
Move a number of steps to a specific position
```
Params : dict
    step : int
Returns : dict | str | None
```
### abort_movement
Abort the current movement operation
```
Params : None
Returns : dict
    position : int the last position of the focuser
```
### get_movement_status
Get the status of the current movement operation
```
Params : None
Returns : dict
    status : bool
```
### get_temperature
Get the current temperature of the focuser,this may require hardware support.
```
Params : None
Returns : dict
    temperature : float
```
### get_current_position
Get the current position of the focuser , this may be called will the movement is in progress.
```
Params : None
Returns : dict
    position : int
```
