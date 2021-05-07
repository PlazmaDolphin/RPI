#buzzer interface & some advanced functions :D
import gpiozero
import time
import math
blink = gpiozero.LED(13)
blinkw = gpiozero.PWMLED(3)#placeholder pin, dont actually use that one
buzz = gpiozero.TonalBuzzer(26, octaves=5)
buzz2 = gpiozero.TonalBuzzer(21, octaves=5)
startms = 0
maxms = 0
recentTick = 0 #will be updated every tick
A0 = 1.04865151217746
A1 = 0.244017811416199
A2 = 1.76379778668885
m = 1
interrupt = False
beeplength =125
ticktempo = 300
def arm(mex):
    global startms, maxms
    startms = int(time.time_ns()/1000000)
    maxms = mex
def armbeep():
    #i kinda stole this function from someone else
    global startms, A0, A1, A2, beeplength, maxms, m
    passedms = int(time.time_ns()/1000000)-startms
    x = passedms / maxms
    n = A1 * x + A2 * x * x
    bps = A0 * math.exp(n)
    bps += (1/m)-1
    waitms = int(1000/bps)
    beeplen = beeplength
    if waitms <= beeplen:
        beeplen = waitms - 10
    if beeplen >= 0:
        buzz.play('A7')
        blink.on()
        time.sleep(beeplength/1000)
        buzz.stop()
        blink.off()
    return waitms - 125
def armloop(maxms):
    global startms, ticktempo
    nextbeep = 0
    arm(maxms)
    while int(time.time_ns()/1000000)<=startms+maxms:
        if int(time.time_ns()/1000000) > nextbeep and not interrupt:
            try:
                waitms = armbeep()
            except gpiozero.exc.PinSetInput:
                print('YOURE A LOSER')
                break
            nextbeep = int(time.time_ns()/1000000) + waitms
        time.sleep(0.02)
    if not interrupt:
        buzz.play('A5')
        blinkw.pulse(0, 2, 1)
        ticktempo = 960 #A5 -> G6 in 2 seconds
        notebend('G6', 32)
def explode():
    for _ in range(8):
        buzz2.play('F7')
        time.sleep(60/ticktempo)
        buzz2.stop()
        time.sleep(60/ticktempo)
    buzz.play('F2') #replace this with whatever the explosion will actually be
    time.sleep(5)
    buzz.stop()
def armloopplus(maxms):
    global m
    m = float(maxms / 45000) #45s is the time it was built for
    armloop(maxms)
def boop():
    for _ in range(0,3):
        buzz2.play('G7')
        time.sleep(0.12)
        buzz2.stop()
        time.sleep(0.08)
def defused():
    for _ in range(0,3):
        buzz2.play('E7')
        time.sleep(0.14)
        buzz2.stop()
        time.sleep(0.12)
def notebend(note, bendticks): 
    #you can do it with regular notes now
    '''End - Start = T1; Now - Start = T2;
    T2 / T1 = Fac'''
    first = buzz.value()
    buzz.play(note)
    final = buzz.value()
    buzz.value = first
    timebegin=recentTick
    timeend=timebegin + 60*1000*bendticks/ticktempo
    T1 = timeend - timebegin
    B1 = final - first
    T2 = 0
    while T2 <= T1:
        T2 = time.time()
        fac = T1 / T2
        print(fac)
        B2 = fac - first
        buzz.value = B2 / B1

def beginsong(): #will probably have more stuff later
    global recentTick 
    recentTick = int((time.time())*1000)

def playnotes(notes,thebuzzer=buzz,tempo=ticktempo): #use this for final beeps
#make it based on time.gettime later so it can sync up good
    global ticktempo, recentTick
    ticktempo = tempo
    for n in notes:
        time.sleep(60/ticktempo)
        if n == '--' or '  ':
            continue # -- will hold the current note
        if n == '==':
            thebuzzer.stop()
            continue
        #add note bending syntax
        thebuzzer.play(n)
def closebuzz():
    buzz.close()
    buzz2.close()
def interrupted():
    global interrupt
    interrupt = True
