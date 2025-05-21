# Automatic failover for Ableton and OSC
## Overview
This project aims to develope a solution for automatic failover if playback on an Ableton live playback dops out. To achive this the OSC Server waits for a playback comand and then starts monitoring an audio impot. When scilence is detected an OSC comand is send to a mixing console or other hardware, to switch inputs to a backup system

## Setup and configuration

work in progress

## Scilence Detector
Scilence Detector is a little script to monitor some input and send OSC messages on detecting scilence

## OSC Server
Contains the main functionality. The program is intended to be used to monitor a playback and send an OSC message to do emergency actions e.g. automatic failover to a different playback source. The program contains an example handler that starts listening if the Reaper Playback toggel is recived as OSC message. If scilence is detected, playback is stopped.

ATTENTION if you install the dependencys regularly there will be no ASIO support

# Installation Guide for PyAudio with ASIO Support

The default PyAudio you can install with 

    pip install PyAudio

does not come with ASIO support. That is becaus the PortAudio Build linked in PyAudio was not compiled with ASIO Support. However you could compile PortAudio yourself like described here
https://portaudio.com/docs/v19-doxydocs/compile_windows.html

Or you can find a PyAudio .whl that was compiled with ASIO support like the one in this repository. If you are brave enough you can download it and install it like so:

    pip install PyAudio-0.2.11-cp311-cp311-win_amd64.whl

Aperently Christoph Gohlke hosts pyaudio .whl with ASIO support. But as of 21.05.2025 I could not find any PyAudio .whl on his site:

https://github.com/cgohlke/win_arm64-wheels?tab=readme-ov-file
