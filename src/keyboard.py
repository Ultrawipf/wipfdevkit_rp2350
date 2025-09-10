import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import time
from wipf import *

class Wipfkeyboard:
    KEYMAP = [Keycode.D,Keycode.V,Keycode.C,Keycode.X,Keycode.S,Keycode.Z,Keycode.A,Keycode.F]
    def __init__(self):
        self.lastkeys = [False * len(BUTTONPINS)]
        self.kbd = Keyboard(usb_hid.devices)

    def keyboard_update(self,buttonstates):
        if(len(buttonstates) != len(self.lastkeys)):
            self.lastkeys = buttonstates
        changedKeys = [(i,state) for i,state in enumerate(buttonstates) if self.lastkeys[i] != state]
        # print(changedKeys)
        self.lastkeys = buttonstates

        presskeys = [self.KEYMAP[i] for i,state in changedKeys if state]
        releasekeys = [self.KEYMAP[i] for i,state in changedKeys if not state]
        if(presskeys):
            # print("Prs",presskeys)
            self.kbd.press(*presskeys)

        if(releasekeys):
            # print("Rls",releasekeys)
            self.kbd.release(*releasekeys)

    def write(self,string,delay=None):
        self.kbd.write(string,delay)
