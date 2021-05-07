#This file is used to interface with the 7-segment display.
import stopwatch
import time
import threading
import random
import config
#use caps unless you want lowercase
#v doesnt mean anything, its just a short name
v = { #letters
     ' ': 0b00000000, 'A': 0b01110111, 'B':0b01111100,
     'C': 0b00111001, 'c': 0b01011000, 'D':0b01011110,
     'E': 0b01111001, 'F': 0b01110001, 'G': 0b01111101,
     'g': 0b01101111, 'H': 0b01110110, 'h': 0b01110100,
     'I': 0b00010001, 'J': 0b00011111, 'j': 0b00001110,
     'K': 0b01110110, 'L': 0b00111000, 'l': 0b00000110,
     'l2':0b00110000, 'M': 0b00010101, 'N': 0b00110111,
     'n': 0b01010100, 'n2':0b00100011, 'O': 0b00111111,
     'o': 0b01011100, 'o2':0b01100011, 'P': 0b01110011,
     'Q': 0b01100111, 'R': 0b01010000, 'S': 0b01101101,
     'T': 0b01111000, 'U': 0b00111110, 'u': 0b00011100,
     'u2':0b01100010, 'V': 0b01110010, 'W': 0b00101010,
     'X': 0b01110110, 'Y': 0b01101110, 'Z': 0b01011011,
     #numbers
     '1': 0b00000110, '2': 0b01011011, '3': 0b01001111,
     '4': 0b01100110, '5': 0b01101101, '6': 0b01111101,
     '7': 0b00000111, '8': 0b01111111, '9': 0b01101111,
     '0': 0b00111111,
     #symbols
     '-': 0b01000000, '_': 0b00001000, '=': 0b01001000,
     ',': 0b00000100, "'": 0b00000010, '?': 0b11010011,
     '"': 0b00100010
     }
rawoutput = [0,0,0,0]
original = 'BKHY'
password = config.bombpass
spd = config.sevenspd
defusegoal = 0
defusecalled = 0
#mode 0 is static, 1 is shifting, 2 is blinking, 3 is letter flickering
mode = 0
exitcase = 0
output = 'ASSS'
lps = 2
givenloops = 0
#flick will also be used for letter flickering
flick = 0
start = 0 #time in ms the program started at (assigned when called)
#str = 'QWERTYUIOPLKJHGFDSAZXCVBNM1234567890'
#output = output + '    '
t=0
def displaythem(c1, c2, c3, c4):   #display function for 7-segment display
    stopwatch.outData(0x00)   #eliminate residual display
    stopwatch.selectDigit(0x08)   #Select the first, and display the single digit
    stopwatch.outData(c1)
    time.sleep(0.002)   #display duration
    stopwatch.outData(0x00)
    stopwatch.selectDigit(0x04)   # Select the second, and display the tens digit
    stopwatch.outData(c2)
    time.sleep(0.002)
    stopwatch.outData(0x00)
    stopwatch.selectDigit(0x02)   # Select the third, and display the hundreds digit
    stopwatch.outData(c3)
    time.sleep(0.002)
    stopwatch.outData(0x00)
    stopwatch.selectDigit(0x01)   # Select the fourth, and display the thousands digit
    stopwatch.outData(c4)
    time.sleep(0.002)


#time function find it here
#time function find it here
#time function find it here
def timer():        #timer function
    global output
    global rawoutput
    global t
    global lps
    global original, mode, start
    global defusecalled, defusegoal
    passedms = int(time.time_ns()/1000000) - start
    lps -= 1
    '''
    t = threading.Timer(spd,timer)   #scroll speed
    t.start()    #Start timing
    ''' #not sure this is neccesary, see if it works when taken out
    if lps == 0:
        mode == 99 #mode 99 will lead to program termination
    if mode == 0:
        pass
    elif mode == 1:
        output= shift(output)
    elif mode == 2:
        output = flkr(original)
    elif mode == 3:
        output = shiftletter(original)
    elif mode == 4:
        output = timeboi(passedms)
    elif mode == 6:
        digs = howmanydigs(defusecalled, time.time_ns()/1000000, defusegoal)
        output = defusing(digs)
    for i in range(0, len(rawoutput)):
        rawoutput[i] = v[output[i]]
        
