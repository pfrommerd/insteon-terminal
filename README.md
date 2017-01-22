# Insteon Terminal
The Insteon Terminal is a simple tool to send and receive messages on an Insteon network, using either a PLM modem or a Hub.

Look elsewhere if you want a polished interface to automate your home, or if you don't like command line interfaces.

The Insteon Terminal is meant as a raw developer tool for the purpose of exploring how a device responds to a message, and what messages a device emits. It is also well suited to examine and modify device link databases.

BE FOREWARNED: you can directly manipulate your modem's link database, and IF YOU TRY HARD YOU CAN WIPE IT OUT, potentially requiring you to re-link with your devices. Use the saveDB() method on the modem to save the database before you modify it.

### Support

Google groups mailing list:
<https://groups.google.com/forum/#!forum/insteon-terminal>

### Note for users updating from pre-December 19, 2015 versions:

After some refactoring in the core terminal code, I realized I had made a mistake when designing the initial python-java integration. I fixed the issue, which broke the init.py "import" statements. The init.py.example has been updated with the correct syntax (which should not include "python." before the module), but any existing init.py's will need to be modified to remove the "python." at the start of all the imports. Sorry for the inconveniance.

# Getting started
All instructions are for Ubuntu 14.04

1) install ant, java jdk, and the java rxtx library:

    sudo apt-get install ant default-jdk librxtx-java

   Note: if you are using Oracle's java version and have it installed under e.g. /usr/lib/jvm/java-8-oracle/, link the serial port library as follows (the last part of the path may vary depending on your hardware). This step is not necessary *only* if you use openjdk.

    cd /usr/lib/jvm/java-8/-oracle/jre/lib/amd64
    ln -s /usr/lib/jni/librxtxSerial.so .


2) clone the repository:

    git clone https://github.com/vastsuperking/insteon-terminal.git

3) create your custom init.py

    cd insteon-terminal
    cp init.py.example init.py

4) edit init.py following the instructions there:

    emacs -nw init.py

5) Run the insteon terminal (this should compile when run the first time)

    ./insteon-terminal

To force the terminal to run in console mode, use the -nw flag. If you are running in a graphics-less environment, the terminal will automatically run in console mode.

Getting the serial terminal to work under java / rxtx can be tricky. Make sure you have the correct port name configured in init.py and that you have read/write permissions to the port (usually this involves adding yourself to the plugdev group and logging out/back in for the changes to take effect).

6) If all goes well you will see the following text:

    Insteon Terminal
    Python interpreter initialized...
    >>>       

### Updating

To update the terminal, run:

    git pull
    ant clean
    ./insteon-terminal


#First steps

    >>> help()
    -------Welcome to the Insteon Terminal-------
    to get a list of available functions, type '?'
    to get help, type help(funcName) or help(objectName)
    for example: help(Modem2413U)
    to quit, type 'quit()'


let's see what functions we have available:

    >>> ?
    ----All available functions---
    Timer() - No doc
    clear() - clears the console screen
    connectToHub() - connectToHub(adr, port, pollMillis, user, password) connects to specific hub
    connectToMyHub() - connects to my insteon hub modem at pre-defined address
    connectToMySerial() - connects to my modem on pre-defined serial port
    connectToSerial() - connectToSerial("/path/to/device") connects to specific serial port
    disconnect() - disconnects from serial port or hub
    err() - prints to std err the value of msg and a newline character
    exit() - quits the interpreter
    help() - help(object) prints out help for object, e.g. help(modem)
    init() - No doc
    listDevices() - lists all configured devices
    out() - out("text") prints text to the console
    quit() - quits the interpreter
    reload() - Reloads the interpreter. Use this whenever you feel the state got screwed up.
    reset() - Resets the interpreter
    trackPort() - start serial port tracker(monitor) that shows all incoming/outgoing bytes

listDevices() will dump a list of all devices that are defined in init.py:

    >>> listDevices()
    diningRoomEastDimmer           20.ac.99
    computerRoomEast               24.ac.f4
    kitchenFireplaceLights         23.e8.2e
    modem                          23.9b.65

you can get help for any device by using the help() function on the object

    >>> help(modem)
    ==============  Insteon PowerLinc modem (PLM) ===============
    addController(addr, group):               adds device with address "addr" to modem link database as controller for group "group"
    addResponder(addr, group):                adds device with address "addr" to modem link database as responder to group "group"
    addSoftwareResponder(addr):               adds device with address "addr" to modem link database as software responder
    cancelLinking()                           takes modem out of linking or unlinking mode
    getId()                                   get category, subcategory, firmware, hardware version
    getdb()                                   download the modem database and print it on the console
    getid()                                   get modem id data
    linkAsController(otherDevice, group)      puts modem in link mode to control device "otherDevice" on group "group"
    linkAsEither(otherDevice, group)          puts modem in link mode to link as controller or responder to device "otherDevice" on group "group"
    linkAsResponder(otherDevice, group)       puts modem in link mode to respond to device "otherDevice" on group "group"
    loadDB(filename)                          restore modem database from file "filename"
    nukeDB()                                  delete complete modem database!
    printdb()                                 print the downloaded link database to the console
    removeController(addr, group)             remove device with "addr" as controller for group "group", with link data "data"
    removeLastRecord()                        removes the last device in the link database
    removeResponder(addr, group)              remove device with "addr" as responder for group "group"
    removeResponderOrController(addr, group)  removes device with address "addr" and group "group" from modem link database
    respondToUnlink(otherDevice, group)       make modem respond to unlink message from other device
    restoreDB()                               restore modem database from file "filename"
    saveDB(filename)                          save modem database to file "filename"
    sendOff(group)                            sends ALLLink broadcast OFF message to group "group"
    sendOn(group)                             sends ALLLink broadcast ON message to group "group"
    startWatch()                              modem will print all incoming messages on terminal
    stopWatch()                               stop modem from printing all incoming messages on terminal
    unlinkAsController(otherDevice, group)    puts modem in unlink mode to unlink as controller from device "otherDevice" on group "group"

