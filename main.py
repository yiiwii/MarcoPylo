#################################################
# term project: Marco Pylo
# Date: 20201209
# Your name: Yiwei Huang
# Your andrew id: yiweih
#################################################
# MVP Definition
#################################################
# user volumn indicator
# maze generation 
# Sound emitters/dampeners
# Limited vision, increases when user gain level
# players try to navigate and find each other
# pathfinding AI
#################################################


import math, random

# for graphics
# source: https://www.cs.cmu.edu/~112/notes/cmu_112_graphics.py
from cmu_112_graphics import *

from dungeon import *
from emitter import Emitter
from user import User
# from recording import Recording
# for spatial audio
# source: http://ajaxsoundstudio.com/pyodoc/about.html
from pyo import *
import random

#################################################
# Helper
#################################################

def make2dList(rows, cols, label):
# Reference: https://www.cs.cmu.edu/~112/notes/notes-2d-lists.html
    return [ ([label] * cols) for row in range(rows) ]

#################################################
# Model
#################################################

def appStarted(app):
    app.isFirstTime = True
    app.leaderboard = [(0,0),(0,0)]
    resetApp(app)
    # marco shoutout 
    app.mm = Mixer(outs=5, chnls=2,time=0.25)
    marcoPath = './marco.wav'
    pyloPath = './pylo.wav'
    wallPath = './wav/wall.wav'
    #footStep = './wav/footStep.wav'
    discoPath = './wav/grassFootSteps.wav'
    # https://freesound.org/people/dkiller2204/sounds/366111/
    app.wall = SfPlayer(wallPath,speed=1,loop=False,mul=2)
    # app.footstep = SfPlayer(footStep,speed=1,loop=False,mul=3)
    app.marco = SfPlayer(marcoPath,speed=1,loop=False,mul=4)
    app.marcofx = Freeverb(app.marco, damp=.5, bal=.1).out()
    app.pylo1=SfPlayer(pyloPath,speed=1.4,loop=False,mul=1.5)
    app.pylofx = Freeverb(app.pylo1, damp=.9, bal=.6).out()
    app.discoplayer = SfPlayer(discoPath,speed=1,loop=False,mul=2)

def resetApp(app):
    app.pylo = 0
    app.score = 0
    app.isEnd = False
    app.isStarted = False

    app.timeStart = 0
    app.timeEnd = 0

    app.isOnNode = False

    # dungeon generation
    app.maxLevel = 9
    app.levelInit = 3
    app.level = app.levelInit
    app.rows = 60
    app.cols = 100
    app.dungeon = None

    # GUI dimensions
    app.grid = 10
    app.xborder = (app.width-app.cols*app.grid)/2
    app.yborder = (app.height-app.rows*app.grid)/2
    # initialize User
    app.emitter = None
    app.emDist = 0
    app.user = None

    # pathfinding ai
    app.path = None
    app.currentTarget = None
    
    # style Sheet
    app.fontName = 'Courier'
    app.darkest = '#23333d'
    app.darkblue = '#304959'
    app.middleblue = '#688e8f'
    app.footstep ='#365261'
    app.lightblue = '#b8dbca' 
    app.red = '#b13f00'
    app.yellow = '#c69d19'
    app.lightyellow = '#e3ce8c'
    app.lighteryellow = '#f7f1de'
    app.darkyellow = '#7b7339'
    app.beige = '#f7e5c8'
    app.isPause = False
    app.isMute = False
    app.starttime = 0
    app.timer = 0
    
    if app.isStarted:
        restartGame(app)
        app.mm.addInput(1,app.pylo1)
        app.mm.addInput(4,app.marco)
        app.mm.addInput(0,app.emitter.player)
        app.mm.addInput(3,app.discoplayer)
        
    # vision
    app.normalSight = False
    app.isMarco = False

    app.isDamp = False
    app.timerDelay = 1000

# helper to generate objects
def generateDungeon(app):
    app.dungeon = Dungeon(app.rows,app.cols,app.level)
    app.dungeon.dungeonGen()

def generateUser(app):
    app.user = User('user1',app.rows,app.cols)
    app.user.uRow,app.user.uCol = generateLegalPosition(app)
    app.user.r = app.grid//2

