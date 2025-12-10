#GUI and main game for UNO
import random
import tkinter as tk #for GUI
from tkinter import messagebox
from tkinter import font as tkfont
from tkinter import simpledialog
from AI_uno import AI_bot

# card settings 
color = ['red', 'yellow', 'green', 'blue']
number = ['0', '1', '1', '2', '2', '3', '3', '4', '4', '5', '5',
          '6', '6', '7', '7', '8', '8', '9', '9'] #num is doubled expect 0
card_types = ['number', 'action', 'wild']

#game settings
action = ['skip', 'reverse', 'draw two']
wild = ['wild', 'wild draw four']


#game window
window = tk.Tk()
window.geometry("800x600")
window.title("UNO Game")


#global variables
game_manager = None
current_player = None
current_card = None

#-----------------------SINGLE CARD-----------------------#
class Card:
    def __init__(self, color, text):
        self.color = color
        self.text = text
        self.is_played = False #boolean to check if card is played

        self.card_font= tkfont.Font(size = 10, weight = "bold")
        self.widget = tk.Label(window,
                font=self.card_font,
                text=self.text,
                bg=self.color
                )
        
        #bind drag, animation and release events
        self.widget.bind("<Button-1>", self.drag_start) 
        self.widget.bind("<B1-Motion>", self.drag_motion)
        self.widget.bind("<ButtonRelease-1>", self.check_drop)

    def place(self, **kwargs):
        self.widget.place(**kwargs)

    #
    def drag_start(self, event):
        if self.is_played:
            return
        self.widget.startX = event.x
        self.widget.startY = event.y

    def drag_motion(self, event):
        new_widget = event.widget
        new_widget.tkraise()
        x = new_widget.winfo_x() + (event.x - new_widget.startX)
        y = new_widget.winfo_y() + (event.y - new_widget.startY)
        new_widget.place(x=x, y=y)
                
    #for checking if card is dropped inside discard pile
    def check_drop(self, event):
        global game_manager, current_card

        if not game_manager or game_manager.current_player != 'human':
            return

        #card is dropped inside discard pile and is valid
        if self.check_inside(self.widget) and game_manager.is_card_valid(self):
            self.is_played = True

            #remove card from hand
            game_manager.human.hand.remove(self)

            #add to discard pile
            game_manager.discard_pile.add_card(self)

            # Update AI's game state tracking
            game_manager.AI.discard_history.append(self)
            game_manager.AI.opponent_hand_size = len(game_manager.human.hand)
            game_manager.AI.deck_size = len(game_manager.deck)

            # Hide draw button
            game_manager.human.turn = False
            game_manager.human.card_button.place_forget()

            # Check if human won (BEFORE scheduling next turn)
            if len(game_manager.human.hand) == 0:
                messagebox.showinfo("Game Over", "You Win!")
                window.quit()
                return

            #update card and handle special cards
            game_manager.end_turn(self)

        #return to hands(organize the card on ur own)
        else:
            self.is_played = False
            self.widget.place(x=random.randint(50, 650), y=450, width = 100, height = 120)
            self.widget.bind("<Button-1>", self.drag_start) 
            self.widget.bind("<B1-Motion>", self.drag_motion)
                

    #check inside discard pile    
    def check_inside(self, label):
        x = label.winfo_x()
        y = label.winfo_y()
        w = label.winfo_width()
        h = label.winfo_height()

        left = x
        right = x + w
        top = y
        bottom = y + h

        return (
            left >= 200 and
            right <= 600 and
            top >= 180 and
            bottom <= 330
        )

#-----------------------PLAYER-----------------------#
class Player:
    def __init__(self, name, deck, hand):
        self.name = name
        self.deck = deck
        self.hand = hand
        self.turn = False #is it player's turn

        #draw card GUI, only appears on player's turn
        self.card_button = tk.Button(window, text="Draw Card")
        self.card_button.bind("<Button-1>", self.draw_card)
        
        #say UNO GUI
        self.uno_button = tk.Button(window, text="Say UNO")
        self.uno_button.place(x=700, y=250)
        self.uno_button.bind("<Button-1>", self.say_UNO)

    #detect if it's player's turn then allow drawing card
    def start_turn(self):
        self.turn = True
        self.card_button.place(x=700, y=200)

    #function name is obvious enough lol
    def draw_card(self, event=None, silent=False):
        global game_manager

        # If silent=True, just draw the card without triggering turn logic (used by special cards)
        if silent:
            if self.deck:
                drawn_card = self.deck.pop()
                self.hand.append(drawn_card)
                drawn_card.place(x=random.randint(50, 650), y=450, width = 100, height = 120)
            return

        #must be our turn
        if(not self.turn):
            print("AI's turn -- draw card") #this line is for debugging only
            return

        #deck is empty
        # if not self.deck:
        #     print("Deck is empty, cannot draw a card.")
        #     return

        drawn_card = self.deck.pop()
        self.hand.append(drawn_card)
        drawn_card.place(x=random.randint(50, 650), y=450, width = 100, height = 120)
        game_manager.switch_player()
        game_manager.turns()
                                                                 
    def say_UNO(self, event=None):
        """
        Call UNO when you have 1 card left.

        Rules:
        - Press when you have 1 card to declare UNO (prevents penalty)
        - If you have 1 card and DON'T call UNO, you should draw 2 cards as penalty
        - You win when you play your last card (0 cards left)
        """
        #QTE?
        
        if len(self.hand) == 1:
            print(f"{self.name} says UNO! (1 card remaining)")
            messagebox.showinfo("UNO!", f"{self.name} has 1 card left!")
        else:
            print(f"{self.name} doesn't have 1 card (has {len(self.hand)} cards)")
            messagebox.showwarning("Invalid UNO", f"You can only call UNO when you have 1 card!\nYou have {len(self.hand)} cards.")
            
   