Here is how to dump the modem's link database:

    >>> modem.getdb()
    0000 kitchenFireplaceLights         23.E8.2E  RESP  10100010 group: 01 data: 00 00 01
    0000 kitchenFireplaceLights         23.E8.2E  CTRL  11100010 group: 01 data: 02 2a 43
    0000 diningRoomEastDimmer           20.AB.26  RESP  10100010 group: 01 data: 01 20 41
    0000 diningRoomEastDimmer           20.AB.26  CTRL  11100010 group: 01 data: 01 20 41

Turns out the computerRoomEast device is not linked to the modem yet, which is sort of a problem, because then it won't respond to
a whole bunch of queries, like asking for its database etc. When pinging it, it returns a nasty NACK_OF_DIRECT.

    >>> computerRoomEast.ping()
    sent msg: OUT:Cmd:0x62|toAddress:24.AC.F4|messageFlags:0x0F=DIRECT:3:3|command1:0x0F|command2:0x01|
    >>> ping got msg: IN:Cmd:0x50|fromAddress:24.AC.F4|toAddress:23.9B.65|messageFlags:0xA7=NACK_OF_DIRECT:3:1|command1:0x0F|command2:0xFF|


And when querying the database:

    >>> computerRoomEast.getdb()
    getting db, be patient!
    sent db query msg, incoming records: >>> did not get full database, giving up!

Nothing comes back.

This is because the computerRoomEast device does not have any entries about the modem in its link database, so it won't answer queries. No way around the press-the-button dance, so we link (using the set button) the modem as a controller, and the computerRoomEast device as a responder. Now things look better:

    >>> computerRoomEast.getdb()
    getting db, be patient!
    sent db query msg, incoming records: >>>  1 2
    ----- database -------

    0fff modem                          23.9B.65  RESP  10101010 group: 01 ON LVL: 254 RMPRT:  28 BUTTON:   1
    0ff7 00.00.00                       00.00.00 (RESP) 00000000 group: 00 ON LVL:   0 RMPRT:   0 BUTTON:   0

If we wanted to modem to be a responder (such that it gets messages when the device is toggled), we could link with the set button, but now that the device responds to modem commands, we can configure it as a controller of the modem by directly manipulating its link database:

    >>> computerRoomEast.addController("23.9b.65", 01, [3, 28, 1])

And now the device's database looks like this:

    >>> computerRoomEast.getdb()
    getting db, be patient!
    sent db query msg, incoming records: >>>  1 2 3
    ----- database -------
    0fff modem                          23.9B.65  RESP  10101010 group: 01 ON LVL: 254 RMPRT:  28 BUTTON:   1
    0ff7 modem                          23.9B.65  CTRL  11100010 group: 01 ON LVL:   3 RMPRT:  28 BUTTON:   1
    0fef 00.00.00                       00.00.00 (RESP) 00000000 group: 00 ON LVL:   0 RMPRT:   0 BUTTON:   0
    ----- end ------------


But let's not forget about the modem database! That one also needs an entry, as a responder. So far the modem has only an entry to control the device:


    >>> modem.getdb()
    0000 computerRoomEast               24.AC.F4  CTRL  11100010 group: 01 data: 01 20 41
    Modem Link DB complete

Let's configure the modem also as a controller:

    >>> modem.addResponder("24.ac.f4", 01)
    sent msg: OUT:Cmd:0x6F|controlCode:0x41|recordFlags:0xA2|ALLLinkGroup:0x01|linkAddress:24.AC.F4|linkData1:0x00|linkData2:0x00|linkData3:0x01|
    >>> addResponder got msg: IN:Cmd:0x6F|controlCode:0x41|recordFlags:0xA2|ALLLinkGroup:0x01|linkAddress:24.AC.F4|linkData1:0x00|linkData2:0x00|linkData3:0x01|ACK/NACK:0x06|

Voila, the modem is now also a responder to the device:

    >>> modem.getdb()
    0000 computerRoomEast               24.AC.F4  RESP  10100010 group: 01 data: 00 00 01
    0000 computerRoomEast               24.AC.F4  CTRL  11100010 group: 01 data: 01 20 41
    Modem Link DB complete



# Supported devices

So far the list of supported devices is fairly short:

- EZRain
- FanLinc (somewhat)
- IOLinc2450 (a little)
- KeypadLinc 2487S
- LED bulb 2672
- Modem 2413U/Hub pre-2014/Hub 2014
- Motion sensors
- SwitchLinc Switch 2477S
- SwitchLinc Dimmer 2477D
- Thermostat 2441TH
- Thermostat 2441V

