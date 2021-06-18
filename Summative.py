#==================================================#
# File Name: Summative.py                                                               
# Description: Top-Down shooting game built on pygame      
# Authors: Peter Gu, Edwin Sun, Edison Du   
# Mr. Mangat P4 ICS2OG-01                                   
# Date: 2020-1-20                                                                
#==================================================#
# WORK DIVISION                                    #
# Sound and Music done by Peter Gu                 #
# Enemy movement and tracking done by Peter Gu     #
# Projectile movement done by Peter Gu             #
# Boss functionality done by Peter Gu              #
# Enemy ray projection done by Peter Gu            #
# Enemy ai and wall tracking done by Edwin Sun     #
# Room generation done by Edwin Sun                #
# Game framework and cleanup done by Edwin Sun     #
# UI done by Edison Du                             #  
# Graphics done by Edison Du                       #
# Collision done by Edison Du                      #
# Player movement done by Edison Du                #   
# Collectibles done by Edison Du                   #  
# Level system done by Edison Du                   # 
#==================================================#

import pygame
from pygame.locals import *
import random
from math import sqrt
import os
pygame.init()

#===============================#
#---Colours,Fonts,Gamedisplay---#
#===============================#
BLACK =  (  0,  0,  0)
WHITE =  (255,255,255)
RED =    (255,  0 , 0)
GREEN =  (  0,255,  0)
WIDTH = 700
HEIGHT = 700
gameWindow = pygame.display.set_mode((WIDTH,HEIGHT))
font = pygame.font.SysFont("Algerian", 40)

#===============#
#---Functions---#   
#===============#
# Checks if two lists (containing coordinates of a rectangle's start and end points) are overlapping
# Next four parameters will extend each side of first rectangle

#=Created by Edison=#
def getCollision (objectOne, objectTwo, leftRange, rightRange, upRange, downRange):
    if (objectOne[0] - leftRange < objectTwo[2] and objectTwo[0] < objectOne[2] + rightRange):
        if (objectTwo[3] > objectOne[1] - upRange and objectOne[3] + downRange > objectTwo[1]):
            return True
    return False

# Given an image name, will find the image file and return a pygame image

#=Created by Edison=#
def createSprite (imageName):
    sprite = pygame.image.load(os.path.join('Art', imageName)).convert_alpha()
    return(sprite)

# Switch Music Load

#=Created by Peter=#
def switchMusic (index):
    pygame.mixer.music.fadeout(25)
    pygame.mixer.music.load(os.path.join("Music",songs[index]))
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)
#=============#
#---Classes---#   
#=============#

#=Created by Edwin=#
class coordinate:
    def __init__ (self, x, y):
        self.x = x
        self.y = y

# Will contain any object that is involved in play (all have a x and y value, as well as a collision rectangle)
class gameObject:
    def __init__ (self,x,y,collision):
        self.x = x
        self.y = y
        self.collision = collision

# If an object is moving, the collision will have to follow the object and will need to be updated (parameters are sides of rectangle relative to the x and y position)
    #=Created by Edison=#
    def updateCollision(self, up, left, down, right):
        self.collision = [self.x-left, self.y-up, self.x+right, self.y+down]

#=Created by Peter=#
class projectile (gameObject):
    def __init__(self,x,y,endX,endY,speed,speedX,speedY):
        gameObject.__init__(self,x,y,[x-7, y-7, x+7, y+7])
        
        # Find the distance using pythagorean theorem as well as speed
        self.endX = endX
        self.endY = endY
        self.speed = speed
        tempX = endX - self.x
        tempY = endY - self.y
        self.endX +=  (tempX*1000)
        self.endY += (tempY*1000)
        distance = sqrt((endX-self.x)**2+(endY-self.y)**2)
        time = (distance/speed)+1
        self.speedX= (((endX)-(x))/time)
        self.speedY= (((endY)-(y))/time)
        self.sprites = [createSprite("CharBullet.png"),createSprite("EnemyBullet.png")]

    # Moves bullet according to previously calculated speed
    def move(self):
        self.x += self.speedX
        self.y += self.speedY

class entity (gameObject):
    def __init__(self, x, y, hp, collision):
        gameObject.__init__(self, x, y, collision)
        self.hp = hp    
        self.displayDamagedCounter = 0

    # Moves the x and y of the entity by a certain amount
    def move(self, xChange, yChange):
        self.x += xChange
        self.y += yChange

class player (entity):
    # Player is initialized with a movement speed, bullet damage (strength) and how fast they can fire bullets (reloadSpeed)
    #=Created by Edison=#
    def __init__(self, x, y, hp, speed, strength, reloadSpeed):
        entity.__init__(self, x, y, hp, [x, y, x+45, y+45])
        self.speed = speed
        self.strength = strength
        self.reloadSpeed = reloadSpeed
        self.directionX = "right"
        self.sprites = [
            createSprite("PlagueDoctor.png"), 
            createSprite("PlagueDoctorLeft.png"),
            createSprite("PlayerDamagedRight.png"),
            createSprite("PlayerDamagedLeft.png"),
            createSprite("PlayerDeath[1].png"), 
            createSprite("PlayerDeath[2].png"),
            createSprite("PlayerDeath[3].png"),
            createSprite("PlayerDeath[4].png"),
            createSprite("PlayerDeath[5].png"),
            createSprite("PlayerDeath[6].png"),
            createSprite("PlayerDeath[7].png"),
            createSprite("PlayerDeath[8].png"),
            createSprite("PlayerDeath[9].png"),
            createSprite("PlayerDeath[10].png") 
        ]
        
class enemy (entity):
    def __init__(self, x, y, hp, collision):
        entity.__init__(self, x, y, hp, collision)

