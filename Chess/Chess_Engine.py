"""class is responsible for all the info about chess game"""
from msilib import knownbits
from shutil import move
from tabnanny import check
from xml.etree.ElementInclude import include


class GameState():
    def __init__(self) :
        self.board=[
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bp","bp","bp","bp","bp","bp","bp","bp"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"], 
            ["--","--","--","--","--","--","--","--"],
            ["wp","wp","wp","wp","wp","wp","wp","wp"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"]
        ]
        self.moveFunction={'p':self.getPawnMoves,'R':self.getRookMoves,'N':self.getKnightMoves,'B':self.getBishopMoves,'Q':self.getQueenMoves,'K':self.getKingMoves}
        self.moveLog = [] 
        self.whiteToMove = True
        self.whiteKingLocation = (7 , 4)
        self.blackKingLocation = (0 , 4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.checkmate= False
        self.stalemate = False
        self.enpassantPossible = () #coordinates for the square where en passant capture is possible
        self.whiteCastleKingside = True
        self.whiteCastleQueenside = True
        self.blackCastleKingside = True
        self.blackCastleQueenside = True
        self.castleRightsLog = [CastleRights(self.whiteCastleKingside,self.blackCastleKingside,self.whiteCastleQueenside,self.blackCastleQueenside)]

    def makeMove(self,move):
        self.board[move.startrow][move.startcol] = "--" 
        self.board[move.endrow][move.endcol] = move.pieceMoved
        self.moveLog.append(move) # log the move so we can undo it later 
        self.whiteToMove = not self.whiteToMove # swap players
        # update king's position
        if move.pieceMoved == "wK" :
            self.whiteKingLocation = (move.endrow,move.endcol)
        elif move.pieceMoved =="bK":
            self.blackKingLocation =(move.endrow,move.endcol)
        # pawn promotion
        if move.isPawnPromotion :
            promotedPiece = input("-->Promote to Q , R , B or N : ")#we can make this part of the ui later
            self.board[move.endrow][move.endcol] = move.pieceMoved[0] + promotedPiece
        
        #if pawn move twice next move ca  capture enpassant
        if move.pieceMoved[1] == 'p' and abs(move.startrow -move.endrow) == 2: #only on 2 squares advances
            self.enpassantPossible = ((move.endrow + move.startrow)//2,move.endcol)
        else:
            self.enpassantPossible = ()
        # if en passant move ,must update the board to capture the pawn 
        if move.isEnpassantMove:
            self.board[move.startrow][move.endcol]='--'#capturing the pawn
        # update castling rights
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.whiteCastleKingside,self.blackCastleKingside,self.whiteCastleQueenside,self.blackCastleQueenside))
        #castle moves
        if move.castle:
            if move.endcol - move.startcol ==2 :#king's side
                self.board[move.endrow][move.endcol-1]= self.board[move.endrow][move.endcol+1]#moverook
                self.board[move.endrow][move.endcol+1]='--' #enmpty space where rook was
            else : #queen side 
                self.board[move.endrow][move.endcol+1]= self.board[move.endrow][move.endcol-2]#moverook
                self.board[move.endrow][move.endcol-2]='--' #enmpty space where rook was   
    def undoMove(self) :
        if len (self.moveLog)!=0:
            move = self.moveLog.pop()
            self.board[move.startrow][move.startcol] = move.pieceMoved #put piece on the starting square
            self.board[move.endrow][move.endcol] = move.pieceCaptured #put back the captured piece
            self.whiteToMove = not self.whiteToMove # switch turn
            #update king's position
            if move.pieceMoved == "wK" :
                self.whiteKingLocation = (move.startrow,move.startcol)
            elif move.pieceMoved =="bK":
                self.blackKingLocation = (move.startrow,move.startcol)
            #undo the enpassant move
            if move.isEnpassantMove:
                self.board[move.endrow][move.endcol]='--'#removes the pawn teht was added in the wrong square
                self.board[move.startrow][move.endcol] = move.pieceCaptured # puts the pawn back on the correct square it was captured from
                self.enpassantPossible = (move.endrow,move.endcol)#allow an en passant to happin on the next move
            # undo a 2 square pawn advance should make enpassanpossiblet empty again
            if move.pieceMoved[1]=='p'and abs(move.startrow - move.endrow) ==2:
                self.enpassantPossible = ()  
            #give back castle rights if move took them away
            self.castleRightsLog.pop()  # remove last move update  
            CastleRights = self.castleRightsLog[-1]
            self.enpassantPossible = () #coordinates for the square where en passant capture is possible
            self.whiteCastleKingside = CastleRights.wks
            self.whiteCastleQueenside = CastleRights.wqs
            self.blackCastleKingside = CastleRights.bks
            self.blackCastleQueenside = CastleRights.bqs
            # undo castle moves
        if move.castle:
            if move.endcol - move.startcol ==2 :#king's side
                self.board[move.endrow][move.endcol+1]= self.board[move.endrow][move.endcol-1]#moverook
                self.board[move.endrow][move.endcol-1]='--' #enmpty space where rook was
            else : #queen side 
                self.board[move.endrow][move.endcol-2]= self.board[move.endrow][move.endcol+1]#moverook
                self.board[move.endrow][move.endcol+1]='--' #enmpty space where rook was   
    #valid the moves
    def getValidMoves(self):
        #generate all the possible moves
        moves = []
        self.inCheck,self.pins,self.checks=self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingrow = self.whiteKingLocation[0]
            kingcol = self.whiteKingLocation[1]
        else:
            kingrow = self.blackKingLocation[0]
            kingcol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1: # only one check , block or move king 
                moves = self.getAllPossibleMoves()
                # to block a check u mast move a piece into one of the squares betwwen the enemy piece and king
                check = self.checks[0] # check information
                checkrow = check[0]
                checkcol = check[1]
                picechecking = self.board[checkrow][checkcol]#enemy piece causing the cheks
                validsquares = [] # squares that pieces can move to 
                # if knight , must capture or move the king , other pices can be blocked
                if picechecking [1]=='N':
                    validsquares = [(checkrow,checkcol)]
                else:
                   for i in range(1,8):
                        validsquare = (kingrow + check[2]*i , kingcol + check[3] *i) 
                        validsquares.append(validsquare)
                        if validsquare[0]==checkrow and validsquare[1] == checkcol: # once u get to piece end checks
                            break
                #get rid of any moves that don't block check or move king 
                for i in range(len(moves)-1,-1,-1): # go through backwards you are removing from a list as iterating 
                    if moves[i].pieceMoved[1] !='K' : #move does'nt move king so it must block or capture   
                        if not (moves[i].endrow,moves[i].endcol) in validsquares: # move doesn't block check or capture piece
                            moves.remove(moves[i])
            else:  #double check , king has to move 
                self.getKingMoves(kingrow,kingcol,moves)
        else:#not in check so all moves allowed   
            moves = self.getAllPossibleMoves()    

        return moves

    def getAllPossibleMoves(self):
        moves = [] 
        for r in range(len(self.board)):
            for c in range (len(self.board)):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b'and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunction[piece](r,c,moves)
        return moves

                            

                    
    def getPawnMoves(self,r,c,moves ):
        piecepinned = False
        pindirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c :
                piecepinned=True
                pindirection = self.pins[i][2],self.pins[i][3]
                self.pins.remove(self.pins[i])
                break
        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            backRow = 0
            enemyColor  = 'b'
        else:
            moveAmount = 1
            startRow = 1
            backRow = 7
            enemyColor = 'w'
        isPawnPromotion = False
        if self.board[r+moveAmount][c] == "--": # 1 square pawn advence
                if not piecepinned or pindirection == (moveAmount,0):
                    if r+moveAmount == backRow: #if piece gets to bank rank then it is a pawn promotion
                        isPawnPromotion = True
                    moves.append(Move((r,c),(r+moveAmount,c),self.board, isPawnPromotion=isPawnPromotion))
                    if r==startRow and self.board[r+2*moveAmount][c] == "--":# 2 squares moves
                        moves.append(Move((r,c),(r+2*moveAmount,c),self.board))
        if c-1>=0: #capture to left
                    if not piecepinned or pindirection == (moveAmount,-1):
                        if self.board[r+moveAmount][c-1][0]== enemyColor:
                            if r + moveAmount == backRow :#if piece gets to bank rank then it is apawn promotion
                                isPawnPromotion = True
                            moves.append(Move((r,c),(r+moveAmount,c-1),self.board,isPawnPromotion=isPawnPromotion))
                        
                        if (r + moveAmount , c-1) == self.enpassantPossible:
                            moves.append(Move((r,c),(r + moveAmount,c-1),self.board,isEnpassantMove=True)) 
        if c+1<=7: # capture to right
                    if not piecepinned or pindirection == (moveAmount,1):
                        if self.board[r+moveAmount][c+1][0]== enemyColor:
                            if r+moveAmount == backRow:#if piece gets to bank then it is a pawn promotion
                                isPawnPromotion = True
                            moves.append(Move((r,c),(r+moveAmount,c+1),self.board,isPawnPromotion=isPawnPromotion)) 
                        if (r + moveAmount , c+1) == self.enpassantPossible:
                            moves.append(Move((r,c),(r+ moveAmount,c+1),self.board,isEnpassantMove=True)) 


    def getRookMoves(self,r,c,moves):
         piecepinned = False
         pindirection = ()
         for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c :
                piecepinned=True
                pindirection = self.pins[i][2],self.pins[i][3]
                if self.board[r][c][1]!='Q': # can't remove queen from pin on rook moves , only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break
         directions = ((-1,0),(0,-1),(1,0),(0,1)) 
         enemyColor = "b" if self.whiteToMove else "w"
         for d in  directions :
             for i in range(1,8):
                 endrow = r + d[0]*i
                 endcol = c + d[1]*i
                 if 0<=endrow <8 and 0<=endcol <8 : 
                     if not piecepinned or pindirection == d or pindirection == (-d[0],-d[1]):
                        endpiece = self.board[endrow][endcol]
                        if endpiece =="--":
                            moves.append(Move((r,c),(endrow,endcol),self.board))
                        elif endpiece[0] == enemyColor:
                            moves.append(Move((r,c),(endrow,endcol),self.board))
                            break
                        else:
                            break
                 else:
                     break
                     
    def getKnightMoves(self,r,c,moves):
        piecepinned = False 
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c :
                piecepinned=True
                self.pins.remove(self.pins[i])
                break
        knightMoves = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))  
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endrow = r + m[0]
            endcol = c + m[1]
            if 0<= endrow <8 and 0<= endcol<8:
                if not piecepinned:
                    endpiece = self.board[endrow][endcol]
                    if endpiece [0] != allyColor:
                        moves.append (Move((r,c),(endrow,endcol),self.board))
    def getBishopMoves(self,r,c,moves):
        piecepinned = False
        pindirection = ()
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c :
                piecepinned=True
                pindirection = self.pins[i][2],self.pins[i][3]
                self.pins.remove(self.pins[i])
                break
        directions = ((-1,-1),(-1,1),(1,-1),(1,1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in  directions :
             for i in range(1,8):
                 endrow = r+ d[0] * i
                 endcol = c + d[1] * i
                 if 0<=endrow <8 and 0<=endcol <8 : 
                     if not piecepinned or pindirection == d or pindirection == (-d[0],-d[1]):
                        endpiece = self.board[endrow][endcol]
                        if endpiece =="--":
                            moves.append(Move((r,c),(endrow,endcol),self.board))
                        elif endpiece[0] == enemyColor:
                            moves.append(Move((r,c),(endrow,endcol),self.board))
                            break
                        else:
                            break
                 else:
                     break  
    def getQueenMoves(self,r,c,moves):
        self.getRookMoves(r,c,moves)
        self.getBishopMoves(r,c,moves)
    def getKingMoves(self,r,c,moves):
        rowmoves = (-1,-1,-1,0,0,1,1,1)
        colmoves = (-1,0,1,-1,1,-1,0,1)
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8): 
            endrow = r + rowmoves[i]
            endcol = c + colmoves[i]
            if 0 <= endrow <8 and 0 <= endcol < 8 :
                endpiece = self.board[endrow][endcol]
                if endpiece[0] !=allyColor:
                    #place king on end square and check for checks
                    if allyColor == 'w' :
                        self.whiteKingLocation =(endrow,endcol)
                    else:
                        self.blackKingLocation = (endrow,endcol)
                    inCheck,pins,checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r,c),(endrow,endcol),self.board))
                    # place king back on original location 
                    if allyColor == 'w':
                        self.whiteKingLocation = (r,c)
                    else:
                        self.blackKingLocation = (r,c)
        self.getCastleMoves(r,c,moves,allyColor)
    def getCastleMoves(self,r,c,moves,allyColor):
        inCheck = self.squaresUnderAttack(r,c,allyColor)
        if inCheck:
            print("off")
            return #can't castle in check
        if (self.whiteToMove and  self.whiteCastleKingside) or (not self.whiteToMove and  self.blackCastleKingside) : # can't castle if given ut rights 
            self.getKingsideCastleMoves(r,c,moves,allyColor)   
        if  (self.whiteToMove and self.whiteCastleQueenside) or ( not self.whiteToMove and self.blackCastleQueenside) :
            self.getQueensideCastleMoves(r,c,moves,allyColor)
    ''' generate kingside castle moves for the king at (r,c) this method will 
    only be called if player still has castle rights king side '''
    def getKingsideCastleMoves(self,r,c,moves,allyColor):
        #check if two squares between king and rook are clear and not under attack
        if self.board[r][c+1] == '--'and self.board[r][c+2] == '--'and \
            not self.squaresUnderAttack(r,c+1,allyColor) and not self.squaresUnderAttack(r,c+2,allyColor):
            moves.append(Move((r,c),(r,c+2),self.board ,castle = True))
        ''' generate kingside castle moves for the king at (r,c) this method will 
    only be called if player still has castle rights queen side '''
    def getQueensideCastleMoves(self,r,c,moves,allyColor):
        #check if two squares between king and rook are clear and not under attack
        if self.board[r][c-1] == '--'and self.board[r][c-2] == '--'and self.board[r][c-3]=='--' and\
            not self.squaresUnderAttack(r,c-1,allyColor) and not self.squaresUnderAttack(r,c-2,allyColor):
            moves.append(Move((r,c),(r,c-2),self.board ,castle = True))
    def squaresUnderAttack(self,r,c,allyColor):
        #check outward from square
        enemyColor = 'w' if allyColor =='b'else 'b'
        directions = ((-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1))
        for j in range (len(directions)):
            s = directions[j]
                #check outward from king pins and checks ,keep track of pins
        directions = ((-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1))
        for j in range (8):
            d = directions[j]
            possiblePin = () #reset possible pins
            for i in range (1,8):
                endrow = r + d[0]*i
                endcol = c + d[1]*i 
                if 0<=endrow < 8 and 0<= endcol < 8:
                    endpiece = self.board[endrow][endcol]
                    if endpiece[0] == allyColor and endpiece[1] !='K':
                        if possiblePin == () : #1st allied piece could be pinned
                            possiblePin = (endrow,endcol,d[0],d[1])
                        else : #2nd allied piece so no possible pin in this direction
                            break
                    elif endpiece[0] == enemyColor:
                        type = endpiece[1]
                        # we have 5 possibelities
                        # 1--> orthogonally away from king and pice is rook
                        # 2--> diagnally away from the king and the pice is a bishop
                        # 3--> 1 square away diagnally and the pice is a pawn
                        # 4--> any  direction and the pice is a queen
                        # 5--> any 1 square direction and the piece is king this is necessary to prevent the king to move to a square controlled b anothor king
                        if (0 <= j <= 3 and type == 'R') or \
                            (4 <= j <= 7 and type == 'B') or \
                            (i == 1 and type == 'p' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                            (type == 'Q') or \
                            (i == 1 and type == 'K'):
                            return True
                        else: #Enemy piece that is not applying check
                            break
                else : #off the board
                    break
        #check for knight checks
        knightMoves =  ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)) 
        for m in knightMoves :
            endrow = r + m[0]
            endcol = c + m[1]               
            if 0 <= endrow < 8 and 0<= endcol <8:
                endpiece = self.board[endrow][endcol]
                if endpiece[0] == enemyColor and endpiece[1] =='N': #enemy knight attacking king 
                    return True
        return False
    def checkForPinsAndChecks(self):
        pins = [] #squares where the allied pinned piece is and direction pinned from
        checks = []
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startrow=self.whiteKingLocation[0]
            startcol=self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startrow = self.blackKingLocation[0]
            startcol = self.blackKingLocation[1]
        #check outward from king pins and checks ,keep track of pins
        directions = ((-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1))
        for j in range (8):
            d = directions[j]
            possiblePin = () #reset possible pins
            for i in range (1,8):
                endrow = startrow + d[0]*i
                endcol = startcol + d[1]*i 
                if 0<=endrow < 8 and 0<= endcol < 8:
                    endpiece = self.board[endrow][endcol]
                    if endpiece[0] == allyColor and endpiece[1] !='K':
                        if possiblePin == () : #1st allied piece could be pinned
                            possiblePin = (endrow,endcol,d[0],d[1])
                        else : #2nd allied piece so no possible pin in this direction
                            break
                    elif endpiece[0] == enemyColor:
                        type = endpiece[1]
                        # we have 5 possibelities
                        # 1--> orthogonally away from king and pice is rook
                        # 2--> diagnally away from the king and the pice is a bishop
                        # 3--> 1 square away diagnally and the pice is a pawn
                        # 4--> any  direction and the pice is a queen
                        # 5--> any 1 square direction and the piece is king this is necessary to prevent the king to move to a square controlled b anothor king
                        if (0 <= j <= 3 and type == 'R') or \
                            (4 <= j <= 7 and type == 'B') or \
                            (i == 1 and type == 'p' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                            (type == 'Q') or \
                            (i == 1 and type == 'K'):
                            if possiblePin == () : # No friendly piece is blocking -> is check
                                inCheck = True                               
                                checks.append((endrow , endcol , d[0],d[1]))
                                break
                            else :# Friendly piece is blocking -> we found a pinned piece
                                pins.append(possiblePin)
                                break
                        else: #Enemy piece that is not applying check or pin
                            break
                else : #off the board
                    break
        #check for knight checks
        knightMoves =  ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)) 
        for m in knightMoves :
            endrow = startrow + m[0]
            endcol = startcol + m[1]               
            if 0 <= endrow < 8 and 0<= endcol <8:
                endpiece = self.board[endrow][endcol]
                if endpiece[0] == enemyColor and endpiece[1] =='N': #enemy knight attacking king 
                    inCheck = True
                    checks.append((endrow , endcol , m[0],m[1]))
        return inCheck,pins,checks
    def updateCastleRights(self,move):
        if move.pieceMoved == 'wK':
            self.whitheCastleQueenside = False
            self.whiteCastleKingside = False
        elif move.pieceMoved == 'bK':
            self.blackCastleKingside = False
            self.blackCastleQueenside = False
        elif move.pieceMoved == 'wR':
            if move.startrow == 7:
                if move.startcol == 7:
                    self.whiteCastleKingside = False
                elif move.startcol == 0:
                    self.whiteCastleQueenside = False
        elif move.pieceMoved == 'bR':
            if move.startrow == 0:
                if move.startcol == 7:
                    self.whiteCastleKingside = False
                elif move.startcol == 0:
                    self.whiteCastleQueenside = False

