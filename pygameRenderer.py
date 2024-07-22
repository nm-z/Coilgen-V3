import pygame       #python game library, used for its nice window management and easy UI code
import pygame.freetype
import numpy as np  #general math library
import time         #used for FPS counter
from typing import Callable # just for type-hints to provide some nice syntax colering

## some basic math functions for 2D cartesian systems:
def distAngleBetwPos(posOne, posTwo): #returns distance and angle between 2 positions
    """get distance and angle between 2 positions (2-sized arrays/lists)"""
    funcPosDelta = [posTwo[0]-posOne[0], posTwo[1]-posOne[1]]
    funcDistance = 0 #var init
    funcAngle = np.arctan2(funcPosDelta[1], funcPosDelta[0]) 
    if(abs(funcPosDelta[0]) < 0.0001): #sin(angle) can be 0, which results in divide by 0 errors.
        funcDistance = abs(funcPosDelta[1])
    elif(abs(funcPosDelta[1]) < 0.0001): #floating point error, alternatively you could check the angle
        funcDistance = abs(funcPosDelta[0])
    else:
        funcDistance = funcPosDelta[1]/np.sin(funcAngle)  #soh
        #funcDistance = funcPosDelta[0]/np.cos(funcAngle)  #cah
    return(np.array([funcDistance, funcAngle])) #return an np.array because the alternative is a tuple, which is (needlessly) immutable

def distSqrdBetwPos(posOne, posTwo): #returns distance^2 between 2 positions (useful for efficient distance thresholding)
    """get distance squared between 2 positions (2-sized arrays/lists), useful for efficient distance thresholding (compare to threshold squared)"""
    return((posTwo[0]-posOne[0])**2 + (posTwo[1]-posOne[1])**2)  #A^2 + B^2 = C^2

def distAnglePosToPos(funcRadius, funcAngle, funcPos): #returns a new pos given an angle, distance and starting pos
    """get position that is the entered distance and angle away from the entered position"""
    return(np.array([funcPos[0] + funcRadius * np.cos(funcAngle), funcPos[1] + funcRadius * np.sin(funcAngle)]))

ASA = lambda scalar, inputArray : [scalar + entry for entry in inputArray]

### some fancy key-binding visuals:
fancyKeyBindImageLoaded = False # if the keyboard fails to load, the rest of the code should just run anyway
try: # the fancy keyboard stuff
    import fancy.keyboard_fancy as KB_fcy
    fancyKeyBindImageLoaded = True
except Exception as excep:
    print("failed to load fancy keyboard stuff. Exception:", excep)