#=Peter=#
class smallMob (enemy):
    def __init__(self, x, y, hp, speed):
        enemy.__init__(self, x, y, hp, [x+5, y+5, x+33, y+37])
        self.speed = speed
        self.xChange = 0
        self.yChange = 0
        self.direction = True
        self.canHurtPlayer = 60
        self.nearestCheckpoint = coordinate(0,0)
        self.onTrack = False
        self.path = []
        self.shouldTrack = False
        self.toNearestCheckpoint = True
        self.sprites = [
            createSprite("SmallMobLeft.png"), 
            createSprite("SmallMobRight.png"),
            createSprite("SmallMobDamagedLeft.png"),
            createSprite("SmallMobDamagedRight.png")
            ]

    # Checking for other enemies in way to avoid mixing together
    def threadMob(self, playerX, playerY):
        oldPlayerX= playerX
        oldPlayerY= playerY
        playerX+=20
        playerY+=20
        ifCollide= False
        tempX= playerX-self.x
        tempY= playerY-self.y
        playerX += tempX
        playerY += tempY
        distance= sqrt((playerX-self.x)**2+(playerY-self.y)**2)
        time = (distance/30)
        currentX = self.x
        currentY = self.y
        # Creates only one future collision box
        for position in range(1):
            currentX += (((playerX)-(self.x))/time)
            currentY += (((playerY)-(self.y))/time)
            # Checking for all mob collision
            for item in currentRoom.smallMobs:
                if item.x == self.x and item.y == self.y:
                    continue
                flag = getCollision([currentX,currentY,currentX+30,currentY+35],item.collision,0,0,0,0)
                if flag is True:
                    ifCollide= True
                    break
            if ifCollide is True:
                break
            elif getCollision([currentX,currentY,currentX,currentY], [oldPlayerX, oldPlayerY, oldPlayerX, oldPlayerY], 0, 0, 0, 0):
                break
        return ifCollide
    
    # Checks if there are any future collisions between mob and player
    def thread(self, playerX, playerY): 
        oldPlayerX= playerX
        oldPlayerY= playerY
        playerX+=20
        playerY+=20
        ifCollide= False
        tempX= playerX-self.x
        tempY= playerY-self.y
        playerX += tempX
        playerY += tempY
        distance = sqrt((playerX-self.x)**2+(playerY-self.y)**2)
        time = (distance/5)
        currentX = self.x
        currentY = self.y
        # Checking for whole map until player or wall
        for position in range(int(time/2)):
            currentX += (((playerX)-(self.x))/time)
            currentY += (((playerY)-(self.y))/time)
            for item in currentRoom.walls:
                flag = getCollision([currentX,currentY,currentX+15,currentY+15],item.collision,0,0,0,0)
                if flag is True:
                    ifCollide= True
                    break
            if ifCollide is True:
                break
            elif getCollision([currentX,currentY,currentX,currentY], [oldPlayerX, oldPlayerY, oldPlayerX, oldPlayerY], 0, 0, 0, 0):
                break
        return ifCollide

    #Moves enemy towards the player using the shortest distance
    def track(self, playerX, playerY):
        temporaryX= playerX-self.x
        temporaryY= playerY-self.y
        if temporaryX >= 0:
            self.direction = True
        else:
            self.direction = False
        playerX += temporaryX
        playerY += temporaryY
        distance= sqrt((playerX-self.x)**2+(playerY-self.y)**2)
        time = (distance/self.speed)+1
        self.x += (((playerX)-(self.x))/time)
        self.y += (((playerY)-(self.y))/time)

#=Peter=#
class rangedMob (enemy):
    # Is intialized with how fast their bullets go and how fast they can fire the bullets
    def __init__(self, x, y, hp, bulletSpeed, reloadSpeed):
        enemy.__init__(self, x, y, hp, [x, y, x+80, y+84])
        self.bullets = []
        self.reloadSpeed = reloadSpeed
        self.reloadCounter = reloadSpeed
        self.bulletSpeed = bulletSpeed
        self.canHurtPlayer = 60
        self.sprites = [
            createSprite("EyeMob1.png"), 
            createSprite("EyeMob2.png"),
            createSprite("EyeMobDamagedLeft.png"),
            createSprite("EyeMobDamagedRight.png")
            ]

    # Adds a projectile to the list of bullets that belong to this mob
    def fire (self,playerX,playerY):
        pygame.mixer.Sound.play(enemyShot)
        self.bullets.append(projectile(self.x+20, self.y+20, playerX, playerY, self.bulletSpeed, 0, 0))

#=Peter=#
class boss (enemy):
    def __init__(self,x,y,hp,speed):
        enemy.__init__(self,x,y,hp,[x,y,x+80,y+100]) 
        self.speed = speed
        self.mode = 0
        self.timer = 80
        self.speedX = 0
        self.speedY = 0
        self.bulletList= []
        self.oldX = 0
        self.oldY = 0
        self.mortarList = []
        self.ifAttack = True
        self.canHurt = 60
        self.recoil = 0
        self.sprites = [createSprite("Boss.png"), createSprite("BossDamaged.png")]

    # Calculate speed for boss to charge
    def calcSpeed(self,playerX,playerY):
        self.oldX = playerX
        self.oldY = playerY
        tempX = playerX - self.x
        tempY = playerY- self.y
        playerX +=  tempX
        playerY += tempY
        distance = sqrt((playerX-self.x)**2+(playerY-self.y)**2)
        time = (distance/self.speed)+1
        self.speedX= (((playerX)-(self.x))/time)
        self.speedY= (((playerY)-(self.y))/time)

    # Stunning boss for player to react
    def stun(self):
        if self.timer <= 0:
            return True
        else:
            self.timer-=1
            return False

    # Charges using previously calculated
    def charge(self):
        self.x+=self.speedX
        self.y+=self.speedY

    # Fires an octogonal shot from boss
    def spreadShot(self):
        allD= []
        # Calculates all velocities 
        for bossShot in range(0,5):
            allD.append([self.x + bossShot*400, self.y + (4-bossShot)*400])
            allD.append([self.x - bossShot*400, self.y - (4-bossShot)*400])
            allD.append([self.x + (4-bossShot)*400, self.y - bossShot*400])
            allD.append([self.x - (4-bossShot)*400, self.y + bossShot*400])
        for i in range(16):
            self.bulletList.append(projectile(self.x+40,self.y+50,allD[i][0],allD[i][1],6,0,0))

    # Fires mortar for boss
    def mortarFire(self):
        target =0
        # Creates random positions for mortars that don't overlap with boss or player
        while (target != 9):
            overlap = False
            x = random.randint(100,600)
            y = random.randint(100,600)
            # Checks for collision
            for otherMortar in self.mortarList:
                ifCollide = getCollision([x,y,x+50,y+50],otherMortar.collision,0,0,0,0)
                if ifCollide:
                    overlap = True
                    break
            if getCollision([x,y,x+50,y+50],self.collision,0,0,0,0):
                overlap = True
            if overlap is False:
                self.mortarList.append(mortar(x, y,100))
                target+=1

    # Fast shot that directly aims at the player     
    def snipe(self,playerX,playerY):
        self.bulletList.append(projectile(self.x+40,self.y+50,playerX,playerY,15,0,0))

