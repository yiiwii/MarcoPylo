# Dungeon generation using BSP trees 
# this file includes the dungeon class, which is the base of our maze
# High level Definition:
# Reference:https://eskerda.com/bsp-dungeon-generation/
# http://www.roguebasin.com/index.php?title=Basic_BSP_Dungeon_generation

import math, copy, random
# source: https://www.cs.cmu.edu/~112/notes/cmu_112_graphics.py

################################################################################
# Helpers
################################################################################

def make2dList(rows, cols, label):
    # Reference: https://www.cs.cmu.edu/~112/notes/notes-2d-lists.html
    return [ ([label] * cols) for row in range(rows) ]

def maxItemLength(a):
    # Reference:https://www.cs.cmu.edu/~112/notes/notes-2d-lists.html#printing
    # Helper function for print2dList.
    maxLen = 0
    rows = len(a)
    cols = len(a[0])
    for row in range(rows):
        for col in range(cols):
            maxLen = max(maxLen, len(str(a[row][col])))
    return maxLen

def print2dList(a):
    # Reference:https://www.cs.cmu.edu/~112/notes/notes-2d-lists.html#printing
    # Helper function for print2dList.
    if (a == []):
        print([])
        return 
    rows, cols = len(a), len(a[0])
    fieldWidth = maxItemLength(a)
    print('[')
    for row in range(rows):
        print(' [ ', end='')
        for col in range(cols):
            if (col > 0): print(', ', end='')
            print(str(a[row][col]).rjust(fieldWidth), end='')
        print(' ]')
    print(']')


################################################################################
# Dungeon Gen
################################################################################

