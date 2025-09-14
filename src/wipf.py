import neopixel
import board
import pwmio
import adafruit_mma8451
from adafruit_led_animation.helper import PixelSubset

from digitalio import DigitalInOut,Direction, Pull
from busio import I2C

import audiocore
import audiopwmio
import asyncio
import time
import microcontroller

# LEDS
NUMLEDS = 18
PINLEDS = board.GP8
LEDS = neopixel.NeoPixel(PINLEDS, NUMLEDS)

# Led pin ids. use with LED[id]
LEDS_LEFTEYE = PixelSubset(LEDS,4,10)
LEDS_RIGHTEYE = PixelSubset(LEDS,10,16)
LEDS_TEETH = PixelSubset(LEDS,0,2)
LEDS_EARS = PixelSubset(LEDS,16,18)
LEDS_NOSE = PixelSubset(LEDS,2,4)

# Turn all off
LEDS.fill((0,0,0))
LEDS.show()

PINBUZZER = board.GP1
BUZZER_PWM = None #pwmio.PWMOut(PINBUZZER, variable_frequency=True)
BUZZER_AUD = None


I2C_EXT = I2C(scl=microcontroller.pin.GPIO29,sda=board.GP28,frequency=400000)
I2C_INT = I2C(scl=board.GP3,sda=board.GP2,frequency=400000)
I2C_EXT.try_lock()
devs = I2C_EXT.scan()
I2C_EXT.unlock()
print('I2C EXT',devs)
I2C_INT.try_lock()
devs = I2C_INT.scan()
I2C_INT.unlock()
print('I2C INT',devs)


for i in range(4):
    try:
        time.sleep(0.2) # Ensure accelerometer is found
        ACCELEROMETER = adafruit_mma8451.MMA8451(I2C_INT,address=0x1C)
        ACCELEROMETER.data_rate = adafruit_mma8451.DATARATE_200HZ
        #ACCELEROMETER.range=adafruit_mma8451.RANGE_8G
        print("Found accelerometer")
        break
    except Exception as e:
        # while not I2C_INT.try_lock():
        #     pass
        # I2C_INT.writeto(0x1C,bytes([0x2B,0x40]))
        # I2C_INT.unlock()
        ACCELEROMETER = None
        print("Accelerometer error",e)
        raise e
        time.sleep(1)
        
        



BUTTONPINS = [board.GP15,board.GP25,board.GP24,board.GP23,board.GP22,board.GP21,board.GP5,board.GP4]
BUTTONS = [DigitalInOut(pin) for pin in BUTTONPINS]

for btn in BUTTONS:
    btn.direction = Direction.INPUT
    btn.pull = Pull.UP

def get_button_states():
    """
    Returns True if a button is pressed
    """
    return [not btn.value for btn in BUTTONS]


def beep(freq = 0,duty = 65535//2):
    """
    Beeps using PWM
    """
    __switch_buzzer_to_pwm()
    if(freq):
        BUZZER_PWM.frequency = freq
        BUZZER_PWM.duty_cycle = duty  # On 50%
    else:
        BUZZER_PWM.duty_cycle = 0


def is_wav_playing():
    return BUZZER_AUD != None and BUZZER_AUD.playing

async def play_wav_async(file):
    global BUZZER_AUD
    if is_wav_playing():
        return

    __switch_buzzer_to_audio()
    
    wave = audiocore.WaveFile(file)

    BUZZER_AUD.play(wave)
    while BUZZER_AUD and BUZZER_AUD.playing:
        await asyncio.sleep(0.25)
    if BUZZER_AUD:
        BUZZER_AUD.deinit()
    BUZZER_AUD = None

def play_wav(file):
    global BUZZER_AUD
    __switch_buzzer_to_audio()
    wave = audiocore.WaveFile(file)
    print("Play",file)
    BUZZER_AUD.play(wave)
    while BUZZER_AUD.playing:
        pass
    print("stopped")
    BUZZER_AUD.deinit()
    BUZZER_AUD = None

    

def get_orientation():
    if ACCELEROMETER:
        return ACCELEROMETER.orientation
    else:
        return 128

def get_acceleration():
    if ACCELEROMETER:
        return ACCELEROMETER.acceleration
    else:
        return [0,0,0]
    


def __switch_buzzer_to_audio():
    global BUZZER_PWM
    global BUZZER_AUD
    if BUZZER_PWM:
        BUZZER_PWM.deinit()
        BUZZER_PWM = None
    if not BUZZER_AUD:
        BUZZER_AUD = audiopwmio.PWMAudioOut(PINBUZZER)

def __switch_buzzer_to_pwm():
    global BUZZER_PWM
    global BUZZER_AUD
    if BUZZER_AUD:
        BUZZER_AUD.deinit()
        BUZZER_AUD = None
    if not BUZZER_PWM:
        BUZZER_PWM = pwmio.PWMOut(PINBUZZER, variable_frequency=True)
