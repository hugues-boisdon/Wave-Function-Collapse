""" Wave Function Collapse library
Author : Hugues Boisdon
"""

# Imports
from enum import Enum
from random import randint, choice
from abc import ABC, abstractmethod
from PIL import Image
import numpy as np

# Constants
NULL_CHAR = "."


# Connections

class ConnectionsManager:
    """class managing the connections of a tile"""
    class ConnectionsTypes(Enum):
        """every connections types possible"""
        UP    = 0
        RIGHT = 1
        DOWN  = 2
        LEFT  = 3
    
    def ConnectionTypesFromOther(self, type:ConnectionsTypes):
        """Connection type for this manager when called by connection type from another.   
        Ex: other: RIGHT(1) -> this: LEFT(3) """
        ret = 0
        if type.value < 2:
            ret = type.value + 2
        else:
            ret = type.value - 2
        return ret
    
    connections :list

    def __init__(self):
        self.connections = [[] for type in range(len(self.ConnectionsTypes))]

    def __str__(self):
        ret = ""
        for t, c in zip(self.ConnectionsTypes, self.connections):
            ret += f' {t.name}: {c}'
        return ret

    def addConnection(self, id:int=0, type:ConnectionsTypes=ConnectionsTypes.UP):
        if id not in (c:=self.connections[type.value]):
            c.append(id)

    
# tiles

class TileType:
    """class that defines a type of a tile with id and rules"""
    id :int=0
    rules :ConnectionsManager

    def __init__(self, id:int=0) -> None:
        self.id = id
        self.rules = ConnectionsManager()

    def __str__(self):
        return f'type: {self.id}, rules : '+str(self.rules)
    

class UncollapsedTile:
    """tile not yet collapsed"""
    possibilities :list

    def __init__(self, typesPossible:list=[0]):
        self.possibilities =  typesPossible
    
    def __str__(self):
        return NULL_CHAR
    
    def notPossible(self, type:int=0):
        if type in self.possibilities:
            self.possibilities.pop(type)
    
    def collapse(self) -> int:
        ret = -1
        if len(self.possibilities) > 0:
            ret = choice(self.possibilities)
        return ret
    





# Patterns are the seed for the WFC algorithm 

class Pattern:
    
    size :tuple=(1,1)
    tiles : dict

    def __init__(self, size:tuple=(1,1)) -> None:
        self.size = size
        self.tiles = {}

    def __str__(self):
        ret = ""
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                ret += str(self.tiles[(x, (self.size[1]-1)-y)]) + " "
            ret += "\n"
        return ret
        


# 'Maps' are the output of the WFC algorithm



