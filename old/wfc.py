""" Wave Function Collapse library
Author : Hugues Boisdon
"""

# Imports
from math import log
import numpy as np
from random import randint, choice

from PIL  import Image

import os
import glob

# Constants


# Functions



# Classes

class Pattern:

    N           :int   # The Pattern will be of size (N x N)
    probability :int   # Probability of this pattern within the patterns distribution
    pixels      :dict  # Pixels of the pattern accessible with (x,y) coordinates ((0,0) being the center pixel)


    def __init__(self, N:int=3) -> None:
        """Constructor of the Pattern class"""
        self.N = N
        self.probability = 0
        self.pixels      = {}
    
    def __eq__(self, other) -> bool:
        """Equality on patterns is purely pixel based"""
        return list(self.pixels.values()) == list(other.pixels.values())
    
    def save(self, path:str) -> None:
        
        pixelsRaw  = list(self.pixels.values())
        pixelsNice = []
        for i in range(self.N):
            pixelsNice.append(pixelsRaw[i*self.N:(i+1)*self.N:])

        pixelArray = np.array(pixelsNice, dtype=np.uint8)
        img = Image.fromarray(pixelArray)
        img.save(path)
    
    def getColorsList(self):
        return list(self.pixels.values())





class Region:

    model        =None   # A reference to the model
    coefficients :list   # list of the coefficients (True/False) in the superposition of patterns
    entropy      :float  # The Shannon entropy for this cell
    pixels       :dict   # Pixels of the Region accessible with (x,y) coordinates ((0,0) being the center pixel)
    center       :tuple  # the position of the region's center pixel in the output image

    def __init__(self, model, centerPos:tuple=(0,0)) -> None:
        """Constructor of the Cell class"""
        self.model = model
        self.entropy = 1.
        self.coefficients = [True for pattern in model.patterns]
        self.pixels = {}
        self.center = centerPos
    
    def ShannonEntropy(self) -> float:
        """Calculates the Shannon Entropy for this Region"""
        entropy = 0
        for i, pattern in enumerate(self.model.patterns):
            if self.coefficients[i]:
                entropy -= pattern.probability * log(pattern.probability)
        self.entropy = entropy
        return entropy
    
    def getColorsList(self):
        return list(self.pixels.values())


class Model:

    N         :int   # The patterns will be of size (NxN)
    patterns  :list  # The list of patterns found in the input image
    pWp       :list  # The pixels' location within a pattern
    pW        :int   # The width of the patterns

    W         :int   # The width of the output image
    H         :int   # The height of the output image
    cells     :dict  # The output cells accessible with (x,y) coordinates ((0,0) being the top-left)


    def __init__(self):
        """Constructor of the Model class"""
        self.patterns    = []
        

    def set(self, path:str, N:int=3):
        """Load the imput image found at path and find all the patterns of size (N x N)"""
        self.N = N
        self.pW  = (N//2)
        self.pWp = [(x,y) for y in range(-self.pW, 1+self.pW) for x in range(-self.pW, 1+self.pW)]

        with Image.open(path, 'r') as img: # loading the image
            iW, iH = img.size
            pixels = img.load()

        self.patterns = []
        patternCount = 0

        for y in range(self.pW, iH-self.pW):
            for x in range(self.pW, iW-self.pW):
                # for all valid pattern center in the image

                newP = Pattern() # create a new Pattern
                for offset in self.pWp:
                    pos = (x+offset[0], y+offset[1])
                    newP.pixels[offset] = pixels[pos] # fill all the pattern's pixel
                
                found = False
                for p in self.patterns:
                    if newP == p: # if the pattern has already been found
                        self.patterns[self.patterns.index(newP)].probability += 1
                        found = True
                if not found:
                    self.patterns.append(newP)
                    newP.probability = 1
                patternCount += 1
        
        for p in self.patterns:
            p.probability /= patternCount


    def savePatterns(self, folderPath:str) -> None:
        """Save the patterns as png files"""

        odlFiles = glob.glob(folderPath+'*')
        for f in odlFiles:
            os.remove(f)  # Clearing the folder of older pattern images

        for i, pattern in enumerate(self.patterns):
            pattern.save(folderPath+f'{i}.png') # Saving the patterns as PNGs
        

    def getRegion(self, centerPos:tuple=(1,1)):
        region = Region(self, centerPos) # create a new Region (we're using the pattern class for more simplicity)
        for offset in self.pWp:
            pos = (centerPos[0]+offset[0], centerPos[1]+offset[1])
            region.pixels[offset] = (self.pixels[pos]) # fill the region
        return region



    def generate(self, size:tuple=(10,10)) -> None:
        """Generate an output image with the size passed """
        if self.patterns == None:
            print("model not set")
            return

        self.W, self.H = size
        self.pixels = {(x,y):(0,0,0,0) for y in range(self.H) for x in range(self.W)} # Initialising the output image pixels
        self.regions = []

        # Creating all the region
        for y in range(self.pW, self.H-self.pW):
                for x in range(self.pW, self.W-self.pW):
                    # for all valid region center in the image
                    self.regions.append(self.getRegion(centerPos=(x,y)))
        self.uncollapsed = [region for region in self.regions]


        while len(self.uncollapsed) > 0:  # while there is an uncollapsed region

            minRegion = choice(self.uncollapsed)
            minRegion.ShannonEntropy()

            # let's find the minimal (N x N) region in the output image
            for region in self.uncollapsed:
                    entropy = region.ShannonEntropy()
                    if entropy < minRegion.entropy : # Checking if this region has the less entropy
                        minRegion = region
            
            print(minRegion.center)
            


            self.uncollapsed = []
            

                    

                    



        





            


