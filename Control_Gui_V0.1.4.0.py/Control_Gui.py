
from ibCom import *
import random
import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg
from pygame.locals import *
import pygame
import sys
from math import floor, ceil
import time
from datetime import datetime
from operator import xor
from copy import copy
import os
import matplotlib.dates as mdates
import smtplib
import ssl
import json


from lakeshore import Model372, generic_instrument
import csv


import matplotlib
matplotlib.use('Agg')


pygame.init()
pygame.font.init()
pRatio = True if pygame.display.Info(
).current_w > pygame.display.Info().current_h else False
bigfont = pygame.font.Font(pygame.font.get_default_font(), int(
    0.025*pygame.display.Info().current_h if pRatio else 0.02*pygame.display.Info().current_w))
midfont = pygame.font.Font(pygame.font.get_default_font(), int(
    0.0185*pygame.display.Info().current_h if pRatio else 0.015*pygame.display.Info().current_w))
smallfont = pygame.font.Font(pygame.font.get_default_font(), int(
    0.0123*pygame.display.Info().current_h if pRatio else 0.01*pygame.display.Info().current_w))


def isFloat(str):
    try:
        float(str)
        return True
    except ValueError:
        return False


def cleanFloatString(str):
    newstr = ''
    for char in str:
        if char.isdigit() or char == '.':
            newstr += char
    return newstr


class button:
    def __init__(self, screen, text, pos, size, colorIdle, colorHeld, id=None, fontsize='mid'):
        if id == None:
            id = text
        self.text = text
        self.pos = pos
        self.screen = screen
        self.size = size
        self.color = colorIdle
        self.colorIdle = colorIdle
        self.colorHeld = colorHeld
        self.id = id
        self.font = smallfont if fontsize == 'small' else midfont if fontsize == 'mid' else bigfont

    def checkClick(self, pos):
        hit = False
        if pos[0] > self.pos[0] and pos[0] < self.pos[0] + self.size[0] and pos[1] > self.pos[1] and pos[1] < self.pos[1] + self.size[1]:
            hit = True

        return hit

    def isHeld(self):
        self.color = self.colorHeld

    def isIdle(self):
        self.color = self.colorIdle

    def draw(self):
        r = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        pygame.draw.rect(self.screen, self.color, r)
        pygame.draw.rect(self.screen, (0, 0, 0), r, width=2)
        label = self.font.render(self.text, True, (0, 0, 0))
        center = r.center
        self.screen.blit(
            label, (center[0]-label.get_rect().w/2, center[1] - label.get_rect().h/2))


class textbox:
    def __init__(self, screen, default, pos, size, color, id=None, fontsize='mid', active=False, postfix=None):
        if id == None:
            id = default
        self.text = default
        self.pos = pos
        self.color = color
        self.id = id
        self.size = size
        self.font = smallfont if fontsize == 'small' else midfont if fontsize == 'mid' else bigfont
        self.active = active
        self.curserPos = self.pos[0]
        self.screen = screen
        self.activePos = 0
        self.postfix = postfix

    def checkClick(self, pos):
        hit = False
        if pos[0] > self.pos[0] and pos[0] < self.pos[0] + self.size[0] and pos[1] > self.pos[1] and pos[1] < self.pos[1] + self.size[1]:
            center = pygame.Rect(
                self.pos[0], self.pos[1], self.size[0], self.size[1]).center[0]
            self.curserPos = center
            if self.text:
                fSize = self.font.size(self.text)[0]

                left = center - fSize/2
                clickpos = left + fSize
                self.activePos = len(self.text)-1
                if pos[0] < clickpos:

                    for ii in range(len(self.text)-1, -1, -1):
                        c = self.text[ii]
                        clickpos -= self.font.size(c)[0]
                        self.activePos -= 1
                        if pos[0] > clickpos:
                            clickpos += self.font.size(c)[0]
                            self.activePos += 1
                            break
                self.curserPos = clickpos
            self.active = True
            hit = True

        if not hit:
            if self.postfix != None and self.active:
                self.setText(self.text + self.postfix)
            self.active = False
        return hit

    def setText(self, text):
        self.text = text
        self.activePos = -1

    def draw(self):
        r = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        pygame.draw.rect(self.screen, self.color, r)
        pygame.draw.rect(self.screen, (0, 0, 0), r, width=2)
        label = self.font.render(self.text, True, (0, 0, 0))
        center = r.center
        self.screen.blit(
            label, (center[0]-label.get_rect().w/2, center[1] - label.get_rect().h/2))
        if self.active:
            zeroPos = r.center[0] - self.font.size(self.text)[0]/2
            pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(
                self.curserPos, self.pos[1], 2, self.size[1]))

    def type(self, key, uni, numOnly=False):
        if self.active:
            if ((not numOnly) and uni and ord(uni) >= 32 and ord(uni) <= 126) or (numOnly and (uni.isdigit() or uni == '.')):
                self.text = self.text[:self.activePos+1] + \
                    uni + self.text[self.activePos+1:]
                self.activePos += 1
                fSize = self.font.size(self.text)[0]
                center = pygame.Rect(
                    self.pos[0], self.pos[1], self.size[0], self.size[1]).center[0]
                left = center - fSize/2
                self.curserPos = left
                for ii in range(self.activePos+1):
                    self.curserPos += self.font.size(self.text[ii])[0]
            elif key == pygame.K_BACKSPACE and self.text and self.activePos >= 0:
                textList = [ii for ii in self.text]
                del textList[self.activePos]
                self.text = self.text[:self.activePos] + \
                    self.text[self.activePos + 1:]
                self.activePos -= 1
                # for ii in textList:
                # self.text += ii

                fSize = self.font.size(self.text)[0]
                center = pygame.Rect(
                    self.pos[0], self.pos[1], self.size[0], self.size[1]).center[0]
                left = center - fSize/2
                self.curserPos = left
                for ii in range(self.activePos+1):
                    self.curserPos += self.font.size(self.text[ii])[0]
            elif key == pygame.K_RETURN:
                self.active = False
            elif key == pygame.K_RIGHT and self.activePos < len(self.text) - 1:
                self.activePos += 1
                fSize = self.font.size(self.text)[0]
                center = pygame.Rect(
                    self.pos[0], self.pos[1], self.size[0], self.size[1]).center[0]
                left = center - fSize/2
                self.curserPos = left
                for ii in range(self.activePos+1):
                    self.curserPos += self.font.size(self.text[ii])[0]
            elif key == pygame.K_LEFT and self.activePos > -1:
                self.activePos -= 1
                fSize = self.font.size(self.text)[0]
                center = pygame.Rect(
                    self.pos[0], self.pos[1], self.size[0], self.size[1]).center[0]
                left = center - fSize/2
                self.curserPos = left
                for ii in range(self.activePos+1):
                    self.curserPos += self.font.size(self.text[ii])[0]


class dropdown:
    def __init__(self, screen, label, pos, size, color, id=None, fontsize='mid', options=[], open=False):
        if id == None:
            id = label
        self.label = label
        self.text = label
        self.options = options
        self.pos = pos
        self.size = size
        self.color = color
        self.fontsize = fontsize
        self.open = open
        self.screen = screen
        self.id = id

    def checkClick(self, pos):
        hit = False
        if not self.open:
            if pos[0] > self.pos[0] and pos[0] < self.pos[0] + self.size[0] and pos[1] > self.pos[1] and pos[1] < self.pos[1] + self.size[1]:
                hit = True

        else:
            if pos[0] > self.pos[0] and pos[0] < self.pos[0] + self.size[0] and pos[1] > self.pos[1] + self.size[1] and pos[1] < self.pos[1] + (len(self.options)+1)*(self.size[1]):
                hit = True
        if hit and self.open and self.options:
            self.text = self.options[floor(
                (pos[1]-self.pos[1])/self.size[1])-1]
        self.open = not self.open if hit else False
        return hit

    def draw(self):
        rects = [pygame.Rect(self.pos[0], self.pos[1] + self.size[1] * ii,
                             self.size[0], self.size[1]) for ii in range(len(self.options)+1)]
        pygame.draw.rect(self.screen, self.color, rects[0])
        pygame.draw.rect(self.screen, (0, 0, 0), rects[0], width=2)
        font = smallfont if self.fontsize == 'small' else midfont if self.fontsize == 'mid' else bigfont
        label = font.render(self.text, True, (0, 0, 0))
        center = rects[0].center
        self.screen.blit(
            label, (center[0]-label.get_rect().w/2, center[1] - label.get_rect().h/2))
        if self.open:
            for ii in range(len(self.options)):
                pygame.draw.rect(self.screen, self.color, rects[ii+1])
                pygame.draw.rect(self.screen, (0, 0, 0), rects[ii+1], width=2)
                label = font.render(self.options[ii], True, (0, 0, 0))
                center = rects[ii + 1].center
                self.screen.blit(
                    label, (center[0]-label.get_rect().w/2, center[1] - label.get_rect().h/2))

    def addOptions(self, option):
        self.options.append(option)

    def setOptions(self, options):
        self.options = options