#discard pile in the center, that gray box
#-----------------------DISCARD PILE-----------------------#
class Discard_Pile:
    discard_pile = tk.Frame(window, width=200, height=150, bg='grey')
    discard_pile.place(x=300, y=180)
    def __init__(self):
        self.cards = []
    
    def add_card(self, card):
        self.cards.append(card)
        card.place(x=350, y=200, width = 100, height = 120) # i figured out it'll be simpler getting another class
        #disable touch
        card.widget.unbind("<Button-1>")
        card.widget.unbind("<B1-Motion>")
        card.widget.unbind("<ButtonRelease-1>")
        card.widget.tkraise()
    
#-----------------------GAME MANAGER-----------------------#
class GameManager:
    def __init__(self, human, AI, deck):
        self.human = human
        self.AI = AI
        self.deck = deck
        self.current_player = 'AI' #what
        self.discard_pile = Discard_Pile()
    
    #initializer starter
    def start(self):
        window.after(1000, self.turns) #start the turns after 1 second


    #base mechanism of changing turns
    def turns(self):
        global current_card

        print(f"--{self.current_player}'s turn") #for debugging only
        print("Current card:", current_card.color, current_card.text)

        if self.current_player == 'human':
            self.human.start_turn()
            # window.after(10000) #wait for 10 seconds
            # self.switch_player()
            return
        else:
            self.AI.is_AI_turn = True
            self.choosen_card = self.AI.choose_card(self.AI.hand, current_card)
            #if there's no valid card for ai, draw card and skip turn
            if self.choosen_card is None:
                print("AI drawing card...")
                if self.deck:
                    drawn_card = self.deck.pop()
                    self.AI.hand.append(drawn_card)
                self.AI.is_AI_turn = False
                self.switch_player()
                window.after(2000, self.turns)
                return

            # Play the card
            self.AI.play_card(self.choosen_card)
            self.AI.hand.remove(self.choosen_card)

            # Update AI's game state tracking
            self.AI.opponent_hand_size = len(self.human.hand)
            self.AI.deck_size = len(self.deck)
            self.AI.discard_history.append(self.choosen_card)

            # Add to discard pile
            self.discard_pile.add_card(self.choosen_card)

            self.AI.is_AI_turn = False

            # Check if AI won
            if len(self.AI.hand) == 0:
                messagebox.showinfo("Game Over", "AI Wins!")
                window.quit()
                return

            # Handle special cards via end_turn
            self.end_turn(self.choosen_card)
        
    #check played card and do stuff  
    def end_turn(self, played_card):
        global current_card
        current_card = played_card

        text = played_card.text
        if text in number:
            self.switch_player()
            window.after(300, self.turns)
            return

        if text == 'skip':
            self.skip()
        elif text == 'reverse':
            self.reverse()
        elif text == 'draw two':
            self.draw_two()
        elif text == 'wild':
            self.wild()
        elif text == 'wild draw four':
            self.wild_draw_four()


    #switch players
    def switch_player(self):
        self.current_player = 'AI' if self.current_player == 'human' else 'human'

    #is the played card valid
    def is_card_valid(self, card):
        global current_card

        if not current_card:
            return True
        #same color or same text
        if(card.color == current_card.color or card.text == current_card.text):
            return True
        elif(card.text in wild):
            return True
        else:
            print("invalid card") #for debugging only
            return False

    #reverse, equal to skip in 2 players (acts like skip in 2-player game)
    def reverse(self):
        print("reverse-- " + self.current_player) #for debugging only
        # In a 2-player game, reverse = skip (next player loses turn)
        self.switch_player()
        self.switch_player()
        window.after(300, self.turns)
    
    def skip(self):
        print("skip-- " + self.current_player) #for debugging only
        self.switch_player()
        self.switch_player()
        window.after(300, self.turns)
        
    def draw_two(self):
        print("draw two-- " + self.current_player) #for debugging only
        # current_player is the one who PLAYED the card, so the OTHER player draws
        if self.current_player == 'AI':
            # AI played draw two, so human draws
            self.human.draw_card(silent=True)
            self.human.draw_card(silent=True)
        else:
            # Human played draw two, so AI draws
            self.AI.draw_card(self.deck)
            self.AI.draw_card(self.deck)

        self.switch_player()
        self.switch_player()
        window.after(300, self.turns)

    def wild(self):
        print(  "wild-- " + self.current_player) #for debugging only
        global current_card
        if self.current_player == 'human':
            #choose color GUI
            choice = tk.simpledialog.askstring("Choose Color", "Enter a color (red, yellow, green, blue):")
            if choice in color:
                current_card.color = choice
                current_card.widget.config(bg=choice)
            else:
                print("Invalid color choice. Defaulting to red.")
                current_card.color = 'red'
                current_card.widget.config(bg='red')
        else:
            #AI - use intelligent color selection
            chosen_color = self.AI.choose_color()
            current_card.color = chosen_color
            current_card.widget.config(bg=chosen_color)
            print(f"AI chose color: {chosen_color}") #for debugging only
        print("color now: ", current_card.color) #for debugging only
        self.switch_player()
        window.after(300, self.turns)

    def wild_draw_four(self):
        global current_card
        print("wild draw four-- " + self.current_player) #for debugging only

        # Choose color first (like wild)
        if self.current_player == 'human':
            choice = tk.simpledialog.askstring("Choose Color", "Enter a color (red, yellow, green, blue):")
            if choice in color:
                current_card.color = choice
                current_card.widget.config(bg=choice)
            else:
                print("Invalid color choice. Defaulting to red.")
                current_card.color = 'red'
                current_card.widget.config(bg='red')
        else:
            # AI chooses color intelligently
            chosen_color = self.AI.choose_color()
            current_card.color = chosen_color
            current_card.widget.config(bg=chosen_color)
            print(f"AI chose color: {chosen_color}")

        # Then the OTHER player draws 4 cards
        if self.current_player == 'AI':
            # AI played wild draw four, so human draws
            self.human.draw_card(silent=True)
            self.human.draw_card(silent=True)
            self.human.draw_card(silent=True)
            self.human.draw_card(silent=True)
        else:
            # Human played wild draw four, so AI draws
            self.AI.draw_card(self.deck)
            self.AI.draw_card(self.deck)
            self.AI.draw_card(self.deck)
            self.AI.draw_card(self.deck)

        print("color now: ", current_card.color) #for debugging only
        self.switch_player()
        window.after(300, self.turns)

    def win(self, player, ai, deck):
        if(player.hand == []):
            messagebox.showinfo("Game Over", f"{player.name} wins!")
        if(ai.hand == []):
            messagebox.showinfo("Game Over", f"{ai.name} wins!")
        if(len(deck) == 0):
            messagebox.showinfo("Out of cards")
        
