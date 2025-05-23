# Automatic failover for Ableton and OSC

Version 1.0

## Overview

This project aims to develope a solution for automatic failover if playback on an Ableton live playback drops out. To achive this the OSC Server waits for a playback comand and then starts monitoring an audio impot. When scilence is detected an OSC comand is send to a mixing console or other hardware. This message is intend to trigger any emergency action like switching audio inputs or unmute a playback device.

## Scilence Detector

Scilence Detector is a little script to monitor some input and send OSC messages on detecting scilence

## OSC Monitor

Is a little OSC server for testing porposes. It recives OSC messages and prints them to console

## OSC Monitor

Is a littel commandline tool to send OSC messages to any device.

## automatic failover

This program is the main functionality. It is intendet to be used in conjunction with a DAW that is able to send and recive OSC messages. This is all setup for Ableton but could also be done with Reaper

# Setup and installation

Download the repo and install a all dependencys

    git clone https://github.com/Nu55k0pF/ScilenceDetector.git
    python -m venv myvenv
    pip install -r requirements.txt

Configure the server to your liking and start the automatic_failover.py

# To does

- Add a helper script to choos your audio settings
- Make automatic failover end gracefully 