def generateEmitter(app):
    sRow, sCol = generateLegalPosition(app)
    sx = sCol * app.grid + app.grid/2
    sy = sRow * app.grid + app.grid/2
    # if its the first emittor
    if app.emitter==None:
        azi, ele, spn, dist = soundCalculator(app, sx, sy)
        newEmitter = Emitter(0, sCol, sRow, azi, ele, spn)
        app.emitter = newEmitter
        newEmitter.bin.out()
    if app.mm[0] == None:
        app.mm.addInput(0,app.emitter.bin)
    if app.emitter!=None:
        app.emitter.sRow = sRow
        app.emitter.sCol = sCol


# helper to define whether the object is in the legal position in the maze
def generateLegalPosition(app):
    row = random.randint(6,app.rows-6)
    col = random.randint(6,app.cols-6)
    #basecase
    if generateIsLegal(app,row,col):
        return row, col
    # recursive calse
    else:
        return generateLegalPosition(app)


def generateIsLegal(app, tempRow, tempCol):
# helper function to check if the user is only generationed in chamber
    if (0 <= tempRow < app.dungeon.rows) and (0 <= tempCol < app.dungeon.cols):
        dungeonMap = app.dungeon.dungeonMap
        mark = dungeonMap[tempRow][tempCol]
        if mark == '#' or mark == '_': 
            return False
        elif mark == 'C': 
            return True
    else:
        return False
  

def generateTreasure(app):
    app.treasures = dict()
    for leaf in app.dungeon.leafDict[2]:
        if leaf!=None:
            chamber = leaf.chamber
            if chamber.isDamp == True:
                if chamber.tx!=None and chamber.ty !=None:
                    app.treasures[(leaf.lx+chamber.tx,leaf.ly+chamber.ty)] = True


def regenObjects(app):
    generateDungeon(app)
    generateUser(app)
    generateEmitter(app)
    generatePath(app)
    generateTreasure(app)
    app.utrail = []
    app.starttime = time.time()

def restartGame(app):
    app.isWinning = False
    regenObjects(app)

#################################################
# Control
#################################################

def keyPressed(app,event):
    if event.key == 'Enter':
        app.isStarted = True
        restartGame(app)

    #if app.isStarted == False:
     #   if event.key == '1':
      #      r = Recording("marco")
       # elif event.key == '2':
        #    m = Recording("pylo")

    if app.isStarted == True:
        uRow, uCol = app.user.uRow, app.user.uCol

        if event.key == 'z' and app.level+1 < app.maxLevel:
            app.level += 1
            regenObjects(app)
        elif event.key == 'x' and app.level-1 > 1:
            app.level -= 1
            regenObjects(app)

        elif event.key == 'Left' and moveIsLegal(app,uRow,uCol-1): 
            app.user.goLeft() 
            app.utrail.append((uRow, uCol,'l'))
            ifTreasure(app)
        elif event.key == 'Right' and moveIsLegal(app,uRow,uCol+1):
            app.user.goRight()
            app.utrail.append((uRow, uCol,'r'))
            ifTreasure(app)
        elif event.key == 'Up' and moveIsLegal(app,uRow-1,uCol): 
            app.user.goUp()  
            app.utrail.append((uRow, uCol,'u'))
            ifTreasure(app)
        elif event.key == 'Down' and moveIsLegal(app,uRow+1,uCol): 
            app.user.goDown()
            app.utrail.append((uRow, uCol,'d'))
            ifTreasure(app)


        # replay Pylo sound
        elif event.key == 'M' or event.key == 'm':
            if app.emitter!=None:
                app.isMarco = True
                app.timeStart=time.time() # create a timestamp
                m = app.marco
                app.marco.out()
                #if marcoDetector()==True:
                app.emitter.pyloplayer.mul = 6*app.emDist
                app.emitter.pyfx.bal=1-app.emDist
                app.emitter.pyfx.out(delay = 1.5)
                app.emitter.pyloplayer.out(delay = 1.5)
               
        elif event.key =='V' or event.key=='v':
            app.normalSight = not app.normalSight

        try:
            leaf = app.dungeon.locateLeaf((uRow,uCol))
            if leaf!=None and leaf.chamber.isDamp == True:
                app.discoplayer.out()
            if leaf == None or leaf.chamber.isDamp == False:
                app.discoplayer.stop()
        except:
            pass




