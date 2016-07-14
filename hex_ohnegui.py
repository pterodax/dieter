from KI import HexKI
from random import randint
from tkinter import *
from tkinter import messagebox
from time import sleep
from UF_final_VP import UnionFind


class HexBoard: # Klasse zur Verwaltung der GUI-Logik
    def __init__(self, m, n):
        self.m = m
        self.n = n
        self.currentPlayer = None
        self.lastMove = None
        self.win = None
        self.unionfind = UnionFind(m, n) # UF-Struktur zur Ermittlung des Gewinners

    def setCurrentPlayer(self, i):
        self.currentPlayer = i

    def finished(self): # gibt True zurueck, wenn aktuell Gewinner vorhanden
        if self.unionfind.getWinner():
            self.win = self.unionfind.getWinner()
            return True
        else:
            return False

    def winner(self):   # gibt gewinner zurueck
        return self.win

    def receiveMove(self, move): # fuege move zur UF-Struktur hinzu
        self.unionfind.makeMove(move[0] + 1, move[1] + 1, self.currentPlayer)
        self.lastMove = move

    def getLastMove(self):
        return self.lastMove

    def getVictoryPath(self):
        ZHK = self.unionfind.getVP()
        visited = {}
        for e in ZHK:
            visited[e] = False

        vorgaenger = {}
        queue = []
        startnode = None
        endnode = None
        if self.unionfind.getWinner() == 1:
            for i in range(self.m + 1):
                if (i,1) in ZHK:
                    startnode = (i,1)

                if (i,self.n) in ZHK:
                    endnode = (i, self.n)

        if self.unionfind.getWinner() == 2:
            for j in range(self.n + 1):
                if (1, j) in ZHK:
                    startnode = (1,j)
                if (self.m,j) in ZHK:
                    endnode = (self.m, j)

        queue.append(startnode)
        vorgaenger[startnode] = startnode
        print(startnode)
        print(endnode)

        while len(queue) > 0:
            node = queue.pop()
            x,y = node
            if node == endnode:
                break
            else:
                nachbarn = [(x-1,y),(x-1,y+1),(x,y+1),(x+1,y),(x+1,y-1),(x,y-1)]
                for e in nachbarn:
                    if e in ZHK and visited[e] == False:
                        queue.append(e)
                        visited[e] = True
                        vorgaenger[e] = (x,y)


        erg = []
        pos = endnode
        erg.append(endnode)
        while not startnode in erg:
            pos = vorgaenger[pos]
            erg.append(pos)

        return erg


