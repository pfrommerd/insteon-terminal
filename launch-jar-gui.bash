echo "Note: the jars must first be built using ant jar before the application can be launched"
echo "Also, for using PLMs, rxtx natives must first be installed on this system"


java -cp "build/jars/insteon-terminal-gui.jar:lib/*:lib/hub/*:lib/logger/*" us.pfrommer.insteon.cmd.gui.GUI
