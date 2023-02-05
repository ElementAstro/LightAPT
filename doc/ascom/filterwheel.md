Filterwheel API
===============

## Client Side 

We will expose the following APIs to the client for calling:

### connect
Connect to the filterwheel by name
```
Params : device_name : str
Returns : dict | str | None
    info : infomation ahout filterwheel containing in a dictionary
```
### disconnect
Disconnect from the connected filterwheel
```
Params : None
Returns : dict | str | None
```
### reconnect
Reconnect to the connected filterwheel
```
Params : None
Returns : dict | str | None
```
### scanning
Scanning the available filterwheels (Maybe only for ASCOM)
```
Params : None
Returns : dict | str | None
    filterwheel : list # a list of the available filterwheels' names
```
### polling
Get the newest infomation about the filterwheel
```
Params : None
Returns : dict | str | None
    info : filterwheel information containing in a dictionary
```
### get_parameter
Get the specified parameter value of the filterwheel
```
Params : name : str
Returns : dict | str | None
    value : the specified parameter value
```
### set_parameter
Set the parameter value of the filterwheel
```
Params :
    name : str
    value : the parameter value
Returns : dict | str | None
```

### slew_to
Let the filterwheel slew to a specified position
```
Params : dict
    position : int
Returns : dict | str | None
```
### get_filter_list
Get the list of filterwheel's filters' names and focusing offsets
```
Params : None
Returns : dict
    name : list of the names of the filters
    offset : list of the offsets of the filter
```
### get_current_filter
Get the current filter
```
Params : None
Returns : dict | str | None
    position : int
```