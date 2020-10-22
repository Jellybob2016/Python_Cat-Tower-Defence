import pygame
import copy
from Towers import *
from Tiles import *
from Enemies import *
from Waves import allWaves
from Colours import colours
from MapList import MapList, AllMaps, AllMapProfiles

#when enabled print statements for testing purposes will show
global toDevPrint #Global *angry face*
toDevPrint = True

########################################################################################################
#                                              - Setup -                                               #
########################################################################################################

if __name__ == "__main__":
    pygame.init()

    resolution = (1280, 720)
    pygame.display.set_caption("Cat Shooty Game")
    window = pygame.display.set_mode(resolution)
    windowIcon = pygame.image.load("Sprites\\GUI\\WindowIcon.png")
    pygame.display.set_icon(windowIcon)

    clock = pygame.time.Clock() 
else:
    exit()

########################################################################################################
#                                              - Classes -                                             #
########################################################################################################

class Main():
    enemyDict = {"a" : WoolLV1, "b" : WoolLV2, "c" : WoolLV3}
    towerDict = {0 : PistolCat, 1 : AngryCat, 2 : StrongCat, 3 : BombCat}
    currentWave = allWaves.pop(0)
    frameDelay = 0
    frameCache = 0
    lives = 100
    money = 200
    waveNum = -1
    upgrading = False
    currentTower = 0
    selectedTower = None
    currentMap = ""
    

    buttonList = []

    towerSpritesList = pygame.sprite.Group() # stores all towers placed, used to check when enemies are in range of towers
    tileSpritesList = pygame.sprite.Group() # stores all tiles that make up the map, not currently used
    collisionSpritesList = pygame.sprite.Group() #used in towerplacment, if anything in this list is touching a tower it will not be placed
    enemySpritesList = pygame.sprite.Group() #used in the movement system, everything in here will follow the path and should be enemy class
    buttonSpritesList = pygame.sprite.Group()
    allSpritesList = pygame.sprite.Group() #list of things to be drawn to screen
    
    def GameLoop(self): #The Main game loop, called when play is clicked
        self.running = True
        self.waveOngoing = False
        self.paused = False

        while self.running == True:
            
            if self.paused == False:
                #clears all buttons
                for sprite in self.buttonSpritesList:
                    sprite.kill()
                    del sprite

                #Adds button information to the list of buttons
                self.buttonList = []
                self.buttonList.append({"text" : "Start!", "xPos" : 1080, "yPos" : 600, "width" : 200, "height" : 120, "colour" : colours["lavender"], "hoverColour" : colours["bright_lavender"], "func" : self.StartWave})
                self.buttonList.append({"text" : "Back!", "xPos" : 1190, "yPos" : 0, "width" : 90, "height" : 70, "colour" : colours["red"], "hoverColour" : colours["bright_red"], "func" : self.PauseGame})
                
                #Yes
                #Loads Image UI
                SelectGUIImage = pygame.image.load("Sprites\\GUI\\LivesHeart.png")
                window.blit(SelectGUIImage, (1100,10))

                SelectGUIImage = pygame.image.load("Sprites\\GUI\\MoneyCoin.png")
                window.blit(SelectGUIImage, (1100,40))

                #Yes
                #Text UI
                largeText = pygame.font.SysFont("comicsansms",30)
                textSurf, textRect = TextObjects(str(self.lives), largeText)
                textRect.center = ((1150),(20))
                window.blit(textSurf, textRect)

                largeText = pygame.font.SysFont("comicsansms",30)
                textSurf, textRect = TextObjects(str(self.money), largeText)
                textRect.center = ((1150),(50))
                window.blit(textSurf, textRect)

                largeText = pygame.font.SysFont("comicsansms", 30)
                textSurf, textRect = TextObjects("Wave:"+ str(self.waveNum + 1), largeText)
                textRect.center = ((1150),(100))
                window.blit(textSurf, textRect)

                #Yes
                #Draws Rectangles
                pygame.draw.rect(window, colours["bright_lavender"], (5, 605, 50, 50), 5)
                towerExample = self.towerDict[self.currentTower](Vector2(-50, -50), colours["white"], window)
                SelectGUIImage = pygame.image.load(towerExample.GetProfile())
                window.blit(SelectGUIImage, (8,608))

                pygame.draw.rect(window, colours["bright_lavender"], (5, 665, 50, 50,), 5)
                largeText = pygame.font.SysFont("comicsansms", 15)
                textSurf, textRect = TextObjects(str(towerExample.GetPrice()), largeText)
                textRect.center = ((29),(688))
                window.blit(textSurf, textRect)

                #Yes
                #calls upgrades UI
                if self.selectedTower != None:
                    self.selectedTower.UpdateRadius() # updates drawn radius
                    self.UpgradesUI(self.selectedTower)

                #No
                #Checking for events each frame while game is running
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        quit()
                    
                    #Upon Click
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse = pygame.mouse.get_pos()
                        
                        for button in self.buttonList:
                            AreaClick(**button)

                        clicked = [s for s in self.buttonSpritesList if s.rect.collidepoint(mouse)]

                        if len(clicked) >= 1:
                            clicked.OnClick()

                        if 1080 > mouse[0] > 0 and 600 > mouse[1] > 0:
                            clicked = [s for s in self.towerSpritesList if s.rect.collidepoint(mouse)]
                            if len(clicked) >= 1:
                                self.selectedTower = clicked[0]
                            else:
                                
                                self.PlaceTower()
                                self.selectedTower = None
                                
                    #Upon Keypress
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            self.currentTower -= 1
                        if event.key == pygame.K_RIGHT:
                            self.currentTower += 1
                    
                    #Checks the current selected tower is valid
                    if self.currentTower <= 0:
                        self.currentTower = 0
                    elif self.currentTower >= len(self.towerDict)-1:
                        self.currentTower = len(self.towerDict)-1

                #Yes
                #updates button visuals
                for button in self.buttonList:
                    ButtonVisuals(**button)
                
                #No
                #all towers check and attack,
                for enemy in self.enemySpritesList:
                    for tower in self.towerSpritesList:
                        self.money += tower.CheckEnemies(enemy, self.enemySpritesList)
                
                #No
                #Move Wool
                for item in self.enemySpritesList:
                    self.lives += item.MoveFrame()

                #No
                #Spawn new Wool
                if self.frameDelay == 0:
                    if len(self.currentWave) > 0:
                        nextThing = self.currentWave[0]

                        if type(nextThing) == int:
                            self.frameDelay = int(nextThing)
                        
                        elif type(nextThing) == str:
                            enemy = self.enemyDict[nextThing](self.pathList, self.startTilePos, colours["white"])
                            self.enemySpritesList.add(enemy)
                            self.allSpritesList.add(enemy)
                        
                        self.currentWave.pop(0)
                else:
                    self.frameDelay -= 1

                #No
                #Check For end of game
                if self.lives <= 0:
                    self.lives = 0 #stop it counting down further after loss screen
                    self.GameEnd()

                #No
                #Check for end of wave
                if self.waveOngoing:
                    if len(self.enemySpritesList) <= 0 and len(self.currentWave) <= 0:
                        self.money += self.waveReward
                        self.waveOngoing = False
                        if len(allWaves) <= 0:
                            self.GameEnd("you win!")

            elif self.paused == True:
                
                self.pauseButtonList = []
                self.pauseButtonList.append({"text" : "Yes!", "xPos" : 450, "yPos": 400, "width" : 100, "height" : 50, "colour" : colours["red"], "hoverColour" : colours["bright_red"], "func" : self.ResetGame})
                self.pauseButtonList.append({"text" : "No!", "xPos" : 740, "yPos": 400, "width" : 100, "height" : 50, "colour" : colours["green"], "hoverColour" : colours["bright_green"], "func" : self.ResumeGame})

                #####################################################################################
                #                                      - Background UI -                            #
                #####################################################################################
                #Loads Image UI
                SelectGUIImage = pygame.image.load("Sprites\\GUI\\LivesHeart.png")
                window.blit(SelectGUIImage, (1100,10))

                SelectGUIImage = pygame.image.load("Sprites\\GUI\\MoneyCoin.png")
                window.blit(SelectGUIImage, (1100,40))

                #Loads Text UI
                largeText = pygame.font.SysFont("comicsansms",30)
                textSurf, textRect = TextObjects(str(self.lives), largeText)
                textRect.center = ((1150),(20))
                window.blit(textSurf, textRect)

                largeText = pygame.font.SysFont("comicsansms",30)
                textSurf, textRect = TextObjects(str(self.money), largeText)
                textRect.center = ((1150),(50))
                window.blit(textSurf, textRect)

                largeText = pygame.font.SysFont("comicsansms", 30)
                textSurf, textRect = TextObjects("Wave:"+ str(self.waveNum + 1), largeText)
                textRect.center = ((1150),(100))
                window.blit(textSurf, textRect)

                #Draws Rectangles
                pygame.draw.rect(window, colours["bright_lavender"], (5, 605, 50, 50), 5)
                pygame.draw.rect(window, colours["grey"], (400, 200, 500, 300), 5)
                towerExample = self.towerDict[self.currentTower](Vector2(-50, -50), colours["white"], window)
                SelectGUIImage = pygame.image.load(towerExample.GetProfile())
                window.blit(SelectGUIImage, (8,608))

                pygame.draw.rect(window, colours["bright_lavender"], (5, 665, 50, 50,), 5)
                largeText = pygame.font.SysFont("comicsansms", 15)
                textSurf, textRect = TextObjects(str(towerExample.GetPrice()), largeText)
                textRect.center = ((29),(688))
                window.blit(textSurf, textRect)

                #Calls upgrades UI
                if self.selectedTower != None:
                    self.selectedTower.UpdateRadius() # updates drawn radius
                    self.UpgradesUI(self.selectedTower)

                #####################################################################################
                #                                      - Foreground UI -                            #
                #####################################################################################

                #Draws Rectangles
                pygame.draw.rect(window, colours["white"], (400, 200, 500, 300))
                pygame.draw.rect(window, colours["grey"], (400, 200, 500, 300), 5)
                
                #Draws Text
                largeText = pygame.font.SysFont("comicsansms",25)
                textSurf, textRect = TextObjects("Are you sure you want to quit?", largeText)
                textRect.center = (650,250)
                window.blit(textSurf, textRect)

                textSurf, textRect = TextObjects("you will lose all progress!", largeText)
                textRect.center = (650,275)
                window.blit(textSurf, textRect)

                #Checking for events each frame while game is paused
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        quit()
                    
                    #Upon Click
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse = pygame.mouse.get_pos()
                        
                        for button in self.pauseButtonList:
                            AreaClick(**button)

                #updates button visuals
                for button in self.pauseButtonList:
                    ButtonVisuals(**button)

            #Final stuff
            pygame.display.update()
            window.fill((255, 255, 255))
            self.allSpritesList.draw(window)
            clock.tick(30)
    
    def PauseGame(self):
        self.paused = True
    
    def ResumeGame(self):
        self.paused = False

    def GameEnd(self, state = "you lose"):
        
        self.buttonList = []
        self.buttonList.append({"text" : "Quit!", "xPos" : 550, "yPos": 450, "width" : 100, "height" : 50, "colour" : colours["red"], "hoverColour" : colours["bright_red"], "func" : quit})

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button in self.buttonList:
                        AreaClick(**button)
                    
            window.fill(colours["white"])
            largeText = pygame.font.SysFont("comicsansms",115)
            textSurf, textRect = TextObjects(state, largeText)
            textRect.center = ((resolution[0]/2),(resolution[1]/2))
            window.blit(textSurf, textRect)

            for button in self.buttonList:
                ButtonVisuals(**button)
            
            pygame.display.update()
            clock.tick(30)

    def GameIntro(self): #The Menu screen Loop, called on play
        intro = True

        self.buttonList = []
        self.buttonList.append({"text" : "Play!", "xPos" : 470, "yPos" : 400, "width" : 300, "height" : 100, "colour" : colours["green"], "hoverColour" : colours["bright_green"], "func" : self.LevelSelect})
        self.buttonList.append({"text" : "Quit!", "xPos" : 570, "yPos": 530, "width" : 100, "height" : 50, "colour" : colours["red"], "hoverColour" : colours["bright_red"], "func" : quit})
    
        while intro:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button in self.buttonList:
                        AreaClick(**button)
                    
            window.fill(colours["white"])
            largeText = pygame.font.SysFont("comicsansms",115)
            textSurf, textRect = TextObjects("Angry Cats!", largeText)
            textRect.center = ((640),(300))
            window.blit(textSurf, textRect)

            for button in self.buttonList:
                ButtonVisuals(**button)

            pygame.display.update()
            clock.tick(30)
    
    def LevelSelect(self):

        window.fill(colours["white"])

        self.currentMap = AllMaps["Map1"]

        levelSelect = True
        self.buttonList = []
        self.buttonList.append({"text" : "Play!", "xPos" : 10, "yPos" : 10, "width" : 100, "height" : 40, "colour" : colours["green"], "hoverColour" : colours["bright_green"], "func" : self.GenerateMap})
        self.buttonList.append({"text" : "Back!", "xPos" : 10, "yPos" : 60, "width" : 50, "height" : 40, "colour" : colours["red"], "hoverColour" : colours["bright_red"], "func" : self.GameIntro})

        self.pos = 0
        self.mapIndex=0 #i would equal the selected maps index

        self.previousMousePos = pygame.mouse.get_pos()

        while levelSelect:
            
            #Checks if it needs to shift the buttons
            if self.pos >= 400:
                self.mapIndex -= 1
                self.pos -= 400
            elif self.pos <= -400:
                self.mapIndex += 1
                self.pos += 400

            #Collects current mouse position
            self.currentMousePos = pygame.mouse.get_pos()

            #Checks mapIndex to see if its out of bounds
            if self.mapIndex >= len(MapList):
                self.mapIndex = 0
            elif self.mapIndex < 0:
                self.mapIndex = len(MapList)-1

            #Creates the currentMaps list
            #currentMaps is the list of the central maps and the 2 maps to either side
            if self.mapIndex+2 > len(MapList)-1:
                mapDifference = (self.mapIndex+2)-(len(MapList)-1)
                currentMaps = MapList[self.mapIndex-2:self.mapIndex+(mapDifference)+1] + MapList[:mapDifference]
            elif self.mapIndex-2 < 0:
                mapDifference = -(self.mapIndex-2)
                currentMaps = MapList[-mapDifference:] + MapList[self.mapIndex-(2-mapDifference):self.mapIndex+3]
            else:
                currentMaps = MapList[self.mapIndex-2:self.mapIndex+3]
        
        

            #Checks current events
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                #Upon Click
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse = pygame.mouse.get_pos()
                    for button in self.buttonList:
                        AreaClick(**button)
                    DevPrint("current map is", self.currentMap)
            
                    #Check of and which buttons are pressed
                    clicked = [s for s in self.buttonSpritesList if s.rect.collidepoint(mouse)] 
                    if len(clicked) == 1:
                        clicked[0].OnClick()

            #Clears button list
            for sprite in self.buttonSpritesList:
                sprite.kill()
                del sprite

            #Generates the map images and names
            for i in range(5):
                if AllMaps[currentMaps[i]] == self.currentMap:
                    tempColour = "sky_blue"
                else:
                    tempColour = "bright_sky_blue"

                button = Button(AllMapProfiles[currentMaps[i]], Vector2(-200 + (420*i) + self.pos, 360), self.SelectMap)
                pygame.draw.rect(window, colours[tempColour], (-400 + (420*i) + self.pos, 250, 400, 220))

                button.SetParams({"map": AllMaps[currentMaps[i]]})
                self.buttonSpritesList.add(button)
                self.allSpritesList.add(button)

                #Adds the text below the image
                largeText = pygame.font.SysFont("comicsansms",20)
                textSurf, textRect = TextObjects(currentMaps[i], largeText)
                textRect.center = ((-200 + (420*i) + self.pos, 500))
                window.blit(textSurf, textRect)

            #Generates non-sprite buttons
            for button in self.buttonList:
                ButtonVisuals(**button)

            
            mouseDifference = self.previousMousePos[0] - self.currentMousePos[0]
            
            if pygame.mouse.get_pressed()[0] == 1:
                self.pos -= mouseDifference


            self.previousMousePos = self.currentMousePos
            self.allSpritesList.draw(window)
            pygame.display.update()
            window.fill(colours["white"])
            clock.tick(30)

    def GenerateMap(self): #Ran just before game loop to generate the map
        
        #for a tile key, check MapList.py

        mapFile = open(self.currentMap, "r")
        fileContents = mapFile.readlines()
        mapFile.close()
        mapString = ""
        for item in fileContents:
            mapString += item.replace("\n", "")

        typeList = {
            "#" : Ground,
            "P" : Path,
            ">" : StartRight,
            "<" : StartLeft,
            "/" : StartDown,
            "^" : StartUp,
            "," : EndLeft,
            "6" : EndDown,
            "." : EndRight,
            "?" : EndUp
        }

        counter = 0
        for char in mapString:
            try:
                nextTile = typeList[char]
            except:
                print("Error! Map tile not in typelist")
            location = [((counter%54)*20)+10, ((counter//54)*20)+10]
            tile = nextTile(location, colours["red"])

            self.allSpritesList.add(tile)
            self.tileSpritesList.add(tile)

            if nextTile != Ground:
                self.collisionSpritesList.add(tile)

            counter += 1

        self.GeneratePath()

    def GeneratePath(self): #Ran after generating the map
        #for a tile key, check MapList.py

        mapFile = open(self.currentMap, "r")
        fileContents = mapFile.readlines()
        mapFile.close()

        mapArray = []
        for item in fileContents:
            tempList = []
            for char in item:
                if char != "\n":
                    tempList.append(char)
            mapArray.append(tempList)
        
        """
        Path Array format:
        U - Go Up
        L - Go Left
        R - Go right
        D - Go Down
        """

        self.pathList = []
        
        row = 0
        column = 0

        startList = ["^", "<", ">", "/"]
        for layer in mapArray:
            for tile in layer:
                for item in startList:
                    if tile == item:
                        self.startTilePos = [column, row]
                        checkPos = [row, column]

                column += 1
            column = 0
            row += 1

        DevPrint("Located start tile position, it is: {}".format(str(checkPos)))
        
        '''
        endList = [",", ".", "6", "?"]
        listItems = [["U", -1, 0],["D", 1, 29],["L", -1, 0],["R", 1, 53]]
        path = True

        while path == True: #Starts going until the path is complete
            for i in range(4):
                if checkPos[0] != listItems[i][2]:
                    if mapArray[checkPos[0] + listItems[i][1]][checkPos[1]] == "P": #Checks for path
                        self.pathList.append(listItems[i][0])
                        mapArray[checkPos[0]][checkPos[1]] = "#"
                        checkPos[0] = checkPos[0] + listItems[i][1]
                        continue
                    else:
                        for item in endList: #Checks for end
                            if mapArray[checkPos[0] + listItems[i][1]][checkPos[1]] == item:
                                self.pathList.append(listItems[i][0])                                      
                                self.pathList.append("END")
                                path = False
                                DevPrint("path should be false now")
                            else:
                                DevPrint(mapArray[checkPos[0] + listItems[i][1]][checkPos[1]])
        self.GameLoop()
        '''

        endList = [",", ".", "6", "?"]
        path = True

        while path == True: #Starts going until the path is complete
                if checkPos[0] != 0: #Checks the tile above
                    if mapArray[checkPos[0]-1][checkPos[1]] == "P": #Checks for path
                        self.pathList.append("U")
                        mapArray[checkPos[0]][checkPos[1]] = "#"
                        checkPos[0] = checkPos[0]-1
                        continue
                    else:
                        for item in endList: #Checks for end
                            if mapArray[checkPos[0]-1][checkPos[1]] == item:
                                self.pathList.append("U")                                      #
                                self.pathList.append("END")
                                path = False
                
                if checkPos[0] != 29: #Checks the tile below
                    if mapArray[checkPos[0]+1][checkPos[1]] == "P": #Checks for path
                        self.pathList.append("D")
                        mapArray[checkPos[0]][checkPos[1]] = "#"
                        checkPos[0] = checkPos[0]+1
                        continue
                    else:
                        for item in endList: #Checks for end
                            if mapArray[checkPos[0]+1][checkPos[1]] == item:
                                self.pathList.append("D")                                      #
                                self.pathList.append("END")
                                path = False
                
                if checkPos[1] != 0: #Checks the tile to the left
                    if mapArray[checkPos[0]][checkPos[1]-1] == "P": #Checks for path
                        self.pathList.append("L")
                        mapArray[checkPos[0]][checkPos[1]] = "#"
                        checkPos[1] = checkPos[1]-1
                        continue
                    else:
                        for item in endList: #Checks for end
                            if mapArray[checkPos[0]][checkPos[1]-1] == item:
                                self.pathList.append("L")                                      #
                                self.pathList.append("END")
                                path = False
                
                if checkPos[1] != 53: #Checks the tile to the right
                    if mapArray[checkPos[0]][checkPos[1]+1] == "P": #Checks for path
                        self.pathList.append("R")
                        mapArray[checkPos[0]][checkPos[1]] = "#"
                        checkPos[1] = checkPos[1]+1
                        continue
                    else:
                        for item in endList: #Checks for end
                            if mapArray[checkPos[0]][checkPos[1]+1] == item:
                                self.pathList.append("R")                                      #
                                self.pathList.append("END")
                                path = False
        self.GameLoop()
            
    def StartWave(self):
        if not self.waveOngoing:
            currentWaveData = allWaves.pop(0)
            self.currentWave = currentWaveData[0]
            self.waveReward = currentWaveData[1]
            self.waveOngoing = True
            self.waveNum += 1

    def PlaceTower(self): #Ran to spawn towers at the mouse position upon click
        """
        To place a tower you will need:
        A sprite (defined in the tower's class data)
        The Location of the tower (Defined by the mouse position)
        To Create an instance of that towers class
        """

        mousePositon = pygame.mouse.get_pos()
        self.tower = self.towerDict[self.currentTower](mousePositon, colours["white"], window)

        if pygame.sprite.spritecollide(self.tower, self.collisionSpritesList, False) == [] and self.money >= self.tower.GetPrice():
            self.towerSpritesList.add(self.tower)
            self.collisionSpritesList.add(self.tower)
            self.allSpritesList.add(self.tower)
            self.money -= self.tower.GetPrice()
        else:
            self.tower.kill()
            del self.tower

        #window.blit(pygame.image.load(self.currentTower.GetSprite()), mousePositon) #Need to replace blits with sprites

    def UpgradeTower(self, upgradeInfo):
        if upgradeInfo[1] <= self.money:
            self.money -= upgradeInfo[1]
            upgradeInfo[2]()

    def UpgradesUI(self, tower):
        #Adds the Delete Button
        elipseBoundries = [self.selectedTower.GetPos()[0]-(10*self.selectedTower.GetRange()), self.selectedTower.GetPos()[1]-(10*self.selectedTower.GetRange()), self.selectedTower.GetRange()*20, self.selectedTower.GetRange()*20]
        pygame.draw.ellipse(window, colours["black"], elipseBoundries, 1)
        self.buttonList.append({"text" : "Delete", "xPos" : 120, "yPos" : 650, "width" : 200, "height" : 60, "colour" : colours["red"], "hoverColour" : colours["bright_red"], "func" : [tower.RemoveExistance, self.DeleteTower]})
        #Adds the Upgrade Buttons
        if len(tower.GetUpgrades()) == 2:
            if tower.GetUpgrades()[0] != None:
                self.buttonList.append({"text" : tower.GetUpgrades()[0][0] + "\n" + str(tower.GetUpgrades()[0][1]), "xPos" : 330, "yPos" : 610, "width" : 365, "height" : 100, "colour" : colours["brown"], "hoverColour" : colours["bright_brown"], "perams" : {"upgradeInfo" : tower.GetUpgrades()[0]}, "func" : self.UpgradeTower})
            else:
                button = Button("Sprites\\GUI\\NoRoute.png", Vector2(513, 660))
                self.buttonSpritesList.add(button)
                self.allSpritesList.add(button)
            
            if tower.GetUpgrades()[1] != None:
                self.buttonList.append({"text" : tower.GetUpgrades()[1][0] + "\n" + str(tower.GetUpgrades()[1][1]), "xPos" : 705, "yPos" : 610, "width" : 365, "height" : 100, "colour" : colours["brown"], "hoverColour" : colours["bright_brown"], "perams" : {"upgradeInfo" : tower.GetUpgrades()[1]}, "func" : self.UpgradeTower})
            else:
                button = Button("Sprites\\GUI\\NoRoute.png", Vector2(888, 660))
                self.buttonSpritesList.add(button)
                self.allSpritesList.add(button)
        else:
            self.buttonList.append({"text" : "Tower Maxed", "xPos" : 330, "yPos" : 610, "width" : 730, "height" : 100, "colour" : colours["bright_brown"], "hoverColour" : colours["bright_brown"], "func" : None})

    def DeleteTower(self):
        self.money += self.selectedTower.GetPrice()
        self.selectedTower = None

    def SelectMap(self, map): #make this take a parameter of the maps location
        self.currentMap = map
        DevPrint("set current map to", map)

    def ResetGame(self):
        self.currentWave = allWaves.pop(0)
        self.lives = 100
        self.money = 200
        self.waveNum = -1
        self.upgrading = False
        self.currentTower = 0
        self.selectedTower = None
        self.currentMap = ""
        

        self.buttonList = []

        self.towerSpritesList.empty()
        self.tileSpritesList.empty()
        self.collisionSpritesList.empty()
        self.enemySpritesList.empty() 
        self.buttonSpritesList.empty()
        self.allSpritesList.empty()
        self.GameIntro()

class Button(pygame.sprite.Sprite):
    params = {}
    def __init__(self, sprite, location, func = None):
        self.func = func
        
        #Sprite stuff
        #Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
    
        #Load the image
        self.image = pygame.image.load(sprite).convert()
    
        #Set our transparent color
        self.image.set_colorkey(colours["purple"])
        self.rect = self.image.get_rect()
        self.rect.center = location

    def SetParams(self, params):
        self.params = params

    def OnClick(self):
        self.func(**self.params)

########################################################################################################
#                                            - Functions -                                             #
########################################################################################################

#Used in the main menu
def AreaClick(xPos, yPos, width, height, func, perams = {}, **kwargs):
    mouse = pygame.mouse.get_pos()
    if xPos+width > mouse[0] > xPos and yPos+height > mouse[1] > yPos:
        if func:
            if type(func) == list:
                for item in func:
                    item(**perams)
                    
            else:
                func(**perams)

def ButtonVisuals(text, xPos, yPos, width, height , colour, hoverColour, border = True, **kwargs):
    mouse = pygame.mouse.get_pos()
    if xPos+width > mouse[0] > xPos and yPos+height > mouse[1] > yPos:
        pygame.draw.rect(window, colour, (xPos,yPos,width,height)) #Draws the fill
        if border:
            pygame.draw.rect(window, Darken(colour), (xPos,yPos,width,height),5) #Draws the border

    else:
        pygame.draw.rect(window, hoverColour,(xPos,yPos,width,height)) #Draws the fill
        if border:
            pygame.draw.rect(window, Darken(hoverColour),(xPos,yPos,width,height),5) #Draws the border

    smallText = pygame.font.SysFont("comicsansms",20)
    textSurf, textRect = TextObjects(text, smallText)
    textRect.center = ( (xPos+(width/2)), (yPos+(height/2)) )
    window.blit(textSurf, textRect)

def Darken(colour):
    newColour = list(colour)
    for i in range(3):
        newColour[i] += 30
        if newColour[i] >= 255:
            newColour[i] = 255
        elif newColour[i] <= 0:
            newColour[i] = 0
    newColour = tuple(newColour)
    return (newColour)

def TextObjects(text, font):
    textSurface = font.render(text, True, colours["black"])
    return textSurface, textSurface.get_rect()

def DevPrint(*text):
    global toDevPrint
    if toDevPrint == True:
        print("\u0332".join("DevPrint "), end = "")
        for i in text:
            print(i, end = "")
        print("")

########################################################################################################
#                                          - Call Functions -                                          #
########################################################################################################
main = Main()
main.GameIntro()
pygame.quit()
quit()

'''
THINGS TO DO

Better tiles system
'''