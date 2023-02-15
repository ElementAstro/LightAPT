[![CodeQL](https://github.com/AstroAir-Develop-Team/lightapt/actions/workflows/codeql.yml/badge.svg)](https://github.com/AstroAir-Develop-Team/lightapt/actions/workflows/codeql.yml)
[![CodeQL](https://github.com/AstroAir-Develop-Team/lightapt/actions/workflows/codeql.yml/badge.svg)](https://github.com/AstroAir-Develop-Team/lightapt/actions/workflows/codeql.yml)
[![build docker image](https://github.com/AstroAir-Develop-Team/lightapt/actions/workflows/docker-image.yml/badge.svg)](https://github.com/AstroAir-Develop-Team/lightapt/actions/workflows/docker-image.yml)

LightAPT
========
Lightweight Astronomical Photography Terminal

- [LightAPT](#lightapt)
  - [Why do we make this software](#why-do-we-make-this-software)
  - [Architecture](#architecture)
  - [Features](#features)
  - [File structure](#file-structure)
  - [Development](#development)
    - [Build](#build)
      - [Requirements](#requirements)
      - [Installation](#installation)
  - [Support](#support)


## Why do we make this software

In previous astronomical photography, enthusiasts had to endure quite bad weather and wait by the computer for the shooting to be completed, which not only required carrying a lot of additional equipment, but also had a very bad experience.

Now, the same products have been sold on the market, but they are closed source commercial, and only support their own devices. The compatibility of other devices is either poor or simply not supported. This makes us very angry, so we have the idea of making open source astronomical pi.

Although there are strong competitors, we will not give up because we firmly believe that the world belongs to open source.

## Architecture

The architecture in LightAPT is inspired by INDI (https://github.com/indilib/indi)
```
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
```
## Features

Although the server is relatively lightweight, it has complete functions. Here are the features of this software.

+ Extensive platform support, supporting all mainstream operating systems
+ The device driver based on INDI and ASCOM supports most astronomical devices
+ Highly optimized asynchronous architecture, stable and efficient
+ The modified PHD2 is built in as the guide tool, and the asap and astrometry are used as the platesolving engine
+ Multiple interface access, supporting web client, desktop client and even terminal interface
+ Fully open source based on GPL3

## File structure

```python
/client # Front-end pages and required static files
    /static # Static Files
        /css # All of the CSS Files
        /font # Fontawesome
        /js # All of the JavaScript Files
        /json # Some JSON needed to be loaded by the client
        /sounds # Some sounds
        /textures # Image...
        /webfonts # Fontawesome
    /templates # Page
/doc # Documents
/locale # I18n
/server # Full back-end
    /api # Call API encapsulation of other software
        /ascom # ASCOM Remote Client
        /astap # Astap Command Line Interface
        /astrometry # Another solver
        /indi # INDI Client
        /phd2 # PHD2 Client
        /tcp2ws # Convert a socket connection to a websocket connection
    /config # Server configuration
    /data # The backend needs something like database
    /guider # PHD2
    /indi # Complete server and compilation options, supported devices required
    /plugins # Some useful tools
    /polaralign # Polar Alignment
    /tui # Terminal UI
    /webssh # Web shell client to connect SSH
    /ws # Websocket Worker
/tools # Some useful shell scripts
/utils # Some interesting functions or components

```

## Development

The project code is mainly written by c++, python and javascript. If you are interested, you can contact Chewang in QQ group, who will be responsible for reviewing whether you can join the development group.

### Build

Just like the name of this software, it does not rely on many software.You only need to run a few lines of commands to complete the installation

Pay attention to that optional dependencies are recommended to be installed for the better performance and experience.After our test , all of the following dependencies are cross-platform.

#### Requirements

+ astropy(optional) : For fits image processing and astronomical calculation
+ cv2 : Image processing and calculations
+ ephem : Calculate star coordinates
+ numpy : Image processing and calculations
+ paramiko(optional) : SSH client to support WebSSH
+ psutil(optional) : System units
+ requsets : Alpyca backend
+ textual : TUI library
+ tornado(optional) : High performance web server for WebSSH

#### Installation

Fisrt , you should install all of the required libraries . You can run this command
```
pip install -r requirements.txt
```

Then get into the root directory , and run the following command
```
python lightserver.py
```

That's all right now and you can enjoy the awesome of the astronomy and universe.

## Support

+ QQ Group 710622107
+ Email astro_air@126.com
