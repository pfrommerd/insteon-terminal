# Insteon Terminal
The Insteon Terminal is a simple tool to send and receive messages on an Insteon network, using either a PLM modem or a Hub.

Look elsewhere if you want a polished interface to automate your home. The Insteon Terminal is meant as a raw developer tool for the purpose of exploring how a device responds to a message, and what messages a device emits. Be forewarned: you can do highly dangerous stuff like directly modifying a device's (or your modem's) link database.

# Getting started
All instructions are for Ubuntu 14.04

- install ant
  sudo apt-get install ant
- clone the repository:
  git clone https://github.com/vastsuperking/insteon-terminal.git
- create your custom init.py
  cd insteon-terminal
  cp init.py.example init.py
- edit init.py following the instructions there:
  emacs -nw init.py