But many of the devices work very similarly. You can easily add your own device by creating a new file in the python directory. Just pick a device that looks similar, copy/rename its .py file, and import it in init.py. If you are looking for code snippets, the most complex device so far is the thermostat, see below

## Thermostat 2441TH

While not complete, most features of the 2441TH are supported:

    >>> help(Thermostat2441TH)
    ==============  Insteon Thermostat 2441TH ===============
    addController(addr, group, data)                           add device with "addr" as controller for group "group", with link data "data"
    addResponder(addr, group, data)                            add device with "addr" as responder for group "group", with link data "data"
    addSoftwareController(addr)                                add device with "addr" as software controller
    beep()                                                     sends beep command to the device
    buttonBeepOff()                                            sets button beep off
    buttonBeepOn()                                             sets button beep on
    buttonLockOff()                                            sets button lock off
    buttonLockOn()                                             sets button lock on
    enableStatusReports()                                      enables status reports being sent to group #0xef
    getData1()                                                 performs data1 query
    getData1b()                                                performs data1b query
    getData2()                                                 performs data2 query
    getEngineVersion()                                         queries device for engine version
    getFirmwareVersion()                                       queries device for firmware version
    getHumidity()                                              queries humidity
    getId()                                                    get category, subcategory, firmware, hardware version
    getOpFlagsExt()                                            gets operational flags via ext message
    getOpFlagsSD()                                             gets operational flags via sd message
    getSchedule(day)                                           gets schedule for day (0=Sunday, 6=Saturday)
    getSetPoint()                                              queries temperature set point
    getTemperature()                                           queries temperature
    getdb()                                                    download the device database and print it on the console
    linkingLockOff()                                           sets linking lock off
    linkingLockOn()                                            sets linking lock on
    ping()                                                     pings the device
    printdb()                                                  print the downloaded link database to the console
    removeController(addr, group)                              remove device with "addr" as controller for group "group", with link data "data"
    removeLastRecord()                                         removes the last device in the link database
    removeResponder(addr, group)                               remove device with "addr" as responder for group "group"
    removeSoftwareController(addr)                             remove device with "addr" as software controller
    sendOff()                                                  sends off command to the device
    sendOn()                                                   sends on command to the device
    setACHysteresis(minutes)                                   set A/C hysteresis (in minutes)
    setAllOff()                                                set system mode to OFF
    setBacklightSeconds(time)                                  set backlight time in seconds
    setCoolPoint(temp)                                         sets cooling temperature
    setFanAuto()                                               set fan mode to AUTO
    setFanOn()                                                 set fan mode to ALWAYS ON
    setHeatPoint(temp)                                         sets heating temperature
    setHumidityHighPoint(point)                                sets high point for dehumidification
    setHumidityLowPoint(point)                                 sets low point for humidification
    setHumidityOffset(offset)                                  set humidity offset(for calibration, use with care!)
    setOnLevel(addr, group, level, ramprate = 28, button = 1)  sets (on level, ramp rate, button) for controller with "addr" and group "group"
    setSchedule(day, period, time, cool, heat)                 sets schedule params: day = 0(Sunday) .. 6 (Saturday), period = (0=wake, 1=leave, 2=return, 3=sleep), time = (e.g.) "06:30", cool/heat = temperatures
    setStage1Minutes(time)                                     set number of minutes to try stage 1 before going into stage2
    setTemperatureOffset(offset)                               set temperature offset(for calibration, use with care!)
    setTime(day, hour, min, sec)                               sets clock time (day = 0(Sunday) .. 6 (Saturday))
    setToAuto()                                                set system mode to AUTO (manual)
    setToCool()                                                set system mode to COOL
    setToHeat()                                                set system mode to HEAT
    setToProgram()                                             set system mode to AUTO (program)
    statusLEDOff()                                             don't switch status LED on when heating/cooling
    statusLEDOn()                                              switch status LED on when heating/cooling
    use12hFormat()                                             set time format 12h
    use24hFormat()                                             set time format 24h
    useCelsius()                                               set temperature display in celsius
    useFahrenheit()                                            set temperature display in fahrenheit

Fully linking the thermostat to modem requires linking the following groups:

- group 1: cooling mode change
- group 2: heating mode change
- group 3: dehumid, high humidity set point
- group 4: humidification, low humidity set point
- group 5: no idea what that one is doing
- group EF: direct message on any change (software controller)