#=CreatePeter=#
# Mortar for boss room
class mortar(gameObject):
    def __init__(self,x,y,timer):
        gameObject.__init__(self,x,y,[x,y,x+36,y+36])
        self.mode = False
        self.timer = timer
        self.sprite = [createSprite("Target.png"),createSprite("Crater.png")]
    # Ticks mortar until expiry or explosion
    def count(self):
        self.timer -=1
        if self.timer == 0 and self.mode == False:
            self.mode = True
            self.timer+=100
        elif self.timer == 0:
            return False
        return True

# Rectangular object with only a collision box
class wall(gameObject):
    def __init__(self, x, y, endX, endY):
        gameObject.__init__(self, x, y, [x, y, endX, endY])

# Object that has an effect when collided with
#=Created by Edison=#
class teleporter(gameObject):
    # Stasis will determine what the effect is
    def __init__(self, x, y, stasis):
        gameObject.__init__(self, x, y, [x, y, x+54, y+54])
        self.stasis = stasis
        self.sprite = createSprite("Teleporter.png")

class collectible (gameObject):
    def __init__(self, x, y, collision):
        gameObject.__init__(self, x, y, collision)

#=Created by Edison=#
class boostCollectible (collectible):
    # Is initialized with how powerful the boost will be, and what type of boost (health, strength, speed, reload)
    def __init__(self, x, y, boostAmount, boostType):
        collectible.__init__(self, x, y, [x, y, x+30,y+30])
        self.boostAmount = boostAmount
        self.boostType = boostType
        self.sprites = [
            createSprite("HealthCollectible.png"),
            createSprite("StrengthCollectible.png"),
            createSprite("SpeedCollectible.png"),
            createSprite("ReloadCollectible.png")
        ]

class room:
    def __init__ (self,x,y,level,roomType):
        self.x = x
        self.y = y
        self.smallMobs = []
        self.rangedMobs = []
        self.boss = ""
        self.items = []
        self.walls = []
        self.checkpoints = []
        self.roads = [[] for i in range(10)]
        self.level = level
        self.walls.append(wall(0, 0, 293, 90))
        self.walls.append(wall(407, 0, 700, 90))
        self.walls.append(wall(0, 90, 40, 350))
        self.walls.append(wall(0, 440, 40, 660))
        self.walls.append(wall(0, 660, 293, 700))
        self.walls.append(wall(407, 660, 700, 700))
        self.walls.append(wall(660, 90, 700, 350))
        self.walls.append(wall(660, 440, 700, 660))
        self.sprites = [createSprite("Map.png"), createSprite("InteriorWall.png")]
        # keyMap is a dictionary with its key being the coordinate of a checkpoint and its value being the checkpoint number
        self.keyMap = {} 
        # valueMap is a dictionary with its key being the checkpoint number and its value being the coordinate of a checkpoint
        self.valueMap = {}
        self.roomType  = roomType

        #= Created by Edwin=#
        if (self.roomType == 2):
            self.walls.append(wall(150,200,550,300))
            self.walls.append(wall(150,450,550,550))            
            self.checkpoints.append(coordinate(100,150)) 
            self.keyMap[str(100)+str(150)] = 1
            self.valueMap[1] = str(100)+" "+str(150)
            self.checkpoints.append(coordinate(350,150)) 
            self.keyMap[str(350)+str(150)] = 2
            self.valueMap[2] = str(350)+" "+str(150)
            self.checkpoints.append(coordinate(600,150)) 
            self.keyMap[str(600)+str(150)] = 3
            self.valueMap[3] = str(600)+" "+str(150)
            self.checkpoints.append(coordinate(100,375)) 
            self.keyMap[str(100)+str(375)] = 4
            self.valueMap[4] = str(100)+" "+str(375)
            self.checkpoints.append(coordinate(350,375)) 
            self.keyMap[str(350)+str(375)] = 5
            self.valueMap[5] = str(350)+" "+str(375)
            self.checkpoints.append(coordinate(600,375)) 
            self.keyMap[str(600)+str(375)] = 6
            self.valueMap[6] = str(600)+" "+str(375)
            self.checkpoints.append(coordinate(100,600)) 
            self.keyMap[str(100)+str(600)] = 7
            self.valueMap[7] = str(100)+" "+str(600)
            self.checkpoints.append(coordinate(350,600)) 
            self.keyMap[str(350)+str(600)] = 8
            self.valueMap[8] = str(350)+" "+str(600)
            self.checkpoints.append(coordinate(600,600)) 
            self.keyMap[str(600)+str(600)] = 9
            self.valueMap[9] = str(600)+" "+str(600)
            self.roads[1].append(2) 
            self.roads[1].append(4)
            self.roads[2].append(1)
            self.roads[2].append(3)
            self.roads[3].append(2)
            self.roads[3].append(6)
            self.roads[4].append(1)
            self.roads[4].append(7)
            self.roads[4].append(5)
            self.roads[5].append(4)
            self.roads[5].append(6)
            self.roads[6].append(5)
            self.roads[6].append(3)
            self.roads[6].append(9)
            self.roads[7].append(4)
            self.roads[7].append(8)
            self.roads[8].append(9)
            self.roads[8].append(7)
            self.roads[9].append(8)
            self.roads[9].append(6)