def moveIsLegal(app, tempRow, tempCol):
# helper function to check if the user move is legal
    # within the canvas
    if (0 <= tempRow < app.dungeon.rows) and (0 <= tempCol < app.dungeon.cols):
        dungeonMap = app.dungeon.dungeonMap
        mark = dungeonMap[tempRow][tempCol]
        if mark == '#': 
            #app.wall.out() 
            return False
        elif mark != '#': 
            return True
    else:
        return False


def soundCalculator(app, sx, sy):
# a calculator that takes in the position of user and emitter
# return the calculation of binural sound parameter azi, ele, spn
# get emittor and user distance
    ux = app.user.uCol * app.grid
    uy = app.user.uRow * app.grid
    dist = ((sx-ux)**2 + (sy-uy)**2)**0.5
    # different conditions
    theta=None
    if sy<uy:
        theta = -math.atan((ux-sx)/(uy-sy))
    elif sy>uy and sx>ux: 
        theta = math.atan((uy-sy)/(ux-sx)) + math.pi/2
    elif sy>uy and sx<ux:
        theta = math.atan((uy-sy)/(ux-sx)) - math.pi/2
    elif sy==uy: 
        if sx>ux: theta=math.pi/2
        elif sx<ux: theta=-math.pi/2
    elif sx==ux:
        theta = 0
    if theta == None: 
        theta = 0
    # translate the binarual parameter
    azi =  theta*(2/math.pi)*90
    ele = 10
    spn = 1-dist/800

    return azi, ele, spn, dist




############ path finding ###########
def generatePath(app):
# helper to generate a node Path
    start = app.emitter.sRow, app.emitter.sCol
    end = app.user.uRow, app.user.uCol
    path=getPath(app.dungeon,start,end)
    path.insert(0,end)
    app.path = path

def nextPosition(app):
# helper to regulate the generate attracted nextPosition
    # if its not legal, then go along the border of the map
    if app.path!=[]:
        app.currentTarget = app.path[-1]
        drow,dcol = goToNode(app,app.currentTarget)
        nextRow, nextCol = drow+app.emitter.sRow, dcol+app.emitter.sCol
        if moveIsLegal(app,nextRow, nextCol):
            return nextRow, nextCol
        else:
            nextRow, nextCol = makeTurn(app,drow, dcol)
            return nextRow, nextCol
    

def goToNode(app,node):
    start = app.emitter.sRow, app.emitter.sCol
    end = node
    drow, dcol = moveEffective(app,start,end)
    return drow,dcol

def moveEffective(app,start,end):
    startRow, startCol = start
    endRow, endCol = end
    if endCol == startCol: 
        if endRow > startRow:
            drow, dcol = (1,0)
        else: drow, dcol = (-1,0)
    elif endCol != startCol:
        k = (endRow-startRow)/(endCol-startCol) # find the vector
        if abs(k) >= 1 and endRow > startRow: drow,dcol = (1,0)
        elif abs(k)<1 and endCol > startCol: drow, dcol = (0,1)
        elif abs(k)<1 and endCol < startCol: drow, dcol = (0,-1)
        elif abs(k) >= 1 and endRow < startRow: drow, dcol = (-1,0)
    return drow, dcol

# helper to make a turn if only hit wall
# because of the tree structure its a rare case
def makeTurn(app,drow,dcol):
    rightTurn = {(0,-1):(-1,0), (-1,0):(0,1), (0,1):(1,0), (1,0):(0,-1)}
    leftTurn = {(0,-1):(1,0), (1,0):(0,1), (0,1):(-1,0), (-1,0):(0,-1)}
    if random.random() < 0.3:
        ndrow,ndcol = rightTurn[(drow,dcol)]
    else:
        ndrow, ndcol = leftTurn[(drow,dcol)]
    nextRow, nextCol = ndrow+app.emitter.sRow, ndcol+app.emitter.sCol
    if moveIsLegal(app,nextRow, nextCol):
        return nextRow, nextCol
    else:
        return makeTurn(app,drow,dcol)
                

def modifyEmitter(app,ux,uy,emitter):
# Helper that updates emitter instance when user make a move
    sx, sy=emitter.sCol*app.grid+emitter.r/2, emitter.sRow*app.grid+emitter.r/2
    azi, ele, spn, dist = soundCalculator(app, sx, sy)
    amp = 1-(dist/600)-0.3
    if amp <=0: amp = 0.01
    else: amp = abs(amp)
    app.emDist = amp
    # modiy instance
    emitter.bin.setAzimuth(azi) # change azimuth angle
    emitter.bin.setElevation(ele) # change elevation angle
    emitter.bin.setAzispan(spn) # change Azispan 
    emitter.player.mul = amp # change amplitude, the further the smaller
    #emitter.theta = theta