The following sequence of commands (wait for each to complete successfully!) will link thermostat to modem (replace the "23.9b.65" with your modem's address):

    thermostat.addResponder("23.9b.65", 00)
    thermostat.addController("23.9b.65", 01)
    thermostat.addController("23.9b.65", 02)
    thermostat.addController("23.9b.65", 03)
    thermostat.addController("23.9b.65", 04)
    thermostat.addController("23.9b.65", 05)
    thermostat.addSoftwareController("23.9b.65")
    thermostat.enableStatusReports()


Here is how the thermostat database should look when you are done:

    >>> thermostat.getdb()    
    getting db, be patient!
    sent db query msg, incoming records: >>> 1 2 3 4 5 6 7 8
    ----- database -------
    1fff modem                     23.9B.65  RESP  10100010 group: 00 data: 00 00 00
    1ff7 modem                     23.9B.65  CTRL  11100010 group: 01 data: 00 00 01
    1fef modem                     23.9B.65  CTRL  11100010 group: 02 data: 00 00 02
    1fe7 modem                     23.9B.65  CTRL  11100010 group: 03 data: 00 00 03
    1fdf modem                     23.9B.65  CTRL  11100010 group: 04 data: 00 00 04
    1fd7 modem                     23.9B.65  CTRL  11100010 group: 05 data: 00 00 05
    1fcf modem                     23.9B.65  CTRL  11100010 group: ef data: 03 1f ef
    1fc7 00.00.00                  00.00.00 (RESP) 00000000 group: 00 data: 00 00 00
    ----- end ------------

Not sure if or why the thermostat has to be configured as a responder, but HouseLinc did it that way, so I followed their example.


Now make the corresponding entries on the modem database (replace "32.f4.22" with your thermostat's address):

    modem.addController("32.f4.22",00)
    modem.addResponder("32.f4.22",01)
    modem.addResponder("32.f4.22",02)
    modem.addResponder("32.f4.22",03)
    modem.addResponder("32.f4.22",04)
    modem.addResponder("32.f4.22",05)
    modem.addSoftwareResponder("32.f4.22")

And the modem db should look like that:

    >>> modem.getdb()
    0000 thermostat                 32.F4.22  RESP  10100010 group: 01 data: 00 00 01
    0000 thermostat                 32.F4.22  RESP  10100010 group: 02 data: 00 00 02
    0000 thermostat                 32.F4.22  RESP  10100010 group: 03 data: 00 00 03
    0000 thermostat                 32.F4.22  RESP  10100010 group: 04 data: 00 00 04
    0000 thermostat                 32.F4.22  RESP  10100010 group: 05 data: 00 00 05
    0000 thermostat                 32.F4.22  RESP  10100010 group: ef data: 00 00 ef
    0000 thermostat                 32.F4.22  CTRL  11100010 group: 00 data: 01 00 00
    Modem Link DB complete

That's it, modem and thermostat are linked up.

## KeypadLinc 2487S

The buttons on the Keypadlinc devices have device internal numbers that need to be provided during configuration. Moreover, when pressed each button emits a broadcast message with a different group #. For the 2487S the assignment looks like this:


|Button Name | Button Number | Group |
|------------|---------------|-------|
|   Load     |        1      |  0x01 |
|     A      |        3      |  0x03 |
|     B      |        4      |  0x04 |
|     C      |        5      |  0x05 |
|     D      |        6      |  0x06 |


### Step by step instructions

If you are impatient and already know what you are doing, skip this
section and go to the next one.

The following example is for a keypad with address "30.0d.9f", and a modem at "23.9b.65"


Begin with linking the modem as a controller: first long press the
modem button until it beeps/blinks. Then switch the keypad ON, and
long press the set button until both modem and keypad double-beep and
stop blinking. This step is necessary so the keypad will start taking
commands from the modem.

Now if you do

    modem.getdb()

you should see something like this in the database:

    0000 keypad                         30.0D.9F  CTRL  11100010 group: 01 data: 02 2c 41

The keypad also has an entry now:

    >>> keypad.getdb()
    getting db, be patient!
    sent db query msg, incoming records: >>>  1 2
    ----- database -------
    0fff modem                          23.9B.65  RESP  10101010 group: 01 ON LVL: 255 RMPRT:  28 BUTTON:   1
    0ff7 00.00.00                       00.00.00 (RESP) 00000000 group: 00 ON LVL:   0 RMPRT:   0 BUTTON:   0

This means the keypad will respond when it gets an ON command on group #1
by going into ON state (brightness level 255 means full on).

The main load (button #1) can be switched on without resorting to
broadcasting group messages. You can simply send a direct message like this:

    keypad.off()
    keypad.on()

This shoulds switch the main light on and off.

However, the modem will not learn if button #1 is pressed. For that,
we need to link the keypad as a controller, and the modem as a
responder so it gets group messages on group #1 (the group on which
the keypad sends its broadcasts):

    modem.addResponder("30.0d.9f", 0x01)
    keypad.addControllerForButton("23.9b.65", 1)

Now the modem database should have two lines like these:

    >>>modem.getdb()
    ...
    0000 keypad                             30.0D.9F  RESP  10100010 group: 01 data: 00 00 01
    0000 keypad                             30.0D.9F  CTRL  11100010 group: 01 data: 02 2c 41
    ...


And the keypad should look like this:

    >>> keypad.getdb()
    getting db, be patient!
    sent db query msg, incoming records: >>>  1 2 3
    ----- database -------
    0fff modem                     23.9B.65  RESP  10101010 group: 01 ON LVL: 255 RMPRT:  28 BUTTON:   1
    0ff7 modem                     23.9B.65  CTRL  11100010 group: 01 ON LVL:   3 RMPRT:  28 BUTTON:   1
    0fef 00.00.00                       00.00.00 (RESP) 00000000 group: 00 ON LVL:   0 RMPRT:   0 BUTTON:   0
    ----- end ------------

Now if you put the modem into "watch" mode:

    >>> modem.startWatch()

and switch on the light, you should see messages coming in:

    >>> modem got msg: IN:Cmd:0x50|fromAddress:30.0D.9F|toAddress:00.00.01|messageFlags:0xCB=ALL_LINK_BROADCAST:3:2|command1:0x11|command2:0x00|
    modem got msg: IN:Cmd:0x50|fromAddress:30.0D.9F|toAddress:23.9B.65|messageFlags:0x40=ALL_LINK_CLEANUP:0:0|command1:0x11|command2:0x01|
    modem got msg: IN:Cmd:0x50|fromAddress:30.0D.9F|toAddress:11.01.01|messageFlags:0xC7=ALL_LINK_BROADCAST:3:1|command1:0x06|command2:0x00|

Don't forget to stop watching:

    >>> modem.stopWatch()


If we want the modem to get messages when the other buttons are
pressed, we analogously establish a keypad controller/modem responder
relationship:

    keypad.addControllerForButton("23.9b.65", 3)
    keypad.addControllerForButton("23.9b.65", 4)
    keypad.addControllerForButton("23.9b.65", 5)
    keypad.addControllerForButton("23.9b.65", 6)

    modem.addResponder("30.0d.9f", 0x03)
    modem.addResponder("30.0d.9f", 0x04)
    modem.addResponder("30.0d.9f", 0x05)
    modem.addResponder("30.0d.9f", 0x06)


Always check your work. Here is how the databases should look now:

    >>>modem.getb()
    ...
    0000 keypad                             30.0D.9F  RESP  10100010 group: 01 data: 00 00 01
    0000 keypad                             30.0D.9F  RESP  10100010 group: 03 data: 00 00 03
    0000 keypad                             30.0D.9F  RESP  10100010 group: 04 data: 00 00 04
    0000 keypad                             30.0D.9F  RESP  10100010 group: 05 data: 00 00 05
    0000 keypad                             30.0D.9F  RESP  10100010 group: 06 data: 00 00 06
    0000 keypad                             30.0D.9F  CTRL  11100010 group: 01 data: 02 2c 41
    ...

    >>> keypad.getdb()
    getting db, be patient!
    sent db query msg, incoming records: >>>  1 2 3 4 5 6 7
    ----- database -------
    0fff modem                     23.9B.65  RESP  10101010 group: 01 ON LVL: 255 RMPRT:  28 BUTTON:   1
    0ff7 modem                     23.9B.65  CTRL  11100010 group: 01 ON LVL:   3 RMPRT:  28 BUTTON:   1
    0fef modem                     23.9B.65  CTRL  11100010 group: 03 ON LVL:   3 RMPRT:  28 BUTTON:   3
    0fe7 modem                     23.9B.65  CTRL  11100010 group: 04 ON LVL:   3 RMPRT:  28 BUTTON:   4
    0fdf modem                     23.9B.65  CTRL  11100010 group: 05 ON LVL:   3 RMPRT:  28 BUTTON:   5
    0fd7 modem                     23.9B.65  CTRL  11100010 group: 06 ON LVL:   3 RMPRT:  28 BUTTON:   6
    0fcf 00.00.00                       00.00.00 (RESP) 00000000 group: 00 ON LVL:   0 RMPRT:   0 BUTTON:   0
    ----- end ------------


Note that the order of records is not important. If some of the
entries aren't there, rerun the respective command until success. The
transmission on the Insteon network isn't always completely reliable.

In the last step, we get the keypad buttons to respond to the
modem. Unlike for the main load (button #1), there is no direct command to
set them. Instead, must set the button up as a responder to a group
(pick any group number you want), and then have the modem send out a broadcast for that
group number.

In the following example the groups 0xf3 to 0xf6 are used. It doesn't
matter exactly what groups you use so long as they are globally (on
the whole insteon network) unique. This is because when the modem sends out the
broadcast on that group number, *all* devices that are configured as responders to it
will change their state!

    keypad.addResponderForButton("23.9b.65", 0xf3, 3)
    keypad.addResponderForButton("23.9b.65", 0xf4, 4)
    keypad.addResponderForButton("23.9b.65", 0xf5, 5)
    keypad.addResponderForButton("23.9b.65", 0xf6, 6)


Likewise, the modem should be set up as a controller for those groups:

    modem.addController("30.0d.9f", 0xf3)
    modem.addController("30.0d.9f", 0xf4)
    modem.addController("30.0d.9f", 0xf5)
    modem.addController("30.0d.9f", 0xf6)


Finally all done, this is how things should look:

    >>> modem.getdb()
    ...
    0000 keypad                             30.0D.9F  RESP  10100010 group: 01 data: 00 00 01
    0000 keypad                             30.0D.9F  RESP  10100010 group: 03 data: 00 00 03
    0000 keypad                             30.0D.9F  RESP  10100010 group: 04 data: 00 00 04
    0000 keypad                             30.0D.9F  RESP  10100010 group: 05 data: 00 00 05
    0000 keypad                             30.0D.9F  RESP  10100010 group: 06 data: 00 00 06
    0000 keypad                             30.0D.9F  CTRL  11100010 group: 01 data: 02 2c 41
    0000 keypad                             30.0D.9F  CTRL  11100010 group: f3 data: 00 00 f3
    0000 keypad                             30.0D.9F  CTRL  11100010 group: f4 data: 00 00 f4
    0000 keypad                             30.0D.9F  CTRL  11100010 group: f5 data: 00 00 f5
    0000 keypad                             30.0D.9F  CTRL  11100010 group: f6 data: 00 00 f6
    ...

    >>> keypad.getdb()
    getting db, be patient!
    sent db query msg, incoming records: >>>  1 2 3 4 5 5 6 7 8 9 10 11
    ----- database -------
    0fff modem                     23.9B.65  RESP  10101010 group: 01 ON LVL: 255 RMPRT:  28 BUTTON:   1
    0ff7 modem                     23.9B.65  CTRL  11100010 group: 01 ON LVL:   3 RMPRT:  28 BUTTON:   1
    0fef modem                     23.9B.65  CTRL  11100010 group: 03 ON LVL:   3 RMPRT:  28 BUTTON:   3
    0fe7 modem                     23.9B.65  CTRL  11100010 group: 04 ON LVL:   3 RMPRT:  28 BUTTON:   4
    0fdf modem                     23.9B.65  CTRL  11100010 group: 05 ON LVL:   3 RMPRT:  28 BUTTON:   5
    0fd7 modem                     23.9B.65  CTRL  11100010 group: 06 ON LVL:   3 RMPRT:  28 BUTTON:   6
    0fcf modem                     23.9B.65  RESP  10100010 group: f3 ON LVL:   3 RMPRT:  28 BUTTON:   3
    0fc7 modem                     23.9B.65  RESP  10100010 group: f4 ON LVL:   3 RMPRT:  28 BUTTON:   4
    0fbf modem                     23.9B.65  RESP  10100010 group: f5 ON LVL:   3 RMPRT:  28 BUTTON:   5
    0fb7 modem                     23.9B.65  RESP  10100010 group: f6 ON LVL:   3 RMPRT:  28 BUTTON:   6
    0faf 00.00.00                       00.00.00 (RESP) 00000000 group: 00 ON LVL:   0 RMPRT:   0 BUTTON:   0
    ----- end ------------


Ready to test the setup: sending a broadcast message from the modem on
group 0xf4 should toggle button #4, which is the "B" button:

    >>> modem.sendOn(0xf4)
    >>> modem.sendOff(0xf4)



### Quick setup

In the following instructions, replace address "30.0d.9f" with the address of your keypad,
replace "23.9b.65" with the address of your modem.

- link modem as a controller via set buttons: first press long on the modem, then press long on the keypad
- establish connections so modem gets notified of button and switch toggles:

        modem.addResponder("30.0d.9f", 0x01)
        modem.addResponder("30.0d.9f", 0x03)
        modem.addResponder("30.0d.9f", 0x04)
        modem.addResponder("30.0d.9f", 0x05)
        modem.addResponder("30.0d.9f", 0x06)

        keypad.addControllerForButton("23.9b.65", 1)
        keypad.addControllerForButton("23.9b.65", 3)
        keypad.addControllerForButton("23.9b.65", 4)
        keypad.addControllerForButton("23.9b.65", 5)
        keypad.addControllerForButton("23.9b.65", 6)


- pick some group numbers that are not used anywhere else,
  (in this case we picked 0xf3, 0xf4, 0xf5, 0xf6, replace with your group numbers) and link the
  modem as controller, the keypad buttons as responders:

        keypad.addResponderForButton("23.9b.65", 0xf3, 3)
        keypad.addResponderForButton("23.9b.65", 0xf4, 4)
        keypad.addResponderForButton("23.9b.65", 0xf5, 5)
        keypad.addResponderForButton("23.9b.65", 0xf6, 6)


        modem.addController("30.0d.9f", 0xf3)
        modem.addController("30.0d.9f", 0xf4)
        modem.addController("30.0d.9f", 0xf5)
        modem.addController("30.0d.9f", 0xf6)

- verify that your databases look correct:

        >>modem.getdb()
        ...
        0000 keypad                             30.0D.9F  RESP  10100010 group: 01 data: 00 00 01
        0000 keypad                             30.0D.9F  RESP  10100010 group: 03 data: 00 00 03
        0000 keypad                             30.0D.9F  RESP  10100010 group: 04 data: 00 00 04
        0000 keypad                             30.0D.9F  RESP  10100010 group: 05 data: 00 00 05
        0000 keypad                             30.0D.9F  RESP  10100010 group: 06 data: 00 00 06
        0000 keypad                             30.0D.9F  CTRL  11100010 group: 01 data: 02 2c 41
        0000 keypad                             30.0D.9F  CTRL  11100010 group: f3 data: 00 00 f3
        0000 keypad                             30.0D.9F  CTRL  11100010 group: f4 data: 00 00 f4
        0000 keypad                             30.0D.9F  CTRL  11100010 group: f5 data: 00 00 f5
        0000 keypad                             30.0D.9F  CTRL  11100010 group: f6 data: 00 00 f6
        ...

        >>> keypad.getdb()
        getting db, be patient!
        sent db query msg, incoming records: >>>  1 2 3 4 5 5 6 7 8 9 10 11
        ----- database -------
        0fff modem                     23.9B.65  RESP  10101010 group: 01 ON LVL: 255 RMPRT:  28 BUTTON:   1
        0ff7 modem                     23.9B.65  CTRL  11100010 group: 01 ON LVL:   3 RMPRT:  28 BUTTON:   1
        0fef modem                     23.9B.65  CTRL  11100010 group: 03 ON LVL:   3 RMPRT:  28 BUTTON:   3
        0fe7 modem                     23.9B.65  CTRL  11100010 group: 04 ON LVL:   3 RMPRT:  28 BUTTON:   4
        0fdf modem                     23.9B.65  CTRL  11100010 group: 05 ON LVL:   3 RMPRT:  28 BUTTON:   5
        0fd7 modem                     23.9B.65  CTRL  11100010 group: 06 ON LVL:   3 RMPRT:  28 BUTTON:   6
        0fcf modem                     23.9B.65  RESP  10100010 group: f3 ON LVL:   3 RMPRT:  28 BUTTON:   3
        0fc7 modem                     23.9B.65  RESP  10100010 group: f4 ON LVL:   3 RMPRT:  28 BUTTON:   4
        0fbf modem                     23.9B.65  RESP  10100010 group: f5 ON LVL:   3 RMPRT:  28 BUTTON:   5
        0fb7 modem                     23.9B.65  RESP  10100010 group: f6 ON LVL:   3 RMPRT:  28 BUTTON:   6
        0faf 00.00.00                       00.00.00 (RESP) 00000000 group: 00 ON LVL:   0 RMPRT:   0 BUTTON:   0
        ----- end ------------

  
## Smoke Bridge 2982-222

In the following example, the smoke bridge has address 3e.e2.c4, the modem has 23.9b.65, and my init.py has an entry like this:

    smokebridge = SmokeBridge("smokebridge", "3e.e2.c4")

Before anything else, do the basic linking between modem and smoke bridge via set buttons: first long press on the modem, then on the smoke bridge (double beep indicates success). Afterwards, this is how your databases should look like (ignore the values in "data"):

    >>> smokebridge.getdb()
    ...
    0fff modem                     23.9B.65  RESP  10100010 group: 01 ON LVL: 255 RMPRT:  28 BUTTON:   0
    ...
    >>> modem.getdb()
    ...
    0000 smokebridge               3E.E2.C4  CTRL  11100010 group: 01 data: 10 0a 43
    ...

Now let's hook up the modem such that it listens to the smoke bridge group messages:

    >>> modem.addResponder("3e.e2.c4", 0x01, [0, 0, 0]);
    >>> modem.addResponder("3e.e2.c4", 0x02, [0, 0, 0]);
    >>> modem.addResponder("3e.e2.c4", 0x03, [0, 0, 0]);
    >>> modem.addResponder("3e.e2.c4", 0x04, [0, 0, 0]);
    >>> modem.addResponder("3e.e2.c4", 0x05, [0, 0, 0]);
    >>> modem.addResponder("3e.e2.c4", 0x06, [0, 0, 0]);
    >>> modem.addResponder("3e.e2.c4", 0x07, [0, 0, 0]);
    >>> modem.addResponder("3e.e2.c4", 0x0a, [0, 0, 0]);

If all went well, you should have a modem database that looks like this ("data" values are ignored, order is unimportant):

    >>> modem.getdb()
    0000 smokebridge                    3E.E2.C4  CTRL  11100010 group: 01 data: 10 0a 43
    0000 smokebridge                    3E.E2.C4  RESP  10100010 group: 01 data: 00 00 00
    0000 smokebridge                    3E.E2.C4  RESP  10100010 group: 02 data: 00 00 00
    0000 smokebridge                    3E.E2.C4  RESP  10100010 group: 03 data: 00 00 00
    0000 smokebridge                    3E.E2.C4  RESP  10100010 group: 04 data: 00 00 00
    0000 smokebridge                    3E.E2.C4  RESP  10100010 group: 05 data: 00 00 00
    0000 smokebridge                    3E.E2.C4  RESP  10100010 group: 06 data: 00 00 00
    0000 smokebridge                    3E.E2.C4  RESP  10100010 group: 07 data: 00 00 00
    0000 smokebridge                    3E.E2.C4  RESP  10100010 group: 0a data: 00 00 00

Now let's tell the smoke bridge that it controls the modem (not sure the [3,31, xxx] data fields are important, just mirroring what houselinc did):

    >>> smokebridge.addController("23.9b.65", 0x01, [3, 31, 1])
    >>> smokebridge.addController("23.9b.65", 0x02, [3, 31, 2])
    >>> smokebridge.addController("23.9b.65", 0x03, [3, 31, 3])
    >>> smokebridge.addController("23.9b.65", 0x04, [3, 31, 4])
    >>> smokebridge.addController("23.9b.65", 0x05, [3, 31, 5])
    >>> smokebridge.addController("23.9b.65", 0x06, [3, 31, 6])
    >>> smokebridge.addController("23.9b.65", 0x07, [3, 31, 7])
    >>> smokebridge.addController("23.9b.65", 0x0a, [3, 31, 0x0a])

This is what the resulting database should look like:

    >>> smokebridge.getdb()
    0fff test_modem                     23.9B.65  RESP  10100010 group: 01 ON LVL: 255 RMPRT:  28 BUTTON:   0
    0ff7 test_modem                     23.9B.65  CTRL  11100010 group: 01 ON LVL:   3 RMPRT:  31 BUTTON:   1
    0fef test_modem                     23.9B.65  CTRL  11100010 group: 02 ON LVL:   3 RMPRT:  31 BUTTON:   2
    0fe7 test_modem                     23.9B.65  CTRL  11100010 group: 03 ON LVL:   3 RMPRT:  31 BUTTON:   3
    0fdf test_modem                     23.9B.65  CTRL  11100010 group: 04 ON LVL:   3 RMPRT:  31 BUTTON:   4
    0fd7 test_modem                     23.9B.65  CTRL  11100010 group: 05 ON LVL:   3 RMPRT:  31 BUTTON:   5
    0fcf test_modem                     23.9B.65  CTRL  11100010 group: 06 ON LVL:   3 RMPRT:  31 BUTTON:   6
    0fc7 test_modem                     23.9B.65  CTRL  11100010 group: 07 ON LVL:   3 RMPRT:  31 BUTTON:   7
    0fbf test_modem                     23.9B.65  CTRL  11100010 group: 0a ON LVL:   3 RMPRT:  31 BUTTON:  10
    0fbf 00.00.00                       00.00.00 (RESP) 00000000 group: 00 ON LVL:   0 RMPRT:   0 BUTTON:   0

Now one little test if everything works fine. Put the modem into "watch" mode:

    modem.startWatch()
       
And short-press the set button on the modem. You should get a bunch of messages like this:

    modem got msg: IN:Cmd:0x50|fromAddress:3E.E2.C4|toAddress:00.00.01|messageFlags:0xCB=ALL_LINK_BROADCAST:3:2|command1:0x11|command2:0x80|
    modem got msg: IN:Cmd:0x50|fromAddress:3E.E2.C4|toAddress:23.9B.65|messageFlags:0x41=ALL_LINK_CLEANUP:1:0|command1:0x11|command2:0x01|
    modem got msg: IN:Cmd:0x50|fromAddress:3E.E2.C4|toAddress:11.01.01|messageFlags:0xCB=ALL_LINK_BROADCAST:3:2|command1:0x06|command2:0x00|
    modem got msg: IN:Cmd:0x50|fromAddress:3E.E2.C4|toAddress:00.00.02|messageFlags:0xCB=ALL_LINK_BROADCAST:3:2|command1:0x11|command2:0x40|
    modem got msg: IN:Cmd:0x50|fromAddress:3E.E2.C4|toAddress:23.9B.65|messageFlags:0x41=ALL_LINK_CLEANUP:1:0|command1:0x11|command2:0x02|
    modem got msg: IN:Cmd:0x50|fromAddress:3E.E2.C4|toAddress:11.01.02|messageFlags:0xCB=ALL_LINK_BROADCAST:3:2|command1:0x06|command2:0x00|
    modem got msg: IN:Cmd:0x50|fromAddress:3E.E2.C4|toAddress:00.00.06|messageFlags:0xCB=ALL_LINK_BROADCAST:3:2|command1:0x11|command2:0x10|
    modem got msg: IN:Cmd:0x50|fromAddress:3E.E2.C4|toAddress:23.9B.65|messageFlags:0x41=ALL_LINK_CLEANUP:1:0|command1:0x11|command2:0x06|
    modem got msg: IN:Cmd:0x50|fromAddress:3E.E2.C4|toAddress:11.01.06|messageFlags:0xCB=ALL_LINK_BROADCAST:3:2|command1:0x06|command2:0x00|
    modem got msg: IN:Cmd:0x50|fromAddress:3E.E2.C4|toAddress:00.00.07|messageFlags:0xCB=ALL_LINK_BROADCAST:3:2|command1:0x11|command2:0x08|
    modem got msg: IN:Cmd:0x50|fromAddress:3E.E2.C4|toAddress:23.9B.65|messageFlags:0x41=ALL_LINK_CLEANUP:1:0|command1:0x11|command2:0x07|
    modem got msg: IN:Cmd:0x50|fromAddress:3E.E2.C4|toAddress:11.01.07|messageFlags:0xCB=ALL_LINK_BROADCAST:3:2|command1:0x06|command2:0x00|
    modem got msg: IN:Cmd:0x50|fromAddress:3E.E2.C4|toAddress:00.00.05|messageFlags:0xCB=ALL_LINK_BROADCAST:3:2|command1:0x11|command2:0x00|
    modem got msg: IN:Cmd:0x50|fromAddress:3E.E2.C4|toAddress:23.9B.65|messageFlags:0x41=ALL_LINK_CLEANUP:1:0|command1:0x11|command2:0x05|
    modem got msg: IN:Cmd:0x50|fromAddress:3E.E2.C4|toAddress:11.01.05|messageFlags:0xCB=ALL_LINK_BROADCAST:3:2|command1:0x06|command2:0x00|

You can see that the bridge sends broadcasts to the groups 0x01, 0x02, 0x06, 0x07, 0x05 (in that order). From the developer notes, this maps to the following conditions:

- smoke:         0x01
- CO:            0x02
- test:          0x03
- unknown:       0x04
- clear:         0x05
- low battery:   0x06
- error:         0x07
- heartbeat:     0x0A