#=Created by Edison=#
# Fills room with mobs given the number of mobs, what type of mob (smallMob or rangedMob) and the player (to prevent mobs spawning on the player)
    def generateMobs(self, quantity, mobType, player):
        while(quantity > 0):
            canSpawn = True
            # Small Mob
            if (mobType == 1):
                # Generate a random spot in the map
                position = coordinate(random.randint(0,600), random.randint(0,600))
                # Create a mob on that position (mob's stats such as health and speed are increased with the level)
                temporaryMob = smallMob(position.x,position.y,10 + 3*level,1 + 0.2*level)
                # Determine if the mob can be spawned there by checking if it spawns on top of other mobs, walls or the player 
                for i in self.smallMobs:
                    if(getCollision(i.collision, temporaryMob.collision, 0,0,0,0)):
                        canSpawn = False
                for w in self.walls:
                    if (getCollision(temporaryMob.collision, w.collision, 0,0,0,0)):
                        canSpawn = False
                # Player will have a larger collision buffer zone where mobs cannot spawn on
                if (getCollision(temporaryMob.collision, player.collision, 40, 40, 40, 40)):
                    canSpawn = False
                # If it can be spawned, it is added to the list of mobs in the room
                if(canSpawn == True):
                    self.smallMobs.append(temporaryMob)
                    quantity -= 1

            # Ranged Mob
            elif (mobType == 2):
                # Exact same logic as above
                position = coordinate(random.randint(0,600), random.randint(0,600))
                temporaryMob = rangedMob(position.x, position.y, 10 + 3*level, 5 + 0.3*level, 120-3*level)
                for i in self.rangedMobs:
                    if(getCollision(i.collision, temporaryMob.collision, 0,0,0,0)):
                        canSpawn = False
                for w in self.walls:
                    if (getCollision(temporaryMob.collision, w.collision, 0,0,0,0)):
                        canSpawn = False
                if (getCollision(temporaryMob.collision, player.collision, 40, 40, 40, 40)):
                    canSpawn = False
                if(canSpawn == True):
                    self.rangedMobs.append(temporaryMob)
                    quantity -= 1
    
    def generateItems(self, quantity, player):
        while(quantity > 0):
            validPosition = True
            position = coordinate(random.randint(0,600), random.randint(0,600))
            # Collectibles are random (health, strength, speed, reload)
            temporaryItem = boostCollectible(position.x, position.y, 1, random.randint(1,4))
            # Check if it is not on top of other items, walls or the player
            for i in self.items:
                if(getCollision(i.collision, temporaryItem.collision, 0,0,0,0)):
                    validPosition = False
            for w in self.walls:
                if (getCollision(temporaryItem.collision, w.collision, 0,0,0,0)):
                    validPosition = False 
            if (getCollision(temporaryItem.collision, player.collision, 40, 40, 40, 40)):
                validPosition = False
            if(validPosition == True):
                self.items.append(temporaryItem)
                quantity -= 1
    
    # Creates the boos room, requires parameter for how often items will be spawned
    def generateBoss(self, collectibleSpawn):
        switchMusic(2)
        self.boss = boss(450,500,1500,9)
        # collectibleSpawn remains constant whereas collectibleTimer will decrement
        self.collectibleSpawn = collectibleSpawn
        self.collectibleTimer = collectibleSpawn

#=Created by Edison=# 
# User interface objects only require an x and y position
class ui:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class button(ui):
    # Is initialized with all four sides (of rectangle) to create collision box
    def __init__(self, startX, startY, endX, endY):
        ui.__init__(self, startX, startY)
        self.collision = (startX, startY, endX, endY)

class playerHealthBar(ui):
    def __init__(self, x, y, health):
        ui.__init__(self, x,y)
        self.health = health
        self.sprites = [createSprite("HealthBar.png"), createSprite("PlayerHead.png")] 
    
    def drawHealth(self):
        # Prevents health bar from being negative and drawing the wrong direction
        if (self.health > 0):
            # The length of the health bar depends on the amount of health the player has
            pygame.draw.rect(gameWindow, GREEN, (self.x, self.y, self.health*30, 30))
            gameWindow.blit(self.sprites[0],(self.x-2.5,self.y))
            gameWindow.blit(self.sprites[1],(self.x-40,self.y-7.5))

class bossHealthBar(ui):
    def __init__(self, x, y, health, totalHealth):
        ui.__init__(self, x, y)
        self.health = health
        self.totalHealth = totalHealth
        self.sprites = [createSprite("BossHealth.png"), createSprite("BossHead.png")]
    
    def drawHealth(self, length):
        # Uses ratios to determine how much of a given length should be filled up (percentage of the length that is the health relative to the total health)
        self.percentageOfBar = self.health * length / self.totalHealth
        pygame.draw.rect(gameWindow, RED, (self.x, self.y, self.percentageOfBar, 30))
        gameWindow.blit(self.sprites[0],(self.x-2.5, self.y))
        gameWindow.blit(self.sprites[1], (self.x-40, self.y-15))

class startScreen(ui):
    def __init__(self, x, y):
        ui.__init__(self, x, y)
        self.sprites = [
            createSprite("StartScreen.png"),
            createSprite("StartScreenClicked1.png"),
            createSprite("StartScreenClicked2.png"),
            createSprite("StartScreenClicked3.png"),
            createSprite("StartScreenControls.png")
        ]

#===============#
#---Variables---#   
#===============#
# Clock
clock = pygame.time.Clock()

# Sound Effects and their Respective Volumes
bossDeath = pygame.mixer.Sound(os.path.join('Sound','BossDeath.wav'))
enemyAttack = pygame.mixer.Sound(os.path.join('Sound','Chomp.wav'))
enemyShot = pygame.mixer.Sound(os.path.join('Sound','EnemyShot.wav'))
powerUp = pygame.mixer.Sound(os.path.join('Sound','PowerUp.flac'))
playerDeath = pygame.mixer.Sound(os.path.join('Sound','PlayerDeath.wav'))
playerShot = pygame.mixer.Sound(os.path.join('Sound','PlayerShot.wav'))
teleport = pygame.mixer.Sound(os.path.join('Sound','Teleport.wav'))
bossDeath.set_volume(0.01)
enemyAttack.set_volume(0.03)
enemyShot.set_volume(0.25)
powerUp.set_volume(0.009)
playerDeath.set_volume(0.2)
playerShot.set_volume(0.07)
teleport.set_volume(0.1)

# Music
pygame.mixer.init()
songs= ["MainMenuMusic.ogg","RoomMusic.ogg","BossMusic.ogg"]
pygame.mixer.music.load(os.path.join("Music",songs[0]))
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1) # Loop

# Game Variables
player = player(330, 600, 10, 3, 1, 40)
teleporter = teleporter(323,345,False)
bulletDeleted = False
bulletList=[]
bulletDelay = 0
canMove = True
playerDeathLoop = 4
level = 1
currentRoom = room(0, 0, level, random.choice([2, 2, 1, 1, 1]))
hasControl = True
bossSound = False

# UI and static display
startScreen = startScreen(0, 0)
playButton = button(45, 355, 187, 400)
controlsButton = button(45, 430, 330, 475)
displayControls = False
closeControlsButton = button(605, 220, 645, 260)
quitButton = button(45, 505, 165, 550)
deathScreen = createSprite("DeathScreen.png")
winScreen = createSprite("WinScreen.png")
playerHealth = playerHealthBar(50, 640, player.hp)
bossHealth = bossHealthBar(350, 60, 500, 500)

# Major game loop conditionals
startingScreen = True
inPlay = True
restart = True

