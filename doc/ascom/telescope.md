Telescope API
=============

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

### goto
Goto operation
```
Params : dict
    j2000 : bool , whether the coordinates format is in J2000
    ra : str | float , suggest to be float
    dec : str | float , suggest to be float
Returns : dict
```
### abort_goto
Abort the current operation
```
Params : None
Returns : dict
    ra : str | the last coordinate of the RA before aborting
    dec : str | the last coordinate of the DEC after aborting
```