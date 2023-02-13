[![CodeQL](https://github.com/AstroAir-Develop-Team/lightapt/actions/workflows/codeql.yml/badge.svg)](https://github.com/AstroAir-Develop-Team/lightapt/actions/workflows/codeql.yml)
[![CodeQL](https://github.com/AstroAir-Develop-Team/lightapt/actions/workflows/codeql.yml/badge.svg)](https://github.com/AstroAir-Develop-Team/lightapt/actions/workflows/codeql.yml)
[![build docker image](https://github.com/AstroAir-Develop-Team/lightapt/actions/workflows/docker-image.yml/badge.svg)](https://github.com/AstroAir-Develop-Team/lightapt/actions/workflows/docker-image.yml)

# LightAPT
Light weight and Flexible Astro Photography Terminal based on Python and JavaScript

## Architecture

The architecture in LightAPT is inspired by INDI (https://github.com/indilib/indi)

    LightAPT Client 1 ----|                      |---- LightAPT Driver A  ---- Dev X
                          |                      |
    LightAPT Client 2 ----|                      |---- LightAPT Driver B  ---- Dev Y
                          |                      |                              |
            ...           |--- LightAPTserver ---|                              |-- Dev Z
                          |                      |
                          |                      |
    LightAPT Client n ----|                      |---- LightAPT Driver C  ---- Dev T


    Client       INET         Server       Driver          Hardware
    processes    websocket    process      processes       devices
    
## Features

Even though LightAPT is very lightweight, it still retains a lot of practical features

+ Based on INDI and ASCOM , most of the devices support
+ Online/Offline skymap , easy to build your image
+ Remote desktop connection support via noVNC
+ Remote shell support via WebSSH
+ Image viewer and compresser support
+ Small tools for image processing and star searching
+ Beautiful web user interface and highly customizable
+ Code optimization support
+ Open source under GPL3 license

## Development
Most of the codes are written in Python and JavaScript, and we will try to add more languages to be supported. No matter what languages you are good at, just join QQ group and discuss together.

### Build

Just like the name of the project, only a few dependent libraries are needed to start
Pay attention to that optional dependencies are recommended to be installed for the better performance and experience.After our test , all of the following dependencies are cross-platform.

#### Requirements

+ astropy(optional) : For fits image processing and astronomical calculation
+ cv2 : Image processing and calculations
+ ephem : Calculate star coordinates
+ numpy : Image processing and calculations
+ paramiko(optional) : SSH client to support WebSSH
+ psutil(optional) : System units
+ requsets : Alpyca backend
+ tornado(optional) : High performance web server for WebSSH

#### Installation

Fisrt , you should install all of the required libraries . You can run this command
`
pip install -r requirements.txt
`

Then get into the root directory , and run the following command
`
python lightserver.py
`

That's all right now and you can enjoy the awesome of the astronomy and universe.

## Support

+ QQ Group 710622107
+ Email astro_air@126.com
