from KI import HexKI
from random import randint
from tkinter import *
from tkinter import messagebox
from time import sleep
from UF_final_VP import UnionFind


class HexGui: # Klasse zum Aufbau der GUI und zur Interaktion mit der GUI

	def restart(self): # beendet aktuelles Spiel, startet neues Spiel + Gui mit den gleichen Ausmaßen
		temp = self.mode
		#self.game = None
		self.frame.quit()
		self.root.destroy()
		a = Game(self.m, self.n, temp)
		b = HexGui(self.m, self.n, a)

	def __init__(self, m, n, game): # Initialisierung der GUI
		self.polygons = {}
		self.m = m
		self.n = n
		self.count = 0
		self.game = game
		self.mode = self.game.mode
		self.root = Tk() # root-Wigdet
		mstr = str(self.m*120)
		nstr = str(self.n*65)
		self.root.geometry(mstr+"x"+nstr) # Einstellung der Spielfeld-Groesse
		self.frame = Frame(self.root,width=m*105, height=n*105) # frame zur Gruppierung der Widgets
		self.frame.pack()
		self.r = Button(self.frame, text="RESTART", fg="blue", command=self.restart) # Restart-Button
		self.r.pack(side=LEFT)
		self.a = Button(self.frame, text="QUIT", fg="red", command=self.frame.quit) # Beenden-Button
		self.a.pack(side=LEFT)
		self.w = Canvas(self.root, width=m*100, height=n*100)
		self.w.bind("<Button-1>", self.click) # Bindung von self.click an linke Maustaste
		self.w.pack()


		for i in range(self.n): # Initialisierun der Spielfeld-Polygone
			for j in range(self.m):
				offset = j*25
				x = i*50 + offset
				y = j*50
				fieldhandle = self.w.create_polygon(x+50,y+25, x+75,y+5, x+100,y+25, x+100,y+55, x+75,y+75, x+50,y+55, outline = "black", fill="grey", activefill = "white")
				self.polygons[(j, i)] = fieldhandle # Polygon mit zugehoerigen Koordinaten wird im polygons-Dictionary hinterlegt
		for i in range(self.n): # Zeichnen der blauen Begrenzungs-Linien
			for j in range(self.m):
				offset = j*25
				x = i*50 + offset
				y = j*50
				if j == 0:
					border1 = self.w.create_line(x+50,y+25, x+75, y+5, fill="blue", width = 4)
					border2 = self.w.create_line(x+75,y+5, x+100, y+25, fill="blue", width = 4)
				if j == self.m-1:
					border1 = self.w.create_line(x+75,y+75, x+100, y+55, fill="blue", width = 4)
					if i != self.m-1:
						border2 = self.w.create_line(x+100,y+55, x+125, y+75, fill="blue", width = 4)
		for i in range(self.n): # Zeichnen der roten Begrenzungs-Linien
			for j in range(self.m):
				offset = j*25
				x = i*50 + offset
				y = j*50
				if i == 0:
					border1 = self.w.create_line(x+50,y+25, x+50,y+55, fill="red", width = 4)
					border2 = self.w.create_line(x+75,y+75, x+50,y+55, fill="red", width = 4)
				if i == self.n-1:
					border1 = self.w.create_line(x+100,y+25, x+100,y+55, fill="red", width = 4)
					if j != self.m-1:
						border2 = self.w.create_line(x+100,y+55, x+125, y+75, fill="red", width = 4)
		currentPlayer = self.game.current # Festlegung der Anzeige des startwindows
		if currentPlayer == 1:
			color = "red"
		else:
			color = "blue"
		startwindow = messagebox.showinfo('', 'Player ' + str(currentPlayer) + " (" + color + ") starts!")
		self.game.startGame()
		self.updateGUI()
		self.root.mainloop() # Start des tkinter-Event-Loops

	def click(self, move_obj): # wird bei Mausklick ausgefuehrt
		if self.mode != "ki":
			click = move_obj.widget.find_closest(move_obj.x, move_obj.y)[0] # findet laufende Nummer des angeklickten Canvas-Objektes anhand der Klick-Koordinaten
			if click <= self.m * self.n:
				i = ((click-1) % self.m)
				j = (click - 1) // self.m
				self.receiveMove((i,j)) # führt receiveMove mit gegebenen move-Koordinaten aus

	def updateGUI(self):
		for i in range(self.m):
			for j in range(self.n):
				if self.game.board[i][j] == 1:
					self.w.itemconfig(self.polygons[(i,j)], fill = "red")
				elif self.game.board[i][j] == 2:
					self.w.itemconfig(self.polygons[(i,j)], fill = "blue")
		if (self.game.round == 1 and self.game.mode == "human") or (self.game.mode == "inter" and self.game.round == 1 and not self.game.switched):
			sleep(0.1)
			first = self.setFirst()
			if self.game.mode == "human" and first != self.game.currentPlayer():
				self.game.current = first
				self.game.switch()
				pass
			if self.game.mode == "inter" and first != self.game.currentPlayer():
				# self.game.current = first
				# if self.game.ki_player == 1:
				#     self.game.ki_player = 2
				#     self.game.human_player = 1
				# else:
				#     self.game.human_player = 2
				#     self.game.ki_player = 1
				# self.game.KI1, self.game.KI2 = self.game.KI2, self.game.KI1
				self.game.switch(0)
				self.updateGUI()
				#self.game.switch()
				
		if (self.game.round ==1 and self.game.mode == "inter" and self.game.ki_switched):
			sleep(0.1)
			self.game.ki_switched = False 
			self.updateGUI()
			startwindow = messagebox.showinfo('', "KI switched")
		
		if self.game.finished():
			self.VictoryPath()
			self.exit() # Beenden des Spiels wenn game zu Ende


	def receiveMove(self, move): # GUI-Logik bei Klick auf move-Koordinaten
		self.game.makeMove(move)
		self.updateGUI()

	def setFirst(self): # Popup zum switch
		switch = messagebox.askquestion("", "Wanna switch?")
		if switch == "no":
			return self.game.currentPlayer()
		elif switch == "yes":
			if self.game.currentPlayer() == 1:
				return 2
			else:
				return 1

	def exit(self): # beendet aktuelles Spiel
		winner = self.game.winner()
		if winner == 1:
			color = "red"
			if self.game.mode == "inter" or self.game.mode == "ki":
				if self.game.KI1:
					name = str(self.game.KI1)
				else:
					name = "human"
			else:
				name = "human"
		else:
			color = "blue"
			if self.game.mode == "inter" or self.game.mode == "ki":
				if self.game.KI2:
					name = str(self.game.KI2)
				else:
					name = "human"
			else:
				name = "human"
		finishbox = messagebox.askquestion("", "Player " + str(winner) + " (" + color + ", " + name +  ") won! Play again?") # Popup am Ende des Spiels
		if finishbox == "yes": # Neustart
			self.restart()
		elif finishbox == "no": # Beenden
			self.root.destroy()

	def VictoryPath(self):
		Path = self.game.hexboard.getVictoryPath()
		print("Path = ")
		print(Path)
		# set Color"
		if self.game.hexboard.win == 1:
			color = "PeachPuff"
		else:
			color = "LightBlue"

		for e in Path:
			# if e != "left" and e!= "right" and e != "top" and e != "bot":
			(x,y) = e
			e1 = (x-1,y-1)
			self.w.itemconfig(self.polygons[e1], fill = color)

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

	def __str()__(self):


mode = "ki"
m = 7
n = 7

a = Game(m, n, mode)
b = HexGui(m, n, a)

results = []
for i in range(20):
	a = Game(m, n, mode)
