# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 20:20:06 2020

@author: wangwil
"""

import pygame
from time import sleep
import sys
import math
import random
from copy import copy

def distance(x1,y1,x2,y2):
    return math.sqrt( (x1-x2)**2 + (y1-y2)**2 )

def rot_center(surf, angle, x, y):
    
    rotated_image = pygame.transform.rotate(surf, angle)
    new_rect = rotated_image.get_rect(center = surf.get_rect(center = (x, y)).center)

    return rotated_image #, new_rect

class Asteroid:
    def __init__(self, heading, resolution, surf_asteroid):
        startX = int(resolution[0]/2)
        startY = int(resolution[1]/2)
        self.resolution = resolution
        self.speed = random.randint(2,7)
        self.heading = random.random() * 2 * math.pi
        self.size = random.randint(15, 25)
        self.rect = pygame.Rect(startX, startY, self.size, self.size)
        self.alive = True
        self.destroyedbyplayer = False
        self.setStartPos()
        self.surf_asteroid = copy(surf_asteroid)
        self.surf_asteroid = pygame.transform.scale(self.surf_asteroid, (self.size, self.size))
        
    def setStartPos(self):
        number = random.randint(1, 4)
        if number == 1:
            #left edge
            x = 0
            y = random.randint(0, self.resolution[1])
            heading = (random.random() * math.pi/3) * 2 - math.pi/3
        elif number == 2:
            #right edge
            x = self.resolution[0]
            y = random.randint(0, self.resolution[1])
            heading = (random.random() * (math.pi/180)*120) + (math.pi/180)*120
        elif number == 3:
            #top edge
            x = random.randint(0, self.resolution[0])
            y = 0
            heading = (random.random() * (math.pi/180)*120) + (math.pi/180)*30
        elif number == 4:
            #bottom edge
            y = self.resolution[1]
            x = random.randint(0, self.resolution[0])
            heading = (random.random() * (math.pi/180)*120) + (math.pi/180)*210
        
        self.heading = heading
        self.rect.centerx = x
        self.rect.centery = y
        
        
    def update(self, playerRef):
        self.rect.centerx += self.speed * math.cos(self.heading)
        self.rect.centery += self.speed * math.sin(self.heading)
        
        if self.rect.centerx > self.resolution[0] or self.rect.centerx < 0 or self.rect.centery > self.resolution[1] or self.rect.centery < 0:
            self.alive = False
            
        # Check collision with the player
        dis = distance(playerRef.x, playerRef.y, self.rect.centerx, self.rect.centery)
        if dis <= ((self.size*0.7) + playerRef.radius):
            playerRef.takeHit()
            print("COLLOSION")
            self.alive = False
            
    def render(self, surf):
        #pygame.draw.rect(surf, (255,0,255), self.rect)
        surf.blit(self.surf_asteroid,
                  (self.rect.centerx-self.size // 2, self.rect.centery-self.size //2))
class Projectile:
    def __init__(self, x, y, heading, resolution):
        self.length = 5
        self.color = (255,255,255)
        self.x = x
        self.y = y
        self.heading = heading
        self.speed = 20
        self.alive = True
        self.resolution = resolution
        
    def update(self, asteroidsRef):
        self.x += self.speed * math.cos(self.heading)
        self.y += self.speed * math.sin(self.heading)
        
        # Check if projectile has moved out of the screen
        if self.x > self.resolution[0] or self.x < 0 or self.y > self.resolution[1] or self.y < 0:
            self.alive = False
        for ast in asteroidsRef:
            dis = distance(self.x, self.y, ast.rect.centerx, ast.rect.centery)
            if dis <= (ast.size*0.7):
                ast.alive = False
                ast.destroyedbyplayer = True
    def render(self, surf):
        start_pos = (self.x,self.y)
        end_pos = (self.x + self.length * math.cos(self.heading), 
                   self.y + self.length * math.sin(self.heading)
                   )
        pygame.draw.line(surf, self.color, start_pos, end_pos, 2)
        
class Player:
    def __init__(self, resolution):
        self.resolution = resolution
        self.color = (255,0,0)
        self.x = self.resolution[0] // 2
        self.y = self.resolution[1] // 2
        self.heading = math.radians(270)
        self.radius = 8
        self.rotation_speed = 0.15
        self.acc_amount = 0.25
        self.dcc_amount = 0.25/3
        self.move_speed = 0
        self.max_move_speed = 10
        self.lives = 5
        self.alive = True
        self.ship = pygame.image.load('gameship.png')
        self.height = int(self.resolution[1] * 0.1)
        self.width = int(self.height * 0.57)
        self.ship = pygame.transform.scale(self.ship, (self.width, self.height))

    def update(self):
        self.move_speed -= self.dcc_amount
        if self.move_speed <= 0:
            self.move_speed = 0
        
        self.x += self.move_speed * math.cos(self.heading)
        self.y += self.move_speed * math.sin(self.heading)
        #self.x = int(self.x)
        #self.y = int(self.y)
        
        #right border 
        if self.x > self.resolution[0] - self.radius:
            self.x = self.resolution[0] - self.radius
            self.heading = math.pi - self.heading
        #left border
        elif self.x < self.radius:
            self.x = self.radius
            self.heading = math.pi - self.heading
            
        #bottom
        if self.y > self.resolution[1] - self.radius:
            self.y = self.resolution[1] - self.radius
            self.heading = math.pi*2 - self.heading
        #top
        elif self.y < self.radius:
            self.y = self.radius
            self.heading = math.pi*2 - self.heading
            
    def render(self, surf):
        rotated_ship = rot_center(self.ship, math.degrees(-self.heading)-90, 
                               self.x-self.width/2, self.y-self.height/2)
        g_w, g_h = rotated_ship.get_size()
        surf.blit(rotated_ship,
                  (int(self.x - g_w//2), int(self.y - g_h//2)))
        
        #self.ship = pygame.transform.rotate(self.ship, math.degrees(self.heading))
        #pygame.draw.circle(surf,self.color, 
                             #  (int(self.x), int(self.y)), self.radius)
        start_pos = (self.x,self.y)
        end_pos = (self.x + self.radius * math.cos(self.heading), 
                   self.y + self.radius * math.sin(self.heading)
                   )
        pygame.draw.line(surf, (255,255,255), start_pos, end_pos)
    
    def dead(self):
        self.alive = False
        
    def takeHit(self):
        self.lives -= 1
        if self.lives <= 0:
            self.dead()
            
    def rotateCW(self):
        self.heading += self.rotation_speed
    
    def rotateCCW(self):
        self.heading -= self.rotation_speed
        
    def moveForward(self):
        self.move_speed += self.acc_amount
        if self.move_speed >= self.max_move_speed:
            self.move_speed = self.max_move_speed
        
        
    
    def moveBackward(self):
        self.x -= self.move_speed * math.cos(self.heading)
        self.y -= self.move_speed * math.sin(self.heading)
        #self.x = int(self.x)
        #self.y = int(self.y)
        
        if self.x > self.resolution[0] - self.radius:
            self.x = self.resolution[0] - self.radius
        elif self.x < self.radius:
            self.x = self.radius
            
        if self.y > self.resolution[1] - self.radius:
            self.y = self.resolution[1] - self.radius
        elif self.y < self.radius:
            self.y = self.radius
            
class Game:
    def __init__(self):
        self.resolution = (500,500)
        self.screen = pygame.display.set_mode(self.resolution)
        self.player = Player(self.resolution)
        self.projectiles = []
        self.asteroids = []
        self.to_delete_projectiles = []
        self.to_delete_asteroids = []
        pygame.font.init()
        self.font = pygame.font.SysFont("comicsansms", 50)
        self.scorefont = pygame.font.SysFont("comicsansms", 25)
        self.score = 0
        #creating text and surfaces
        self.gameoverscreen = self.font.render("GAME OVER G", True, (255,255,255))
        self.scoreboard = self.scorefont.render("SCORE: " + str(self.score), True, (255,255,255))
        self.asteroid_surf = pygame.image.load('asteroid.png')
        
    def handleInput(self):
        for event in pygame.event.get():
               if event.type == pygame.QUIT:
                   print("Bye bye.")
                   sleep(2)
                   sys.exit(0)
               
               if event.type == pygame.KEYDOWN:
                   #print("A key a pressed")
                   if event.key == pygame.K_w:
                       self.flagW = True
                       print("Key `w` was pressed.")
                   elif event.key == pygame.K_a:
                       self.flagA = True
                       print("Key `a` was pressed.")
                   elif event.key == pygame.K_s:
                       self.flagS = True
                       print("Key `s` was pressed.")
                   elif event.key == pygame.K_d:
                       self.flagD = True
                       print("Key `d` was pressed.")
                   elif event.key == pygame.K_SPACE:
                       projectile = Projectile(self.player.x, self.player.y, self.player.heading, self.resolution)
                       self.projectiles.append(projectile)
               if event.type == pygame.KEYUP:
                   if event.key == pygame.K_w:
                       self.flagW = False
                       print('Key `w` was released.')
                   if event.key == pygame.K_a:
                       self.flagA = False
                       print('Key `w` was released.')
                   if event.key == pygame.K_s:
                       self.flagS = False
                       print('Key `w` was released.')
                   if event.key == pygame.K_d:
                       self.flagD = False
                       print('Key `w` was released.')
           
        if self.flagW:
            self.player.moveForward()
        if self.flagA:
            self.player.rotateCCW()
        if self.flagS:
            self.player.moveBackward()
        if self.flagD:
            self.player.rotateCW()
            
    def garbageCollection(self):
        # Delete
        for i in self.to_delete_projectiles[::-1]:
            del self.projectiles[i]
            
        self.to_delete_projectiles = []
        
        for i in self.to_delete_asteroids[::-1]:
            if self.asteroids[i].destroyedbyplayer:
                self.score += 1
                print(self.score)
                self.scoreboard = self.scorefont.render("SCORE: " + str(self.score),
                                                        True, (255,255,255))
                
            del self.asteroids[i]
            
        self.to_delete_asteroids = []
    def run(self):
        iters = 0
        self.flagW = False
        self.flagA = False
        self.flagS = False
        self.flagD = False
        deathiter = None
        fps = 30
        
        while True:
            # Blank the screen
            self.screen.fill((0, 0, 0))
        
            if not self.player.alive:
                g_w,g_h = self.gameoverscreen.get_size()
                
                #putting gameoverscreen on screen
                self.screen.blit(self.gameoverscreen, 
                                 (self.resolution[0]//2 - g_w//2,
                                  self.resolution[1]//2 - g_h//2))
                
            
            # Draw everything on the screen
            self.player.render(self.screen)
            
            
            i = 0
            for proj in self.projectiles:
                proj.render(self.screen)
                proj.update(self.asteroids)
                if not proj.alive:
                    self.to_delete_projectiles.append(i)
                i += 1
            
            i = 0
            #drawing and updating the asteroids
            for ast in self.asteroids:
                ast.render(self.screen)
                ast.update(self.player)
                if not ast.alive:
                    self.to_delete_asteroids.append(i)
                i += 1
                
            self.screen.blit(self.scoreboard,
                             (0,0))
            
            # Deal with input
            if self.player.alive:
                self.handleInput()      
            
            self.player.update()
            # Display the screen
            pygame.display.flip()
            
            # Sleep for a bit
            sleep(1/fps)
            
            self.garbageCollection()
        
            iters += 1
            if iters % 15 == 0 and self.player.alive == True:
                self.asteroids.append(Asteroid(math.radians(180), self.resolution, self.asteroid_surf))
                
            if not self.player.alive and deathiter == None:
                deathiter = iters
            
            #wait one second and finish the game
            if self.player.alive == False and iters == (deathiter + fps*3):
                break

while True:
    game = Game()
    game.run()
    print("game finished")

