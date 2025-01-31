import pygame       #python game library, used for the visualization
import time         #used for debugging
import numpy as np  #general math library

import pygameRenderer as rend

# cursor in the shape of a flag
flagCurs = ("ooo         ooooooooo   ",
            "oo ooooooooo...XXXX..ooo",
            "oo ....XXXX....XXXX....o",
            "oo ....XXXX....XXXX....o",
            "oo ....XXXX.XXX....XX..o",
            "oo XXXX....XXXX....XXXXo",
            "oo XXXX....XXXX....XXXXo",
            "oo XXXX....X...XXXX..XXo",
            "oo ....XXXX....XXXX....o",
            "oo ....XXXX....XXXX....o",
            "ooo....XXXX.ooooooooo..o",
            "oo ooooooooo         ooo",
            "oo                      ",
            "oo                      ",
            "oo                      ",
            "oo                      ",
            "oo                      ",
            "oo                      ",
            "oo                      ",
            "oo                      ",
            "oo                      ",
            "oo                      ",
            "oo                      ",
            "oo                      ")
flagCurs16  =  ("oooooooooooooooo", #1
                "oo ...XXX...XXXo",
                "oo ...XXX...XXXo",
                "oo XXX...XXX...o", #4
                "oo XXX...XXX...o",
                "oo ...XXX...XXXo",
                "oo ...XXX...XXXo",
                "oo XXX...XXX...o", #8
                "oo XXX...XXX...o",
                "oooooooooooooooo",
                "oo              ",
                "oo              ", #12
                "oo              ",
                "oo              ",
                "oo              ",
                "oo              ") #16
global flagCurs24Data, flagCurs16Data, flagCursorSet, deleteCursorSet
flagCurs24Data = ((24,24),(0,23)) + pygame.cursors.compile(flagCurs, 'X', '.', 'o')
flagCurs16Data = ((16,16),(0,15)) + pygame.cursors.compile(flagCurs16, 'X', '.', 'o')
flagCursorSet = False
deleteCursorSet = False

## key bindings array
keyBindings: dict[str, int|tuple[int]] = { \
    "showKeyBind_toggle" : pygame.K_h,
    "zoom_toggle" : pygame.K_z,
    "grid_toggle" : pygame.K_g,
    "saveToFile" : pygame.K_s,
    "text_toggle" : pygame.K_t,
    "viewPlot" : pygame.K_v,
    # "debug" : pygame.K_d,
    "paramTurnCount_change" : (pygame.K_MINUS, pygame.K_EQUALS),
    "paramDiameter_change" : (pygame.K_LEFTBRACKET, pygame.K_RIGHTBRACKET),
    "paramTraceWidth_change" : (pygame.K_SEMICOLON, pygame.K_QUOTE),
    "paramClearance_change" : (pygame.K_PERIOD, pygame.K_SLASH),
    "paramCopperThickness_change" : (pygame.K_u, pygame.K_i),
    "paramLayerCount_change" : (pygame.K_k, pygame.K_l),
    "paramPcbTickness_change" : (pygame.K_m, pygame.K_COMMA),
    "paramShape_change" : (pygame.K_9, pygame.K_0),
    "paramFormula_change" : (pygame.K_o, pygame.K_p),
    "paramDirection_toggle" : pygame.K_SPACE,
    }


def handleMousePress(pygameDrawerInput: rend.pygameDrawer, buttonDown: bool, button: int, pos, eventToHandle: pygame.event.Event):
    """(UI element) handle the mouse-press-events"""
    if(buttonDown and ((button == 1) or (button == 3))): #left/rigth mouse button pressed (down)
        pygame.event.set_grab(1)
        if(pygame.key.get_pressed()[pygame.K_f]):
            pygame.mouse.set_cursor(flagCurs16Data[0], flagCurs16Data[1], flagCurs16Data[2], flagCurs16Data[3]) #smaller flag cursor
        ## put code you want to run when a mouse button is pressed (not released) here
        leftOrRight = (True if (button == 3) else False)
        realPos = pygameDrawerInput.pixelsToRealPos(pos) # convert to real units
    elif((button == 1) or (button == 3)): #if left/right mouse button released
        pygame.event.set_grab(0) # allow the mouse to exit the window once again
        if(pygame.key.get_pressed()[pygame.K_f]): #flag cursor stuff
            pygame.mouse.set_cursor(flagCurs24Data[0], flagCurs24Data[1], flagCurs24Data[2], flagCurs24Data[3]) #smaller flag cursor
        ## put code you want to run when a mouse button is released here
        leftOrRight = (True if (button == 3) else False)
        realPos = pygameDrawerInput.pixelsToRealPos(pos) # convert to real units
    elif(button==2): #middle mouse button
        ## dragging the view by holding the middle mouse button
        if(buttonDown): #mouse pressed down
            pygame.event.set_grab(1)
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            pygameDrawerInput.movingViewOffset = True
            pygameDrawerInput.movingViewOffsetMouseStart = pygame.mouse.get_pos()
            pygameDrawerInput.prevViewOffset = (pygameDrawerInput.viewOffset[0], pygameDrawerInput.viewOffset[1])
        else:           #mouse released
            pygame.event.set_grab(0)
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            pygameDrawerInput._updateViewOffset() #update it one last time (or at all, if this hasn't been running in redraw())
            pygameDrawerInput.movingViewOffset = False


