ASCOM Interface
===============

Here is the calling interface provided for the client. All interfaces are asynchronous.

If the returned format is as shown below.Here, returning a dictionary means returning the default format, just like the following
```
Returns : dict
```
Equivalent to
```
{
    "status" : int , 0 means success , 1 means error , 2 means warning
    "message" : str , a short message about the result
    "params" : None , just a placeholder
}
```
But if it is in the following format, it has different meanings:
```
Returns : dict
    xxx : xxx
```
Equivalent to
```
{
    "status" : int ,
    "message" : str ,
    "params" : {
        "xxx" : xxx
    }
}
```
All parameters to be returned are stored in the parameter dictionary.

Unfortunately, this structure is not an ideal return structure, so we wrote a function to generate commands in addition. In order to highlight the advanced nature, we used completely unnecessary asynchronous functions to complete this task.
You can run the following functions to get the format that the client really needs
```
await generate_message(dict)
```

At the same time, due to the problem of connection and disconnection of the ws client, we cannot directly pass the instance of ws into the class during initialization, so each function needs to be passed into the instance of ws. By default, it does not need to be managed. Because the default is empty, only a few functions, such as starting exposure, need to be monitored by thread.