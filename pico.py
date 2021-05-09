import digitalio
import pwmio
import board
import time
notes = {'C': 262, 'C#': 277, 'D': 294, 'D#': 311,
    'E': 320, 'F': 349, 'F#': 370, 'G': 392,
    'G#': 415, 'A': 440, 'A#': 466, 'B': 494
}
fontA = { #letters
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
numfont = [0b00111111, 0b00000110, 0b01011011, 0b01001111, 0b01100110,
           0b01101101, 0b01111101, 0b00000111, 0b01111111, 0b01101111]
class segdisp:
    def __init__(self, dpin, lpin, cpin):
        d = digitalio.DigitalInOut(dpin)
        d.direction = digitalio.Direction.OUTPUT
        self.d = d #data
        l = digitalio.DigitalInOut(lpin)
        l.direction = digitalio.Direction.OUTPUT
        self.l = l #latch
        c = digitalio.DigitalInOut(cpin)
        c.direction = digitalio.Direction.OUTPUT
        self.c = c #clock
        self.dig = 0
        self.data = [0,0,0,0]
    def setnum(self, num):
        for i in range(4):
            out = num // 10 ** (3-i)
            out %= 10
            self.data[i] = numfont[out]
    def settxt(self, txt, font=fontA):
        for i in range(4):
            self.data[i] = font[txt[i]]
    def setout(self, out):
            self.data = out
    def display(self):
        self.l.value = False
        self.d.value = False
        out = self.data[self.dig]
        pos = 2 ** self.dig
        for i in range(4):
            self.c.value = False
            self.d.value = (0b1000&(pos<<i)!=0b1000) #this is wrong but eh
            self.c.value = True
        for i in range(8):
            self.c.value = False
            self.d.value = (0x80&(out<<i)==0x80)
            self.c.value = True
        self.l.value = True
        self.dig += 1
        self.dig %= 4

class countdown:
    def __init__(self, t):
        self.start = time.monotonic_ns()
        self.finish = self.start + t * 1000000000
    def display(self):
        times = (self.finish - time.monotonic_ns())//10000000
        ms = times%100#actually centiseconds but who cares
        times = int(times/100)
        secs = times % 60
        mins = int(times / 60)
        tint = 0
        if mins:
            tint += mins*100
            tint += secs
        else:
            tint += secs*100
            tint += ms
        return tint
    def buzzbend(self, SN, EN):
        '''End - Start = T1; Now - Start = T2;
        T2 / T1 = Fac'''
        ET = self.finish - self.start
        NT = time.time() - self.start
        X = ET / NT
        D = EN / SN
        C = D / X
        return SN + C
    def expirechk(self):
        return time.monotonic_ns() > self.finish

class buzzer:
    def __init__(self, pin):
        self.buzz = pwmio.PWMOut(pin, duty_cycle=0, frequency=440, variable_frequency=True)
        self.BN1 = 0
        self.BN2 = 0
        self.bend = None
    def playnote(self, note, octave):
        octave -= 4
        self.playfreq(notes[note]*(2 ** octave))#not sure if powers work with negatives
    def playfreq(self, freq):
        self.buzz.duty_cycle = 2**15
        self.buzz.frequency = int(freq)
    def rest(self):
        self.buzz.duty_cycle = 0
    def setbend(self, N, btime, octave=4):
        self.BN1 = self.buzz.frequency
        self.bend = countdown(btime)
        if N in notes:
            octave -= 4
            self.BN2 = (notes[N]*(2 ** octave))
        else:
            self.BN2 = N
    def bender(self):
        if self.bend:
            self.buzz.frequency = self.bend.buzzbend(self.BN1, self.BN2)
            if self.bend.expirechk():
                self.bend = None