class Leaf():
    # respresents a leaf in the binary tree (a partition of the canvas)
    def __init__(self,rows,cols,lx,ly,split):
        # leaf dimension
        self.cols = cols
        self.rows = rows

        # coordinate of leftupper corner
        self.lx = lx
        self.ly = ly
        self.map = make2dList(rows,cols,'#')

        # setting up tree pointer
        self.parent = None
        self.left = None
        self.right = None
        self.split = split # marker to store whether is a vsplit or hsplit
        self.center = (ly+self.rows//2, lx+self.cols//2)

        # storing tunnel dimensions
        self.tx0 = None
        self.ty0 = None
        self.tx1 = None
        self.ty1 = None
        self.tw = None

        # chamber pointer
        self.chamber = None
        self.gridSet = set()

        #
        self.tunnelSet = set() 
        

    def __repr__(self):
        return f'{self.map}'

class Chamber():
    def __init__(self, leaf):
        self.leaf = None
        # storing chamber diminsions
        self.cx0 = None
        self.cy0 = None
        self.cx1 = None
        self.cy1 = None
        self.tx = None
        self.ty = None
        self.isDamp = False


class Dungeon():
    # a Dungeon map given dimention and complex level
    def __init__(self,rows,cols,level):
        # initlaize dungeon dimensions
        self.rows = rows
        self.cols = cols
        self.level = level

        # initialize the dict with level complexity
        leaves = dict()
        for i in range(0,level+1):
            leaves[i] = set()
        self.leafDict = leaves

        # initialize a 2dList as Map
        # representing cells of dungeon for move check
        self.dungeonMap = make2dList(rows,cols,'#')
    
    def __repr__(self):
        return f'{self.leafDict[2]}'

    def dungeonGen(self):
        # method to do the BSP partition
        # initialize rootMap
        rows,cols,level = self.rows, self.cols, self.level
        rootMap = Leaf(self.rows,self.cols,0,0,None)
        leafDict = self.leafDict
        Dungeon.dungeonGenHelper(self, level, rootMap, leafDict)
        Dungeon.chamberGen(self)
        Dungeon.makeMap(self)
        Dungeon.tunnelGen(self)
        

    def dungeonGenHelper(self, level,rootMap,leafDict):
        if rootMap!=None:
            rows,cols = rootMap.rows, rootMap.cols
            lx,ly = rootMap.lx, rootMap.ly
            
            # base case
            if level == 1:
                return
                
            # recursive Case
            elif level != 1:
                # when leaf is horizontal
                if (self.leafDirection(cols,rows) == 'Horizontal'):
                    if self.verticalSplit(rows,cols,lx,ly) == None: left,right=None,None
                    else: left, right = self.verticalSplit(rows,cols,lx,ly)
                # when leaf is vertical
                elif (self.leafDirection(cols,rows) == 'Vertical'):
                    if self.horizontalSplit(rows,cols,lx,ly) == None: left,right=None,None
                    else: left, right = self.horizontalSplit(rows,cols,lx,ly)
                # when leaf is squarish, randomly pick one split method
                elif (self.leafDirection(cols,rows) == 'Squarish'):
                    choice = random.randint(0,1)
                    if (choice == 1): 
                        if (self.verticalSplit(rows,cols,lx,ly) == None): left,right=None,None
                        else: left, right = self.verticalSplit(rows, cols, lx, ly)
                    elif (choice == 0): 
                        if (self.horizontalSplit(rows,cols,lx,ly) == None): left,right=None,None
                        else: left, right = self.horizontalSplit(rows,cols,lx,ly)
                rootMap.left, rootMap.right = left, right
                try:
                    left.parent = rootMap
                    right.parent = rootMap
                except: pass
                self.leafDict[level].add(left)
                self.leafDict[level].add(right)
                self.dungeonGenHelper(level-1,left,leafDict)
                self.dungeonGenHelper(level-1,right,leafDict)

    
    def leafDirection(self,width,height):
        # Helper to define if the cell is vertical or horizontal or squarish
        prop = width/height
        if (prop > 1.25): return 'Horizontal'
        elif (prop < 0.75) : return 'Vertical'
        elif (0.75 <= prop <= 1.25): return 'Squarish'


    def verticalSplit(self,rows,cols,lx,ly):
        # Helper to randomly split leaf vertically
        # and add the splitted leaf in leafDict
        prop = int(cols * 0.3) # leave 15% space on both sides
        if prop >= 1:
            splitRand = random.randint(prop,cols-prop)
            left = Leaf(rows,splitRand,lx,ly,'vLeft')
            right = Leaf(rows, cols-splitRand, lx+splitRand, ly,'vRight')
            return left, right
        

    def horizontalSplit(self,rows,cols,lx,ly):
        # Helper to randomly split leaf horizontally
        # and append the splitted leaf in leafDict
        prop = int(rows * 0.4) # leave 20% space on both sides
        if prop >= 1:
            splitRand = random.randint(prop,rows-prop)
            upper = Leaf(splitRand,cols,lx,ly, 'hUpper')
            lower = Leaf(rows-splitRand,cols, lx, ly+splitRand, 'hLower')
            return upper, lower
    

    def chamberGen(self):
        # generate chambers in the divided leaf
        for leaf in self.leafDict[2]:
            if (leaf != None):
                for i in range(leaf.rows):
                    for j in range(leaf.cols):
                        leaf.gridSet.add((leaf.ly+i,leaf.lx+j)) # row col
                rows, cols = leaf.rows, leaf.cols
                leafMap = leaf.map
                # get the indexing for chamber
                if (self.level <4): para = 0.3
                else: para = 0.2
                cx0,cy0 = random.randint(1,max(int(para*cols),1)), random.randint(1,max(int(para*rows),1)) 
                cx1,cy1 = cols-random.randint(1,max(int(para*cols),1)), rows-random.randint(1,max(int(para*rows),1))
                # storing info in leaf instance
                chamber = Chamber(leaf)
                leaf.chamber = chamber
                # 10 percent chance that the chamber is a dampening area
                chamber.cx0, chamber.cy0 = cx0, cy0
                chamber.cx1, chamber.cy1 = cx1, cy1
                if abs(chamber.cx0-chamber.cx1)>=3 and abs(chamber.cy0-chamber.cy1)>=3:
                    chamber.tx, chamber.ty = (cx0+cx1)//2, (cy0+cy1)//2
                if random.random() < 0.02: chamber.isDamp = True # 2% of chance generating treasure room
                
                # modifying 2d leaf map
                if (int(cx0)!=int(cx1) and int(cy0)!=int(cy1)):
                    for i in range(cy0,cy1):
                        for j in range(cx0,cx1):
                            if chamber.isDamp: leafMap[i][j] = 'D'
                            else: leafMap[i][j] = 'C'
                            # adding (chamber grid global coordinate) to the gridSet

    def tunnelGen(self):
        # method to draw the half tunnel in the leaf
        level = self.level
        for key in self.leafDict:
            if key >= 2:
                for leaf in self.leafDict[key]:
                    if leaf != None:
                        rows, cols, lx, ly = leaf.rows, leaf.cols, leaf.lx, leaf.ly
                        tunnelWidth = int(key)

                        # getting a suitable tunnel Width
                        if level > 7:
                            if tunnelWidth <5: tunnelWidth = 2
                            if tunnelWidth >=5: tunnelWidth = 1
                        else:
                            if tunnelWidth <5: tunnelWidth = 3
                            if tunnelWidth >=5: tunnelWidth = 2

                        # building tunneling between leaves
                        # note that rows value and row index are shifted by 1
                        if leaf.split=='hUpper':
                            leaf.tx0, leaf.ty0 = cols//2, rows//2
                            leaf.tx1, leaf.ty1 = cols//2+tunnelWidth, rows
                            for j in range(rows//2,rows):
                                for w in range(tunnelWidth):
                                    try:
                                        grid = self.dungeonMap[ly+j][lx+cols//2+w]
                                        if grid == '#': 
                                            self.dungeonMap[ly+j][lx+cols//2+w]  = '_'
                                            # store the tunnel coordinate in leaf for path finding
                                            leaf.tunnelSet.add(((ly+j),(lx+cols//2+w)))
                                    except: pass
                                
                        elif leaf.split=='hLower':
                            leaf.tx0, leaf.ty0 = cols//2, 0
                            leaf.tx1, leaf.ty1 = cols//2+tunnelWidth, rows//2
                            for j in range(0,rows//2):
                                for w in range(tunnelWidth):
                                    try:
                                        grid = self. dungeonMap[ly+j][lx+cols//2+w]
                                        if grid == '#': 
                                            self. dungeonMap[ly+j][lx+cols//2+w] = '_'
                                            # store the tunnel coordinate in leaf for path finding
                                            leaf.tunnelSet.add(((ly+j),(lx+cols//2+w)))
                                    except: pass
                        
                        elif leaf.split=='vLeft':
                            leaf.tx0, leaf.ty0 = cols//2, rows//2
                            leaf.tx1, leaf.ty1 = cols, rows//2+tunnelWidth
                            for i in range(cols//2,cols):
                                for w in range(tunnelWidth):
                                    try:
                                        grid = self.dungeonMap[ly+rows//2+w][lx+i]
                                        if grid == '#': 
                                            self.dungeonMap[ly+rows//2+w][lx+i] = '_'
                                            # store the tunnel coordinate in leaf for path finding
                                            leaf.tunnelSet.add(((ly+rows//2+w),(lx+i)))
                                    except: pass
             
                        elif leaf.split=='vRight':
                            leaf.tx0, leaf.ty0 = 0, rows//2
                            leaf.tx1, leaf.ty1 = cols//2, rows//2+tunnelWidth
                            for i in range(0, cols//2):
                                for w in range(tunnelWidth):
                                    try:
                                        grid = self.dungeonMap[ly+rows//2+w][lx+i]
                                        if grid == '#': 
                                            self.dungeonMap[ly+rows//2+w][lx+i] = '_'
                                            # store the tunnel coordinate in leaf for path finding
                                            leaf.tunnelSet.add(((ly+rows//2+w),(lx+i)))
                                    except: pass
   
    # method to make the smallest eaves into one 2dlist map 
    def makeMap(self):
        for leaf in self.leafDict[2]:
            if leaf!=None:
                for i in range(leaf.rows):
                    for j in range(leaf.cols):
                        self.dungeonMap[leaf.ly+i][leaf.lx+j] = leaf.map[i][j]
    
    #helper to locate the smallest containter leaf of position
    def locateLeaf(self,position):
        for leaf in self.leafDict[2]:
            try:
                if position in leaf.gridSet:
                    return leaf
            except: pass
        else:
            return None
            

################################################################################
# Closet path generation
################################################################################

#leveraging the binart tree structure of my dungeon
#to get a path

def getPath(game,start,end):
    # function that takes in the start position and end position
    # return a closet path on the tree from start to end 
    leafStart = game.locateLeaf(start)
    leafEnd = game.locateLeaf(end)
    path1 = pathToRoot(game, leafStart)
    path2 = pathToRoot(game, leafEnd)
    if path1!= None and path2!= None:
        try:
            iLeft, iRight = shapeLists(path1,path2)
        except:
            iLeft, iRight = 0,0
        leftPath = path1[0:iLeft+1]
        rightPath = path2[0:iRight][::-1]
        leftPath.extend(rightPath)
        return leftPath[::-1]
    else: 
        return[]

def shapeLists(path1, path2):
    # helper to get the midpoint nodes in two paths
    for node in path1:
        if node in path2:
            iLeft = path1.index(node)
            iRight = path2.index(node)
            return iLeft, iRight

def pathToRoot(game,leaf):
    # wrapper to get path to root
    result = []
    return pathToRootHelper(game, leaf, result)

def pathToRootHelper(game, leaf, result):
    # recursive function to get path to root
    if leaf == None or leaf.parent == None:
        return result
    else:
        center = leaf.parent.center
        result.append(center)
        return pathToRootHelper(game, leaf.parent,result)




