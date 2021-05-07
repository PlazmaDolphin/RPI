import gpiozero
import threading
import seven
import score as scorelog
import time
from math import sqrt
import random
#add high score functionality to this pls
rotA = gpiozero.Button(26)
rotB = gpiozero.Button(20)
exitbut = gpiozero.Button(2)
score = 0 #not displayed until game ends
obstaclepos = 0
cursor = 0
unblocked = 0
lives = 4
speed = 1
alive = True
def cursormove():
    global cursor, obstaclepos, unblocked
    if rotB.value == 1:
        cursor -= 1
    elif rotB.value == 0:
        cursor += 1
    cursor %= 4
    display(obstaclepos, unblocked, cursor)
def display(obstacle, unblock, mouse):
    global lives
    data = [0, 0, 0, 0]
    objseg = 0
    lifeseg = 0b10000000
    mouseseg = 0b00001000
    if obstacle == 3:
        objseg = 0b00000001 #top
    elif obstacle == 2:
        objseg = 0b01000000 #middle
    elif obstacle == 1:
        objseg = 0b00001000 #bottom
    life = lives
    for i in range(0,4):
        if unblock != i:
            data[i] += objseg
        if mouse == i:
            data[i] += mouseseg
        if life > 0:
            data[i] += lifeseg
            life -= 1
    seven.setrawoutput(data)
def setup():
    global obstaclepos, unblocked, cursor, score, lives, speed
    obstaclepos = 4
    unblocked = 2
    cursor = 0
    score = 0
    lives = 4
    speed = 1
    display(obstaclepos, unblocked, cursor)
def obmove():
    global lives, score, speed, obstaclepos, unblocked, cursor
    obstaclepos -= 1
    obstaclepos %= 4
    fit = True
    if obstaclepos == 1:
        fit = doesfit(cursor, unblocked)
        if fit:
            score += 1
            speed += 1
        else:
            lives -= 1
            speed /= 3
            if lives < 0:
                die()
    if obstaclepos == 0:
        rando = random.randrange(3)
        rando += 1
        unblocked += rando
        unblocked %= 4
    display(obstaclepos, unblocked, cursor)
    if not fit:
        time.sleep(1)
def doesfit(mouse, gap):
    if mouse == gap:
        return True
    else:
        return False
def die():
    global alive
    alive = False
sevenout = threading.Thread(target= seven.setupnoclk, args= [])
sevenout.start()
def highscore():
    #do something with this please
    pass
def nothing():
    pass
def aliveloop():
    global speed
    while alive:
        obmove()
        time.sleep(1/sqrt(speed/2))
seven.setrawoutput([0,0,0,0])
while True:
    setup()
    if not alive:
        break
    rotA.when_pressed = cursormove
    exitbut.when_pressed = nothing
    aliveloop()
    alive = True
    exitbut.when_pressed = die
    rotA.when_pressed = nothing
    seven.setoutput(str(score) + '    ')
    time.sleep(2)
    rotA.wait_for_press()
seven.setrawoutput([0,0,0,0])
