"""
KeyBeepMixin

This mixin provides functionality to control the key beep feature of some devices.
"""

class KeyBeepMixin:
    def setKeyBeepOn(self):
        """setKeyBeepOn()
        This sets the dimmer to beep when key is pressed"""
        self.querier.setMsgHandler(DefaultMsgHandler("Set Key Beep ON"))
        return self.querier.queryext(0x20, 0x0A, [0x00, 0x00, 0x00]);

    def setKeyBeepOff(self):
        """setKeyBeepOff()
        This sets the dimmer to not beep when key is pressed"""
        self.querier.setMsgHandler(DefaultMsgHandler("Set Key Beep OFF"))
        return self.querier.queryext(0x20, 0x0B, [0x00, 0x00, 0x00]);