def generateFancyKeyBindingImage(maxRes: tuple[int,int], silent:bool=False) -> pygame.Surface:
    """ produce a legend of all the key bindings. Only call if(fancyKeyBindImageLoaded == True) """
    if(not fancyKeyBindImageLoaded):  print("can't generateFancyKeyBindingImage(), because fancyKeyBindImageLoaded == False");  return(None)
    ## some sub-functions:
    def drawRectAlpha(surfaceToDrawOn:pygame.Surface, colorWithAlpha:pygame.Color|tuple[int,int,int,int], rect:pygame.Rect):
        rect_surf = pygame.Surface(rect.size, pygame.SRCALPHA) # drawing with alpha requires a little more effort
        pygame.draw.rect(rect_surf, colorWithAlpha, rect_surf.get_rect())
        surfaceToDrawOn.blit(rect_surf, rect_surf.get_rect().move(*rect.topleft))
    def HSVAcolor(hueIndex:float=1.0, saturation:float=1.0, value:float=1.0, alpha:float=1.0) -> pygame.Color:
        color = pygame.Color(0,0,0,0) # init var
        color.hsva = (int(hueIndex*360),int(saturation*100),int(value*100),int(alpha*100)) # Note: the hueIndex multiplier should not be easily multiply to a multiple of 360
        return(color)
    ## house everything in a try-except, as this is kinda funky (and definitly NOT backwards-compatible)
    try:
        import pygameUI as PGUI
        keyBindColorList: dict[str,pygame.Color] = PGUI.keyBindings.copy() # copy the list and replace the (whole!) entries with color objects
        ## start with the keyboard itself:
        keyboardSurface: pygame.Surface = KB_fcy.keyboardImage.copy()
        colorCounter = 0
        for bindingName in PGUI.keyBindings: # Note: iterator 'bindingName' is the name to display in the legend, and the key (asin dict{} key) to retrieve the (list of) keycode(s)
            ## pick a color
            hue = colorCounter/len(PGUI.keyBindings);  saturation = 0.5 + (0.5 * np.random.random());  value = 0.5 + (0.5 * np.random.random());  alpha = 0.5 + (0.25 * np.random.random()) # TBD: improve?
            keyBindColorList[bindingName] = HSVAcolor(hue, saturation, value, alpha) # generate a unique color
            colorCounter += 1 # bit of a crappy forloop, but whatever (Dicts will be Dicts)
            ## find the keys (that corrospond to the current bind-group) and color them in
            keyCodesToColor: list[int] = []
            if(type(PGUI.keyBindings[bindingName]) is int): # if it's a single key binding
                keyCodesToColor.append(PGUI.keyBindings[bindingName])
            else: # assume the key binding is in an iterable (list, tuple, etc.)
                keyCodesToColor = PGUI.keyBindings[bindingName] # replace list
            for keyCode in keyCodesToColor:
                for (keyCodes, boundingRect) in KB_fcy.keyBoundingBoxes:
                    if(keyCode == keyCodes[0]):
                        drawRectAlpha(keyboardSurface, keyBindColorList[bindingName], pygame.Rect(boundingRect))
                        break # bounding box and key binding are successfully paired, move onto the next key (but use the same color)
        ## next, make a legend of all the key bindings
        ## (NOTE: you could try to predict whether it will fit within maxRes here, but it's just easier to do it inefficiently...)
        legendFontArgs = ['Century Gothic', 20, True, False] # font parameters as: [font_name, size, BOLD, italic]
        legendFont = pygame.font.SysFont(*legendFontArgs) # Note: font size may shrink, depending on whether the whole thing fits on the screen or not
        legendFontColor = pygame.Color(0,0,0);  legendBackgroundColor = pygame.Color(255,255,255) # black letters, white background (to match the keyboard image)
        for renderRetryCount in range(3): # should only repeat once at most. loop is broken by break call when it the thing fits into maxRes
            renderedFonts: list[pygame.Surface] = [] # init list
            legendSurfaceMinWidth: int = 0;   legendTextEdgeMargin = 10;   legendTextSpacing = 2
            for bindingName in keyBindColorList:
                boundKeyString: str = " "
                if(type(PGUI.keyBindings[bindingName]) is int): # if it's a single key binding
                    boundKeyString += pygame.key.name(PGUI.keyBindings[bindingName]) # single key
                else: # assume the key binding is in an iterable (list, tuple, etc.)
                    for i in range(len(PGUI.keyBindings[bindingName])): # multiple key
                        boundKeyString += pygame.key.name(PGUI.keyBindings[bindingName][i])  +  (" / " if(i<(len(PGUI.keyBindings[bindingName])-1)) else "")
                invertedColor = pygame.Color(255-keyBindColorList[bindingName].r, 255-keyBindColorList[bindingName].g, 255-keyBindColorList[bindingName].b, 255-keyBindColorList[bindingName].a)
                # combinedLegendEntrySurface = legendFont.render(boundKeyString + "  -> " + bindingName, False, legendFontColor, keyBindColorList[bindingName]) # the quicker way
                boundKeyText = legendFont.render(boundKeyString+" ", False, invertedColor, keyBindColorList[bindingName]) # color the background of the text like the corrosponding keys
                functionText = legendFont.render(" = " + bindingName, False, legendFontColor, legendBackgroundColor)
                combinedLegendEntrySurface = pygame.Surface([boundKeyText.get_width()+functionText.get_width(), max(boundKeyText.get_height(),functionText.get_height())]) # init combined text surface
                combinedLegendEntrySurface.blits(((boundKeyText,[0,0]),(functionText,[boundKeyText.get_width(),0])),False) # blit the texts together
                renderedFonts.append(combinedLegendEntrySurface)
                legendSurfaceMinWidth = max(legendSurfaceMinWidth, renderedFonts[-1].get_width()) # widest text determines legend width
            legendSurface = pygame.Surface([legendSurfaceMinWidth + legendTextEdgeMargin, len(keyBindColorList) * (legendFont.get_linesize()+legendTextSpacing) + legendTextEdgeMargin])
            legendSurface.fill(legendBackgroundColor)
            for i in range(len(renderedFonts)):
                legendSurface.blit(renderedFonts[i], [int(legendTextEdgeMargin/2), int(legendTextEdgeMargin/2) + (i * (legendFont.get_linesize() + legendTextSpacing))])
            ## combine the keyboard and the legend:
            completeLegendSurface = pygame.Surface([keyboardSurface.get_width()+legendSurface.get_width(), max(keyboardSurface.get_height(),legendSurface.get_height())])
            completeLegendSurface.fill(legendBackgroundColor)
            completeLegendSurface.blits(((keyboardSurface,[0,0]),(legendSurface,[keyboardSurface.get_width(),0])),False)
            ## now take a small detour to save an image (for the github README, mostly)
            if(renderRetryCount == 0): # only save the highest-res version
                pygame.image.save(completeLegendSurface, "keyBindLegend.png")
            ## (this next part is not very efficient...) See if the keyboard + legend fits, and if it doesn't, resize the keyboard and re-render the text
            if((completeLegendSurface.get_width() > maxRes[0]) or (completeLegendSurface.get_height() > maxRes[1])): # if the created image is too large
                ## OH NO, the whole thing was too large!. Figure out what dimensions it should have been, scale the keyboard image and re-render the text
                scalar = min(maxRes[0]/completeLegendSurface.get_width(), maxRes[1]/completeLegendSurface.get_height()) # make it just barely fit
                # keyboardSurface = pygame.transform.scale_by(keyboardSurface, scalar) # Note: this function was only introduced in pygame 2.1.3, so i'll just stick with the old scale() for now
                keyboardSurface = pygame.transform.scale(keyboardSurface, [int(keyboardSurface.get_width()*scalar), int(keyboardSurface.get_height()*scalar)]) # Note: in pygame 2.1.3, a function
                legendFontArgs[1] = max(8, int(scalar*(legendFont.get_ascent()-1))) # update scale. NOTE: not sure why, but 'ascent'-1 is the 'size' value in this initializer
                legendFont = pygame.font.SysFont(*legendFontArgs) # to change the font size, the whole thing needs to re-init. That's why legendFontArgs exist
            else: break # the whole thing fits within the maxRes, return that sucker!
        return(completeLegendSurface)
    except Exception as excep:
        if(not silent):  print("failed to render fancy key binding thingy. Exception:", excep)