class Game: # zentrale Klasse zur Verwaltung des Spielablaufs
    def __init__(self, m, n, mode):
        if mode == "inter" or mode == "ki":
            self.switched = False
        else:
            self.switched = False
        self.ki_switched = False
        self.m = m
        self.n = n
        self.mode = mode
        self.gui = None
        self.hexboard = HexBoard(m, n)
        self.board = [[0 for j in range(n)] for i in range(m)]
        self.current = self.chooseFirst()
        self.round = 0
        self.KI1 = None
        self.KI2 = None
        self.ki_player = None
        self.human_player = None
        # initialisiere die KI zufaellig als rot oder blau, falls Mensch vs. KI
        if self.mode == "inter":
            self.ki_player = randint(1, 2)
            if self.ki_player == 1:
                print('ki1')
                self.KI1 = HexKI(m, n, "eins")
                self.human_player = 2
            else:
                print('ki2')
                self.KI2 = HexKI(m, n, "zwei")
                self.human_player = 1

        # initialisiere zwei KIs
        elif self.mode == "ki":
            self.KI1 = HexKI(m, n, "eins", True)
            self.KI2 = HexKI(m, n, "zwei")


    def startGame(self): # initiiert ersten move wenn KI am Zug ist
        if self.mode == "inter":
            if self.current == self.ki_player:
                if self.ki_player == 1:
                    self.makeMove(self.KI1.nextMove())
                else:
                    self.makeMove(self.KI2.nextMove())


            #elif self.current == 2 and self.switched:
            #    self.current == 1
            # elif self.current == 2 and self.m != self.n and self.switched:
            #     self.makeMove(self.KI2.nextMove())
        if self.mode == "ki":
            if self.current == 2:
                self.makeMove(self.KI2.nextMove())
            elif self.current ==1:
                self.makeMove(self.KI1.nextMove())

    def getBoard(self):
        return self.board

    def makeMove(self, move): # fuehrt Zug mit uebergebenen move-Koordinaten aus
        for line in self.board:
            print(line)
        if self.board[move[0]][move[1]] != 0:
            print("Error")
            print(move)
            print(self.current)
            return

        else:   # move wird ausgefuehrt
            self.hexboard.setCurrentPlayer(self.current)
            self.hexboard.receiveMove(move)
            if self.currentPlayer() == 1:
                self.board[move[0]][move[1]] = 1
                self.current = 2
            elif self.currentPlayer() == 2:
                self.board[move[0]][move[1]] = 2
                self.current = 1
            self.hexboard.setCurrentPlayer(self.current)
            self.round += 1
            print('made move')

        if self.mode == "inter" and self.current == self.ki_player: # Besonderheiten bei der Move-Ausfuehrung im inter-Modus
            if not self.hexboard.finished():
                if self.ki_player == 1:
                    self.KI1.receiveMove(move)
                    if self.round == 1:
                        if self.KI1.chooseOrder(self.getLastMove()) == 1:
                            self.ki_switched = True
                            self.switch(1)
                        else:
                            self.KI1.calculateMove()
                            self.makeMove(self.KI1.nextMove())
                    else:
                        self.KI1.calculateMove()
                        self.makeMove(self.KI1.nextMove())
                elif self.ki_player == 2:
                    self.KI2.receiveMove(move)
                    if self.round == 1:
                        if self.KI2.chooseOrder(self.getLastMove()) == 1:
                            self.ki_switched = True
                            self.switch(2)
                        else:
                            self.KI2.calculateMove()
                            self.makeMove(self.KI2.nextMove())
                    else:
                        self.KI2.calculateMove()
                        self.makeMove(self.KI2.nextMove())

                #if not self.hexboard.finished() and self.current == 2:
                #    self.makeMove(self.KI2.nextMove())

        if self.mode == "ki":   # Besonderheiten bei der Move-Ausfuehrung im ki-Modus
            if not self.hexboard.finished():
                if self.current == 1:
                    self.KI1.receiveMove(move)
                    if self.round == 1 and not self.switched:
                        if self.KI1.chooseOrder(self.getLastMove()) == 1:
                            self.switch(1)
                        else:
                            self.KI1.calculateMove()
                            self.makeMove(self.KI1.nextMove())
                    else:
                        self.KI1.calculateMove()
                        self.makeMove(self.KI1.nextMove())
                elif self.current == 2:
                    self.KI2.receiveMove(move)
                    if self.round == 1 and not self.switched:
                        if self.KI2.chooseOrder(self.getLastMove()) == 1:
                            self.switch(2)
                        else:
                            self.KI2.calculateMove()
                            self.makeMove(self.KI2.nextMove())
                    else:
                        self.KI2.calculateMove()
                        self.makeMove(self.KI2.nextMove())


    def chooseFirst(self): # waehlt zufaellig ersten Spieler
        return randint(1, 2)

    def currentPlayer(self): # gibt Spieler zurueck, der aktuell am Zug ist
        return self.current

    def getLastMove(self):
        return self.hexboard.getLastMove()

    def switch(self, ki_player):   # tauscht die Spieler-Belegung des letzten moves im switch-fall
        if self.mode == "inter":
            self.ki_player, self.human_player = self.human_player, self.ki_player
            self.KI1, self.KI2 = self.KI2, self.KI1
            self.switched = True
            if ki_player == 0:
                print('human switched')
                if self.ki_player == 2:
                    self.KI2.readBoard(self.board, True)
                    self.KI2.calculateMove()
                    self.makeMove(self.KI2.nextMove())
                else:
                    self.KI1.readBoard(self.board, True)
                    self.KI1.calculateMove()
                    self.makeMove(self.KI1.nextMove())


        elif self.mode == "human":
            if self.current == 1:
                self.current = 2
            else:
                self.current = 1
            self.switched = True

        elif self.mode == "ki":
            self.switched = True
            self.KI1, self.KI2 = self.KI2, self.KI1
            if ki_player == 1:
                self.KI1.readBoard(self.board, True)
                self.KI1.calculateMove()
                self.makeMove(self.KI1.nextMove())
            elif ki_player == 2:
                self.KI2.readBoard(self.board, True)
                self.KI2.calculateMove()
                self.makeMove(self.KI2.nextMove())



    def finished(self):
        return self.hexboard.finished()

    def winner(self):
        return self.hexboard.winner()

    def __str__(self):
        if self.winner() == 1:
            return str(self.KI1)
        else:
            return str(self.KI2)


mode = "ki"
m = 11
n = 11


results = []
for i in range(20):
    a = Game(m, n, mode)
    a.startGame( )
    results.append(str(a))

print(results)