class TopEdge:
    def __init__(self, screen, buttons={}, labels={}, dropdowns={}):
        self.screen = screen
        x, y = screen.get_size()
        self.height = y/10
        self.width = x
        self.bgColor = (150, 150, 150)
        self.buttons = buttons
        self.labels = labels
        self.dropdowns = dropdowns

    def draw(self):
        pygame.draw.rect(self.screen, self.bgColor,
                         pygame.Rect(0, 0, self.width, self.height))
        for kk in self.buttons:
            ii = self.buttons[kk]
            font = smallfont if ii[3] == 'small' else midfont if ii[3] == 'mid' else bigfont
            pygame.draw.rect(self.screen, ii[1], pygame.Rect(
                ii[0][0], ii[0][1], ii[0][2], ii[0][3]))
            pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(
                ii[0][0], ii[0][1], ii[0][2], ii[0][3]), width=2)
            buttonLabel = font.render(ii[2], True, (0, 0, 0))
            center = pygame.Rect(ii[0][0], ii[0][1], ii[0][2], ii[0][3]).center
            self.screen.blit(font.render(ii[2], True, (0, 0, 0)), (
                center[0]-buttonLabel.get_rect().w/2, center[1]-buttonLabel.get_rect().h/2))
        for kk in self.labels:
            ii = self.labels[kk]
            font = smallfont if ii[3] == 'small' else midfont if ii[3] == 'mid' else bigfont
            buttonLabel = font.render(ii[2], True, (0, 0, 0))
            self.screen.blit(font.render(
                ii[2], True, (0, 0, 0)), (ii[0][0], ii[0][1]))

    def addLabel(self, text, pos, color, id=None, fontsize='big'):
        if id == None:
            id = text
        self.labels[id] = [[pos[0], pos[1]], color, text, fontsize]

    def checkClick(self, pos):
        hitEdge = False
        if pos[1] <= self.height:
            hitEdge = True
        return hitEdge


class LeftEdge:
    def __init__(self, screen, labels={}):
        self.screen = screen
        x, y = screen.get_size()
        self.height = y
        self.width = x/5
        self.labels = labels
        self.bgColor = (150, 150, 150)

    def draw(self):
        pygame.draw.rect(self.screen, self.bgColor, pygame.Rect(
            0, self.screen.get_size()[1]/10, self.width, self.height))
        pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(
            0, self.screen.get_size()[1]/10, self.width, self.height), width=2)
        for kk in self.labels:
            ii = self.labels[kk]
            font = smallfont if ii[3] == 'small' else midfont if ii[3] == 'mid' else bigfont
            label = font.render(ii[2], True, (0, 0, 0))
            self.screen.blit(label, (ii[0][0], ii[0][1]))

    def addLabel(self, text, pos, color, id=None, fontsize='big'):
        if id == None:
            id = text
        self.labels[id] = [[pos[0], pos[1]], color, text, fontsize]


class Edge:
    def __init__(self, screen, pos, size, color, drawBG=False, labels={}):
        self.screen = screen
        x, y = screen.get_size()
        self.height = y*size[1]
        self.width = x*size[0]
        self.labels = labels
        self.color = color
        self.pos = (x * pos[0], y * pos[1])
        self.drawBG = drawBG

    def draw(self):
        pygame.draw.rect(self.screen, self.color, pygame.Rect(
            self.pos[0], self.pos[1], self.width, self.height))
        if self.drawBG:
            pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(
                self.pos[0], self.pos[1], self.width, self.height), width=2)
        for kk in self.labels:
            ii = self.labels[kk]
            font = smallfont if ii[3] == 'small' else midfont if ii[3] == 'mid' else bigfont
            label = font.render(ii[2], True, (0, 0, 0))
            self.screen.blit(label, (ii[0][0], ii[0][1]))

    def addLabel(self, text, pos, color, id=None, fontsize='big'):
        if id == None:
            id = text
        self.labels[id] = [[pos[0], pos[1]], color, text, fontsize]

    def removeLabel(self, id):
        del self.labels[id]

    def checkClick(self, pos):
        hitEdge = False
        if pos[0] > self.pos[0] and pos[0] < self.pos[0] + self.width and pos[1] > self.pos[1] and pos[1] < self.height + self.pos[1]:
            hitEdge = True
        return hitEdge

    def updateLabel(self, id, text):
        self.labels[id][2] = text


class Background:
    def __init__(self, screen, image, vblocks={}, hblocks={}, cblocks={}, pos=[0, 0]):
        self.screen = screen
        self.baseImage = pygame.image.load(image)
        self.bgImage = pygame.image.load(image)
        self.vblocks = vblocks
        self.hblocks = hblocks
        self.cblocks = cblocks
        self.pos = pos
        self.zoom = 1

    def draw(self):
        # self.screen.blit(self.bgImage, self.pos)
        for kk in self.vblocks:
            ii = self.vblocks[kk]
            pygame.draw.rect(self.screen, ii[1], pygame.Rect(
                self.pos[0]+self.zoom*ii[0][0], self.pos[1]+self.zoom*ii[0][1], 30*self.zoom, 50*self.zoom))
        for kk in self.hblocks:
            ii = self.hblocks[kk]
            pygame.draw.rect(self.screen, ii[1], pygame.Rect(
                self.pos[0]+self.zoom*ii[0][0], self.pos[1]+self.zoom*ii[0][1], 50*self.zoom, 30*self.zoom))
        for kk in self.cblocks:
            ii = self.cblocks[kk]
            pygame.draw.circle(self.screen, ii[1], (
                self.pos[0]+self.zoom*ii[0][0], self.pos[1]+self.zoom*ii[0][1]), 40*self.zoom)
        self.screen.blit(self.bgImage, self.pos)

    def move(self, x, y):
        self.pos[0] += x
        self.pos[1] += y

    def scale(self, size):
        self.zoom += size/50
        self.bgImage = pygame.transform.rotozoom(self.baseImage, 0, self.zoom)

    def addBlock(self, pos, name='', type='v'):
        if type == 'v':
            self.vblocks[name] = ([pos, (255, 0, 0)])
        if type == 'h':
            self.hblocks[name] = ([pos, (255, 0, 0)])
        if type == 'c':
            self.cblocks[name] = ([pos, (255, 0, 0)])

    def checkClick(self, pos, newColor=None):
        # print(f"{(pos[0] - self.pos[0])/(self.zoom)}, {(pos[1] - self.pos[1])/(self.zoom)}")
        for kk in self.vblocks:
            ii = self.vblocks[kk]
            oldColor = ii[1]
            if pos[0] >= self.pos[0]+self.zoom*ii[0][0] and pos[0] <= self.pos[0]+self.zoom*ii[0][0] + 30 * self.zoom and\
                    pos[1] >= self.pos[1]+self.zoom * ii[0][1] and pos[1] <= self.pos[1]+self.zoom * ii[0][1] + 50 * self.zoom:
                if newColor != None:
                    ii[1] = newColor
                return kk, oldColor
        for kk in self.hblocks:
            ii = self.hblocks[kk]
            oldColor = ii[1]
            if pos[0] >= self.pos[0]+self.zoom*ii[0][0] and pos[0] <= self.pos[0]+self.zoom*ii[0][0] + 50 * self.zoom and\
                    pos[1] >= self.pos[1]+self.zoom * ii[0][1] and pos[1] <= self.pos[1]+self.zoom * ii[0][1] + 30 * self.zoom:
                if newColor != None:
                    ii[1] = newColor
                return kk, oldColor
        for kk in self.cblocks:
            ii = self.cblocks[kk]
            oldColor = ii[1]
            if pos[0] >= self.pos[0]+self.zoom*ii[0][0] - 40*self.zoom and pos[0] <= self.pos[0]+self.zoom*ii[0][0] + 40 * self.zoom and\
                    pos[1] >= self.pos[1]+self.zoom * ii[0][1] - 40*self.zoom and pos[1] <= self.pos[1]+self.zoom * ii[0][1] + 40 * self.zoom:
                if newColor != None:
                    ii[1] = newColor
                return kk, oldColor

    def changeColor(self, item, color):
        if item in self.vblocks:
            self.vblocks[item][1] = color
            return
        if item in self.hblocks:
            self.hblocks[item][1] = color
            return
        if item in self.cblocks:
            self.cblocks[item][1] = color
            return

    def setZoom(self, zoom):
        self.zoom = zoom
        self.bgImage = pygame.transform.rotozoom(self.baseImage, 0, self.zoom)