class pygameWindowHandler():
    """ a handler for a pygame window. This class does not render things,
         it just handles the basic interactions with the OS,
         like opening, closing changing resolution, etc."""
    def __init__(self, resolution: tuple[int,int], windowName:str="(pygame) window", iconFilename:str|None=None):
        """initialize pygame window
            (one pygame window can host multiple pygameDrawer objects by using the drawOffset variable)"""
        self.windowStarted = False # just handy for debug
        self.keepRunning = False # intended to be set to false by the UI handler (or any other code of course) when the window should close
        pygame.init()
        # pygame.font.init() # automatically done in pygame.init()
        # pygame.freetype.init() # automatically done in pygame.init()
        self.window: pygame.Surface = pygame.display.set_mode(resolution, pygame.RESIZABLE)
        self.oldWindowSize: tuple[int, int] = self.window.get_size()
        pygame.display.set_caption(windowName)
        if((iconFilename != "") if (iconFilename is not None) else False):
            try: pygame.display.set_icon(pygame.image.load(iconFilename))
            except Exception as excep: print("failed to replace pygame icon from filename:", iconFilename, " Exception:", excep)
        self.windowStarted = True # indicate that the code ran successfully
        self.keepRunning = True

    def __del__(self):
        self.end()

    def end(self):
        """deinitialize the pygame window (required for ending without crashing)"""
        if(self.windowStarted): #if the window never started, quit might error out or something stupid
            print("quitting pygame window...")
            pygame.quit()
            self.keepRunning = False # should already have been done, but just to be sure
            self.windowStarted = False # just in case end() is called multiple times

    def frameRefresh(self):
        """push the drawn frame(buffer) to the display"""
        pygame.display.flip() #send (finished) frame to display

    # @staticmethod
    # def frameRefresh():
    #     """push the drawn frame(buffer) to the display"""
    #     pygame.display.flip() #send (finished) frame to display