def ifTreasure(app):
    for key in app.treasures:
        if (app.user.uCol,app.user.uRow) == key:
            app.treasures[key] = False
            app.score += 100

def ifWinning(app, tempRow,tempCol):
# helper to check if its winning
    emitter = app.emitter
    if tempRow==emitter.sRow and tempCol==emitter.sCol:
        app.isWinning = True
        app.pylo += 1
        app.score += 100*app.level
        app.level += 1
        if app.level > app.maxLevel-1:
            app.level = app.maxLevel
        restartGame(app)

def timerFired(app):
    # adding a timer in timerFired
    if app.timer>=20 and app.isStarted:
        app.isEnd = True
        app.isFirstTime = False
        app.leaderboard[0] = (app.pylo,app.score) # stores score
        # update topscore
        if app.score > app.leaderboard[1][1]:
            app.leaderboard[1] = app.pylo,app.score
        resetApp(app)

    if app.isStarted:
        current = time.time()
        app.timer = current-app.starttime
        print(app.timer,int(current),int(app.starttime))
        ifWinning(app, app.user.uRow,app.user.uCol)
        if app.emitter != None:
            emitter = app.emitter
            ux = app.user.uCol * app.grid
            uy = app.user.uRow * app.grid
            if nextPosition(app)!=None:
                nextRow, nextCol = nextPosition(app)
                app.emitter.sRow = nextRow
                app.emitter.sCol = nextCol
            if (app.emitter.sRow, app.emitter.sCol )==app.currentTarget and app.path!=[]:
                app.path.pop()
            if app.path==[]:
                generatePath(app)
            modifyEmitter(app, ux, uy, emitter)
            
    if app.isMarco:
        app.timeEnd = time.time()
        if app.timeEnd-app.timeStart >= 2:
            app.isMarco = False


#################################################
# View
#################################################
def drawDungeon(app,canvas):
    dungeonMap = app.dungeon.dungeonMap
    leafDict = app.dungeon.leafDict
    grid = app.grid
    xb,yb=app.xborder,app.yborder
    # limited vision draws grid
    # draw a circular partial dungeon
    if app.normalSight == False:
        rowStart, colStart, rowEnd, colEnd = regulateView(app)
        for row in range(rowStart-1, rowEnd):
            if row==rowStart-1 or row==rowEnd-1:
                for col in range(colStart, colEnd-1):
      
                    x0,y0 = xb+col*grid, yb+row*grid
                    x1,y1 = x0+grid, y0+grid
                    if dungeonMap[row][col] == '#':
                        canvas.create_rectangle(x0,y0,x1,y1,fill=app.darkblue,outline=app.darkblue)
                    elif dungeonMap[row][col] == 'D':
                        canvas.create_rectangle(x0,y0,x1,y1,fill=app.beige,outline=app.beige)
                    elif dungeonMap[row][col] == '_':
                        canvas.create_rectangle(x0,y0,x1,y1,fill=app.middleblue,outline=app.middleblue)
                    elif dungeonMap[row][col] == 'C':
                        canvas.create_rectangle(x0,y0,x1,y1,fill=app.middleblue,outline=app.middleblue)
            else:
                for col in range(colStart-1, colEnd):
                    x0,y0 = xb+col*grid, yb+row*grid
                    x1,y1 = x0+grid, y0+grid
                    if dungeonMap[row][col] == '#':
                        canvas.create_rectangle(x0,y0,x1,y1,fill=app.darkblue,outline=app.darkblue)
                    elif dungeonMap[row][col] == 'D':
                        canvas.create_rectangle(x0,y0,x1,y1,fill=app.beige,outline=app.beige)
                    elif dungeonMap[row][col] == '_':
                        canvas.create_rectangle(x0,y0,x1,y1,fill=app.middleblue,outline=app.middleblue)
                    elif dungeonMap[row][col] == 'C':
                        canvas.create_rectangle(x0,y0,x1,y1,fill=app.middleblue,outline=app.middleblue)

    # non-grid map
    # draws the tunnels
    elif app.normalSight:
        # draw background
        canvas.create_rectangle(0,0,app.width,app.height,fill=app.darkblue)
        for key in leafDict:
            if key >= 2:
                for leaf in leafDict[key]:
                    if leaf!=None:
                        tx0,ty0 = xb+(leaf.lx+leaf.tx0)*app.grid, yb+(leaf.ly+leaf.ty0)*app.grid
                        tx1,ty1 = xb+(leaf.lx+leaf.tx1)*app.grid, yb+(leaf.ly+leaf.ty1)*app.grid
                        canvas.create_rectangle(tx0, ty0, tx1, ty1, fill=app.middleblue, outline=app.middleblue)
        # draws the chambers
        for leaf in leafDict[2]:
            if leaf!=None:
                chamber = leaf.chamber
                if chamber!= None:
                    x0,y0 = xb+(leaf.lx+chamber.cx0)*app.grid, yb+(leaf.ly+chamber.cy0)*app.grid
                    x1,y1 = xb+(leaf.lx+chamber.cx1)*app.grid, yb+(leaf.ly+chamber.cy1)*app.grid
                    if chamber.isDamp == True: color = app.beige
                    else: color = app.middleblue
                    if not (x0 == x1 or y0==y1):
                        canvas.create_rectangle(x0,y0,x1,y1,fill=color,outline=color)


