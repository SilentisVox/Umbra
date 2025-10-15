# Umbra

Umbra is an open source, cross platform framework designed to help organizations of all sizes practice security testing. Its primary purpose is to stage and manage HTTPS/TLS reverse shells. This makes it a very important tool for pentesters and offsec practicers.

The service as a whole, is fully operational on both Windows and Linux. 

[![Python](https://img.shields.io/badge/Python-%E2%89%A5%203.6-yellow.svg)](https://www.python.org/)
<img src="https://img.shields.io/badge/Developed%20on-Windows%2011-1677CF">
[![License](https://img.shields.io/badge/License-BSD%203%20Clause%20license-C91515)](https://github.com/SilentisVox/Silence/blob/master/LICENSE)
<img src="https://img.shields.io/badge/Maintained%3F-Yes-1FC408">

### Features

- Interactive CLI
- Argument Parsing for Configuration
- HTTPS/TLS Stager
- Payload Generation
- Session Management Commands
- Service Control Commands
- Utility Commands
- Core Client-Side Payload
- Colorized Output and Formatting
- API Integration
- API Logging

### Setup

```
git clone https://github.com/SilentisVox/Umbra
cd Umbra
python3 Umbra.py
```

### Usage

```
python3 Umbra.py [-h] -c [callback_address] -p [callback_port]
```

### Example

```
 → python Umbra.py -h

usage: Umbra.py [-h] [-c C] [-p P] [-l L]

options:
  -h, --help  show this help message and exit
  -c C        Callback address
  -p P        HTTPS Handler port (Default 443)
  -d D        Client dwell time.
```

```
Umbra> help

 Command       Description
 ----------------------------------------------------------------------

 shell    [+]  Begins communication with a specified client.
 sessions      Displays current sessions avaialable.
 generate      Generates a reverse shell payload w/ settings.
 jobs          Displays current services running.
 start    [+]  Starts the HTTPS service.
 stop     [+]  Stops the HTTPS service.
 kill     [+]  Kills a connection with a specified client.
 eradicate     Kills all current sessions.
 help          Displays this menu.
 clear         Clears the terminal window.
 exit          Exits Silence.
```