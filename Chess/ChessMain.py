"""this is out maine driver file it will handle all user input and display the current game state object """
from turtle import color
from matplotlib import colors
from numpy import True_, square, squeeze
from Chess_Engine import GameState
from Chess_Engine import Move
import pygame as p
p.init()
WIDTH = HEIGHT = 800
DIMENTION = 8 #dimention of cehss board
SQ_size = HEIGHT // DIMENTION
MAX_FPS = 15
IMAGES = {} 

# Initilize a globale dict of images .this will call exactly once in main
def loadImages() :
    pieces = ["wR","wN","wB","wQ","wK","wB","wN","wR","wp","bR","bN","bB","bQ","bK","bB","bN","bR","bp"]
    for piece in pieces:
        IMAGES [piece]= p.transform.scale(p.image.load ("images/"+piece+".png"),(SQ_size,SQ_size))

def main() :
    p.init()
    screen = p.display.set_mode((WIDTH,HEIGHT)) 
    p.display.set_caption('Python Chess Game')
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = GameState()
    validMoves = gs.getValidMoves()
    moveMade = False #flag variable for when a move is made
    loadImages()
    sqSelected = () #keep track of the click of user
    playerClicks = [] # keep track of the player clicks (two tuples old pos and new pos )
    running=True
    animate = False#flag variable fo when we should animate
    gameOver = False
    while running :
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #mouse handler
            if e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()
                    col = location[0]//SQ_size
                    row = location[1]//SQ_size
                    if sqSelected == (row,col) :# if the user click the same sq twice
                        sqSelected = () #deselect
                        playerClicks = [] #clear player clicks
                    else :
                        sqSelected=(row,col)
                        playerClicks.append(sqSelected) # append the two clicks
                    if len(playerClicks) == 2:
                        move = Move(playerClicks[0],playerClicks[1],gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []     
                        if not moveMade:
                            playerClicks = [sqSelected]
            #key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
                    animate = False
                if e.key == p.K_r: #reset the board when ' r' is pressed
                    gs = GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1],screen,gs.board,clock)
            validMoves=gs.getValidMoves()
            moveMade = False
            animate = False
        drawGameState(screen ,gs,validMoves,sqSelected)
        if gs.checkmate :
            gameOver = True
            if gs.whiteToMove : 
                drawText(screen,'Black wins by checkmate')
            else :
                drawText(screen, 'white wins by checkmate')
        elif gs.stalemate :
            gameOver = True
            drawText(screen,'stalemate')

        clock.tick(MAX_FPS)
        p.display.flip()
''' highlight square selected and moves for piece selcted '''
def highlightSquares(screen , gs , validMoves,sqSelected) :
    if sqSelected!=():
        r,c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove  else 'b')  : # square selcted is a piece that can be moved
            #gihlight selected square
            s= p.Surface ((SQ_size,SQ_size))   
            s.set_alpha(100) 
            s.fill(p.Color("#2959df"))
            screen.blit(s,(c*SQ_size,r*SQ_size))
            #hightlight moves from that square
            s.fill(p.Color('#baca44'))
            for move in validMoves:
                if move.startrow == r and  move.startcol == c :
                    screen.blit(s,(move.endcol*SQ_size,move.endrow*SQ_size))
""" all graphics within a current game state"""
def drawGameState(screen ,gs,validMoves,sqSelected) :
    
    drawBoard(screen,)
    highlightSquares(screen , gs , validMoves,sqSelected)
    drawPieces(screen,gs.board)

def drawBoard(screen):
    global colors
    colors =[p.Color("#eeeed2"),p.Color("#769656")]
    for r in range (DIMENTION):
        for c in range (DIMENTION):
            color = colors[((r+c)%2)]
            p.draw.rect (screen,color , p.Rect(c*SQ_size,r*SQ_size,SQ_size,SQ_size))
def drawPieces(screen,board):
    for r in range (DIMENTION):
        for c in range (DIMENTION):
            piece = board[r][c]
            if piece !="--":
                screen.blit(IMAGES[piece],p.Rect(c*SQ_size,r*SQ_size,SQ_size,SQ_size))
def animateMove(move , screen ,board ,clock):
    global colors
    coords = [] #list of coords that the animation will move through
    dR = move.endrow - move.startrow
    dC = move.endcol - move.startcol
    framesPerSquare = 8 # frame of one square
    framesCount = (abs(dR) + abs(dC))*framesPerSquare
    for frame in range(framesCount + 1):
        r,c = (move.startrow + dR * frame/framesCount,move.startcol+dC*frame/framesCount)
        drawBoard(screen)
        drawPieces(screen,board)
        #erase the piece moves from its ending square
        color = colors[(move.endrow+move.endcol)%2]
        endSquere = p.Rect(move.endcol*SQ_size,move.endrow*SQ_size,SQ_size,SQ_size)
        p.draw.rect(screen,color,endSquere)
        #draw captured piece into rectangle
        if move.pieceCaptured !='--':
            screen.blit(IMAGES[move.pieceMoved]),p.Rect(c*SQ_size,r*SQ_size,SQ_size,SQ_size)
        # draw moving piece
        screen.blit(IMAGES[move.pieceMoved],p.Rect(c*SQ_size,r*SQ_size,SQ_size,SQ_size))
        p.display.flip()
        clock.tick(60)
def drawText(screen,text):
        font =  p.font.SysFont("helvitica",32,True,False)
        textObject = font.render(text,0,p.Color("black"))
        textLocation = p.Rect(0,0,WIDTH,HEIGHT).move(WIDTH/2 - textObject.get_width()/2,HEIGHT/2 - textObject.get_height()/2)
        screen.blit(textObject,textLocation(2,2))
if __name__ == "__main__":
    main()