def regulateView(app):
# helper to define limited viewpoint
    level = app.level
    rowStart, colStart = app.user.uRow-level, app.user.uCol-level
    rowEnd, colEnd = app.user.uRow+level+2, app.user.uCol+level+2
    # with in board
    if rowStart<0: rowStart=0
    if colStart<0: colStart=0 
    if rowEnd>app.rows: rowEnd = app.rows
    if colEnd>app.cols: colEnd = app.cols
    return rowStart, colStart, rowEnd, colEnd
    
def drawUser(app, canvas):
    row,col = app.user.uRow, app.user.uCol
    xb,yb=app.xborder,app.yborder
    x0,y0, = xb+col * app.grid, yb+row * app.grid
    x1,y1 = x0+app.grid, y0+app.grid
    if app.isStarted:
        canvas.create_oval(x0,y0,x1,y1,fill=app.red,outline=app.red)
    # draw speach bubble
    if app.isMarco:
        cx ,cy = (x0+x1)/2, (y0+y1)/2 # center point of user
        bsize = 30
        canvas.create_polygon(cx,cy-8,cx-8,cy-5-2*bsize,cx-8-4,cy-8-2*bsize,fill=app.lighteryellow,outline=app.lighteryellow,width=2)
        canvas.create_rectangle(x0-5-2*bsize,y0-4*bsize,x1-5+2*bsize,y1-2*bsize,fill=app.lighteryellow,outline=app.lighteryellow,width=2)
        canvas.create_text(cx,cy-3*bsize,fill=app.darkblue, text=f'MARCO!', font=f'{app.fontName} 30 bold')

def drawEmittor(app, canvas):
# draws sound emittor objects
    xb,yb=app.xborder,app.yborder
    emitter = app.emitter
    if app.normalSight==True:
        x0,y0 = xb+emitter.sCol*app.grid, yb+emitter.sRow*app.grid
        x1,y1 = x0+2*emitter.r, y0+2*emitter.r
        canvas.create_rectangle(x0,y0,x1,y1,fill=app.yellow,outline=app.yellow)
    if app.normalSight==False:
        rowStart,colStart, rowEnd, colEnd = regulateView(app)
        if rowStart<=emitter.sRow+1<=rowEnd and colStart<=emitter.sCol+1<=colEnd:
            x0,y0 = xb+emitter.sCol*app.grid, yb+emitter.sRow*app.grid
            x1,y1 = x0+2*emitter.r, y0+2*emitter.r
            canvas.create_rectangle(x0,y0,x1,y1,fill=app.yellow,outline=app.yellow)