def point(number):
    number += 0b10000000
    return number

def clear():
    global output
    output = '    '

def shift(text):
    first = text[0]
    text2 = ''
    for i in range(1, len(text)):
        text2 += text[i]
    text2 += first
    return text2

def begindefuse(deftime):
    global defusegoal, mode, defusecalled, spd
    defusecalled = time.time_ns()/1000000
    defusegoal = defusecalled + (deftime * 1000)
    mode = 6
    #spd = 0.2

def howmanydigs(start, now, stop):
    global exitcase, mode
    defusetime = stop - start
    sofar = now - start
    sofar /= defusetime
    sofar *= 4
    print('so far:')
    print(sofar)
    if sofar >= 4: #make sure to flash passcode after; this will terminate the loop
        exitcase = 2
        mode = 99
    return int(sofar)

def defusing(solved):
    string = ''
    for i in range(0,solved): #amount of digits solved
        string += str(config.password[i])
    rando = random.randrange(10)
    string += str(rando)
    string += '    '
    return string
        
def loop():
    global rawoutput
    global mode, exitcase
    while mode != 99:
        displaythem(rawoutput[0], rawoutput[1], rawoutput[2], rawoutput[3])
    destroy()
    raise FloatingPointError
    return exitcase

def destroy():   # When "Ctrl+C" is pressed, the function is executed. 
    global t, mode
    mode = 99
    t.cancel()

def flkr(text):
    global flick
    if not flick:
        text = '    '
    flick += 1
    flick %= 3
    return text

def timeboi(times):
    #times will just be loop count (this is a countdown)
    global givenloops, mode, exitcase
    times = givenloops - times
    if times <= 0 and mode == 4:
        exitcase = 1 #exploded
        mode = 99
    ms = '000'+str(times%1000)
    times = int(times/1000)
    secs = '0'+str(times % 60)
    mins = int(times / 60)
    tstring = ''
    if mins:
        mins = '0'+str(mins)
        tstring += mins[-2:]
        tstring += secs[-2:]     
    else:
        tstring += secs[-2:]
        tstring += ms[-4:-2]
    return tstring

def shiftletter(original):
    global flick
    out = '' 
    for i in range(0, len(original)):
        if flick == i:
            out += original[i]
        else:
            out += '_'
    flick += 1
    flick %= len(original)
    return out

def changemode(newmode):
    global mode
    mode = newmode

def print7(string, shift, loops=9999, speed=spd):
    global t, output, mode, lps, spd
    stopwatch.setup()
    t = threading.Timer(1.0,timer)      #set the timer
    spd = speed
    mode = 0
    if shift:
        mode = 1#its a number now :/
    output = string + '    '
    lps = len(output)*loops
    t.start()
    loop()

def time7(timeaa):
    global t, spd, givenloops, output, original, mode, lps, start
    stopwatch.setup()
    reason = 0
    t = threading.Timer(0.01, timer)
    spd = 0.05
    mode = 4
    lps = 0.1
    original = '    '#placeholder; original text not used for this mode
    output = original
    lps = timeaa * 1000
    givenloops = lps #its in ms
    start = int(time.time_ns()/1000000)
    t.start()
    reason = loop()
    return reason

def flick7(text, speed, loops):
    global t
    global spd
    global output
    global lps
    global original
    global mode
    stopwatch.setup()
    t = threading.Timer(speed, timer)
    spd = speed
    mode = 2
    original = text + '    '
    output = original
    lps = loops*4
    t.start()
    loop()
def flash7(text, speed, loops):
    global t, spd, output, lps, original, mode
    stopwatch.setup()
    t = threading.Timer(speed, timer)
    spd = speed
    mode = 3
    for i in range (1, 4):
        if len(text) >= 4:
            break
        text += '_'
    original = text
    output = '____'
    lps = loops*4
    t.start()
    loop()
    
def setoutput(newoutput):
    global output, rawoutput
    output = newoutput
    for i in range(0, len(rawoutput)):
        rawoutput[i] = v[output[i]]
def setrawoutput(newrawoutput):
    global rawoutput
    rawoutput = newrawoutput
def setupnoclk():
    stopwatch.setup()
    loop()
