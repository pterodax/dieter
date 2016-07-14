from random import randint
import tkinter
from tkinter import *
from sys import stdin


class UnionFind:
	def __init__(self, m,n):
		self.m = m
		self.n = n
		self.lastMove = [(-1,-1), -1]

		self.ZHK1 = {}
		self.ZHK2 = {}
		self.Rep1 = {}
		self.Rep2 = {}
		self.winner = None

		self.ZHK1["left"] = set()
		self.ZHK1["left"].add("left")
		self.ZHK1["right"] = set()
		self.ZHK1["right"].add("right")

		self.ZHK2["top"] = set()
		self.ZHK2["top"].add("top")
		self.ZHK2["bot"] = set()
		self.ZHK2["bot"].add("bot")

		self.Rep1["left"]="left"
		self.Rep1["right"] = "right"

		self.Rep2["top"] = "top"
		self.Rep2["bot"] = "bot"

		for i in range(m+2):
			self.Rep1[(i,0)] = "left"
			self.Rep1[(i,n+1)] = "right"


		for j in range(n+2):
			self.Rep2[(0,j)] = "top"
			self.Rep2[(m+1,j)] = "bot"

	def makeMove(self, x,y, player):
		if x < 1 or x>self.m or y < 1 or y> self.n:
			# print("index problem")
			return

		if player == 1:
			ZHK = self.ZHK1
			Rep = self.Rep1
			start = "left"
			goal = "right"
		else:
			ZHK = self.ZHK2
			Rep = self.Rep2
			start = "top"
			goal = "bot"

		move = (x,y)
		ZHK[move] = set()
		ZHK[move].add(move)
		Rep[move] = move
		nachbarn = [(x-1,y),(x-1,y+1),(x,y+1),(x+1,y),(x+1,y-1),(x,y-1)]
		for e in nachbarn: #fuer alle nachbarn einmal ausfuehren
			if e in Rep:
				ZHK[Rep[move]] = ZHK[Rep[move]] | ZHK[Rep[e]]
				for p in ZHK[Rep[move]]: #reihenfolge aendern? nach allen nachbarn machen
					Rep[p] = Rep[move]

		for e in Rep:
			if Rep[e] != e and e in ZHK and e != start and e!= goal:
				del ZHK[e]
		if start in ZHK[Rep[move]] and goal in ZHK[Rep[move]]:
			self.winner = player

		self.lastMove = [move,player]
		#print(self)

	def __str__(self):
		if self.lastMove[1]==1:
			ZHK = self.ZHK1
			Rep = self.Rep1
			player = 1
		else:
			ZHK = self.ZHK2
			Rep = self.Rep2
			player = 2
		return("\n \n \n Move = " + str(self.lastMove[0]) + " by player " + str(player) + "\n ZHK1 = " + str(ZHK) + "\n\n Rep1 = " + str(Rep)) # "\n \n \n\n ZHK2 = " + str(self.ZHK2) + "\n\n Rep2 = " + str(self.Rep2))

	def getWinner(self):
		return self.winner
	
	def getVP(self):
		if self.winner == 1:
			ZHK = self.ZHK1
		if self.winner ==2:
			ZHK = self.ZHK2
		return ZHK[self.lastMove[0]]

		# FOR HEX_MAIN GUI KLASSE:
		
	# def VictoryPath(self):
		# ZHK = self.game.hexboard.unionfind.getVP()
		# print("ZHK = ")
		# print(ZHK)
		"set Color"
		# if self.game.hexboard.win == 1:
			# color = "PeachPuff"
		# else:
			# color = "LightBlue"
			
		# for e in ZHK:

			# if e != "left" and e!= "right" and e != "top" and e != "bot":
				# (x,y) = e
				# e1 = (x-1,y-1)
				# self.w.itemconfig(self.polygons[e1], fill = color)