def drawStart(app, canvas):
# draws welcome screen
    if app.isStarted == False:
        if app.isFirstTime:
            # draw Welcome cover background
            canvas.create_rectangle(0, 0, app.width,app.height, fill=app.darkblue, width=0)
            # draw Welcome text(shadow)
            canvas.create_text(app.width/2+3, app.height/2-50+2, 
            text='MARCO! PYLO!', font=f'{app.fontName} 60 bold', 
            fill=app.middleblue, width=0)
            # draw Welcome text
            canvas.create_text(app.width/2, app.height/2-50, 
            text='MARCO! PYLO!', font=f'{app.fontName} 60 bold', 
            fill=app.yellow, width=0)
            canvas.create_text(app.width/2, app.height/2+80, 
            text='Press \'1\' to record Marco', font=f'{app.fontName} 18 normal', 
            fill=app.lightblue, width=0)
            canvas.create_text(app.width/2, app.height/2+100, 
            text='Press \'2\' to record Pylo', font=f'{app.fontName} 18 normal', 
            fill=app.lightblue, width=0)




        elif app.isFirstTime==False:
            canvas.create_text(app.width/2+3, app.height/2-50+2, 
            text='TIMER UP!', font=f'{app.fontName} 60 bold', 
            fill=app.middleblue, width=0)
            # draw Welcome text
            canvas.create_text(app.width/2, app.height/2-50, 
            text='TIMER UP!', font=f'{app.fontName} 60 bold', 
            fill=app.yellow, width=0)
            pylo, score = app.leaderboard[0]
            canvas.create_text(app.width/2, app.height/2-120, fill=app.lightblue,text=f'you have found {pylo} pylos! score:{score}', font=f'{app.fontName} 30 normal')



        canvas.create_text(app.width/2, app.height/2+20, 
        text='Press \'Enter\' to Start', font=f'{app.fontName} 18 normal', 
        fill=app.lightblue, width=0)
        canvas.create_text(app.width/2, app.height/2+40, 
        text='Press \'M\' to Find Pylo!', font=f'{app.fontName} 18 normal', 
        fill=app.lightblue, width=0)
        canvas.create_text(app.width/2, app.height/2+60, 
        text='Press Arrow Keys to Navigate', font=f'{app.fontName} 18 normal', 
        fill=app.lightblue, width=0)
        drawLeaderboard(app,canvas)


def drawDebugging(app,canvas):
    if app.isStarted == True:
        size = 20
        try:
            canvas.create_text(app.width-140, 2*size, fill=app.lightblue,text=f'score:{app.score}', font=f'{app.fontName} 30 bold')
            canvas.create_text(app.width/2, 2*size, fill=app.lightblue,text=f'pylo found:{app.pylo}', font=f'{app.fontName} 30 bold')
        except:
            canvas.create_text(app.width-140, 2*size, fill=app.lightblue,text=f'score:0', font=f'{app.fontName} 30 bold')
            canvas.create_text(app.width/2, 2*size, fill=app.lightblue,text=f'pylo found:0', font=f'{app.fontName} 30 bold')



    


def drawRadar(app,canvas):
# draws the volumn indicator at the bottom of the page
    emitter = app.emitter
    dist = app.emDist*100
    if dist<10: dist = 10
    cx,cy = app.width/2, app.height
    canvas.create_oval(cx-dist-10, cy-dist-10, cx+dist+10, cy+dist+10,fill=app.yellow,width=10,outline=app.darkblue)# outer rim
    canvas.create_oval(cx-dist, cy-dist, cx+dist, cy+dist,fill=app.yellow,width=10,outline=app.darkyellow)
    canvas.create_oval(cx-dist+10, cy-dist+10, cx+dist-10, cy+dist-10,fill=app.lighteryellow,width=10,outline=app.lightyellow)#inner rim
    if dist==10:
        canvas.create_text(app.width/2, app.height-dist-2*20, fill=app.lightblue, text=f'Marco is finding Pylo...',font=f'{app.fontName} 30 bold')
    elif 10<dist<50:
        canvas.create_text(app.width/2, app.height-dist-2*20, fill=app.lightblue, text=f'Where is Pylo?',font=f'{app.fontName} 30 bold')
    elif 50<=dist<80:
        canvas.create_text(app.width/2, app.height-dist-2*20, fill=app.lightblue, text=f'Plyo is near!',font=f'{app.fontName} 30 bold')
    elif 80<=dist<=100:
        canvas.create_text(app.width/2, app.height-dist-2*20, fill=app.lightblue, text=f'Almost there!',font=f'{app.fontName} 30 bold')
    