#==========================#
#---Pre-Game Menu Screen---#   
#==========================#
while startingScreen:
    gameWindow.fill(BLACK)
    pygame.event.clear()
    clock.tick(60)

    pygame.event.get()
    keys = pygame.key.get_pressed()
    mouseX,mouseY= pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    #=Created by Edison=#
    # Nothing else can be clicked if the controls panel is open (game cannot start)
    if (displayControls):
        gameWindow.blit(startScreen.sprites[4], (startScreen.x, startScreen.y))
        # Determines if the controls have been closed by clicking on the "X"
        if (getCollision(closeControlsButton.collision, [mouseX, mouseY, mouseX, mouseY], 0, 0, 0, 0)):
            if (click[0] == True):
                displayControls = False
                
    # If the player is hovering the play button, the button will enlarge
    elif getCollision(playButton.collision, [mouseX, mouseY, mouseX, mouseY], 0, 0, 0, 0):
        gameWindow.blit(startScreen.sprites[1], (startScreen.x, startScreen.y))
        # If the play button is clicked, the starting screen will be exited and the game will begin
        if click[0] == True:
            startingScreen = False
            switchMusic(1)
    
    # Enlarge control button when hovered
    elif getCollision(controlsButton.collision, [mouseX, mouseY, mouseX, mouseY], 0, 0, 0, 0):
        gameWindow.blit(startScreen.sprites[2], (startScreen.x, startScreen.y))
        # Open control panel if clicked
        if click[0] == True:
            displayControls = True
            
    # Enlarge quit button when hovered
    elif (getCollision(quitButton.collision, [mouseX, mouseY, mouseX, mouseY], 0, 0, 0, 0)):
        gameWindow.blit(startScreen.sprites[3], (startScreen.x, startScreen.y))

        # When clicked, starting screen and main game will be exited and pygame will quit
        if click[0] == True:
            startingScreen = False
            restart = False
            inPlay = False

    # No butons enlarged if nothing is hoverd
    else:
        gameWindow.blit(startScreen.sprites[0], (startScreen.x, startScreen.y))

    # Exit starting screen and main game and quit pygame
    if (keys[pygame.K_ESCAPE]):
        startingScreen = False
        restart = False
        inPlay = False 

    pygame.display.update()

