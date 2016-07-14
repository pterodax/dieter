from random import randint
from UF_final_VP import UnionFind
from copy import deepcopy
from time import sleep


class HexKI:
    # Initialiesierung mit Feldgroesse und Information ob oben -> unten oder rechts -> links
    def __init__(self, m, n, player, random = False):
        # initialisiere KI abhaengig von m und n und gegebenenfalls random
        if random:
            self.activeKI = HexKI_rnd(m, n, player)
        elif m != n:
            self.activeKI = HexKI_asym(m, n, player)
        elif m == n:
            self.activeKI = HexKI_dieter(m, n, player)

    def chooseOrder(self, firstmove):
        return self.activeKI.chooseOrder(firstmove)

    def calculateMove(self):
        return self.activeKI.calculateMove()

    def nextMove(self):
        return self.activeKI.nextMove()

    def receiveMove(self, move):
        self.activeKI.receiveMove(move)

    def readBoard(self, board, current=True):
        self.activeKI.readBoard(board, current)

    def __str__(self):
        return str(self.activeKI)


# brueckenbasierte KI namens dieter fuer Hex
class HexKI_dieter:

    # Initialiesierung mit Feldgroesse und Information ob oben -> unten oder rechts -> links
    def __init__(self, m, n, player):
        # Zuweisung der Variablen fuer belegte Felder
        if player == "eins":
            self.player = 1
            self.opponent = 2
            print('dieter ist 1')
        if player == "zwei":
            self.player = 2
            self.opponent = 1
            print('dieter ist 2')

        self.m = m
        self.n = n

        # Initialisierung des Boards mit 3 fuer freie Felder, um die Bewertungsfunktion umzusetzen
        self.board = [[3 for j in range(n)] for i in range(m)]
        #self.monitoredFields = set()

        if n % 2 == 0 and m % 2 == 0:
            self.candidates = [(m//2-1  , n//2),(m//2  , n//2-1),(m//2-1  , n//2-1),(m//2  , n//2)]
            self.bestmove = self.candidates[randint(0,3)]
        else:
            self.candidates = [(m//2, n//2)]
            self.bestmove = self.candidates[0]

        # Initialiesierung einer UnionFind-Struktur
        self.UF = UnionFind(m, n)

        # Speichern der bisher besetzten Felder
        self.myFields = []
        self.opponentFields  = []
        self.allFields = []
        #self.roundOne = False

    # ueberpruefe, ob geswitcht werden soll
    def chooseOrder(self, firstmove):
        for move in self.candidates:
            if firstmove == move:
                if self.player == 1:
                    self.player = 2
                    self.opponent = 1
                else:
                    self.player = 1
                    self.opponent = 2
                self.transposeBoard()

                self.myFields, self.opponentFields = self.opponentFields, self.myFields
                # print("myFields:")
                # print(self.myFields)
                # print()
                # print("opponent.Fields:")
                # print(self.opponentFields)
                print("dieter hat geswitcht")
                print(self.player)
                # sleep(1)
                return 1
        print("dieter wollte nicht switchen")
        return 2

    # Berechnung des naechsten Zuges durch Bewertung der moeglichen Zuege, Rueckgabe eines bestbewerteten Zuges
    def calculateMove(self):
        # if self.roundOne:
        #     candidates = [(self.m//2-1  , self.n//2),(self.m//2  , self.n//2-1),(self.m//2-1  , self.n//2-1),(self.m//2  , self.n//2)]

        #     validCandidates= []
        #     for e in candidates:
        #         x,y = e
        #         if self.board[x][y] == 3:
        #             validCandidates.append(e)

        #     self.bestmove = validCandidates[randint(0,len(validCandidates)-1)]
        #     self.roundOne = False

        ratedBoard = deepcopy(self.board)
        HigherRatings = []
        ReduceRatings = []
        for line in self.board:
            print(line)

        #higher ratings with priority functions
        for field in self.myFields:

            HigherRatings += self.findBridges(field,self.player)
            HigherRatings += self.checkMonitoredFields(field)
            HigherRatings += self.findEndBridgeMonitored(field)
            HigherRatings += self.findCriticalFields(self.UF, field,self.player, 0)

        for field in self.opponentFields:
            HigherRatings += self.findCriticalFields(self.UF, field, self.opponent, 0)
            HigherRatings += self.findBridges(field,self.opponent)
            #reduce ratings with reduce functions
        for field in self.allFields:
            ReduceRatings += self.checkEingekesselt(field)
            HigherRatings += self.checkEmptyArea(field)

        #update ratings
        for e in HigherRatings:
            x, y = e[0]
            rating = e[1]
            if ratedBoard[x][y] < rating:
                ratedBoard[x][y] = rating

        for e in ReduceRatings:
            x, y = e[0]
            rating = e[1]
            if ratedBoard[x][y] > rating:
                ratedBoard[x][y] = rating

        # for fields in self.opponentFields:
            # bridges = self.findBridges(fields,self.opponent)
            # for e in bridges:
                # x, y = e[0]
                # rating = e[1]
                # ratedBoard[y][x] += rating

        print('rated:')
        for line in ratedBoard:
            print(line)


        #chooseMove
        max = [[(-1,-1), 0]]
        for i in range(self.m):
            for j in range(self.n):
                if ratedBoard[i][j] >= max[0][1]:
                    if ratedBoard[i][j] > max[0][1]:
                        max = []
                    max.append([(i,j),ratedBoard[i][j]])
        list = sorted(max, key = lambda a: a[0][0])

        # if list[0][1] == 3:
            # return list[randint(0,len(list))][0]
        # if list[0][0][0] < self.m - list[-1][0][0]:
            # print(list[0])
            # return(list[0][0])
        # else:
            # print(list[0])
            # return(list[-1][0])
        erg = list[randint(0,len(list)-1)]
        # print(erg)
        self.bestmove = erg[0]
        return True

    def HighestLowest(self):
        highest = None
        lowest = None
        for i in range(self.m):
            for j in range(self.n):
                if self.board[i][j] == self.player and highest == None:
                    highest = (i,j)

                if self.board[self.m-i-1][self.n-j-1] == self.player and lowest == None:
                    lowest = (self.m-i-1,self.n-j-1)


        # print("highest: "+ str(highest))
        # print("lowest: " +str( lowest))
        return([highest,lowest])

    # setze den naechsten Zug
    def nextMove(self):
        print("bestmove = " + str(self.bestmove))
        x,y = self.bestmove
        self.board[x][y] = self.player
        self.UF.makeMove(x+1, y+1, self.player)
        self.myFields.append(self.bestmove)
        if self.player ==2:
            return (x,y)

        if self.player ==1:
            return (y,x)

    # empfaengt den Zug des Gegners
    def receiveMove(self, move):
        if self.player == 2:
            x, y = move
        else:
            y, x = move
        # setze den Zug in Board, UnionFind und opponentFields
        self.board[x][y] = self.opponent
        self.UF.makeMove(x+1, y+1, self.opponent)
        self.opponentFields.append((x, y))
        #if self.UF.getWinner() == None:
            # berechne den naechsten, bestbewerteten Zug
            #self.bestmove = self.calculateMove()

    def receiveMyMove(self, move):
        if self.player == 2:
            x, y = move
        else:
            y, x = move
        self.board[x][y] = self.player
        self.UF.makeMove(x+1, y+1, self.player)
        self.myFields.append((x, y))

    # liest einen gegebenen Spielstand ein
    def readBoard(self, board, current = True):
        m = len(board)
        n = len(board[0])
        self.board = [[3 for i in range(self.m)] for j in range(self.n)]
        self.UF = UnionFind(self.m, self.n)
        self.myFields = []
        self.opponentFields = []
        for i in range(m):
            for j in range(n):
                # setze die bereits gemachten Zuege auch in UF, Board und my/opponentFields
                if board[i][j] == self.opponent:
                    self.receiveMove((i, j))
                elif board[i][j] == self.player:
                    self.receiveMyMove((i, j))
        #print(self.board)
        if current and len(self.opponentFields) < len(self.myFields):
            print('dieter meldet: switch received')
            self.opponentFields, self.myFields = self.myFields, self.opponentFields
            self.player, self.opponent = self.opponent, self.player
            self.transposeBoard()
            for line in self.board:
                print(line)
        elif not current and len(self.opponentFields) > len(self.myFields):
            self.opponentFields, self.myFields = self.myFields, self.opponentFields
            self.player, self.opponent = self.opponent, self.player
            self.transposeBoard()


    def transposeBoard(self):
        new_board = [[0 for i in range(self.n)] for j in range(self.m)]
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                    new_board[j][i] = self.board[i][j]
        self.board = new_board


    # Funktion, die ueberprueft, ob der Gegner die Bruecken eines Feldes field angegriffen hat
    def checkMonitoredFields(self, field):
        x,y = field
        score = 200
        p = self.player
        opponent = self.opponent
        temp = []
        # print(self.moves)
        # self.moves.pop()
        # Bruecke zum Feld oben links von field
        if x-1 >= 0 and y-1 >= 0 and self.board[x-1][y-1] == p:
            # linkes Feld vom Gegner besetzt
            if self.board[x-1][y] == opponent and self.board[x][y-1] == 3:
                temp.append([(x, y-1), score])
            # rechtes Feld vom Gegner besetzt
            elif self.board[x-1][y] == 3 and self.board[x][y-1] == opponent:
                temp.append([(x-1, y), score])

        # Bruecken zum Feld direkt ueber field
        if x-2 >= 0 and y+1 <= self.m-1 and self.board[x-2][y+1] == p:
            # linkes Feld vom Gegner besetzt
            if self.board[x-1][y] == opponent and self.board[x-1][y+1] == 3:
                temp.append([(x-1,y+1), score*2])
            # rechtes Feld vom Gegner besetzt
            elif self.board[x-1][y] ==3 and self.board[x-1][y+1] == opponent:
                temp.append([(x-1, y), score*2])

        # Bruecke zum Feld oben rechts von field
        if x-1 >= 0 and y+2 <= self.m-1 and self.board[x-1][y+2] == p:
            # oberes Feld vom Gegner besetzt
            if self.board[x-1][y+1] == opponent and self.board[x][y+1] == 3:
                temp.append([(x,y+1), score])
            # unteres Feld vom Gegner besetzt
            elif self.board[x-1][y+1] == 3 and self.board[x][y+1] == opponent:
                temp.append([(x-1,y+1), score])

        # Bruecke zum Feld unten rechts von field
        if x+1 <= self.m-1 and y+1 <= self.m-1 and self.board[x+1][y+1] == p:
            # oberes Feld vom Gegner besetzt
            if self.board[x][y+1] == opponent and self.board[x+1][y] == 3:
                temp.append([(x+1,y), score])
            # unteres Feld vom Gegner besetzt
            elif self.board[x][y+1] == 3 and self.board[x+1][y] == opponent:
                temp.append([(x,y+1), score])

        # Bruecke zum Feld direkt unter field
        if x+2 <= self.m-1 and y-1 >= 0 and self.board[x+2][y-1] == p:
            # rechtes Feld vom Gegner besetzt
            if self.board[x+1][y] == opponent and self.board[x+1][y-1] == 3:
                temp.append([(x+1, y-1), score*2])
            # linkes Feld vom Gegner besetzt
            elif self.board[x+1][y] == 3 and self.board[x+1][y-1] == opponent:
                temp.append([(x+1, y), score*2])

        # Bruecke zum Feld unten links von Field
        if x+1 <= self.m-1 and y-2 >= 0 and self.board[x+1][y-2] == p:
            # unteres Feld vom Gegner besetzt
            if self.board[x+1][y-1] == opponent and self.board[x][y-1] == 3:
                temp.append([(x, y-1), score])
            # oberes Feld vom Gegner besetzt
            if self.board[x+1][y-1] == 3 and self.board[x][y-1] == opponent: # unten links oben
                temp.append([(x+1, y-1), score])
        return temp

    # finde Brueckenfelder ausgehend von field, falls beide(!) Felder zwischendrin frei sind
    def findBridges(self, field, player):
        Score = 20
        HighScore = Score
        LowScore = Score
        highest = self.HighestLowest()[0]
        lowest = self.HighestLowest()[1]

        if player == self.opponent:
            x = field[0]
            y = field[1]
            opponent = self.player
            Score = Score #####stellschraube
        else:
            x = field[0]
            y = field[1]
            opponent = self.opponent
            if (x,y) == highest :
                HighScore *=3
            if (x,y) == lowest:
                LowScore *=3




        temp = []
        # print(self.moves)
        # self.moves.pop()
        if x-1 >= 0 and y-1 >= 0 and self.board[x-1][y-1] == 3:  #oben links
            if not (self.board[x-1][y] == opponent or self.board[x][y-1] == opponent):
                temp.append([(x-1,y-1),HighScore])
        if x-2 >= 0 and y+1 <= self.m-1 and self.board[x-2][y+1] == 3: #oben
            if not (self.board[x-1][y] == opponent or self.board[x-1][y+1] == opponent):
                temp.append([(x-2, y+1), HighScore*2])
        if x-1 >= 0 and y+2 <= self.m-1 and self.board[x-1][y+2] == 3: #oben rechts
            if not (self.board[x-1][y+1] == opponent or self.board[x][y+1] == opponent):
                temp.append([(x-1, y+2), HighScore])
        if x+1 <= self.m-1 and y+1 <= self.m-1 and self.board[x+1][y+1] == 3: #unten rechts
            if not (self.board[x][y+1] == opponent or self.board[x+1][y] == opponent):
                temp.append([(x+1, y+1),LowScore])
        if x+2 <= self.m-1 and y-1 >= 0 and self.board[x+2][y-1] == 3: #unten
            if not (self.board[x+1][y] == opponent or self.board[x+1][y-1] == opponent):
                temp.append([(x+2, y-1),LowScore*2])
        if x+1 <= self.m-1 and y-2 >= 0 and self.board[x+1][y-2] == 3: #unten links
            if not (self.board[x+1][y-1] == opponent or self.board[x][y-1] == opponent):
                temp.append([(x+1, y-2),LowScore])
        #print("bruecken sind:  " + str(temp))
        return temp

    def findEndBridgeMonitored(self,field):
        x,y = field
        Score = 300
        temp = []
        opponent = self.opponent
        if x == 1:
            try:
                if (self.board[x-1][y] == opponent and self.board[x-1][y+1] == 3): # oben rechts
                    temp.append([(x-1,y+1), Score])
                    # print("oben rechts rand")
                elif (self.board[x-1][y] ==3 and self.board[x-1][y+1] == opponent): # oben links
                    temp.append([(x-1, y), Score])
                    # print("oben links rand")
            except IndexError:
                pass
        if x == self.m-2:
            try:
                if self.board[x+1][y] == opponent and self.board[x+1][y-1] == 3: # unten rechts
                    temp.append([(x+1, y-1), Score])
                    # print("unten links rand ")
                elif self.board[x+1][y] == 3 and self.board[x+1][y-1] == opponent: # unten links
                    temp.append([(x+1, y), Score])
                    # print("unten rechts rand ")
            except IndexError:
                pass
        return temp

    def findCriticalFields(self, UF, field, player, level):
        if level >=3:
            return []
        if player == 1:
            opponent = 2
        else:
            opponent = 1
        # if player == self.player:
            # moves = self.myFields
        # else:
            # moves = self.opponentFields


        Score = 1000
        temp1 = []
        temp2 = []
        x,y = field
        nachbarn = [(x-1,y),(x-1,y+1),(x,y+1),(x+1,y),(x+1,y-1),(x,y-1)]

        #schmeisse ungueltige nachbarn raus   unnoetig, da UF schlau !???
        validNachbarn = []
        for e in nachbarn:
            u,v = e
            if not (u < 0 or u > self.m-1 or v <0 or v>self.n-1) and self.board[u][v] ==3:
                validNachbarn.append(e)


        for e in validNachbarn:
            x,y = e

            TestUF = deepcopy(UF)
            TestUF.makeMove(x+1,y+1,player)
            if TestUF.getWinner() == player:
                temp1.append([(x,y),Score*2])  #([(x+1, y-2),LowScore])
            elif TestUF.getWinner() == opponent:
                temp1.append([(x,y),Score])

            if TestUF.getWinner() == None:
                # for k in moves:                                                                       #laufzeit hoch
                    # temptemp = self.findCriticalFields(TestUF, k, player, level +1)

                temptemp = self.findCriticalFields(TestUF, e, player, level +1)                       #laufzeit runter
                for e in temptemp:
                    e[1] = 0.5 * e[1]

                    # print(temptemp)
                temp2 += temptemp

        # print(temp1)
        return temp1 + temp2

    def checkEingekesselt(self,field):
        temp = []
        x,y = field
        if self.board[x][y] != 3:
            return temp

        player = self.player
        opponent = self.opponent
        try:
            #nachbarn = [(x-1,y),(x-1,y+1),(x,y+1),(x+1,y),(x+1,y-1),(x,y-1)]
            LinksOben = (self.board[x-1][y] == opponent and self.board[x-1][y+1] == player and self.board[x][y+1] == 3 and self.board[x+1][y] == player and self.board[x+1][y-1] == 3 and self.board[x][y-1] == player)
            RechtsOben =(self.board[x-1][y] == 3 and self.board[x-1][y+1] == player and self.board[x][y+1] == opponent and self.board[x+1][y] == player and self.board[x+1][y-1] == 3 and self.board[x][y-1] == player)
            Unten = (self.board[x-1][y] == 3 and self.board[x-1][y+1] == player and self.board[x][y+1] == 3 and self.board[x+1][y] == player and self.board[x+1][y-1] == opponent and self.board[x][y-1] == player)
            Frei = (self.board[x-1][y] == 3 and self.board[x-1][y+1] == player and self.board[x][y+1] == 3 and self.board[x+1][y] == player and self.board[x+1][y-1] == 3 and self.board[x][y-1] == player)



            if (LinksOben or RechtsOben or Unten or Frei):
                # print("eingekesseltes feld: " + str(field))
                temp.append([(x,y),3])
        except:
            pass

        return temp

    def checkEmptyArea(self,field):
        temp = []
        x,y = field
        try:
            empty = (self.board[x][y] == 3 and self.board[x-1][y] == 3 and self.board[x-1][y+1] == 3 and self.board[x][y+1] == 3 and self.board[x+1][y] == 3 and self.board[x+1][y-1] == 3 and self.board[x][y-1] == 3)
            if empty:
                temp.append([(x,y),40])

            return temp
        except IndexError:
            return temp

    def __str__(self):
        return "dieter"

class HexKI_rnd:

    def __init__(self, m, n, player):
        if player == "eins":
            self.player = 1
            self.opponent = 2
        else:
            self.player = 2
            self.opponent = 1
        self.m = m
        self.n = n
        self.board = [[0 for j in range(n)] for i in range(m)]
        self.bestmove = self.randomMove()
        print("AI_rnd")

    def randomMove(self):
        free_spaces = []
        for i in range(self.m):
            for j in range(self.n):
                if self.board[i][j] == 0:
                    free_spaces.append((i,j))
        length = len(free_spaces)
        res = randint(0, length-1)
        return(free_spaces[res])

    def chooseOrder(self, firstmove):
        switch = randint(1,2)
        if switch == 1:
            self.player, self.opponent = self.opponent, self.player
            print("random switched")
        return switch

    def calculateMove(self):
        self.bestmove = self.randomMove()
        return True

    def nextMove(self):
        x,y = self.bestmove
        self.board[x][y] = self.player
        return (x,y)

    def receiveMove(self, move):  #empfange gegnermove
        self.board[move[0]][move[1]] = self.opponent

    def readBoard(self, board, current = True):
        self.board = board
        count = 0
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                if self.board[i][j] == self.player:
                    count +=1
        if count == 1:
            self.player, self.opponent = self.opponent, self.player

    def __str__(self):
        return 'random'


class HexKI_asym:

    def __init__(self, m, n, player):
        self.rows = m
        self.columns = n
        self.round = 0
        if player == "eins":
            self.player = 1
            self.opponent = 2
        else:
            self.player = 2
            self.opponent = 1
        if n > m:
            self.m = m
            self.n = n
        elif m > n:
            self.m = n
            self.n = m
        self.board = [[0 for j in range(self.n)] for i in range(self.m)]
        self.matrix = [[0 for j in range(self.n)] for i in range(self.m)]
        x = 1
        for i in range(self.m):
            for j in range(self.m+1):
                if j < (self.m+1)-(i+1):
                    self.matrix[i][j] = x
                    self.matrix[self.m-1-j][(self.m+1)-1-i] = x
                    x +=1
        for line in self.matrix:
            print(line)
        self.bestmove = self.randomMove(self.m, self.m+1)
        self.lastmove = None
        #print("AI_asym")

    def chooseOrder(self, firstmove):
        if self.player == 1 and self.rows < self.columns:
            return 1
        elif self.player == 2 and self.rows > self.columns:
            return 1
        else:
            return 2

    def randomMove(self, m, n):
        free_spaces = []
        for i in range(m):
            for j in range(n):
                if self.board[i][j] == 0:
                    free_spaces.append((i,j))
        length = len(free_spaces)
        res = randint(0, length-1)
        return(free_spaces[res])

    def calculateMove(self):
        print('calculateMove')
        for e in self.board:
            print(e)
        res = None
        if self.lastmove[1] > self.m + 1:
            self.bestmove = self.randomMove(self.m, self.n)
        else:
            x = self.lastmove[0]
            y = self.lastmove[1]
            if x+y <= self.m-1:
                print('if')
                number = self.matrix[x][y]
                for i in range(self.m):
                    for j in range(self.m+1):
                        if (i+j > x+y) and self.matrix[i][j] == number:
                            res = (i,j)
            else:
                print('else')
                number = self.matrix[x][y]
                for i in range(self.m):
                    for j in range(self.m+1):
                        if (i+j < x+y) and self.matrix[i][j] == number:
                            res = (i,j)
                            #return(i,j)
            if res and self.board[res[0]][res[1]] == 0:
                self.bestmove = res
            else:

                self.bestmove = self.randomMove(self.m, self.n)
        for e in self.matrix:
            print(e)
        return True

    def nextMove(self):
        # self.calculateMove()
        print("nextMove")
        x,y = self.bestmove
        print((x, y))
        self.board[x][y] = self.player
        if self.rows > self.columns:
            x,y = y,x
        self.round += 1
        return (x,y)

    def receiveMove(self, move):  #empfange gegnermove
        x,y = move
        if self.rows > self.columns:
            x,y = y,x
        self.board[x][y] = self.opponent
        self.round += 1
        self.lastmove = (x, y)

    def readBoard(self, board, current = True):
        work_board = deepcopy(board)
        if len(work_board) == self.m:
            transposed = False
        else:
            transposed = True
        if transposed:
            self.board = self.transposeBoard(work_board)
        else:
            self.board = work_board
        count = 0
        res = None
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                if self.board[i][j] == self.player:
                    count +=1
                    res = (i, j)
        if count == 1:
            print('switched player /opponent')
            self.player, self.opponent = self.opponent, self.player
            self.lastmove = res

    def transposeBoard(self, board):
        new_board = [[0 for j in range(len(board))] for i in range(len(board[0]))]
        for i in range(len(board)):
            for j in range(len(board[0])):
                new_board[j][i] = board[i][j]
        return new_board

    def __str__(self):
        return 'asym'
