import gpiozero
import time
import threading
LSBFIRST = 1
MSBFIRST = 2

dataPin   = 24      #DS Pin of 74HC595(Pin14)
latchPin  = 23      #ST_CP Pin of 74HC595(Pin12)
clockPin = 18       #SH_CP Pin of 74HC595(Pin11)
num = (0b00111111,0b00000110,0b01011011,0b01001111,0b01100110,
       0b01101101,0b01111101,0b00000111,0b01111111,0b01100111,
10,0b0111001,0b01110001)
# Define the pin of 7-segment display common end
counter = 0         # Variable counter, the number will be dislayed by 7-segment display
t = 0               # define the Timer object
dataP =0
latch=0
clock=0
dig1=0
dig2=0
dig3=0
dig4=0
def setup():
    global dataP, latch, clock, dig1, dig2, dig3, dig4
    dataP = gpiozero.LED(dataPin)    # Set pin mode to output
chPin)
ckPin)


    dig3 = gpiozero.LED(22)
    dig4 = gpiozero.LED(10)
    
def shiftOut(dPin,cPin,val):      
    for i in range(0,8):
        cPin.off()
        if (0x80&(val<<i)==0x80):
            dataP.on()
        else:
            dataP.off()
        cPin.on()
            
def outData(data):      #function used to output data for 74HC595
    latch.off()
    shiftOut(dataP,clock,data)
    latch.on()
    
def selectDigit(digit): # Open one of the 7-segment display and close the remaining three, the parameter digit is optional for 1,2,4,8
    if digit == 0x08:
        dig1.off()
        dig4.on()
    elif digit == 0x04:
        dig2.off()
        dig1.on()
   elif digit == 0x02:
.on()
    elif digit == 0x01:
        dig4.off()
        dig3.on()

#no need to continue converting!
def display(dec):   #display function for 7-segment display
    outData(0x00)   #eliminate residual display
    selectDigit(0x01)   #Select the first, and display the single digit
    outData(num[dec%10])
    time.sleep(0.002)   #display duration
    outData(0x00)
    selectDigit(0x02)   # Select the second, and display the tens digit
    outData(num[dec%100//10])
    time.sleep(0.002)
    outData(0x00)
    selectDigit(0x04)   # Select the third, and display the hundreds digit
    outData(num[dec%1000//100])
    time.sleep(0.002)
    outData(0x00)
    selectDigit(0x08)   # Select the fourth, and display the thousands digit
    outData(num[dec%10000//1000])
    time.sleep(0.002)
def timer():        #timer function
    global counter
    global t
    t = threading.Timer(1.0,timer)      #reset time of timer to 1s
    t.start()                           #Start timing
    counter+=7                          
    print ("counter : %d"%counter)
    
def loop():
    global t
    global counter
    t = threading.Timer(1.0,timer)      #set the timer
    t.start()                           # Start timing
    while True:
        display(counter)                # display the number counter
        
def destroy():   # When "Ctrl+C" is pressed, the function is executed. 
    global t
    #GPIO.cleanup()      
    t.cancel()      #cancel the timer

if __name__ == '__main__': # Program starting from here 
    print ('Program is starting...' )
    setup() 
    try:
        loop()  
    except KeyboardInterrupt:  
        destroy()  