#====================#
#---Main Game Loop---#   
#====================#
while restart:
    # Initialize everything to default (default player stats and first level)
    level = 1
    player.x = 330
    player.y = 600
    player.hp = 10
    player.speed = 3
    player.strength = 1
    player.reloadSpeed = 40
    playerDeathLoop = 4
    player.updateCollision(0, 0, 45, 45)
    bulletList=[]
    currentRoom = room(0, 0, level, random.choice([2, 2, 1, 1, 1]))
    currentRoom.generateMobs(level, 1, player)
    currentRoom.generateMobs(round(level/2), 2, player)
    currentRoom.generateItems(round((10+level)/2), player)
    inPlay = True
    hasControl = True
    
    while inPlay:
        gameWindow.fill(BLACK)
        pygame.event.clear()
        clock.tick(60)
        pygame.event.get()
        keys = pygame.key.get_pressed()

        # Draw the room and the walls
        gameWindow.blit(currentRoom.sprites[0],(currentRoom.x,currentRoom.y))
        if (currentRoom.roomType == 2):
            gameWindow.blit(currentRoom.sprites[1],(currentRoom.walls[8].x,currentRoom.walls[8].y))
            gameWindow.blit(currentRoom.sprites[1],(currentRoom.walls[9].x,currentRoom.walls[9].y))
        
        # Display level in top left corner
        gameWindow.blit(font.render("Level " + str(level),1,WHITE),(20,20))
        
        #=Created by Edison=#
        #---Items---#
        for s in currentRoom.items:
            if (s.boostType == 1):
                gameWindow.blit(s.sprites[2],(s.x,s.y))
            elif (s.boostType == 2):
                gameWindow.blit(s.sprites[3],(s.x,s.y))
            elif (s.boostType == 3):
                gameWindow.blit(s.sprites[1],(s.x,s.y))
            elif (s.boostType == 4):
                gameWindow.blit(s.sprites[0],(s.x,s.y))

            # Different effects depending on which collectible the player has hit
            if (getCollision(player.collision, s.collision, 0, 0, 0, 0)):
                pygame.mixer.Sound.play(powerUp)
                if (s.boostType == 1):
                    # Speed collectible
                    player.speed += s.boostAmount*0.3
                elif (s.boostType == 2):
                    # Reload collectible (capped at one bullet every 5 frames)
                    if (player.reloadSpeed >= 5):
                        player.reloadSpeed -= s.boostAmount 
                elif (s.boostType == 3):
                    # Damage collectible (capped at 20 damage)
                    if (player.strength < 20):
                        player.strength += s.boostAmount
                elif (s.boostType == 4):
                     # Health collectible (capped at 10 health)
                    if (player.hp < 10):
                        player.hp += s.boostAmount  
                currentRoom.items.remove(s)

        #=Created by Edwin=#
        #---Small Mobs---#
        for e in currentRoom.smallMobs:
            # Draw the mob depending on which direction it is facing
            if (e.direction):
                gameWindow.blit(e.sprites[0],(e.x,e.y))
                # If the mob has been damaged, it will glow red for a few frames
                if (e.displayDamagedCounter > 0):
                    gameWindow.blit(e.sprites[2],(e.x,e.y))
                    e.displayDamagedCounter -= 1
            else:
                gameWindow.blit(e.sprites[1],(e.x,e.y))
                if (e.displayDamagedCounter > 0):
                    gameWindow.blit(e.sprites[3],(e.x,e.y))
                    e.displayDamagedCounter -= 1
            e.updateCollision(-5, -5, 33, 37) 
            # Limit on how often the mob does damage when colliding with the player
            if (e.canHurtPlayer > 0):
                e.canHurtPlayer -= 1
            if (e.canHurtPlayer == 0):
                if (getCollision(e.collision, player.collision, 0, 0, 0, 0)):
                    # Player takes damage for every second it collides with the mob
                    player.hp -= 1
                    if player.hp >= 0:
                        pygame.mixer.Sound.play(enemyAttack)
                    player.displayDamagedCounter = 5
                    e.canHurtPlayer = 60
            # Mob movement (will only move if the player has control, i.e. neither a death screen or win screen)
            if (hasControl):
                if(currentRoom.roomType == 1):
                    ifCollide = e.threadMob(player.x,player.y)
                    if ifCollide:
                        continue
                    else:
                        e.track(player.x,player.y)
                elif (currentRoom.roomType == 2):
                    # Check if mob AI would be able to directly track the player
                    if(e.shouldTrack == True):
                        if(e.thread(player.x,player.y) == False and e.thread(player.x+25,player.y) == False or e.thread(player.x+25,player.y+25) == False and e.thread(player.x,player.y+25) == False):
                            e.track(player.x,player.y)
                            e.onTrack = False
                            e.path = []
                        else:
                            e.shouldTrack = False
                        continue
                    e.x = round(e.x)
                    e.y = round(e.y)
                    e.x = int(e.x)
                    e.y = int(e.y)
                    # Makes mobs that are off track (not traversing through checkpoints) go to its nearest checkpoint
                    if(e.onTrack == False):
                        minDistance = 99999999
                        minX = 99999
                        minY = 99999
                        for f in currentRoom.checkpoints:
                            if(sqrt((f.x-e.x)**2+(f.y-e.y)**2) < minDistance):
                                minDistance = sqrt((f.x-e.x)**2+(f.y-e.y)**2)
                                minX = f.x
                                minY = f.y
                        e.nearestCheckpoint = coordinate(minX,minY)
                        e.track(e.nearestCheckpoint.x,e.nearestCheckpoint.y)

                    # Check if an off track mob has reached its nearest checkpoint 
                    if(e.onTrack == False):
                        if(e.x == e.nearestCheckpoint.x or e.x-1 == e.nearestCheckpoint.x or e.x+1 == e.nearestCheckpoint.x):
                            if(e.y == e.nearestCheckpoint.y or e.y-1 == e.nearestCheckpoint.y or e.y+1 == e.nearestCheckpoint.y):
                                e.x = e.nearestCheckpoint.x
                                e.y = e.nearestCheckpoint.y
                                e.onTrack = True
                    
                    e.x = round(e.x)
                    e.y = round(e.y)
                    e.x = int(e.x)
                    e.y = int(e.y)

                    #Once the mob has reached its nearest checkpoint, it uses the shortest path of checkpoints to get the checkpoint nearest the player
                    if(e.onTrack == True):
                        if(len(e.path) == 0):
                            destinationX = 0
                            destinationY = 0
                            minDistance = 999999
                            for k in currentRoom.checkpoints:
                                if(sqrt((player.x-k.x)**2+(player.y-k.y)**2) < minDistance):
                                    minDistance = sqrt((player.x-k.x)**2+(player.y-k.y)**2)
                                    destinationX = k.x
                                    destinationY = k.y
                            start = currentRoom.keyMap[str(e.x)+str(e.y)]
                            end = currentRoom.keyMap[str(destinationX)+str(destinationY)]
                            # A breadth first search to determine shortest path through the checkpoints
                            queue = []
                            previousCheckpoint = [0 for i in range (10)]
                            isVisited = [False for i in range (10)]
                            queue.append(start)
                            isVisited[start] = True
                            while(len(queue) > 0 or isVisited[end] != True):
                                current = queue[0]
                                queue.pop(0)
                                for d in currentRoom.roads[current]:
                                    if(isVisited[d] == False):
                                        isVisited[d] = True
                                        previousCheckpoint[d] = current
                                        queue.append(d)
                            
                            while(end != start):
                                e.path.append(end)
                                end = previousCheckpoint[end]
                        
                        # When the mob reaches the nearest checkpoint to the player, it is allowed to directly go to the player 
                        else:
                            temporaryX,temporaryY = currentRoom.valueMap[e.path[len(e.path)-1]].split()
                            temporaryX = int(temporaryX)
                            temporaryY = int(temporaryY)
                            if(e.x == temporaryX and e.y == temporaryY):
                                e.path.pop(len(e.path)-1)
                                if(len(e.path) == 0):
                                    e.shouldTrack = True
                            else:
                                e.track(temporaryX, temporaryY)    
        
        #Created by Edison#
        #---Ranged Mobs---#
        for e in currentRoom.rangedMobs:
            if (hasControl):
                # Mob fires a bullet
                e.reloadCounter -= 1 
                if (e.reloadCounter <= 0):
                    e.fire(player.x, player.y)
                    e.reloadCounter = e.reloadSpeed
                # Player takes damage for every second it collides with the mob
                e.canHurtPlayer -= 1
                if (e.canHurtPlayer <= 0):
                    if (getCollision(e.collision, player.collision, 0, 0, 0, 0)):
                        player.hp -= 1
                        player.displayDamagedCounter = 5
                        e.canHurtPlayer = 60
            
            for i in e.bullets:
                bulletDeleted = False
                if (hasControl):
                    i.move()
                i.updateCollision(0, 0, 20, 20)
                gameWindow.blit(i.sprites[1], (i.x, i.y))
                # Remove bullet when it collides with a wall or the player
                for w in currentRoom.walls:
                    if (getCollision(i.collision, w.collision, 0, 0, 0, 0)):
                        bulletDeleted = True
                        break
                if (getCollision(player.collision, i.collision, 0, 0, 0, 0)):
                    player.hp -= 1
                    player.displayDamagedCounter = 5
                    bulletDeleted = True
                if (bulletDeleted == True):
                    e.bullets.remove(i)

            # Draw the mob depending on its position relative to the player (left or right)
            if (player.x < e.x):
                gameWindow.blit(e.sprites[0], (e.x, e.y))
                # Glow red for a few frames if damaged
                if (e.displayDamagedCounter > 0):
                    gameWindow.blit(e.sprites[2], (e.x, e.y))
                    e.displayDamagedCounter -= 1
            elif (player.x >= e.x):
                gameWindow.blit(e.sprites[1], (e.x, e.y))
                if (e.displayDamagedCounter > 0):
                    gameWindow.blit(e.sprites[3], (e.x, e.y))
                    e.displayDamagedCounter -= 1

        #---Boss---#
        #=Created by Peter=#
        if currentRoom.boss != "":
            currentRoom.boss.updateCollision(0, 0, 80, 100)
            currentRoom.boss.recoil -= 1
            awake = currentRoom.boss.stun()
            if hasControl:
                #If stun if over or if charge is complete
                if (currentRoom.boss.ifAttack == True and currentRoom.boss.mode == 1 and currentRoom.boss.recoil <= 0) or (awake is True and currentRoom.boss.mode != 1):
                    # Choosing mode
                    currentRoom.boss.mode = random.choice([0,0,0,0,0,3,3,3,3,3,3,3,2,2,1,1])
                    # Different attacks from different modes
                    if currentRoom.boss.ifAttack:
                        if currentRoom.boss.mode == 0:
                            currentRoom.boss.spreadShot()
                        elif currentRoom.boss.mode == 1:
                            currentRoom.boss.calcSpeed(player.x,player.y)
                            currentRoom.boss.ifAttack = False
                        elif currentRoom.boss.mode == 2:
                            currentRoom.boss.mortarFire()
                        elif currentRoom.boss.mode ==3:
                            currentRoom.boss.snipe(player.x,player.y)
                            currentRoom.boss.timer -= 15
                        currentRoom.boss.timer += 30
                    
                    # Boss gets stronger after losing health
                    if currentRoom.boss.hp <= 500:
                        currentRoom.boss.timer -=5

                # Charge move by boss, only continues after collision
                if currentRoom.boss.mode == 1 and currentRoom.boss.ifAttack is False:
                    currentRoom.boss.charge()
                    c = getCollision(currentRoom.boss.collision,[currentRoom.boss.oldX,currentRoom.boss.oldY,currentRoom.boss.oldX,currentRoom.boss.oldY],0,0,currentRoom.boss.speed,0)
                    c_2 = getCollision(currentRoom.boss.collision,player.collision,currentRoom.boss.speed,0,0,0)
                    c_3 = getCollision(currentRoom.boss.collision,player.collision,0,currentRoom.boss.speed,0,0)
                    c_4 = getCollision(currentRoom.boss.collision,player.collision,0,0,0,currentRoom.boss.speed)
                    if c:
                        currentRoom.boss.ifAttack = True
                        currentRoom.boss.recoil = 30
                    if c_2:
                        currentRoom.boss.ifAttack = True
                        currentRoom.boss.recoil = 30
                    if c_3:
                        currentRoom.boss.ifAttack = True
                        currentRoom.boss.recoil = 30 
                    if c_4:
                        currentRoom.boss.ifAttack = True
                        currentRoom.boss.recoil = 30

                # Mortar List      
                for mortarShot in currentRoom.boss.mortarList:
                    expiry = mortarShot.count()
                    playerMortar = getCollision(mortarShot.collision,player.collision,0,0,0,0)
                    if playerMortar and mortarShot.mode is True:
                        player.hp -= 1
                        player.displayDamagedCounter = 5
                        currentRoom.boss.mortarList.remove(mortarShot)
                        continue
                    if mortarShot.mode is True and mortarShot.timer > 0:
                        gameWindow.blit(mortarShot.sprite[1],(mortarShot.x-2,mortarShot.y-2))
                    elif mortarShot.timer > 0 and expiry is True:
                        gameWindow.blit(mortarShot.sprite[0],(mortarShot.x,mortarShot.y))
                    elif expiry is False:
                        currentRoom.boss.mortarList.remove(mortarShot)
                        continue
            # Boss bullet            
            for bullet in currentRoom.boss.bulletList:
                bulletDeleted = False
                if (hasControl):
                    bullet.move()
                    bullet.updateCollision(0, 0, 20, 20)
                gameWindow.blit(bullet.sprites[1],(bullet.x,bullet.y))
                for w in currentRoom.walls:
                    if (getCollision(bullet.collision, w.collision, 0, 0, 0, 0)):
                        bulletDeleted = True
                        break
                if (getCollision(player.collision, bullet.collision, 0, 0, 0, 0)):
                    player.hp -= 1
                    player.displayDamagedCounter = 5
                    bulletDeleted = True
                if (bulletDeleted == True):
                    currentRoom.boss.bulletList.remove(bullet)
            
            if getCollision(currentRoom.boss.collision, player.collision, 0, 0, 0 , 0) is True and currentRoom.boss.canHurt <= 0:
                player.hp -= 1
                player.displayDamagedCounter = 5
                currentRoom.boss.canHurt = 60

            currentRoom.boss.canHurt -= 1
            gameWindow.blit(currentRoom.boss.sprites[0], (currentRoom.boss.x-15, currentRoom.boss.y-15))
            if (currentRoom.boss.displayDamagedCounter > 0):
                # If the boss has been damaged, it glows red
                gameWindow.blit(currentRoom.boss.sprites[1], (currentRoom.boss.x-15, currentRoom.boss.y-15))
                currentRoom.boss.displayDamagedCounter -= 1

        #---Player Shooting---#
        #=Created by Peter=#
        if (hasControl):
            click = pygame.mouse.get_pressed()
            if click[0] == True:
                # Player has a reload timer before they can shoot
                if bulletDelay<=0: 
                    x,y= pygame.mouse.get_pos()
                    # Ensures player is not shooting on himself
                    if not(getCollision(player.collision, [x, y, x, y], 0, 0, 0, 0)):
                        pygame.mixer.Sound.play(playerShot)
                        bulletList.append(projectile(player.x+20,player.y+20,x,y,10,1,1))
                    # Once shot, reset the reload timer
                    bulletDelay = player.reloadSpeed
            bulletDelay-=1

       #---Player Bullets---#
       #=Created by Edison=#
        for bullet in bulletList:
            bulletDeleted = False
            if (hasControl):
                bullet.move()
            bullet.updateCollision(0, 0, 20, 20)
            gameWindow.blit(bullet.sprites[0],(bullet.x, bullet.y))
            # Check if the bullet has hit a wall, any of the mobs, or the boss
            # If so, the bullet will be deleted
            for w in currentRoom.walls:
                if (getCollision(bullet.collision, w.collision, 0, 0, 0, 0)):
                    bulletDeleted = True
                    break
            for e in currentRoom.smallMobs:
                e.updateCollision(-5, -5, 33, 37)
                if (getCollision(bullet.collision, e.collision, 0, 0, 0, 0)):
                    bulletDeleted = True
                    # Subtract health of enemy once hit, as well as set a timer for the red damage effect
                    e.hp -= player.strength
                    e.displayDamagedCounter = 5
                    if (e.hp <= 0):
                        currentRoom.smallMobs.remove(e)
                    break
            for r in currentRoom.rangedMobs:
                if (getCollision(bullet.collision, r.collision, 0, 0, 0, 0)):
                    bulletDeleted = True
                    r.hp -= player.strength
                    r.displayDamagedCounter = 5
                    if (r.hp <= 0):
                        currentRoom.rangedMobs.remove(r)
                    break
            if (currentRoom.boss != ""):
                if getCollision(bullet.collision, currentRoom.boss.collision, 0, 0, 0, 0):
                    bulletDeleted = True
                    currentRoom.boss.hp -= player.strength
                    currentRoom.boss.displayDamagedCounter = 5
                
            if (bulletDeleted == True):
                bulletList.remove(bullet)
                
        #---Player---#
        #=Created by Edison=#
        player.updateCollision(0, 0, 45, 45)
        # If the player is alive, draw the player sprite depending on the direction the player is facing
        if (player.hp > 0):
            if (player.directionX == "right"):
                gameWindow.blit(player.sprites[0], (player.x, player.y))
                # If the player has been damaged, the player will glow red for a few frames
                if (player.displayDamagedCounter > 0):
                    gameWindow.blit(player.sprites[2], (player.x, player.y))
                    player.displayDamagedCounter -= 1
            elif (player.directionX == "left"):
                gameWindow.blit(player.sprites[1], (player.x, player.y))
                if (player.displayDamagedCounter > 0):
                    gameWindow.blit(player.sprites[3], (player.x, player.y))
                    player.displayDamagedCounter -= 1
    
        #=Created by Edison=#
        if (hasControl):
            # Movement of player Up, Down, Left and Right using WASD controls
            if (keys[pygame.K_d]): # Right
                canMove = True
                # Check if the player will run into a wall if the player moves any further in the direction (right)
                for i in currentRoom.walls:
                    if (getCollision(player.collision, i.collision, 0, player.speed, 0, 0)):
                        # If the player is amount to run into a wall, snap their position to the edge of the wall and then forbid further movement
                        player.x = i.collision[0] - 45
                        canMove = False
                if canMove:
                    player.directionX = "right"
                    player.move(player.speed, 0)
                    player.updateCollision(0, 0, 45, 45)

            if (keys[pygame.K_a]): # Left
                canMove = True
                for i in currentRoom.walls:
                    if (getCollision(player.collision, i.collision, player.speed, 0, 0, 0)):
                        player.x = i.collision[2]
                        canMove = False
                if canMove:
                    player.directionX = "left"
                    player.move(0 - player.speed, 0)
                    player.updateCollision(0, 0, 45, 45)

            if (keys[pygame.K_s]): # Down
                canMove = True
                for i in currentRoom.walls:
                    if (getCollision(player.collision, i.collision, 0, 0, 0, player.speed)):
                        player.y = i.collision[1] - 45
                        canMove = False
                if canMove:
                    player.move(0, player.speed)
                    player.updateCollision(0, 0, 45, 45)

            if (keys[pygame.K_w]): # Up
                canMove = True
                for i in currentRoom.walls:
                    if (getCollision(player.collision, i.collision, 0, 0, player.speed, 0)):
                        player.y = i.collision[3]
                        canMove = False
                if canMove:
                    player.move(0, 0 - player.speed)
                    player.updateCollision(0, 0, 45, 45)

        # If the player walks through the top door, the player teleports to the bottom door and vice versa
        if (player.x < -20):
            player.x = 680
        elif (player.x > 680):
            player.x = -20
        # If the player walks through the left door, the player teleports to the right door and vice versa
        if (player.y < -20):
            player.y = 680
        elif (player.y > 680):
            player.y = -20

        #---Boss and Player Health Bars---#
        playerHealth = playerHealthBar(50, 640, player.hp)
        playerHealth.drawHealth()
        
        if (currentRoom.boss != ""):
            bossHealth = bossHealthBar(350, 60, currentRoom.boss.hp, 1500) 
            bossHealth.drawHealth(300)

        #=Created by Edison=#
        # If there are no remaining mobs in the room (and it is not the boss room), the player can access the teleporter
        if (len(currentRoom.rangedMobs) + len(currentRoom.smallMobs) == 0 and level < 10):
            teleporter.stasis = True
        if (teleporter.stasis == True):
            gameWindow.blit(teleporter.sprite,(teleporter.x,teleporter.y))
            # Once the player walks on the teleporter, the player enters the next level
            if (getCollision(player.collision, teleporter.collision, 0, 0, 0, 0)):
                pygame.mixer.Sound.play(teleport)
                level += 1
                # Boss appears on level 10
                if (level < 10):
                    # There is a 2 in 5 chance of getting a type 2 room (two walls in the middle)
                    currentRoom = room(0, 0, level, random.choice([2, 2, 1, 1, 1]))
                    # Amount of mobs will increase depending on the level
                    currentRoom.generateMobs(level, 1, player)
                    currentRoom.generateMobs(round(level/2), 2, player)
                    currentRoom.generateItems(round((10+level)/2),player) 
                elif (level >= 10):
                    currentRoom = room(0, 0, level, 1)
                    currentRoom.generateBoss(300)
                teleporter.stasis = False

        #=Created by Edison=#
        if (currentRoom.boss != ""):
            # Generate collectibles every few seconds in the boss room
            currentRoom.collectibleTimer -= 1
            if (currentRoom.collectibleTimer <= 0):
                currentRoom.generateItems(3, player)
                currentRoom.collectibleTimer = currentRoom.collectibleSpawn
            if (currentRoom.boss.hp <= 0):
                if bossSound == False:
                    pygame.mixer.Sound.play(bossDeath)
                    bossSound = True
                # Prevent movement during the end screen
                hasControl = False
                pygame.mixer.music.stop()
                gameWindow.blit(winScreen, (0, 0))
                # Will break out of the current game and reset to the beginning
                if (keys[pygame.K_r]):
                    inPlay = False
        
        #=Created by Edison=#
        # Player Death
        if (player.hp <= 0):
            # Ensure that death sound is only played once
            if player.hp == 0:
                pygame.mixer.Sound.play(playerDeath)
                player.hp-=1
            # Loop through a series of images to animate the player's death
            if (playerDeathLoop < 13): 
                gameWindow.blit(player.sprites[round(playerDeathLoop)], (player.x, player.y))
                playerDeathLoop += 0.1
            elif (playerDeathLoop >= 13):
                pygame.mixer.music.stop()
                gameWindow.blit(deathScreen, (0, 0))

            # Prevent movement during the end screen
            hasControl = False
            if (keys[pygame.K_r]):
                # Will break out of the current game and reset to the beginning
                inPlay = False
                switchMusic(1)

        # Break out of both the current game and any resets
        if (keys[pygame.K_ESCAPE]):
            inPlay = False 
            restart = False

        pygame.display.update()
pygame.quit()