def handleWindowEvent(pygameDrawerInput: rend.pygameDrawer, eventToHandle: pygame.event.Event):
    """(UI element) handle general (pygame) window-event"""
    if(eventToHandle.type == pygame.QUIT):
        print("pygame.QUIT event")
        pygameDrawerInput.windowHandler.keepRunning = False # stop program (soon)
    
    elif(eventToHandle.type == pygame.VIDEORESIZE):
        newSize = eventToHandle.size
        if((pygameDrawerInput.windowHandler.oldWindowSize[0] != newSize[0]) or (pygameDrawerInput.windowHandler.oldWindowSize[1] != newSize[1])): #if new size is actually different
            print("VIDEORESIZE from", pygameDrawerInput.windowHandler.oldWindowSize, "to", newSize)
            correctedSize = [newSize[0], newSize[1]]
            pygameDrawerInput.windowHandler.window = pygame.display.set_mode(correctedSize, pygame.RESIZABLE)
            #for pygameDrawerInput in pygameDrawerInputList:
            localNewSize = [int((pygameDrawerInput.drawSize[0]*correctedSize[0])/pygameDrawerInput.windowHandler.oldWindowSize[0]), int((pygameDrawerInput.drawSize[1]*correctedSize[1])/pygameDrawerInput.windowHandler.oldWindowSize[1])]
            localNewDrawPos = [int((pygameDrawerInput.drawOffset[0]*correctedSize[0])/pygameDrawerInput.windowHandler.oldWindowSize[0]), int((pygameDrawerInput.drawOffset[1]*correctedSize[1])/pygameDrawerInput.windowHandler.oldWindowSize[1])]
            pygameDrawerInput.updateWindowSize(localNewSize, localNewDrawPos, autoMatchSizeScale=False)
        pygameDrawerInput.windowHandler.oldWindowSize = pygameDrawerInput.windowHandler.window.get_size() #update size (get_size() returns tuple of (width, height))
    
    elif(eventToHandle.type == pygame.WINDOWSIZECHANGED): # pygame 2.0.1 compatible    (right now (aug 2021, pygame 2.0.1 (SDL 2.0.14, Python 3.8.3)) both get called (on windows at least), but it should be fine)
        newSize = pygameDrawerInput.windowHandler.window.get_size()
        if((pygameDrawerInput.windowHandler.oldWindowSize[0] != newSize[0]) or (pygameDrawerInput.windowHandler.oldWindowSize[1] != newSize[1])): #if new size is actually different
            print("WINDOWSIZECHANGED from", pygameDrawerInput.windowHandler.oldWindowSize, "to", newSize)
            correctedSize = [newSize[0], newSize[1]]
            #for pygameDrawerInput in pygameDrawerInputList:
            localNewSize = [int((pygameDrawerInput.drawSize[0]*correctedSize[0])/pygameDrawerInput.windowHandler.oldWindowSize[0]), int((pygameDrawerInput.drawSize[1]*correctedSize[1])/pygameDrawerInput.windowHandler.oldWindowSize[1])]
            localNewDrawPos = [int((pygameDrawerInput.drawOffset[0]*correctedSize[0])/pygameDrawerInput.windowHandler.oldWindowSize[0]), int((pygameDrawerInput.drawOffset[1]*correctedSize[1])/pygameDrawerInput.windowHandler.oldWindowSize[1])]
            pygameDrawerInput.updateWindowSize(localNewSize, localNewDrawPos, autoMatchSizeScale=False)
        pygameDrawerInput.windowHandler.oldWindowSize = pygameDrawerInput.windowHandler.window.get_size() #update size (get_size() returns tuple of (width, height))
    
    elif(eventToHandle.type == pygame.DROPFILE): #drag and drop files to import them
        #pygameDrawerInput = currentpygameDrawerInput(pygameDrawerInputList, None, False)
        print("attempting to load drag-dropped file:", eventToHandle.file)
        try:
            #note: drag and drop functionality is a little iffy for multi-drawer applications
            ## TBD: file importing code here
            print("no file handler set yet, just doing nothing with the drag-dropped file!")
        except Exception as excep:
            print("failed to load drag-dropped file, exception:", excep)
    
    elif((eventToHandle.type == pygame.MOUSEBUTTONDOWN) or (eventToHandle.type == pygame.MOUSEBUTTONUP)):
        #print("mouse press", eventToHandle.type == pygame.MOUSEBUTTONDOWN, eventToHandle.button, eventToHandle.pos)
        #handleMousePress(currentpygameDrawerInput(pygameDrawerInputList, eventToHandle.pos, True), eventToHandle.type == pygame.MOUSEBUTTONDOWN, eventToHandle.button, eventToHandle.pos, eventToHandle)
        handleMousePress(pygameDrawerInput, eventToHandle.type == pygame.MOUSEBUTTONDOWN, eventToHandle.button, eventToHandle.pos, eventToHandle)
        

    
    elif(eventToHandle.type == pygame.MOUSEWHEEL): #scroll wheel (zooming / rotating)
        #simToScale = currentpygameDrawerInput(pygameDrawerInputList, None, True)
        simToScale = pygameDrawerInput
        # if(pygame.key.get_pressed()[pygame.K_LCTRL]): #if holding (left) CTRL while scrolling
        #     ## do stuff
        # else:
        if(not simToScale.movingViewOffset):
            ## save some stuff before the change
            viewSizeBeforeChange = [simToScale.drawSize[0]/simToScale.sizeScale, simToScale.drawSize[1]/simToScale.sizeScale]
            mousePosBeforeChange = simToScale.pixelsToRealPos(pygame.mouse.get_pos())
            ## update sizeScale
            simToScale.sizeScale *= 1.0+(eventToHandle.y/10.0) #10.0 is an arbetrary zoomspeed
            if(simToScale.sizeScale < simToScale.minSizeScale):
                # print("can't zoom out any further")s
                simToScale.sizeScale = simToScale.minSizeScale
            elif(simToScale.sizeScale > simToScale.maxSizeScale):
                # print("can't zoom in any further")
                simToScale.sizeScale = simToScale.maxSizeScale
            dif = None # init var
            if(simToScale.centerZooming): ## center zooming:
                dif = [(viewSizeBeforeChange[0]-(simToScale.drawSize[0]/simToScale.sizeScale))/2, (viewSizeBeforeChange[1]-(simToScale.drawSize[1]/simToScale.sizeScale))/2]
            else: ## mouse position based zooming:
                mousePosAfterChange = simToScale.pixelsToRealPos(pygame.mouse.get_pos())
                dif = [mousePosBeforeChange[0] - mousePosAfterChange[0], mousePosBeforeChange[1] - mousePosAfterChange[1]]
            simToScale.viewOffset[0] -= dif[0] #equalizes from the zoom to 'happen' from the middle of the screen
            simToScale.viewOffset[1] -= dif[1]