class pygameDrawer():
    def __init__(self, windowHandler: pygameWindowHandler, drawSize:tuple[int,int]=None, drawOffset:tuple[int,int]=(0,0), sizeScale:float=15, invertYaxis:bool=True):
        self.windowHandler = windowHandler
        self.drawSize :tuple[int,int]= ((int(drawSize[0]),int(drawSize[1])) if (drawSize is not None) else self.windowHandler.oldWindowSize) # width and height of the display area (does not need to be 100% of the window)
        self.drawOffset :tuple[int,int]= (int(drawOffset[0]), int(drawOffset[1])) #draw position offset, (0,0) is topleft
        self.viewOffset :list[float,float]= [0.0, 0.0] #'camera' view offsets, changing this affects the real part of realToPixelPos()
        self.sizeScale :float= sizeScale #pixels per meter
        self.invertYaxis :bool= invertYaxis #pygame has pixel(0,0) in the topleft, so this just flips the y-axis when drawing things

        self.minSizeScale = 5.0 # note: the unit for sizeScale is pixels per millimeter, so there's no need to make this too small
        self.maxSizeScale = 2000.0 # a reasonable limit to how much you can zoom in
        # self.maxSizeScaleWithCar = 500.0 # zooming in too much makes drawing (the car) really slow (because it has to render the car image at such a high resolution)
        self.centerZooming = False # whether zooming (using the scroll wheel) uses the center of the screen (or the mouse position)

        # [255,255,0] #yellow
        # [0,50,255] #dark blue
        # [127,127,0] #faded yellow
        # [0,25,127] #faded blue
        # [127, 20, 0] #faded red
        # [0,220,255] #light blue

        self.bgColor = [50,50,50] #dark gray
        
        self.normalFontColor = [200, 200, 200]
        # self.normalFont = pygame.freetype.SysFont('Calibri', 25, bold=False, italic=False) # TODO: move to freetype font (pygame docs seem to like it better). Requires some changes further down
        self.normalFont = pygame.font.SysFont('Century Gothic', 25, bold=True, italic=False)
        
        self.gridColor = [100,100,100] #light gray
        gridFontSize = max(int((((self.normalFont.height//100) if (isinstance(self.normalFont, pygame.freetype.Font)) else self.normalFont.get_height()) * 0.66)), 10) #
        self.gridFont = pygame.font.SysFont('Calibri', gridFontSize, bold=False, italic=True)
        
        self.movingViewOffset = False
        self.prevViewOffset = (self.viewOffset[0], self.viewOffset[1])
        self.movingViewOffsetMouseStart = [0,0]

        self.layerColors = [[255,  0,  0], # red
                            [153,153,102], # grayish brown
                            [  0,128,  0], # dark green
                            [  0,255,  0], # bright green
                            [188,142,  0], # light brown
                            [  0,  0,255]] # blue
        
        self.FPStimer = time.time()
        self.FPSdata = []
        self.FPSdisplayInterval = 0.25
        self.FPSdisplayTimer = time.time()
        self.FPSrenderedFonts: list[pygame.Surface] = []
        
        self.statDisplayTimer = time.time()
        self.statDisplayInterval = 0.1
        self.statRenderedFonts: list[pygame.Surface] = []

        self.lastFilename = "" # the name of a loaded file

        self.drawGrid = True #a simple grid to help make clear how big units of measurement are. (TBD in 3D rendering mode!)
        
        try:
            # self.viewOffset = [((self.drawSize[0]/self.sizeScale)/2), ((self.drawSize[1]/self.sizeScale)/2)] # center view on (0.0,0.0) coordinate
            self.viewOffset = [(2*(self.drawSize[0]/self.sizeScale)/3), ((self.drawSize[1]/self.sizeScale)/2)] # put (0.0,0.0) coordinate at 2/3 to the right of the screen
            # self.viewOffset = # TBD: center view on thing
            # self.sizeScale = # TBD: show whole thing
        except Exception as theExcept:
            print("couldn't set viewOffset and sizeScale to show the thing:", theExcept)

        self.showHelpScreen = False # display the keyboard bindings in a fun and visual way
        if(fancyKeyBindImageLoaded): # only if the keyboard stuff actually loaded correctly
            self.keyBindImageRendered = generateFancyKeyBindingImage(self.drawSize)

        self.localVar = None # a terrible hack to get python pointers
        self.localVarUpdated = False # a flag for UI interactions to set
        self.debugText: dict[str,list[str]] = None # a list of some text to display
        self.debugTextKey: str = 'few' # when no key is selected, default to empty string
        from __main__ import coilClass, mmCopperToOz # bad
        self.makeDebugText: Callable[['coilClass'], dict[str,list[str]]] = lambda coil:{     'few' : [
                                                                                    "diam [mm]: "+str(round(coil.diam, 1)),
                                                                                    "shape: "+coil.shape.__class__.__name__,
                                                                                    "turns: "+str(coil.turns),
                                                                                    "traceWidth [mm]: "+str(round(coil.traceWidth, 2)),
                                                                                    "clearance [mm]: "+str(round(coil.clearance, 2)),
                                                                                    "um copper: "+str(round(coil.copperThickness * 1000, 1)),
                                                                                    "layers: "+str(coil.layers),
                                                                                    (("PCBthickness [mm]: "+str(round(coil.PCBthickness, 2))) if (coil.layers>1) else ""),
                                                                                    "resistance [mOhm]: "+str(round(coil.calcTotalResistance() * 1000, 2)),
                                                                                    "inductance [uH]: "+str(round(coil.calcInductance() * 1000000, 2)) ],
                                                                                        'all' : [
                                                                                    "diam [mm]: "+str(round(coil.diam, 2)),
                                                                                    "trueDiam [mm]: "+str(round(coil.calcTrueDiam(), 2)),
                                                                                    "simpleInnerDiam [mm]: "+str(round(coil.calcSimpleInnerDiam(), 2)),
                                                                                    "trueInnerDiam [mm]: "+str(round(coil.calcTrueInnerDiam(), 2)),
                                                                                    "trueDiamOffset [mm]: "+str(round(coil._calcTrueDiamOffset(), 2)),
                                                                                    "shape: "+coil.shape.__class__.__name__,
                                                                                    "formula: "+coil.formula,
                                                                                    "turns: "+str(coil.turns),
                                                                                    "traceWidth [mm]: "+str(round(coil.traceWidth, 2)),
                                                                                    "clearance [mm]: "+str(round(coil.clearance, 2)),
                                                                                    "um copper: "+str(round(coil.copperThickness * 1000, 1)),
                                                                                    "oz copper: "+str(round(mmCopperToOz(coil.copperThickness), 1)),
                                                                                    "layers: "+str(coil.layers),
                                                                                    (("PCBthickness [mm]: "+str(round(coil.PCBthickness, 2))) if (coil.layers>1) else ""),
                                                                                    (("layer spacing [mm]: "+str(round(coil.calcLayerSpacing(), 2))) if (coil.layers>1) else ""),
                                                                                    "lenght (uncoiled) [mm]: "+str(round(coil.calcCoilTraceLength(), 2)),
                                                                                    "return trace length [mm]: "+str(round(coil.calcReturnTraceLength(), 2)),
                                                                                    "resistance [mOhm]: "+str(round(coil.calcTotalResistance() * 1000, 2)),
                                                                                    "inductance [uH]: "+str(round(coil.calcInductance() * 1000000, 3)),
                                                                                    (("inductance 1-layer [uH]: "+str(round(coil.calcInductanceSingleLayer() * 1000000, 3))) if (coil.layers>1) else ""),
                                                                                    "induct/resist [uH/Ohm]: "+str(round(coil.calcInductance() * 1000000 / coil.calcTotalResistance(), 2)),
                                                                                    "induct/radius [uH/mm]: "+str(round(coil.calcInductance() * 1000000 / (coil.diam/2), 2)),
                                                                                    "induct/turns [uH/mm]: "+str(round(coil.calcInductance() * 1000000 / coil.turns, 2)) ] }
        
    def _updateViewOffset(self, mousePos: tuple[int,int]=None): #screen dragging
        """(UI element) if active (button press), 'drag' the screen around by using the mouse"""
        if(self.movingViewOffset):
            if(mousePos is None):
                mousePos = pygame.mouse.get_pos()
            mouseDelta = [] #init var
            if(self.invertYaxis):
                mouseDelta = [float(mousePos[0] - self.movingViewOffsetMouseStart[0]), float(self.movingViewOffsetMouseStart[1] - mousePos[1])]
            else:
                mouseDelta = [float(mousePos[0] - self.movingViewOffsetMouseStart[0]), float(mousePos[1] - self.movingViewOffsetMouseStart[1])]
            self.viewOffset[0] = self.prevViewOffset[0] + (mouseDelta[0]/self.sizeScale)
            self.viewOffset[1] = self.prevViewOffset[1] + (mouseDelta[1]/self.sizeScale)

    def isInsideWindowPixels(self, pixelPos: np.ndarray):
        """whether or not a pixel-position is inside the window"""
        return((pixelPos[0] < (self.drawSize[0] + self.drawOffset[0])) and (pixelPos[0] > self.drawOffset[0]) and (pixelPos[1] < (self.drawSize[1] + self.drawOffset[1])) and (pixelPos[1] > self.drawOffset[1]))
    
    def drawFPScounter(self):
        """draw a little Frames Per Second counter in the corner to show program performance"""
        newTime = time.time()
        if((newTime - self.FPStimer)>0): #avoid divide by 0
            self.FPSdata.append(round(1/(newTime-self.FPStimer), 1))
        self.FPStimer = newTime #save for next time
        if((newTime - self.FPSdisplayTimer)>self.FPSdisplayInterval):
            self.FPSdisplayTimer = newTime
            FPSstrings = []
            if(len(self.FPSdata)>0):
                FPSstrings.append(str(round(np.average(np.array(self.FPSdata)), 1))) #average FPS
                FPSstrings.append(str(min(self.FPSdata)))                  #minimum FPS
                FPSstrings.append(str(max(self.FPSdata)))                  #maximum FPS
                self.FPSdata.sort()
                FPSstrings.append(str(self.FPSdata[int((len(self.FPSdata)-1)/2)])) #median FPS
                #print("FPS:", round(np.average(np.array(self.FPSdata)), 1), min(self.FPSdata), max(self.FPSdata), self.FPSdata[int((len(self.FPSdata)-1)/2)])
            else:
                FPSstrings = ["inf"]
                #print("FPS: inf")
            self.FPSdata.clear()
            self.FPSrenderedFonts.clear()
            for FPSstr in FPSstrings:
                self.FPSrenderedFonts.append(self.normalFont.render(FPSstr, False, self.normalFontColor)) #render string (only 1 line per render allowed), no antialiasing, text color opposite of bgColor
        for i in range(len(self.FPSrenderedFonts)):
            self.windowHandler.window.blit(self.FPSrenderedFonts[i], [self.drawOffset[0]+ self.drawSize[0]-5-self.FPSrenderedFonts[i].get_width(),self.drawOffset[1]+5+(i*self.normalFont.get_linesize())])
            ## NOTE: for tighter line spacing, consider using self.normalFont.get_height() instead of linesize
    
    def drawStatText(self):
        """draw some usefull information/statistics on-screen"""
        newTime = time.time()
        if((newTime - self.statDisplayTimer)>self.statDisplayInterval):
            self.statDisplayTimer = newTime
            statsToShow = [] # a list of strings
            # statsToShow.append(str(round(self.sizeScale, 2)))
            if((self.debugTextKey in self.debugText) if (self.debugText is not None) else False):
                [statsToShow.append(entry) for entry in self.debugText[self.debugTextKey] if (entry != "")]
                    
            self.statRenderedFonts.clear() # a list of rendered fonts (images)
            for textStr in statsToShow:
                self.statRenderedFonts.append(self.normalFont.render(textStr, False, self.normalFontColor))
        for i in range(len(self.statRenderedFonts)):
            self.windowHandler.window.blit(self.statRenderedFonts[i], [self.drawOffset[0]+5,self.drawOffset[1]+5+(i*self.normalFont.get_linesize())])
            ## NOTE: for tighter line spacing, consider using self.normalFont.get_height() instead of linesize
    
    def drawLoadedFilename(self):
        """shows the name of a loaded file in the corner of the screen"""
        if(len(self.lastFilename) > 0):
            renderedFont = self.normalFont.render(self.lastFilename, False, self.normalFontColor)
            self.windowHandler.window.blit(renderedFont, [self.drawOffset[0]+self.drawSize[0]-renderedFont.get_width()-5,self.drawOffset[1]+self.drawSize[1]-renderedFont.get_height()-5])
    
    #pixel conversion functions (the most important functions in here)
    def pixelsToRealPos(self, pixelPos: np.ndarray):
        """return a (real) position for a given pixel position (usually mouse position)
            (mostly used for UI)"""
        if(self.invertYaxis):
            return(np.array([((pixelPos[0]-self.drawOffset[0])/self.sizeScale)-self.viewOffset[0], ((self.drawSize[1]-pixelPos[1]+self.drawOffset[1])/self.sizeScale)-self.viewOffset[1]]))
        else:
            return(np.array([((pixelPos[0]-self.drawOffset[0])/self.sizeScale)-self.viewOffset[0], ((pixelPos[1]-self.drawOffset[1])/self.sizeScale)-self.viewOffset[1]]))
    
    def realToPixelPos(self, realPos: np.ndarray):
        """return the pixel-position (for pygame) for a given (real) position"""
        if(self.invertYaxis):
            return(np.array([((realPos[0]+self.viewOffset[0])*self.sizeScale)+self.drawOffset[0], self.drawSize[1]-((realPos[1]+self.viewOffset[1])*self.sizeScale)+self.drawOffset[1]])) #invert Y-axis for normal (0,0) at bottomleft display
        else:
            return(np.array([((realPos[0]+self.viewOffset[0])*self.sizeScale)+self.drawOffset[0], ((realPos[1]+self.viewOffset[1])*self.sizeScale)+self.drawOffset[1]]))
    
    #check if things need to be drawn at all    
    def isInsideWindowReal(self, realPos: np.ndarray):
        """whether or not a (real) position is inside the window (note: not computationally efficient)"""
        return(self.isInsideWindowPixels(self.realToPixelPos(realPos))) #not very efficient, but simple
    
    #drawing functions
    def _drawGrid(self):
        gridSpacing = 1.0 # line spacing (in meters). Should be calculated based on sizeScale, but that's TBD!
        ## attempt to calculate an appropriate scale for the grid (to minimize the number of lines drawn)
        gridSpacings = (10.0, 5.0, 2.0, 1.0, 0.5, 0.25, 0.1) # = (0.5, 1.0, 5.0, 10.0, 25.0)
        gridSpacingIndex = (np.log(self.sizeScale) - np.log(self.minSizeScale)) / (np.log(self.maxSizeScale) - np.log(self.minSizeScale)) # produces a number between 0 and 1 (linearized)
        gridSpacingIndex = min(int(gridSpacingIndex*len(gridSpacings)), len(gridSpacings)-1)
        gridSpacing = gridSpacings[gridSpacingIndex]
        lineWidth = int(1)
        ## first, figure out what the window sees. (keeping rotated views in mind)
        screenCenterRealPos = self.pixelsToRealPos(np.array(self.drawSize) / 2.0)
        roundedCenterPos = np.array([screenCenterRealPos[0]-(screenCenterRealPos[0]%gridSpacing), screenCenterRealPos[1]-(screenCenterRealPos[1]%gridSpacing)]) # rounded (down) to the nearest multiple of gridSpacing
        screenMaxRadiusSquared = distSqrdBetwPos(screenCenterRealPos, self.pixelsToRealPos(np.zeros(2))) # terribly inefficient, but whatever.
        gridIttToVal = lambda axis, value : (roundedCenterPos[axis]+(value*gridSpacing)) # obviously excessive use of lambda, but it makes it more abstract when rendering the text in the loop
        gridIttToPos = lambda x, y : np.array([gridIttToVal(0,x),gridIttToVal(1,y)],float) # to go from abstract grid forloop iterator (int) to actual coordinates (real, not pixel)
        withinScreenRadius = lambda x, y : (distSqrdBetwPos(screenCenterRealPos, gridIttToPos(x,y)) < screenMaxRadiusSquared) # the fastest check to see if a position is (probably/bluntly) visible
        ## the following code needs to be refactored to be a little shorter, but at least this is sort of legible and stuff
        def xloop(x): # vertical lines
            yMax = 0
            for y in range(0, 100):
                if(not withinScreenRadius(x,y)):
                    yMax = y;  break # yMax is found, stop this loop
            if(yMax == 0):
                return(False) # if the first entry was already outside the screenRadius, stop looping in this direction
            for y in range(-1, -100, -1):
                if(not withinScreenRadius(x,y)):
                    pygame.draw.line(self.windowHandler.window, self.gridColor, self.realToPixelPos(gridIttToPos(x,y)), self.realToPixelPos(gridIttToPos(x,yMax)), lineWidth) # draw the vertical line
                    textToRender = str(round(gridIttToVal(0,x),   len(str(gridSpacing)[max(str(gridSpacing).rfind('.')+1, 0):]))) # a needlessly difficult way of rounding to the same number of decimals as the number in the gridSpacings array
                    renderedFont = self.gridFont.render(textToRender, False, self.gridColor)
                    self.windowHandler.window.blit(renderedFont, [self.realToPixelPos(gridIttToPos(x,y))[0] + 5, self.drawOffset[1]+self.drawSize[1]-renderedFont.get_height() - 5]) # display the text at the bottom of the screen and to the right of the line
                    break # line is drawn, stop this loop
            return(True)
        for x in range(0, 100): # note: loop should break before reaching end!
            if(not xloop(x)):
                break
        for x in range(-1, -100, -1): # note: loop should break before reaching end!
            if(not xloop(x)):
                break
        def yloop(y): # horizontal lines
            xMax = 0
            for x in range(0, 100):
                if(not withinScreenRadius(x,y)):
                    xMax = x;  break # xMax is found, stop this loop
            if(xMax == 0):
                return(False) # if the first entry was already outside the screenRadius, stop looping in this direction
            for x in range(-1, -100, -1):
                if(not withinScreenRadius(x,y)):
                    pygame.draw.line(self.windowHandler.window, self.gridColor, self.realToPixelPos(gridIttToPos(x,y)), self.realToPixelPos(gridIttToPos(xMax,y)), lineWidth) # draw the horizontal line
                    textToRender = str(round(gridIttToVal(1,y),   len(str(gridSpacing)[max(str(gridSpacing).rfind('.')+1, 0):]))) # a needlessly difficult way of rounding to the same number of decimals as the number in the gridSpacings array
                    renderedFont = self.gridFont.render(textToRender, False, self.gridColor)
                    self.windowHandler.window.blit(renderedFont, [self.drawOffset[0]+self.drawSize[0]-renderedFont.get_width() - 5, self.realToPixelPos(gridIttToPos(x,y))[1] + 5]) # display the text at the bottom of the screen and to the right of the line
                    break # line is drawn, stop this loop
            return(True)
        for y in range(0, 100): # note: loop should break before reaching end!
            if(not yloop(y)):
                break
        for y in range(-1, -100, -1): # note: loop should break before reaching end!
            if(not yloop(y)):
                break

    def background(self):
        """draw the background and a grid (if enabled)"""
        self.windowHandler.window.fill(self.bgColor, (self.drawOffset[0], self.drawOffset[1], self.drawSize[0], self.drawSize[1])) #dont fill entire screen, just this pygamesim's area (allowing for multiple sims in one window)
        if(self.drawGrid):
            self._drawGrid()
    
    def _dashedLine(self, lineColor: pygame.Color, startPixelPos: np.ndarray, endPixelPos: np.ndarray, lineWidth: int, dashPixelPeriod=20, dashDutyCycle=0.5):
        """(sub function) draw a dashed line"""
        pixelDist, angle = distAngleBetwPos(startPixelPos, endPixelPos)
        for i in range(int(pixelDist/dashPixelPeriod)):
            dashStartPos = distAnglePosToPos(i*dashPixelPeriod, angle, startPixelPos)
            dashEndPos = distAnglePosToPos(i*dashPixelPeriod + dashPixelPeriod*dashDutyCycle, angle, startPixelPos)
            pygame.draw.line(self.windowHandler.window, lineColor, dashStartPos, dashEndPos, int(lineWidth))
    
    def drawKeyBindLegend(self):
        if((self.keyBindImageRendered is not None) if (fancyKeyBindImageLoaded and self.showHelpScreen) else False): # only if the keyboard stuff actually loaded correctly
            offset_temp = [self.drawSize[0]/2 - self.keyBindImageRendered.get_width()/2, self.drawSize[1]/2 - self.keyBindImageRendered.get_height()/2]
            self.windowHandler.window.blit(self.keyBindImageRendered, offset_temp)

    ## the arc drawing function works just fine, but it looks bad and makes the whole code terribly slow (not even my fault (this time), pygame is to blame)
    # def _shortArc(self, lineColor: pygame.Color, startPos: np.ndarray, endPos: np.ndarray, centerPos: np.ndarray, lineWidthReal: float):
    #     """draw an arc (in place of a straight line, which has some rendering limitations)
    #         radius of startPos and endPos (to centerPos) should not be too different, or it will look wrong"""
    #     startEndDistAngle = distAngleBetwPos(startPos, endPos)
    #     averageRadius = (distAngleBetwPos(centerPos, startPos)[0] + distAngleBetwPos(centerPos, endPos)[0]) / 2
    #     angleToAdjCenter = np.arccos((startEndDistAngle[0]/2) / averageRadius) # cos-1(a/h)
    #     adjCenterPos = distAnglePosToPos(averageRadius, startEndDistAngle[1] - angleToAdjCenter, startPos) # TODO: check if angle always correct (may need invert option)
    #     adjCenterPixelPos = self.realToPixelPos(adjCenterPos)
    #     boundBoxRadius = (averageRadius + (lineWidthReal/2)) * self.sizeScale
    #     boundingRect = [(adjCenterPixelPos[0]-boundBoxRadius, adjCenterPixelPos[1]-boundBoxRadius),   # (left,top), NOTE: self.invertYaxis missing
    #                     (boundBoxRadius*2, boundBoxRadius*2)] # (width, height)
    #     arcStartAngle = distAngleBetwPos(adjCenterPos, endPos)[1];   arcEndAngle = distAngleBetwPos(adjCenterPos, startPos)[1]
    #     pygame.draw.arc(self.windowHandler.window, lineColor, boundingRect, arcStartAngle, arcEndAngle, int(lineWidthReal * self.sizeScale))






    def drawLineList(self, lineLists: list[list[tuple[int,int]]]):
        """draw a series of lines (used for rendering coils)"""
        from __main__ import coilClass # bad code!
        coilToDraw: 'coilClass' = self.localVar # if it crashes here, then it's probably time to fix this whole mess (rewrite the rendering class interaction with __main__)

        # Validate and correct the structure of lineLists
        if not all(isinstance(sublist, list) and all(isinstance(coord, tuple) and len(coord) == 2 for coord in sublist) for sublist in lineLists):
            # Attempt to correct the structure or provide a fallback
            try:
                corrected_lineLists = [[(int(x), int(y)) for x, y in sublist] for sublist in lineLists]
                lineLists = corrected_lineLists
            except Exception as e:
                print(f"Failed to correct lineLists structure: {e}")
                return

        if((len(lineLists) < 1) or (len(lineLists) < min(coilToDraw.layers, 2))):
            print("can't drawLineList(), not enough lineLists provided")
            return

        if(len(lineLists[0]) < 2):
            print("can't drawLineList(), lineLists[0] too short!")
            return

        # Check if lineLists[0] has the required structure
        if not (isinstance(lineLists[0], list) and all(isinstance(j, tuple) and len(j) == 2 for j in lineLists[0])):
            print("can't drawLineList(), lineLists[0] does not have the required structure!")
            return

        isCircular = (True if isinstance(coilToDraw.shape.stepsPerTurn, float) else False) # only smooth corners for squares
        lineWidthPixels = int(coilToDraw.traceWidth * self.sizeScale)
        layerAdjust: Callable[[tuple[float,float],int], tuple[float,float]] = lambda pos, currentLayer : (pos[0] + coilToDraw.diam*currentLayer, pos[1]) # offset the positions of the different layers to make them visible

        if((coilToDraw.layers%2)!=0): # only in case of an un-even number of layers
            pygame.draw.line(self.windowHandler.window, self.layerColors[coilToDraw.layers % len(self.layerColors)], self.realToPixelPos((lineLists[0][-1][0], lineLists[0][0][1])), self.realToPixelPos(lineLists[0][-1]), lineWidthPixels) # draw return trace first

        for layerItt in range(coilToDraw.layers):
            currentLayer = coilToDraw.layers-1-layerItt
            currentLayerColor = self.layerColors[currentLayer % len(self.layerColors)] # draw layers back to front
            lineList = lineLists[currentLayer % 2] # one list is CW and the other is CCW. (NOTE: this replaces the mirroring of layerAdjust in previous versions)
            for i in range(len(lineList)-1):
                startPos = self.realToPixelPos(layerAdjust(lineList[i], currentLayer))
                endPos = self.realToPixelPos(layerAdjust(lineList[i+1], currentLayer))
                pygame.draw.line(self.windowHandler.window, currentLayerColor, startPos, endPos, lineWidthPixels)
                if(not isCircular):
                    pygame.draw.ellipse(self.windowHandler.window, currentLayerColor, [ASA(-((lineWidthPixels-2)/2), endPos), [lineWidthPixels, lineWidthPixels]]) # draw a little circle in the corners for a smoother look






        # Render loop antenna if enabled and available in lineLists
        self.debugPrinted = False
        if coilToDraw.loop_enabled and len(lineLists) > coilToDraw.layers:
            loop_antenna_coords = lineLists[coilToDraw.layers]
            loop_color = (255, 0, 0)  # Color for the loop antenna, e.g., red
            debug = False  # Set to False to disable debugging outputs
            if debug and len(loop_antenna_coords) > 0:
                if not self.debugPrinted:
                    print(f"Drawing loop antenna with {len(loop_antenna_coords)} points")
                    self.debugPrinted = True  # Set the flag to True after printing
                # Example of drawing the loop antenna
                for i in range(len(loop_antenna_coords) - 1):
                    startPos = self.realToPixelPos(loop_antenna_coords[i])
                    endPos = self.realToPixelPos(loop_antenna_coords[i+1])
                    pygame.draw.line(self.windowHandler.window, loop_color, startPos, endPos, lineWidthPixels)

        # Clear the update flag after drawing
        self.localVarUpdated = False

        diamDebugColor = [127,127,127]
        pygame.draw.circle(self.windowHandler.window, diamDebugColor, tuple(map(int, self.realToPixelPos(np.zeros(2)))), int(coilToDraw.diam*self.sizeScale/2), 2) # (naive) outer diam
        pygame.draw.circle(self.windowHandler.window, diamDebugColor, tuple(map(int, self.realToPixelPos(np.zeros(2)))), int(coilToDraw.calcSimpleInnerDiam()*self.sizeScale/2), 2) # simple inner diam
        pygame.draw.circle(self.windowHandler.window, diamDebugColor, tuple(map(int, self.realToPixelPos((0, -coilToDraw._calcTrueDiamOffset())))), int(coilToDraw.calcTrueDiam()*self.sizeScale/2), 2) # what the papers define as the outer diam
        pygame.draw.circle(self.windowHandler.window, diamDebugColor, tuple(map(int, self.realToPixelPos((0, coilToDraw._calcTrueDiamOffset())))), int(coilToDraw.calcTrueInnerDiam()*self.sizeScale/2), 2) # what the papers define as the inner diam
    




    
    def renderBG(self, drawSpeedTimers: list = None):
        self._updateViewOffset() #handle mouse dragging
        if(drawSpeedTimers is not None):  drawSpeedTimers.append(('_updateViewOffset', time.time()))
        self.background()
        if(drawSpeedTimers is not None):  drawSpeedTimers.append(('background', time.time()))

    def renderFG(self, drawSpeedTimers: list = None):
        self.drawFPScounter()
        if(drawSpeedTimers is not None):  drawSpeedTimers.append(('drawFPScounter', time.time()))
        self.drawStatText()
        if(drawSpeedTimers is not None):  drawSpeedTimers.append(('drawStatText', time.time()))
        self.drawLoadedFilename()
        if(drawSpeedTimers is not None):  drawSpeedTimers.append(('drawLoadedFilename', time.time()))
        self.drawKeyBindLegend()
        if(drawSpeedTimers is not None):  drawSpeedTimers.append(('drawLoadedFilename', time.time()))

    def redraw(self):
        """draw all elements"""
        drawSpeedTimers = [('start', time.time()),]
        self.renderBG(drawSpeedTimers)

        #self.drawLineList([self.localVar.renderAsCoordinateList(False), self.localVar.renderAsCoordinateList(True)]) # inefficient!, line list can just be stored

        self.renderFG(drawSpeedTimers)

        drawSpeedTimers = [(drawSpeedTimers[i][0], round((drawSpeedTimers[i][1]-drawSpeedTimers[i-1][1])*1000, 1)) for i in range(1,len(drawSpeedTimers)) if ((drawSpeedTimers[i][1]-drawSpeedTimers[i-1][1]) > 0.0001)]
        # print("draw speed times:", sorted(drawSpeedTimers, key=lambda item : item[1], reverse=True))
    
    def updateWindowSize(self, drawSize=[1200, 600], drawOffset=[0,0], sizeScale=-1, autoMatchSizeScale=True):
        """handle the size of the window changing
            (optional) scale sizeScale (zooming) to match previous window size"""
        if(sizeScale > 0):
            self.sizeScale = sizeScale
        elif(autoMatchSizeScale):
            self.sizeScale = min(drawSize[0]/self.drawSize[0], drawSize[1]/self.drawSize[1]) * self.sizeScale #auto update sizeScale to match previous size
        self.drawSize = (int(drawSize[0]), int(drawSize[1]))
        self.drawOffset = (int(drawOffset[0]), int(drawOffset[1]))
        if(fancyKeyBindImageLoaded): # only if the keyboard stuff actually loaded correctly
            self.keyBindImageRendered = generateFancyKeyBindingImage(self.drawSize, True) # update keyboard layout (silently)
        print("updateWindowSize:", self.drawSize, self.drawOffset, self.sizeScale, autoMatchSizeScale)






# if __name__ == "__main__": # an example of how this file may be used
#     try:
#         import pygameUI as UI
#         resolution = [1280, 720]
#         windowHandler = pygameWindowHandler(resolution)
#         drawer = pygameDrawer(windowHandler, resolution) # only 1 renderer in the window
#         ## NOTE: by using the drawSize and drawOffset parameters, multiple pygameDrawer objects can use the same window (or simple picture-in-picture). The UI code may get more complicated though
#         while(windowHandler.keepRunning):
#             drawer.redraw()
#             windowHandler.frameRefresh()
#             UI.handleAllWindowEvents(drawer) #handle all window events like key/mouse presses, quitting and most other things
#     finally:
#         try:
#             windowHandler.end() # correctly shut down pygame window
#             print("drawer stopping done")
#         except:
#             print("couldn't run windowHandler.end()")