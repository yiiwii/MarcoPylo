# this is a file containg the user class which stores user information on the map
import random
# define user object class
class User():
    def __init__(self,name,rows,cols):
        self.name = name
        self.uRow = rows//2
        self.uCol = cols//2
        self.r = 10
        self.marco = None
        self.polo = None
        self.path = []

    moveValue = 1
    def goLeft(self):
        self.uCol -= self.moveValue

    def goRight(self):
        self.uCol += self.moveValue

    def goUp(self):
        self.uRow -= self.moveValue

    def goDown(self):
        self.uRow += self.moveValue
    
    def pathFinding(self,Dungeon):
        
        self.path = []
    


    