def main():

    with open("System_Config.json") as sconf:
        systemConfig = json.load(sconf)

    pm1Manager = opsManager()
    pm1Manager.id = 'PM1'
    pm2Manager = opsManager()
    pm2Manager.id = 'PM2'
    valveManager = valveCom()
    lakeshoreManager = lakeShoreCom(systemConfig["Temperature_Sensors"])
    pressureManager = pressureCom()

    flowValue = "N/A"

    timers = systemConfig["Timers"]

    emailManager = email(systemConfig["Email_List"], timers["Email_Timer"])

    plotWithoutLogScale = systemConfig["Focus_Plot"]

    pm1Manager.mainTimer = timers["Turbo_Com_Timer"]
    pm2Manager.mainTimer = timers["Turbo_Com_Timer"]
    valveManager.updateTime = timers["Valve_Update_Timer"]
    logTimer = 0
    logTime = timers["Log_Timer"]
    flowTimer = 0
    flowTime = timers["Flow_Readout_Timer"]
    pressureManager.updateTime = timers["Pressure_Readout_Timer"]
    lakeshoreManager.updateTime = timers["Temperature_Readout_Timer"]
    emailManager.updateTime = timers["Email_Timer"]
    configUpdateTimer = 0
    configUpdateTime = timers["System_Config_Update_Timer"]

    draggingPlotTime = timers["Dragging_Plot_Timer"]

    sensorNames = list(systemConfig["Temperature_Sensors"].keys())
    sensorNum = len(systemConfig["Temperature_Sensors"])

    tVals = [[] for ii in range(sensorNum)]
    times = []
    graphView = False
    screenWidth = pygame.display.Info().current_w
    screenHeight = pygame.display.Info().current_h-60
    fig = plt.figure(figsize=[ceil(0.5*screenWidth) /
                     100, ceil(0.75*screenHeight)/100], dpi=100)
    ax = fig.gca()
    for ii in tVals:
        ax.plot(times, ii)

    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()

    # size = (800,800)
    graphImage = pygame.image.fromstring(
        raw_data, (ceil(0.5*screenWidth), ceil(0.75*screenHeight)), "RGB")

    screen = pygame.display.set_mode((screenWidth, screenHeight))
    # background = Background(screen, 'Icebox-pneumatic-valves_v2_all_off_tp.png')
    background = Background(
        screen, 'System_1-pneumatic-valves_v3_for_software.png')
    background.setZoom(0.75*screenHeight/1380)

    # background.addBlock((1055,160), 'v1')
    # background.addBlock((1170,160), 'v2')
    # background.addBlock((1055,500), 'v3')
    # background.addBlock((1170,500), 'v4')
    # background.addBlock((1112,670), 'v23')
    # background.addBlock((1112,955), 'v10')
    # background.addBlock((150,955), 'v18')
    # background.addBlock((150,670), 'v26')
    # background.addBlock((260,955), 'v20')
    # background.addBlock((35,895), 'v17')
    # background.addBlock((260,780), 'v15')
    # background.addBlock((600,725), 'v12')

    # background.addBlock((80,735), 'v25', 'h')
    # background.addBlock((1155,735), 'v22', 'h')
    # background.addBlock((960,225), 'v5', 'h')
    # background.addBlock((960,285), 'v6', 'h')
    # background.addBlock((535,565), 'v16', 'h')
    # background.addBlock((310,850), 'v14', 'h')
    # background.addBlock((425,850), 'v13', 'h')
    # background.addBlock((535,850), 'v19', 'h')
    # background.addBlock((1160,620), 'v21', 'h')
    # background.addBlock((705,905), 'v11', 'h')
    # background.addBlock((765,1020), 'v24', 'h')
    # background.addBlock((990,1020), 'v9', 'h')
    # background.addBlock((1045,1135), 'v27', 'h')
    # background.addBlock((1195,960), 'v7', 'h')
    # background.addBlock((1195,1075), 'v8', 'h')

    # background.addBlock((617, 637), 'pm1', 'c')
    # background.addBlock((1012, 923), 'pm2', 'c')
    # background.addBlock((220, 1090), 'pm3', 'c')
    # background.addBlock((162, 1150), 'pm4', 'c')
    # background.addBlock((1240, 692), 'pm5', 'c')

    background.addBlock((1096, 105), 'v1')
    background.addBlock((1210, 105), 'v2')
    background.addBlock((1096, 330), 'v3')
    background.addBlock((1210, 330), 'v4')
    background.addBlock((1150, 672), 'v24')
    background.addBlock((1094, 956), 'v10')
    background.addBlock((1200, 1077), 'v18', 'h')
    background.addBlock((414, 786), 'v17')
    background.addBlock((416, 900), 'v15')
    background.addBlock((529, 786), 'v12')
    background.addBlock((1202, 625), 'v22', 'h')
    background.addBlock((1197, 735), 'v23', 'h')
    background.addBlock((1029, 285), 'v5', 'h')
    background.addBlock((1029, 228), 'v6', 'h')
    background.addBlock((464, 850), 'v16', 'h')
    background.addBlock((462, 1021), 'v14', 'h')
    # background.addBlock((425,850), 'v13', 'h')
    background.addBlock((461, 965), 'v19', 'h')
    background.addBlock((576, 965), 'v11', 'h')
    background.addBlock((972, 1020), 'v9', 'h')
    background.addBlock((1195, 960), 'v7', 'h')
    # background.addBlock((300,1015), 'v8', 'v')
    background.addBlock((655, 864), 'pm1', 'c')
    background.addBlock((655, 752), 'pm2', 'c')

    topEdge = Edge(screen, (0, 0), (1, 1/10), (150, 150, 150), True, labels={})
    topEdge2 = Edge(screen, (0, 1/10), (1, 1/10),
                    (150, 150, 150), True, labels={})
    leftEdge = Edge(screen, (0, 2/10), (1/5, 1),
                    (150, 150, 150), True, labels={})
    rightEdge = Edge(screen, (4/5, 2/10), (1/5, 1),
                     (150, 150, 150), True, labels={})

    topEdge.addLabel(text='PM1', pos=(ceil(0.00125*screenWidth),
                     ceil(0.0015*screenHeight)), color=(0, 0, 0), fontsize='mid')
    topEdge.addLabel(text='Stator Speed: ', pos=(ceil(0.01*screenWidth), ceil(
        0.02*screenHeight)), color=(0, 0, 0), id='PM1STATORSPEEDLABEL', fontsize='small')
    topEdge.addLabel(text='Computer Temp: ', pos=(ceil(0.01*screenWidth), ceil(
        0.035*screenHeight)), color=(0, 0, 0), id='PM1COMPUTERTEMPLABEL', fontsize='small')
    topEdge.addLabel(text='Motor Current: ', pos=(ceil(0.01*screenWidth), ceil(
        0.05*screenHeight)), color=(0, 0, 0), id='PM1MOTORCURRENTLABEL', fontsize='small')
    topEdge.addLabel(text='Bearing Temp: ', pos=(ceil(0.01*screenWidth), ceil(
        0.065*screenHeight)), color=(0, 0, 0), id='PM1BEARINGTEMPLABEL', fontsize='small')
    topEdge.addLabel(text='Voltage: ', pos=(ceil(0.01*screenWidth), ceil(0.08 *
                     screenHeight)), color=(0, 0, 0), id='PM1VOLTAGELABEL', fontsize='small')

    topEdge.addLabel(text='00000', pos=(ceil(0.1*screenWidth), ceil(0.02 *
                     screenHeight)), color=(0, 0, 0), id='PM1STATORSPEED', fontsize='small')
    topEdge.addLabel(text='00000', pos=(ceil(0.1*screenWidth), ceil(0.035 *
                     screenHeight)), color=(0, 0, 0), id='PM1COMPUTERTEMP', fontsize='small')
    topEdge.addLabel(text='00000', pos=(ceil(0.1*screenWidth), ceil(0.05 *
                     screenHeight)), color=(0, 0, 0), id='PM1MOTORCURRENT', fontsize='small')
    topEdge.addLabel(text='00000', pos=(ceil(0.1*screenWidth), ceil(0.065 *
                     screenHeight)), color=(0, 0, 0), id='PM1BEARINGTEMP', fontsize='small')
    topEdge.addLabel(text='00000', pos=(ceil(0.1*screenWidth), ceil(0.08 *
                     screenHeight)), color=(0, 0, 0), id='PM1VOLTAGE', fontsize='small')

    topEdge2.addLabel(text='PM2', pos=(ceil(0.00125*screenWidth),
                      ceil(0.1*screenHeight)), color=(0, 0, 0), fontsize='mid')
    topEdge2.addLabel(text='Stator Speed: ', pos=(ceil(0.01*screenWidth), ceil(
        0.12*screenHeight)), color=(0, 0, 0), id='PM2STATORSPEEDLABEL', fontsize='small')
    topEdge2.addLabel(text='Computer Temp: ', pos=(ceil(0.01*screenWidth), ceil(
        0.135*screenHeight)), color=(0, 0, 0), id='PM2COMPUTERTEMPLABEL', fontsize='small')
    topEdge2.addLabel(text='Motor Current: ', pos=(ceil(0.01*screenWidth), ceil(
        0.15*screenHeight)), color=(0, 0, 0), id='PM2MOTORCURRENTLABEL', fontsize='small')
    topEdge2.addLabel(text='Bearing Temp: ', pos=(ceil(0.01*screenWidth), ceil(
        0.165*screenHeight)), color=(0, 0, 0), id='PM2BEARINGTEMPLABEL', fontsize='small')
    topEdge2.addLabel(text='Voltage: ', pos=(ceil(0.01*screenWidth), ceil(
        0.18*screenHeight)), color=(0, 0, 0), id='PM2VOLTAGELABEL', fontsize='small')

    topEdge2.addLabel(text='00000', pos=(ceil(0.1*screenWidth), ceil(0.12 *
                      screenHeight)), color=(0, 0, 0), id='PM2STATORSPEED', fontsize='small')
    topEdge2.addLabel(text='00000', pos=(ceil(0.1*screenWidth), ceil(0.135 *
                      screenHeight)), color=(0, 0, 0), id='PM2COMPUTERTEMP', fontsize='small')
    topEdge2.addLabel(text='00000', pos=(ceil(0.1*screenWidth), ceil(0.15 *
                      screenHeight)), color=(0, 0, 0), id='PM2MOTORCURRENT', fontsize='small')
    topEdge2.addLabel(text='00000', pos=(ceil(0.1*screenWidth), ceil(0.165 *
                      screenHeight)), color=(0, 0, 0), id='PM2BEARINGTEMP', fontsize='small')
    topEdge2.addLabel(text='00000', pos=(ceil(0.1*screenWidth), ceil(0.18 *
                      screenHeight)), color=(0, 0, 0), id='PM2VOLTAGE', fontsize='small')

    topEdge.addLabel(text='Query Type: ', pos=(ceil(0.15*screenWidth), ceil(
        0.03*screenHeight)), color=(0, 0, 0), id='PM1QUERYTYPE', fontsize='small')
    pm1QueryTypeDropdown = dropdown(screen, 'Select Query Type', (ceil(0.25*screenWidth), ceil(0.03*screenHeight)), (ceil(
        0.125*screenWidth), ceil(0.015*screenHeight)), (200, 200, 200), id='PM1QUERYTYPEBOX', fontsize='small')
    pm1QueryTypeDropdown.setOptions(['Value Request', '16 Bit Write', '32 Bit Write',
                                    'Field Value Request', '16 Bit Field Value Write', '32 Bit Field Value Write'])
    topEdge.addLabel(text='Parameter Number: ', pos=(ceil(0.15*screenWidth), ceil(
        0.045*screenHeight)), color=(0, 0, 0), id='PM1PARAMETERNUMBER', fontsize='small')
    pm1ParameterNumberBox = textbox(screen, '0', (ceil(0.25*screenWidth), ceil(0.045*screenHeight)), (ceil(
        0.125*screenWidth), ceil(0.015*screenHeight)), (200, 200, 200), fontsize='small', id='PM1PARAMETERNUMBERBOX')
    topEdge.addLabel(text='Parameter Index: ', pos=(ceil(0.15*screenWidth), ceil(
        0.06*screenHeight)), color=(0, 0, 0), id='PM1PARAMETERINDEX', fontsize='small')
    pm1ParameterIndexBox = textbox(screen, '0', (ceil(0.25*screenWidth), ceil(0.06*screenHeight)), (ceil(
        0.125*screenWidth), ceil(0.015*screenHeight)), (200, 200, 200), fontsize='small', id='PM1PARAMETERIndexBOX')
    topEdge.addLabel(text='Parameter Value: ', pos=(ceil(0.15*screenWidth), ceil(
        0.075*screenHeight)), color=(0, 0, 0), id='PM1PARAMETERVALUE', fontsize='small')
    pm1ParameterValueBox = textbox(screen, '0', (ceil(0.25*screenWidth), ceil(0.075*screenHeight)), (ceil(
        0.125*screenWidth), ceil(0.015*screenHeight)), (200, 200, 200), fontsize='small', id='PM1PARAMETERVALUEBOX')

    pm1SendQueryButton = button(screen=screen, text='Send Query', pos=(ceil(0.4*screenWidth), ceil(0.046*screenHeight)), size=(
        ceil(0.125*screenWidth), ceil(0.03*screenHeight)), colorIdle=(200, 200, 200), colorHeld=(150, 150, 150), id='PM1SENDQUERY')

    topEdge.addLabel(text='Response Type: ', pos=(ceil(0.55*screenWidth), ceil(
        0.03*screenHeight)), color=(0, 0, 0), id='PM1RESPONSETYPE', fontsize='small')
    topEdge.addLabel(text='Response Number: ', pos=(ceil(0.55*screenWidth), ceil(
        0.045*screenHeight)), color=(0, 0, 0), id='PM1RESPONSENUMBER', fontsize='small')
    topEdge.addLabel(text='Response Index: ', pos=(ceil(0.55*screenWidth), ceil(
        0.06*screenHeight)), color=(0, 0, 0), id='PM1RESPONSEINDEX', fontsize='small')
    topEdge.addLabel(text='Response Value: ', pos=(ceil(0.55*screenWidth), ceil(
        0.075*screenHeight)), color=(0, 0, 0), id='PM1RESPONSEVALUE', fontsize='small')
    topEdge.addLabel(text='No Response', pos=(ceil(0.65*screenWidth), ceil(0.03 *
                     screenHeight)), color=(0, 0, 0), id='PM1RESPONSETYPEVALUE', fontsize='small')
    topEdge.addLabel(text='00000', pos=(ceil(0.65*screenWidth), ceil(0.045*screenHeight)),
                     color=(0, 0, 0), id='PM1RESPONSENUMBERVALUE', fontsize='small')
    topEdge.addLabel(text='00000', pos=(ceil(0.65*screenWidth), ceil(0.06*screenHeight)),
                     color=(0, 0, 0), id='PM1RESPONSEINDEXVALUE', fontsize='small')
    topEdge.addLabel(text='00000', pos=(ceil(0.65*screenWidth), ceil(0.075*screenHeight)),
                     color=(0, 0, 0), id='PM1RESPONSEVALUEVALUE', fontsize='small')

    topEdge2.addLabel(text='Query Type: ', pos=(ceil(0.15*screenWidth), ceil(
        0.13*screenHeight)), color=(0, 0, 0), id='PM2QUERYTYPE', fontsize='small')
    pm2QueryTypeDropdown = dropdown(screen, 'Select Query Type', (ceil(0.25*screenWidth), ceil(0.13*screenHeight)), (ceil(
        0.125*screenWidth), ceil(0.015*screenHeight)), (200, 200, 200), id='PM2QUERYTYPEBOX', fontsize='small')
    pm2QueryTypeDropdown.setOptions(['Value Request', '16 Bit Write', '32 Bit Write',
                                    'Field Value Request', '16 Bit Field Value Write', '32 Bit Field Value Write'])
    topEdge2.addLabel(text='Parameter Number: ', pos=(ceil(0.15*screenWidth), ceil(
        0.145*screenHeight)), color=(0, 0, 0), id='PM2PARAMETERNUMBER', fontsize='small')
    pm2ParameterNumberBox = textbox(screen, '0', (ceil(0.25*screenWidth), ceil(0.145*screenHeight)), (ceil(
        0.125*screenWidth), ceil(0.015*screenHeight)), (200, 200, 200), fontsize='small', id='PM2PARAMETERNUMBERBOX')
    topEdge2.addLabel(text='Parameter Index: ', pos=(ceil(0.15*screenWidth), ceil(
        0.16*screenHeight)), color=(0, 0, 0), id='PM2PARAMETERINDEX', fontsize='small')
    pm2ParameterIndexBox = textbox(screen, '0', (ceil(0.25*screenWidth), ceil(0.16*screenHeight)), (ceil(
        0.125*screenWidth), ceil(0.015*screenHeight)), (200, 200, 200), fontsize='small', id='PM2PARAMETERIndexBOX')
    topEdge2.addLabel(text='Parameter Value: ', pos=(ceil(0.15*screenWidth), ceil(
        0.175*screenHeight)), color=(0, 0, 0), id='PM2PARAMETERVALUE', fontsize='small')
    pm2ParameterValueBox = textbox(screen, '0', (ceil(0.25*screenWidth), ceil(0.175*screenHeight)), (ceil(
        0.125*screenWidth), ceil(0.015*screenHeight)), (200, 200, 200), fontsize='small', id='PM2PARAMETERVALUEBOX')

    pm2SendQueryButton = button(screen=screen, text='Send Query', pos=(ceil(0.4*screenWidth), ceil(0.146*screenHeight)), size=(
        ceil(0.125*screenWidth), ceil(0.03*screenHeight)), colorIdle=(200, 200, 200), colorHeld=(150, 150, 150), id='PM1SENDQUERY')

    topEdge2.addLabel(text='Response Type: ', pos=(ceil(0.55*screenWidth), ceil(
        0.13*screenHeight)), color=(0, 0, 0), id='PM2RESPONSETYPE', fontsize='small')
    topEdge2.addLabel(text='Response Number: ', pos=(ceil(0.55*screenWidth), ceil(
        0.145*screenHeight)), color=(0, 0, 0), id='PM2RESPONSENUMBER', fontsize='small')
    topEdge2.addLabel(text='Response Index: ', pos=(ceil(0.55*screenWidth), ceil(
        0.16*screenHeight)), color=(0, 0, 0), id='PM2RESPONSEINDEX', fontsize='small')
    topEdge2.addLabel(text='Response Value: ', pos=(ceil(0.55*screenWidth), ceil(
        0.175*screenHeight)), color=(0, 0, 0), id='PM2RESPONSEVALUE', fontsize='small')
    topEdge2.addLabel(text='No Response', pos=(ceil(0.65*screenWidth), ceil(0.13 *
                      screenHeight)), color=(0, 0, 0), id='PM2RESPONSETYPEVALUE', fontsize='small')
    topEdge2.addLabel(text='00000', pos=(ceil(0.65*screenWidth), ceil(0.145*screenHeight)),
                      color=(0, 0, 0), id='PM2RESPONSENUMBERVALUE', fontsize='small')
    topEdge2.addLabel(text='00000', pos=(ceil(0.65*screenWidth), ceil(0.16*screenHeight)),
                      color=(0, 0, 0), id='PM2RESPONSEINDEXVALUE', fontsize='small')
    topEdge2.addLabel(text='00000', pos=(ceil(0.65*screenWidth), ceil(0.175*screenHeight)),
                      color=(0, 0, 0), id='PM2RESPONSEVALUEVALUE', fontsize='small')

    leftEdge.addLabel(text='Temperatures', pos=(
        ceil(0.000625*screenWidth), ceil(0.2*screenHeight)), color=(0, 0, 0))

    for ii in range(sensorNum):
        leftEdge.addLabel(text=sensorNames[ii] + " ", pos=(ceil(0.000625*screenWidth), ceil(
            (0.23+0.05*(ii))*screenHeight)), color=(0, 0, 0), fontsize='mid')
        leftEdge.addLabel(text='00.00', pos=(ceil(0.125*screenWidth), ceil((0.23+0.05*(ii))
                          * screenHeight)), color=(0, 0, 0), fontsize='mid', id='T_S_'+str(sensorNames[ii]))

    rightEdge.addLabel(text='Pressures', pos=(
        ceil((4/5+0.000625)*screenWidth), ceil(0.2*screenHeight)), color=(0, 0, 0))

    for ii in range(6):
        rightEdge.addLabel(text='Sensor '+str(ii+1)+':', pos=(ceil((4/5+0.000625)*screenWidth),
                           ceil((0.25+0.05*(ii))*screenHeight)), color=(0, 0, 0), fontsize='mid')
        rightEdge.addLabel(text='00.00', pos=(ceil((4/5+0.125)*screenWidth), ceil((0.25+0.05*(
            ii))*screenHeight)), color=(0, 0, 0), fontsize='mid', id='Pr'+str(ii+1)+'VALUE')

    rightEdge.addLabel(text='Flow', pos=(ceil((4/5+0.000625)*screenWidth),
                       ceil((0.25+0.05*(6))*screenHeight)), color=(0, 0, 0), id="flowlabel")
    rightEdge.addLabel(text='00.00', pos=(ceil((4/5+0.000625)*screenWidth), ceil(
        (0.25+0.05*(7))*screenHeight)), color=(0, 0, 0), fontsize='mid', id='Flow')

    rightEdge.addLabel(text='Heaters', pos=(ceil(
        (4/5+0.000625)*screenWidth), ceil((0.25+0.05*(8))*screenHeight)), color=(0, 0, 0))
    rightEdge.addLabel(text='Warm Up', pos=(ceil((4/5+0.000625)*screenWidth),
                       ceil((0.25+0.05*(9))*screenHeight)), color=(0, 0, 0), fontsize='mid')
    warmUpSetpoint = textbox(screen, '0.0 %', pos=(ceil((4/5+0.000625)*screenWidth), ceil((0.25+0.05*(10))*screenHeight)), size=(
        ceil(screenWidth/15), ceil(0.03*screenHeight)), color=(200, 200, 200), fontsize='small', id='WARMUPSETPOINT', postfix=' %')
    stopWarmUp = button(screen, "Stop", (ceil((8.5/10)*screenWidth), ceil((0.252+0.05*(9))*screenHeight)), (ceil(
        screenWidth/30), ceil(0.015*screenHeight)), (200, 200, 200), (150, 150, 150), "WARMUPSTOPBUTTON", 'small')
    sendWarmUpValue = button(screen, "->", pos=(ceil((8.7/10+0.000625)*screenWidth), ceil((0.25+0.05*(10))*screenHeight)), size=(
        ceil(screenWidth/50), ceil(0.03*screenHeight)), colorIdle=(200, 200, 200), colorHeld=(150, 150, 150), id='WARMUPSENDBUTTON')
    rightEdge.addLabel(text="00.00", pos=(ceil((4/5+0.125)*screenWidth), ceil((0.25+0.05*(10))
                       * screenHeight)), color=(0, 0, 0), fontsize='mid', id='WARMUPHEATERVALUE')

    rightEdge.addLabel(text='Still', pos=(ceil((4/5+0.000625)*screenWidth),
                       ceil((0.25+0.05*(11))*screenHeight)), color=(0, 0, 0), fontsize='mid')
    stillSetpoint = textbox(screen, '0.0 %', pos=(ceil((4/5+0.000625)*screenWidth), ceil((0.25+0.05*(12))*screenHeight)), size=(
        ceil(screenWidth/15), ceil(0.03*screenHeight)), color=(200, 200, 200), fontsize='small', id='STILLSETPOINT', postfix=' %')
    stopStill = button(screen, "Stop", (ceil((8.5/10)*screenWidth), ceil((0.252+0.05*(11))*screenHeight)), (ceil(
        screenWidth/30), ceil(0.015*screenHeight)), (200, 200, 200), (150, 150, 150), "STILLSTOPBUTTON", 'small')
    sendStillValue = button(screen, "->", pos=(ceil((8.7/10+0.000625)*screenWidth), ceil((0.25+0.05*(12))*screenHeight)), size=(
        ceil(screenWidth/50), ceil(0.03*screenHeight)), colorIdle=(200, 200, 200), colorHeld=(150, 150, 150), id='STILLSENDBUTTON')
    rightEdge.addLabel(text="00.00", pos=(ceil((4/5+0.125)*screenWidth), ceil(
        (0.25+0.05*(12))*screenHeight)), color=(0, 0, 0), fontsize='mid', id='STILLHEATERVALUE')

    rightEdge.addLabel(text='Sample', pos=(ceil((4/5+0.000625)*screenWidth),
                       ceil((0.25+0.05*(13))*screenHeight)), color=(0, 0, 0), fontsize='mid')
    sampleSetPoint = textbox(screen, '0.0 mA', pos=(ceil((4/5+0.000625)*screenWidth), ceil((0.25+0.05*(14))*screenHeight)), size=(
        ceil(screenWidth/15), ceil(0.03*screenHeight)), color=(200, 200, 200), fontsize='small', id='SAMPLESETPOINT', postfix=' mA')
    stopSample = button(screen, "Stop", (ceil((8.5/10)*screenWidth), ceil((0.252+0.05*(13))*screenHeight)), (ceil(
        screenWidth/30), ceil(0.015*screenHeight)), (200, 200, 200), (150, 150, 150), "SAMPLESTOPBUTTON", 'small')
    sendSampleValue = button(screen, "->", pos=(ceil((8.7/10+0.000625)*screenWidth), ceil((0.25+0.05*(14))*screenHeight)), size=(
        ceil(screenWidth/50), ceil(0.03*screenHeight)), colorIdle=(200, 200, 200), colorHeld=(150, 150, 150), id='SAMPLESENDBUTTON')
    rightEdge.addLabel(text="00.00", pos=(ceil((4/5+0.125)*screenWidth), ceil((0.25+0.05*(14))
                       * screenHeight)), color=(0, 0, 0), fontsize='mid', id='SAMPLEHEATERVALUE')

    background.pos = [ceil(0.25*screenWidth), ceil(0.25*screenHeight)]
    background.draw()
    pygame.display.flip()

    clicked = (False, False, False)
    mousePos = pygame.mouse.get_pos()
    itemClicked = ''
    oldItemColor = (0, 0, 0)

    toggleViewButton = button(screen, 'Toggle View', (ceil(screenWidth/5), ceil(screenHeight/5)),
                              (ceil(0.1*screenWidth), ceil(0.03*screenHeight)), (200, 200, 200), (150, 150, 150), 'TOGGLEVIEWBUTTON')
    resetViewButton = button(screen, 'Reset View', (ceil(screenWidth/5+2*ceil(0.1*screenWidth)), ceil(screenHeight/5)),
                             (ceil(0.1*screenWidth), ceil(0.03*screenHeight)), (200, 200, 200), (150, 150, 150), 'RESETVIEWBUTTON')
    toggleLogButton = button(screen, 'Start Logging', (ceil(0.005*screenWidth), ceil(0.9*screenHeight)), (ceil(
        screenWidth/5-0.01*screenWidth), ceil(0.03*screenHeight)), (200, 200, 200), (150, 150, 150), 'TOGGLELOGBUTTON')
    logNameBox = textbox(screen, 'enter log name',  (ceil(0.005*screenWidth), ceil(0.85*screenHeight)), (ceil(
        screenWidth/5-0.01*screenWidth), ceil(0.03*screenHeight)), (200, 200, 200), fontsize='small', id='LOGNAME')
    pauseLogButton = button(screen, 'Resume Previous Log', (ceil(0.005*screenWidth), ceil(0.95*screenHeight)), (ceil(
        screenWidth/5-0.01*screenWidth), ceil(0.03*screenHeight)), (200, 200, 200), (150, 150, 150), 'PAUSELOGBUTTON')
    buttonClicked = ''

    valveStatus = {}
    for kk in ['v' + str(ii) for ii in range(1, 28, 1)]:
        valveStatus[kk] = 'closed'
    for kk in ['pm' + str(ii) for ii in range(1, 6, 1)]:
        valveStatus[kk] = 'closed'
    graphClicked = False
    graphZoomed = False
    plotTime = datetime.timestamp(datetime.now())
    zoomRect = [[0, 0], [1, 1]]
    zoomVals = []
    zoomTimes = []

    queryDict = {'Select Query Type': 0, 'Value Request': 1, '16 Bit Write': 2, '32 Bit Write': 3,
                 'Field Value Request': 6, '16 Bit Field Value Write': 7, '32 Bit Field Value Write': 8}

    logging = False
    logPaused = False
    logName = 'test_datalog.csv'

    plotType = "SHORT"

    while (1):
        if time.time() - configUpdateTimer >= configUpdateTime:
            configUpdateTimer = time.time()
            with open("System_Config.json") as sconf:
                systemConfig = json.load(sconf)

            timers = systemConfig["Timers"]
            emailManager.updateTime = timers["Email_Timer"]
            emailManager.recipients = systemConfig["Email_List"]
            pm1Manager.mainTimer = timers["Turbo_Com_Timer"]
            pm2Manager.mainTimer = timers["Turbo_Com_Timer"]
            valveManager.updateTime = timers["Valve_Update_Timer"]
            logTime = timers["Log_Timer"]
            flowTime = timers["Flow_Readout_Timer"]
            pressureManager.updateTime = timers["Pressure_Readout_Timer"]
            lakeshoreManager.updateTime = timers["Temperature_Readout_Timer"]
            emailManager.updateTime = timers["Email_Timer"]
            configUpdateTime = timers["System_Config_Update_Timer"]
        if lakeshoreManager.update():
            emailMessage = 'Subject: ' + str(datetime.now()) + '\n\n'
            for ii in range(sensorNum):
                leftEdge.updateLabel(
                    'T_S_'+str(sensorNames[ii]), str(round(lakeshoreManager.currentTemp[ii], 2)))
                emailMessage += sensorNames[ii] + ': ' + \
                    str(lakeshoreManager.currentTemp[ii])+'\n'
            for ii in range(len(pressureManager.pressures)):
                emailMessage += 'Pressure ' + \
                    str(ii+1)+':'+str(pressureManager.pressures[ii])+'\n'
            emailMessage += 'Flow: ' + str(flowValue) + '\n'
            if logging:
                if not logPaused:
                    times.append(datetime.now())
                    for ii in range(sensorNum):

                        tVals[ii].append(lakeshoreManager.currentTemp[ii])

                    emailManager.update(emailMessage)

            if graphView and logging and not logPaused:
                if not (graphClicked or graphZoomed):
                    plt.close()
                    size = (ceil(0.5*screenWidth), ceil(0.75*screenHeight))
                    fig = plt.figure(
                        figsize=[size[0]/100, size[1]/100], dpi=100)
                    ax = fig.gca()
                    if plotType == "SHORT":
                        for jj in range(len(tVals)):
                            if list(lakeshoreManager.sensors.keys())[jj] in plotWithoutLogScale:
                                ii = tVals[jj]
                                ax.plot(times[-int(draggingPlotTime/lakeshoreManager.updateTime):],
                                        ii[-int(draggingPlotTime/lakeshoreManager.updateTime):])
                            plt.legend([ii for ii in lakeshoreManager.sensors.keys(
                            ) if ii in plotWithoutLogScale], loc=0)
                    else:
                        for ii in tVals:
                            ax.plot(times, ii)
                        plt.legend(
                            list(lakeshoreManager.sensors.keys()), loc=0)
                        plt.yscale('log')
                    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=int(
                        (datetime.timestamp(datetime.now())-plotTime)/(60*5)+1)))

                    # plt.legend(['Sensor' + str(ii+1) for ii in range(len(tVals))], loc = 'upper right')
                    canvas = agg.FigureCanvasAgg(fig)
                    canvas.draw()
                    renderer = canvas.get_renderer()
                    raw_data = renderer.tostring_rgb()
                    # size = (800,800)
                    graphImage = pygame.image.fromstring(raw_data, size, "RGB")

        

            rightEdge.updateLabel("WARMUPHEATERVALUE", str(
                lakeshoreManager.actualWarmupHeaterPercent) + " %")
            rightEdge.updateLabel("STILLHEATERVALUE", str(
                lakeshoreManager.actualStillHeaterPercent) + " %")
            rightEdge.updateLabel("SAMPLEHEATERVALUE", str(
                lakeshoreManager.actualSampleHeaterCurrent) + " mA")

            if time.perf_counter() - logTimer > logTime and logging and not logPaused:
                logTimer = time.perf_counter()
                with open(logName, 'a', encoding='UTF8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([str(datetime.now()), str(datetime.timestamp(datetime.now())-plotTime)] + sum(
                        [[lakeshoreManager.currentRes[ii], lakeshoreManager.currentTemp[ii]] for ii in range(sensorNum)], [])+pressureManager.pressures+[flowValue])
        if pm1Manager.update():
            running = pm1Manager.running
            response = pm1Manager.response
            background.changeColor(
                'pm1', (0, 255, 0) if running else (255, 0, 0))
            valveStatus['pm1'] = 'open' if running else 'closed'
            topEdge.updateLabel('PM1STATORSPEED', str(
                response["stator_frequency"]))
            topEdge.updateLabel('PM1COMPUTERTEMP', str(
                response["converter_temperature"]))
            topEdge.updateLabel('PM1MOTORCURRENT', str(
                response["motor_current"]))
            topEdge.updateLabel('PM1BEARINGTEMP', str(
                response["bearing_temperature"]))
            topEdge.updateLabel('PM1VOLTAGE', str(
                response["circuit_voltage"]))

        if pm2Manager.update():
            running = pm2Manager.running
            response = pm2Manager.response
            background.changeColor(
                'pm2', (0, 255, 0) if running else (255, 0, 0))
            valveStatus['pm2'] = 'open' if running else 'closed'
            topEdge2.updateLabel('PM2STATORSPEED', str(
                response["stator_frequency"]))
            topEdge2.updateLabel('PM2COMPUTERTEMP', str(
                response["converter_temperature"]))
            topEdge2.updateLabel('PM2MOTORCURRENT', str(
                response["motor_current"]))
            topEdge2.updateLabel('PM2BEARINGTEMP', str(
                response["bearing_temperature"]))
            topEdge2.updateLabel('PM2VOLTAGE', str(
                response["circuit_voltage"]))

        if valveManager.update():
            state = valveManager.getValveState()
            print(state)
            for ii in range(len(state)):
                kk = state[ii]
                valveStatus['v'+str(ii+1)] = 'open' if not kk else 'closed'
                background.changeColor(
                    'v'+str(ii+1), (0, 255, 0) if not kk else (255, 0, 0))

        if time.perf_counter() - flowTimer >= flowTime:
            flowTimer = time.perf_counter()
            flowValue = valveManager.getFlowVoltage()
            rightEdge.updateLabel('Flow', flowValue)

        if pressureManager.update():
            for ii in range(6):
                rightEdge.updateLabel(
                    'Pr'+str(ii+1)+'VALUE', pressureManager.pressures[ii])

                # Check Available ports

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:

                dropdownclicked = False
                if pm1QueryTypeDropdown.checkClick(event.pos) or\
                        pm2QueryTypeDropdown.checkClick(event.pos):
                    dropdownclicked = True
                edgeClicked = False
                if topEdge.checkClick(event.pos) or leftEdge.checkClick(event.pos) or topEdge2.checkClick(event.pos):
                    edgeClicked = True

                mousePresses = pygame.mouse.get_pressed()
                clicked = (mousePresses[0], mousePresses[1], mousePresses[2])
                if event.button == 1 and not edgeClicked and not dropdownclicked:
                    item = background.checkClick(event.pos, (255, 255, 195))
                    if item != None:
                        itemClicked, oldItemColor = item

                if not dropdownclicked:
                    if event.pos[0]/screenWidth >= 0.25 and event.pos[1]/screenHeight >= 0.25\
                            and event.pos[0]/screenWidth <= 0.75 and not graphZoomed and graphView and len(times):
                        graphClicked = True
                        zoomRect[0] = event.pos
                        zoomRect[1] = event.pos
                        zoomVals = copy(tVals)
                        zoomTimes = copy(times)

                    pm1ParameterNumberBox.checkClick(event.pos)
                    pm1ParameterIndexBox.checkClick(event.pos)
                    pm1ParameterValueBox.checkClick(event.pos)
                    pm2ParameterNumberBox.checkClick(event.pos)
                    pm2ParameterIndexBox.checkClick(event.pos)
                    pm2ParameterValueBox.checkClick(event.pos)
                    if not logging and logNameBox.checkClick(event.pos):
                        if logNameBox.text == 'enter log name':
                            logNameBox.setText('')
                            logNameBox.checkClick(event.pos)
                    if warmUpSetpoint.checkClick(event.pos):
                        warmUpSetpoint.setText('')
                        warmUpSetpoint.checkClick(event.pos)
                        warmUpSetpoint.color = (200, 200, 200)
                    if sendWarmUpValue.checkClick(event.pos):
                        buttonClicked = sendWarmUpValue.id
                        sendWarmUpValue.isHeld()
                    if sendStillValue.checkClick(event.pos):
                        buttonClicked = sendStillValue.id
                        sendStillValue.isHeld()
                    if sendSampleValue.checkClick(event.pos):
                        buttonClicked = sendSampleValue.id
                        sendSampleValue.isHeld()
                    if stopWarmUp.checkClick(event.pos):
                        buttonClicked = stopWarmUp.id
                        stopWarmUp.isHeld()
                    if stopStill.checkClick(event.pos):
                        buttonClicked = stopStill.id
                        stopStill.isHeld()
                    if stopSample.checkClick(event.pos):
                        buttonClicked = stopSample.id
                        stopSample.isHeld()
                    if stillSetpoint.checkClick(event.pos):
                        stillSetpoint.setText('')
                        stillSetpoint.checkClick(event.pos)
                        stillSetpoint.color = (200, 200, 200)
                    if sampleSetPoint.checkClick(event.pos):
                        sampleSetPoint.setText('')
                        sampleSetPoint.checkClick(event.pos)
                        sampleSetPoint.color = (200, 200, 200)
                    if pm1SendQueryButton.checkClick(event.pos):
                        buttonClicked = pm1SendQueryButton.id
                        pm1SendQueryButton.isHeld()
                    if pm2SendQueryButton.checkClick(event.pos):
                        buttonClicked = pm2SendQueryButton.id
                        pm2SendQueryButton.isHeld()
                    if toggleViewButton.checkClick(event.pos):
                        buttonClicked = toggleViewButton.id
                        toggleViewButton.isHeld()
                    if resetViewButton.checkClick(event.pos) and graphZoomed:
                        buttonClicked = resetViewButton.id
                        resetViewButton.isHeld()
                    if toggleLogButton.checkClick(event.pos):
                        buttonClicked = toggleLogButton.id
                        toggleLogButton.isHeld()
                    if pauseLogButton.checkClick(event.pos):
                        buttonClicked = pauseLogButton.id
                        pauseLogButton.isHeld()

            if event.type == pygame.MOUSEBUTTONUP:
                mousePresses = pygame.mouse.get_pressed()
                clicked = (mousePresses[0], mousePresses[1], mousePresses[2])
                if event.button == 1 and not edgeClicked:
                    newClick = background.checkClick(event.pos)
                    if newClick != None:
                        if newClick[0] == itemClicked:
                            background.changeColor(itemClicked, (255, 255, 0))
                            print(itemClicked)
                            if valveStatus[itemClicked] == 'open':
                                if itemClicked == 'pm1':
                                    pm1Manager._stopOperation_()
                                    background.changeColor(
                                        itemClicked, (255, 255, 0))
                                    valveStatus[itemClicked] = 'waiting'
                                elif itemClicked == 'pm2':
                                    pm2Manager._stopOperation_()
                                    background.changeColor(
                                        itemClicked, (255, 255, 0))
                                    valveStatus[itemClicked] = 'waiting'
                                elif itemClicked[0] == 'v':
                                    if valveManager.toggleValve(itemClicked):
                                        background.changeColor(
                                            itemClicked, (255, 0, 0))
                                        valveStatus[itemClicked] = 'closed'

                            else:
                                if itemClicked == 'pm1':
                                    pm1Manager._startOperation_()
                                    background.changeColor(
                                        itemClicked, (255, 255, 0))
                                    valveStatus[itemClicked] = 'waiting'
                                elif itemClicked == 'pm2':
                                    pm2Manager._startOperation_()
                                    background.changeColor(
                                        itemClicked, (255, 255, 0))
                                    valveStatus[itemClicked] = 'waiting'
                                elif itemClicked[0] == 'v':
                                    if valveManager.toggleValve(itemClicked):
                                        background.changeColor(
                                            itemClicked, (0, 255, 0))
                                        valveStatus[itemClicked] = 'open'

                        else:
                            background.changeColor(itemClicked, oldItemColor)
                        itemClicked = ''
                        oldItemColor = (0, 0, 0)
                    else:
                        background.changeColor(itemClicked, oldItemColor)
                        itemClicked = ''
                        oldItemColor = (0, 0, 0)

                if pm1SendQueryButton.checkClick(event.pos) and buttonClicked == pm1SendQueryButton.id:
                    query = {}
                    query['type'] = queryDict[pm1QueryTypeDropdown.text]
                    query['number'] = int(pm1ParameterNumberBox.text)
                    query['index'] = int(pm1ParameterIndexBox.text)
                    query['value'] = int(pm1ParameterValueBox.text)


                    if pm1Manager.sendQuery(query):
                        paramQueryResponse = pm1Manager.response
                        topEdge.updateLabel('PM1RESPONSETYPEVALUE', str(
                            paramQueryResponse['type']))
                        topEdge.updateLabel('PM1RESPONSENUMBERVALUE', str(
                            paramQueryResponse['number']))
                        topEdge.updateLabel('PM1RESPONSEINDEXVALUE', str(
                            paramQueryResponse['index']))
                        topEdge.updateLabel('PM1RESPONSEVALUEVALUE', str(
                            paramQueryResponse['value']))

                pm1SendQueryButton.isIdle()
                if pm2SendQueryButton.checkClick(event.pos) and buttonClicked == pm2SendQueryButton.id:
                    query = {}
                    query['type'] = queryDict[pm2QueryTypeDropdown.text]
                    query['number'] = int(pm2ParameterNumberBox.text)
                    query['index'] = int(pm2ParameterIndexBox.text)
                    query['value'] = int(pm2ParameterValueBox.text)

                    if pm2Manager.sendQuery(query):
                        paramQueryResponse = pm2Manager.response
                        topEdge2.updateLabel('PM2RESPONSETYPEVALUE', str(
                            paramQueryResponse['type']))
                        topEdge2.updateLabel('PM2RESPONSENUMBERVALUE', str(
                            paramQueryResponse['type']))
                        topEdge2.updateLabel('PM2RESPONSEINDEXVALUE', str(
                            paramQueryResponse['type']))
                        topEdge2.updateLabel('PM2RESPONSEVALUEVALUE', str(
                            paramQueryResponse['type']))
                pm2SendQueryButton.isIdle()
                if toggleViewButton.checkClick(event.pos) and buttonClicked == toggleViewButton.id:
                    if plotType == 'FULL':
                        plotType = 'SHORT'
                    elif plotType == 'SHORT':
                        graphView = not graphView
                        if graphView:
                            plotType = 'FULL'
                    plt.close()
                    size = (ceil(0.5*screenWidth), ceil(0.75*screenHeight))
                    fig = plt.figure(
                        figsize=[size[0]/100, size[1]/100], dpi=100)
                    ax = fig.gca()
                    if plotType == "SHORT":
                        for jj in range(len(tVals)):
                            if list(lakeshoreManager.sensors.keys())[jj] in plotWithoutLogScale:
                                ii = tVals[jj]
                                ax.plot(times[-int(draggingPlotTime/lakeshoreManager.updateTime):],
                                        ii[-int(draggingPlotTime/lakeshoreManager.updateTime):])
                            plt.legend([ii for ii in lakeshoreManager.sensors.keys(
                            ) if ii in plotWithoutLogScale], loc=0)
                    else:
                        for ii in tVals:
                            ax.plot(times, ii)
                        plt.legend(
                            list(lakeshoreManager.sensors.keys()), loc=0)
                        plt.yscale('log')
                    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=int(
                        (datetime.timestamp(datetime.now())-plotTime)/(60*5)+1)))

                    # plt.legend(['Sensor' + str(ii+1) for ii in range(len(tVals))], loc = 'upper right')
                    canvas = agg.FigureCanvasAgg(fig)
                    if len(times):
                        canvas.draw()
                        renderer = canvas.get_renderer()
                        raw_data = renderer.tostring_rgb()
                        # size = (800,800)
                        graphImage = pygame.image.fromstring(
                            raw_data, size, "RGB")

                toggleViewButton.isIdle()
                if resetViewButton.checkClick(event.pos) and buttonClicked == resetViewButton.id:
                    graphZoomed = False
                    graphClicked = False
                    plt.close()
                    size = (ceil(0.5*screenWidth), ceil(0.75*screenHeight))
                    fig = plt.figure(
                        figsize=[size[0]/100, size[1]/100], dpi=100)
                    ax = fig.gca()
                    if plotType == "SHORT":
                        for jj in range(len(tVals)):
                            if list(lakeshoreManager.sensors.keys())[jj] in plotWithoutLogScale:
                                ii = tVals[jj]
                                ax.plot(times[-int(draggingPlotTime/lakeshoreManager.updateTime):],
                                        ii[-int(draggingPlotTime/lakeshoreManager.updateTime):])
                            plt.legend([ii for ii in lakeshoreManager.sensors.keys(
                            ) if ii in plotWithoutLogScale], loc=0)
                    else:
                        for ii in tVals:
                            ax.plot(times, ii)
                        plt.legend(
                            list(lakeshoreManager.sensors.keys()), loc=0)
                        plt.yscale('log')
                    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=int(
                        (datetime.timestamp(datetime.now())-plotTime)/(60*5)+1)))

                    # plt.legend(['Sensor' + str(ii+1) for ii in range(len(tVals))], loc = 'upper right')
                    canvas = agg.FigureCanvasAgg(fig)
                    canvas.draw()
                    renderer = canvas.get_renderer()
                    raw_data = renderer.tostring_rgb()
                    # size = (800,800)
                    graphImage = pygame.image.fromstring(raw_data, size, "RGB")
                resetViewButton.isIdle()

                if toggleLogButton.checkClick(event.pos) and buttonClicked == toggleLogButton.id:
                    if logging:
                        toggleLogButton.text = 'Start Logging'
                        logging = False
                        logPaused = False
                        logNameBox.setText('enter log name')
                        pauseLogButton.text = 'Resume Previous Log'

                    else:
                        toggleLogButton.text = 'Stop Logging'
                        logging = True
                        plotTime = datetime.timestamp(datetime.now())
                        logName = './Logs/'+(str(datetime.date(datetime.now())).replace(
                            '-', '')+'_'+logNameBox.text+'_data_log.csv').replace(' ', '_')
                        with open(logName, 'w', encoding='UTF8', newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow(['Current Time', 'Run Time']+sum([[sensorNames[ii] + ' (Resistance)', 'Sensor ' + sensorNames[ii] +
                                            ' (Temperature)'] for ii in range(sensorNum)], [])+['Pressure ' + str(ii+1) for ii in range(6)]+['Flow'])

                        logNameBox.setText('')
                        pauseLogButton.text = 'Pause Logging'
                        tVals = [[] for ii in range(sensorNum)]

                toggleLogButton.isIdle()
                if pauseLogButton.checkClick(event.pos) and buttonClicked == pauseLogButton.id:
                    if logging:
                        if logPaused:
                            pauseLogButton.text = 'Pause Logging'
                        else:
                            pauseLogButton.text = 'Resume Logging'
                        logPaused = not logPaused
                    else:
                        logs = [
                            './Logs/' + log for log in os.listdir('./Logs') if log.endswith('csv')]
                        if logs:
                            try:
                                previousLog = max(logs, key=os.path.getctime)
                                toggleLogButton.text = 'Stop Logging'
                                logging = True
                                logName = previousLog
                                with open(logName, 'r', encoding='UTF8', newline='') as f:
                                    reader = csv.reader(f)
                                    next(reader)
                                    tVals = [[] for ii in range(sensorNum)]
                                    row = next(reader)
                                    t = row[0]
                                    plotTime = time.mktime(datetime.strptime(
                                        t, "%Y-%m-%d %H:%M:%S.%f").timetuple())
                                    times.append(datetime.strptime(
                                        t, "%Y-%m-%d %H:%M:%S.%f"))
                                    for ii in range(sensorNum):
                                        tVals[ii].append(float(row[3+2*ii]))
                                    for row in reader:
                                        t = row[0]
                                        times.append(datetime.strptime(
                                            t, "%Y-%m-%d %H:%M:%S.%f"))
                                        for ii in range(sensorNum):
                                            tVals[ii].append(
                                                float(row[3+2*ii]))
                                logNameBox.setText('')
                                pauseLogButton.text = 'Pause Logging'
                            except PermissionError:
                                toggleLogButton.text = 'Start Logging'
                                logging = False
                                logPaused = False
                                logNameBox.setText('enter log name')
                                pauseLogButton.text = 'Resume Previous Log'

                pauseLogButton.isIdle()

                if buttonClicked == sendWarmUpValue.id and sendWarmUpValue.checkClick(event.pos):
                    try:
                        value = float(cleanFloatString(warmUpSetpoint.text))
                        lakeshoreManager.setWarmupHeaterOutputPercent(value)
                    except ValueError:
                        warmUpSetpoint.color = (255, 0, 0)
                    else:
                        rightEdge.updateLabel("WARMUPHEATERVALUE", str(
                            lakeshoreManager.getWarmupHeaterOutput()) + " %")

                sendWarmUpValue.isIdle()
                if buttonClicked == sendStillValue.id and sendStillValue.checkClick(event.pos):
                    try:
                        value = float(cleanFloatString(stillSetpoint.text))
                        lakeshoreManager.setStillOutput(value)
                    except ValueError:
                        stillSetpoint.color = (255, 0, 0)
                    else:
                        rightEdge.updateLabel("STILLHEATERVALUE", str(
                            lakeshoreManager.getStillHeaterOutput()) + " %")
                sendStillValue.isIdle()
                if buttonClicked == sendSampleValue.id and sendSampleValue.checkClick(event.pos):
                    try:
                        value = float(cleanFloatString(sampleSetPoint.text))
                        lakeshoreManager.setSampleHeaterOutputCurrent(value)
                    except ValueError:
                        sampleSetPoint.color = (255, 0, 0)
                    else:
                        rightEdge.updateLabel("SAMPLEHEATERVALUE", str(
                            lakeshoreManager.getSampleHeaterOutputCurrent()) + " mA")
                sendSampleValue.isIdle()
                if buttonClicked == stopWarmUp.id and stopWarmUp.checkClick(event.pos):
                    lakeshoreManager.stopWarmupHeater()
                    rightEdge.updateLabel("WARMUPHEATERVALUE", str(
                        lakeshoreManager.getWarmupHeaterOutput()) + " %")
                stopWarmUp.isIdle()
                if buttonClicked == stopStill.id and stopStill.checkClick(event.pos):
                    lakeshoreManager.stopStillHeater()
                    rightEdge.updateLabel("STILLHEATERVALUE", str(
                        lakeshoreManager.getStillHeaterOutput()) + " %")
                stopStill.isIdle()
                if buttonClicked == stopSample.id and stopSample.checkClick(event.pos):
                    lakeshoreManager.stopSampleHeater()
                    rightEdge.updateLabel("SAMPLEHEATERVALUE", str(
                        lakeshoreManager.getSampleHeaterOutputCurrent()) + " mA")
                stopSample.isIdle()

                if graphView and graphClicked:
                    graphClicked = False
                    # graphZoomed = True
                    # plt.close()
                    # size = (ceil(0.5*screenWidth), ceil(0.75*screenHeight))
                    # fig = plt.figure(figsize = [size[0]/100,size[1]/100], dpi = 100)
                    # ax = fig.gca()
                    # for ii in zoomVals:
                    #     ax.plot(zoomTimes, ii)
                    # ax.xaxis.set_major_locator(mdates.MinuteLocator(interval = int((len(zoomTimes)*lakeshoreManager.updateTime)/(60*5)+1)))
                    # plt.yscale('log')
                    # plt.legend(['Sensor' + str(ii+1) for ii in range(len(zoomVals))], loc = 'upper right')
                    # zxMin = min(zoomRect[0][0], zoomRect[1][0])
                    # zxMax = max(zoomRect[0][0], zoomRect[1][0])
                    # zyMin = max(zoomRect[0][1], zoomRect[1][1])
                    # zyMax = min(zoomRect[0][1], zoomRect[1][1])
                    # minX = min([min(zoomTimes[ii]) for ii in range(len(zoomVals))])
                    # maxX = max([max(zoomTimes[ii]) for ii in range(len(zoomVals))])

                    # minY = min([min(zoomVals[ii]) for ii in range(len(zoomVals))])
                    # maxY = max([max(zoomVals[ii]) for ii in range(len(zoomVals))])
                    # buffer = 0.05 * (maxY-minY)

                    # if zxMin < 0.33*screenWidth:
                    #     zxMin = minX
                    # else:
                    #     zxMin = (((zxMin- 0.33*screenWidth)/(0.6828*screenWidth-0.33*screenWidth))*(maxX-minX)+minX)
                    # if zxMax > 0.6828*screenWidth:
                    #     zxMax = maxX
                    # else:
                    #     zxMax = (((zxMax- 0.33*screenWidth)/(0.6828*screenWidth-0.33*screenWidth))*(maxX-minX)+minX)
                    # if zyMin > 0.8913*screenHeight:
                    #     zyMin = minY - buffer
                    # else:
                    #     zyMin = ((1-(zyMin - 0.3659*screenHeight)/(0.8913*screenHeight-0.3659*screenHeight))*(maxY-minY)+minY)
                    # if zyMax < 0.3659*screenHeight or zyMax > 0.8913*screenHeight:
                    #     zyMax = maxY + buffer
                    # else:

                    #     zyMax = ((1-(zyMax - 0.3659*screenHeight)/(0.8913*screenHeight-0.3659*screenHeight))*(maxY-minY)+minY)
                    # ax.set_xlim(zxMin, zxMax)
                    # ax.set_ylim(zyMin, zyMax)

                    # canvas = agg.FigureCanvasAgg(fig)
                    # canvas.draw()
                    # renderer = canvas.get_renderer()
                    # raw_data = renderer.tostring_rgb()
                    # #size = (800,800)
                    # graphImage = pygame.image.fromstring(raw_data, size, "RGB")

                if graphView and event.pos[0]/screenWidth >= 0.33 and event.pos[1]/screenHeight >= 0.3659\
                        and event.pos[0]/screenWidth <= 0.6828 and event.pos[1]/screenHeight <= 0.8913 and not graphZoomed and len(times):
                    graphClicked = True
                    zoomRect[0] = event.pos
                    zoomRect[1] = event.pos

                buttonClicked = ''

            if event.type == pygame.KEYUP:
                pm1ParameterNumberBox.type(event.key, event.unicode)
                pm1ParameterIndexBox.type(event.key, event.unicode)
                pm1ParameterValueBox.type(event.key, event.unicode)
                pm2ParameterNumberBox.type(event.key, event.unicode)
                pm2ParameterIndexBox.type(event.key, event.unicode)
                pm2ParameterValueBox.type(event.key, event.unicode)
                logNameBox.type(event.key, event.unicode)
                warmUpSetpoint.type(event.key, event.unicode, numOnly=True)
                stillSetpoint.type(event.key, event.unicode, numOnly=True)
                sampleSetPoint.type(event.key, event.unicode, numOnly=True)

            if event.type == pygame.MOUSEMOTION:
                motionVector = (event.pos[0]-mousePos[0],
                                event.pos[1]-mousePos[1])
                mousePos = event.pos
                if clicked[2]:
                    pass
                    # background.move(motionVector[0], motionVector[1])

                # if graphView and graphClicked:
                    # zoomRect[1] = event.pos
            if event.type == pygame.MOUSEWHEEL:
                pass
                # background.scale(event.y)
        screen.fill((255, 255, 255))
        if not graphView:
            background.draw()
        else:
            screen.blit(graphImage, (ceil(0.25*screenWidth),
                        ceil(0.25*screenHeight)))
            # if graphClicked:
            # pygame.draw.rect(screen, (0,0,0), pygame.Rect(min(zoomRect[0][0], zoomRect[1][0]), min(zoomRect[0][1], zoomRect[1][1]), abs(zoomRect[0][0]-zoomRect[1][0]), abs(zoomRect[0][1]-zoomRect[1][1])), width = 1)
        toggleViewButton.draw()

        if graphZoomed:
            resetViewButton.draw()
        leftEdge.draw()
        rightEdge.draw()
        topEdge2.draw()
        topEdge.draw()

        pm2ParameterNumberBox.draw()
        pm2ParameterIndexBox.draw()
        pm2ParameterValueBox.draw()
        pm2QueryTypeDropdown.draw()
        pm1ParameterNumberBox.draw()
        pm1ParameterIndexBox.draw()
        pm1ParameterValueBox.draw()
        pm1QueryTypeDropdown.draw()
        pm1SendQueryButton.draw()

        pm2SendQueryButton.draw()

        toggleLogButton.draw()

        pauseLogButton.draw()
        warmUpSetpoint.draw()
        stillSetpoint.draw()
        sampleSetPoint.draw()
        stopWarmUp.draw()
        stopStill.draw()
        stopSample.draw()
        sendWarmUpValue.draw()
        sendStillValue.draw()
        sendSampleValue.draw()

        if not logging:
            logNameBox.draw()

        pygame.display.flip()


if __name__ == '__main__':
    main()
