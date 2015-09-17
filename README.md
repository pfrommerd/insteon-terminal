# Insteon Terminal
The Insteon Terminal is a simple tool to send and receive messages on an Insteon network, using either a PLM modem or a Hub.

Look elsewhere if you want a polished interface to automate your home. The Insteon Terminal is meant as a raw developer tool for the purpose of exploring how a device responds to a message, and what messages a device emits. Be forewarned: you can do highly dangerous stuff like directly modifying a device's (or your modem's) link database.

### Support

Google groups mailing list:
<https://groups.google.com/forum/#!forum/insteon-terminal>

# Getting started
All instructions are for Ubuntu 14.04

1) install ant, java jdk, and the java rxtx library:

    sudo apt-get install ant default-jdk librxtx-java

2) clone the repository:

    git clone https://github.com/vastsuperking/insteon-terminal.git

3) create your custom init.py

    cd insteon-terminal
    cp init.py.example init.py

4) edit init.py following the instructions there:

    emacs -nw init.py

5) See if it compiles:

    ant compile

6) Start the terminal:

    ant run

Getting the serial terminal to work under java / rxtx can be tricky. Make sure you have the correct port name configured in init.py and that you have read/write permissions to the port (usually this involves adding yourself to the plugdev group and logging out/back in for the changes to take effect).

7) If all goes well, try using some of the devices you defined in init.py, for example print out your modem db:

    modem.getdb()

or switch on a light:

    closetLight.on()
    