class CastleRights():
    def __init__(self,wks,bks,wqs,bqs) :
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs
        
class Move() :
    # maps keys to values
    ranksToRows = {"1":7,"2":6,"3":5,"4":4,"5":3,"6":2,"7":1,"8":0}
    rowsToRanks = {v:k for k,v in ranksToRows.items()}
    filesToCols = {"a":0,"b":1,"c":2,"d":3,"e":4,"f":5,"g":6,"h":7}
    colsToFiles = {v:k for k,v in filesToCols.items()}
    def __init__(self,startsq,endsq,board,isEnpassantMove = False,isPawnPromotion=False,castle=False) :
        self.startrow = startsq[0]
        self.startcol = startsq[1]
        self.endrow = endsq[0]
        self.endcol = endsq[1]
        self.pieceMoved = board[self.startrow][self.startcol]
        self.pieceCaptured = board[self.endrow][self.endcol] 
        # pawn promotion
        self.isPawnPromotion = isPawnPromotion
        #enpassant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'bp'if self.pieceMoved == 'wp' else 'wp'
        self.castle = castle
        self.moveID = self.startrow*1000 + self.startcol*100+self.endrow*10+self.endcol
    #overriding the equals method
    def __eq__(self, other) :
        if isinstance(other ,Move):
            return self.moveID == other.moveID
        return False
    def getChessNotation(self):
        #Real chess notation -->
        return self.getRankFile(self.startrow,self.startcol) + self.getRankFile(self.endrow,self.endcol)
    def getRankFile(self,r,c):
        return self.colsToFiles[c]+self.rowsToRanks[r]
