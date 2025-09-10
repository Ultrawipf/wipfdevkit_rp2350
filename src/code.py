from wipf import *
import time
import random
from adafruit_led_animation import helper
from adafruit_led_animation.animation.rainbowcomet  import RainbowComet
from adafruit_led_animation.animation.rainbow import Rainbow
from adafruit_led_animation.group import AnimationGroup
from adafruit_led_animation.animation.blink import Blink
from adafruit_led_animation.animation.pulse import Pulse
from adafruit_led_animation.animation.rainbowsparkle import RainbowSparkle

import asyncio
from keyboard import Wipfkeyboard

# Make it blinky
async def blinkleds():
    rainbow_chase_lefteye = RainbowComet(LEDS_LEFTEYE, speed=0.1, tail_length=10, bounce=True)
    rainbow_chase_righteye = RainbowComet(LEDS_RIGHTEYE, speed=0.1, tail_length=10, bounce=True)
    #rainbowears = RainbowSparkle(LEDS_EARS, speed=0.1, num_sparkles=1)
    blinknose = Pulse(LEDS_NOSE, speed=0.05, color=(128,128,0),period=5)
    #blinkteeth = Pulse(LEDS_TEETH, speed=0.05, color=(255,0,0),period=3)
    group = AnimationGroup(rainbow_chase_lefteye,rainbow_chase_righteye,blinknose,sync=False)

    while(1):
        group.animate() # Group animates all
        # blinknose.animate()
        # blinkteeth.animate()
        # rainbowears.animate()
        await asyncio.sleep(0.05)

# Demo function for accelerometer
async def accelerometer_func():
    if not ACCELEROMETER:
        return
    
    while(1):
        accs = get_acceleration()
        # print("ACC",accs,get_orientation())
        accsum = sum([abs(a) for a in accs])
        LEDS.brightness = (3*LEDS.brightness+min(max(0.1,(accsum-5)/35),1)) / 4
        # if(accsum) > 20:
        #     beep(int(50*accsum))
        # else:
        #     beep()

        # orientation = get_orientation()
        LEDS_EARS.fill((0,0,0))
        LEDS_TEETH.fill((0,0,0))
        basecolor = (max(0,(accs[2]*20)+20),15,128)
        ledvals = [accs[0]-accs[1],accs[0]+accs[1],-accs[0]-accs[1],-accs[0]+accs[1]]
        ledvals = [[c * max(v/10,0) for c in basecolor] for v in ledvals]
        # print(ledvals)
        
        LEDS_TEETH[0] = ledvals[0]
        LEDS_TEETH[1] = ledvals[1] 
        LEDS_EARS[0] = ledvals[2] 
        LEDS_EARS[1] = ledvals[3] 

        LEDS.show()

        await asyncio.sleep(0.05)

# Demo function for a simple clonk keyboard
async def keyboard_func():
    try:
        keyboard = Wipfkeyboard()
    except Exception as e:
        return
    if not keyboard:
        return
    while(1):
        buttonstates = [not btn.value for btn in BUTTONS]
        #print("BTN:",buttonstates)
        keyboard.keyboard_update(buttonstates)

        if buttonstates[0] and not is_wav_playing():
            asyncio.create_task(play_wav_async("sd/Snuff1.wav"))
            
        await asyncio.sleep(0.1)

# Main function
def main():
    # Play sound async
    # snuffer = asyncio.create_task(play_wav_async("sd/Snuff1.wav"))

    while(1):

        led_task = asyncio.create_task(blinkleds())
   
        acc_task = asyncio.create_task(accelerometer_func())

        buttons_task = asyncio.create_task(keyboard_func()) # Enables the clonk keyboard
        await asyncio.gather(led_task,buttons_task,acc_task)

LEDS.auto_write = False # If false must use LEDS.show()
LEDS.brightness = 0.25 # 0 - 1.0

# Startup chirp
if random.randint(0,100) > 10:
    for f in range(200,3000,150):
        beep(f)
        time.sleep(0.005)
    beep() # Stop beep
else:
    play_wav("sd/Snuff1.wav")
# beep(2000)
# time.sleep(0.1)
# beep()
# time.sleep(0.25)

# Or play sound
# play_wav("sd/Snuff1.wav")
time.sleep(0.25)
# Enable accelerometer orientations
if ACCELEROMETER:
    ACCELEROMETER._write_u8(0x13,0x40)

asyncio.run(main())