#-----------------------HELPER FUNCTIONS-----------------------#
#spawn the entire in game deck
def spawn_deck():
    deck = []
    #add num cards
    for c in color:
        for n in number:
            deck.append(Card(c, n))

    #add action cards
    for c in color:
        for a in action:
            for i in range(2):
                deck.append(Card(c, a)) 
    #add wild cards
    for i in range(4):
        for w in wild:
            deck.append(Card('gray40', w))
    
    return deck

#spawn hand cards(randomly taking 7 cards from deck)
def spawn_hands(deck, hand_size=7):
    hands = random.sample(deck, hand_size)
    for i in hands:
        deck.remove(i)
    return hands

#check if card is num, if not then do things(geez i never know UNO is this complicated)
def check_cards(current_card):
    while(current_card.text != 'number'):
        #action card
        if(current_card.text not in action):
            if(current_card.text == 'skip'):
                #game_manager.skip()
                pass
            if(current_card.text == 'reverse'):
                #reverse, but skip in 2 player
                pass
            if(current_card.text == 'draw two'):
                #1st player draw 2 cards from deck and skip turn
                pass
        #wild card
        if(current_card.text not in wild):
            if(current_card.text == 'wild'):
                #player choose card
                pass
            if(current_card.text == 'wild draw four'):
                #return to deck, shuffle, repeat
                pass
    #take turns?
    return current_card

#-----------------------MAIN GAME-----------------------#
#spawn deck and hands
deck = spawn_deck()
random.shuffle(deck) #shuffle deck
hands = spawn_hands(deck)
print("Total cards in hand:", len(hands))
print("______START GAME____")

#idk how to deal with overlapping cards yet so just random x positions for now
for(i) in hands:
    i.place(x=random.randint(50, 650), y=450, width = 100, height = 120)

#pick the top card from the deck, must be num, put in center
current_card = deck.pop()
#if the first card is not a number, keep picking until it is, I DONT WANNA USE WHILE LOOP HELP, fix later
if(current_card.text not in number):
    print("Shuffling the cards......")
    deck.append(current_card)
    random.shuffle(deck)
    current_card = deck.pop()

current_card.place(x=350, y=200, width = 100, height = 120)

#setup
player = Player("Player 1", deck, hands)
ai = AI_bot("AI", deck, spawn_hands(deck), difficulty='medium') #choose difficulty
game_manager = GameManager(player, ai, deck)

#game iteration
game_manager.start()

window.mainloop()