class Map:

    def __init__(self, size:tuple=(1,1), allTypes:dict={}):
        self.size = size
        self.types = allTypes
        self.map = {}
        self.uncollapsed = []

        for x in range(size[0]):
            for y in range(size[1]):
                self.uncollapsed.append(UncollapsedTile(list(allTypes.keys())))
                self.map[(x,y)] = self.uncollapsed[-1]


    def __str__(self):
        ret = ""
        strSize = f'{self.size}'
        lenght = self.size[0]-len(strSize)
        firstSpacer = "="*(lenght//2)
        secondSpacer = firstSpacer + "="*(lenght%2)

        print(firstSpacer+strSize+secondSpacer)
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                ret += str(self.map[(x, (self.size[1]-1)-y)])
            ret += "\n"
        return ret


    def collapseAuto(self):
        self.uncollapsed = sorted(self.uncollapsed, key=lambda tile: len(tile.possibilities))
        if len(self.uncollapsed) == self.size[0]*self.size[1]:
            tileTocollapse = self.map[(self.size[0]//2,self.size[1]//2)]
            self.uncollapsed.remove(tileTocollapse)
        else:
            tileTocollapse = self.uncollapsed.pop(0)
        tileType = tileTocollapse.collapse()
            
        pos  = [k for (k,v) in self.map.items() if v == tileTocollapse][0]
        self.map[pos] = tileType
        if tileType > -1:
            rules = self.types[tileType].rules
            dirs = [(0,1), (1,0), (0,-1), (-1,0)] # up, right, down, left
            for connectionType, currentDir in zip(ConnectionsManager.ConnectionsTypes, dirs):
                newPos = (pos[0]+currentDir[0], pos[1]+currentDir[1])
                if newPos in self.map and isinstance(self.map[newPos],UncollapsedTile):
                    tile = self.map[newPos]
                    newPossibilities = []
                    for p in tile.possibilities:
                        if p in rules.connections[connectionType.value]:
                            newPossibilities.append(p)
                    tile.possibilities = newPossibilities
                    









# WFC algorithm Implementation

class WFC_Algorithm:
    tileTypes :dict

    def fit(self, pattern:Pattern):
        self.tileTypes = {}
        dirs = [(0,1), (1,0), (0,-1), (-1,0)] # up, right, down, left

        for (x,y), i in pattern.tiles.items():
            if not i in self.tileTypes:
                self.tileTypes[i] = TileType(i)

            for connectionType, currentDir in zip(ConnectionsManager.ConnectionsTypes, dirs):
                newPos = (x+currentDir[0], y+currentDir[1])
                if newPos in pattern.tiles:
                    currentId = pattern.tiles[newPos]
                    self.tileTypes[i].rules.addConnection(currentId, connectionType)
    
    def printRules(self):
        for t in self.tileTypes.values():
            print(f'{t}')
    
    def generate(self, size:tuple=(10,10)):
        ret = Map(size, self.tileTypes)
        while len(ret.uncollapsed) > 0:
            ret.collapseAuto()
        return ret

    

class WFC_Wrapper(ABC):
    
    def __init__(self):
        self.fitted = False
        self.algo = WFC_Algorithm()
        self.map = None
        self.pattern = Pattern()
    
    def fit(self):
        self.fitted = True

    def execute(self, size:tuple=(10,10)):
        ret = None
        if self.fitted:
            ret = self.algo.generate(size)
        return ret
        


class WFC_TXT(WFC_Wrapper):

    def __init__(self):
        super().__init__()
        self.typesToChar = {}

    def fit(self, path:str):
        super().fit()
        self.pattern = Pattern()
        self.typesToChar = {-1: NULL_CHAR}
        with open(path,encoding='utf-8') as file:
            lines = file.readlines()
        
        y = 0
        for l in lines[::-1]:
            x = 0
            row = (l).replace(" ","xoxo").strip().replace("xoxo"," ")
            if len(row) > 0:
                print(row)
                for char in row:
                    if char not in self.typesToChar.values():
                        self.typesToChar[index] = char
                        index += 1
                    self.pattern.tiles[(x,y)] = [k for (k,v) in self.typesToChar.items() if v == char][0]
                    x += 1
                y +=1
        self.pattern.size = (x, y)
        self.algo.fit(self.pattern)
        print(self.typesToChar)
        self.algo.printRules()


    def execute(self, size:tuple=(10,10)):
        newMap = super().execute(size)
        for k,v in newMap.map.items():
            newMap.map[k] = self.typesToChar[v]
        return newMap


class WFC_IMG(WFC_Wrapper):

    def __init__(self):
        super().__init__()
        self.typesToColors = {}

    def fit(self, path:str):
        super().fit()
        self.typesToColors = {}
        with Image.open(path) as img:
            colors = list(img.convert('RGB').getdata())
            size = img.size
        self.pattern = Pattern(size)

        (x,y) = (0,0)
        index = 0
        for c in colors:
            if c not in self.typesToColors.values():
                self.typesToColors[index] = c
                index += 1
            self.pattern.tiles[(x,y)] = [k for (k,v) in self.typesToColors.items() if v == c][0]
            x = (x+1)%size[0]
            if x == 0:
                y += 1
        self.algo.fit(self.pattern)
        print(self.typesToColors)
        self.algo.printRules()
            



    def execute(self, size:tuple=(10,10)):
        newMap = super().execute(size)
        colors = []
        for y in range(size[1]):
            for x in range(size[0]):
                if (t := newMap.map[(x,y)]) > -1:
                    colors.append(self.typesToColors[t])
                else :
                    colors.append((255,0,255))
        im = Image.new('RGB', newMap.size)
        im.putdata(colors)
        im.save('image.png')



        


        

                