def handleAllWindowEvents(pygameDrawerInput: rend.pygameDrawer):
    """(UI element) loop through (pygame) window-events and handle all of them"""
    # pygameDrawerInputList = []
    # if(type(pygameDrawerInput) is list):
    #     if(len(pygameDrawerInput) > 0):
    #         for entry in pygameDrawerInput:
    #             if(type(entry) is list):
    #                 for subEntry in entry:
    #                     pygameDrawerInputList.append(subEntry) #2D lists
    #             else:
    #                 pygameDrawerInputList.append(entry) #1D lists
    # else:
    #     pygameDrawerInputList = [pygameDrawerInput] #convert to 1-sizes array
    # #pygameDrawerInputList = pygameDrawerInput #assume input is list of pygamesims
    # if(len(pygameDrawerInputList) < 1):
    #     print("len(pygameDrawerInputList) < 1")
    #     pygameDrawerInput.windowHandler.keepRunning = False
    #     pygame.event.pump()
    #     return()
    for eventToHandle in pygame.event.get(): #handle all events
        if(eventToHandle.type != pygame.MOUSEMOTION): #skip mousemotion events early (fast)
            #handleWindowEvent(pygameDrawerInputList, eventToHandle)
            handleWindowEvent(pygameDrawerInput, eventToHandle)
        # else: # any mouse movement will trigger this code, so be careful to make it fast/efficient
        #     ## mouse movement trigger code here