def drawPath(app, canvas):
    xb,yb=app.xborder+5,app.yborder+5
    if app.normalSight==True:
        r = 5
        # draw emitter path
        if app.path!=[]:
            if len(app.path) == 1:
                row, col = app.path[0]
                x0,y0 = xb + col*app.grid, yb + row*app.grid
                canvas.create_oval(x0-r,y0-r, x0+r, y0+r, fill='white')
            else:
                for i in range(len(app.path)-1):
                    row1, col1 = app.path[i]
                    x1, y1 = xb + col1*app.grid, yb + row1*app.grid
                    row2, col2 = app.path[i+1]
                    x2, y2 = xb + col2*app.grid, yb + row2*app.grid
                    canvas.create_line(x1,y1,x2,y2, dash=(2,2), fill='white')
                    canvas.create_oval(x1-r,y1-r, x1+r, y1+r, fill='white')
                    canvas.create_oval(x2-r,y2-r, x2+r, y2+r, fill='white')
    # draw user trial:
    for footstep in app.utrail:
        row1, col1 , direction = footstep
        x0,y0= xb-5 + app.grid*col1, yb-5 + app.grid*row1
        if app.normalSight == False:
            rowStart, colStart, rowEnd, colEnd = regulateView(app)
            if rowStart-1<=row1<=rowEnd-1 and colStart-1<=col1<=colEnd-1:

                if direction == 'u' or direction =='d':
                    canvas.create_rectangle(x0+2,y0+1,x0+4,y0+5,  fill =app.footstep,outline=app.footstep)
                    canvas.create_rectangle(x0+6,y0+5,x0+8,y0+9,fill =app.footstep,outline=app.footstep)
                elif direction == 'l' or direction =='r':
                    canvas.create_rectangle(x0+1,y0+6,x0+5,y0+8,  fill =app.footstep,outline=app.footstep)
                    canvas.create_rectangle(x0+5,y0+2,x0+9,y0+4,fill =app.footstep,outline=app.footstep)
        else:
            if direction == 'u' or direction =='d':
                canvas.create_rectangle(x0+2,y0+1,x0+4,y0+5,  fill =app.footstep,outline=app.footstep)
                canvas.create_rectangle(x0+6,y0+5,x0+8,y0+9,fill =app.footstep,outline=app.footstep)
            elif direction == 'l' or direction =='r':
                canvas.create_rectangle(x0+1,y0+6,x0+5,y0+8,  fill =app.footstep,outline=app.footstep)
                canvas.create_rectangle(x0+5,y0+2,x0+9,y0+4,fill =app.footstep,outline=app.footstep)
        

def drawTreasure(app, canvas):
    for key in app.treasures:
        if app.treasures[key] == True:
            tx,ty = key
            if app.normalSight == True:
                x0, y0 = app.xborder+app.grid*tx, app.yborder+ty*app.grid
                canvas.create_rectangle(x0, y0,x0+10,y0+10, fill ='orange')
            elif app.normalSight == False:
                rowStart, colStart, rowEnd, colEnd = regulateView(app)
                if rowStart-1<=ty<=rowEnd-1 and colStart-1<=tx<=colEnd-1:
                    x0, y0 = app.xborder+app.grid*tx, app.yborder+ty*app.grid
                    canvas.create_rectangle(x0, y0,x0+10,y0+10, fill ='orange')
                    
def drawTimer(app, canvas):
    canvas.create_text(app.xborder+40, 2*20, fill=app.lightblue, text=f'Timer:{int((20)-app.timer)}s',font=f'{app.fontName} 30 bold')

def drawLeaderboard(app, canvas):
    gap = 20
    pyloNum, score = app.leaderboard[1]

    canvas.create_text(app.width/2, app.height-60, 
    text=f'Top Moments: {pyloNum} pylos found, score:{score}', font=f'{app.fontName} 18 normal', 
    fill=app.lightblue, width=0)





def redrawAll(app, canvas):
    # draw background
    canvas.create_rectangle(0,0,app.width,app.height,fill=app.darkest)
    if app.isStarted:
        drawDungeon(app,canvas)
        drawTreasure(app,canvas)
        drawPath(app,canvas)
        drawEmittor(app,canvas)
        drawUser(app,canvas)
        drawRadar(app,canvas)
        drawTimer(app,canvas)
    drawDebugging(app,canvas)
    drawStart(app,canvas)
    


#################################################
# Main
###########################################z######

def main():
    # Source http://ajaxsoundstudio.com/pyodoc/api/classes/pan.html?highlight=pan#pyo.Binaural.elevation
    # Initialiez Sound Server
    s = Server(nchnls=2).boot()
    s.start()
    runApp(width=1200, height=800)

if __name__ == '__main__':
    main()