# main_game.py
import random
import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import font as tkfont
from AI_uno import AI_bot

# global variables
window = None          # main Tkinter window
game_manager = None    # instance of GameManager to control game flow
current_card = None    # currently active card on discard pile
ai_hand_label = None   # label displaying AI's hand size

# ---------------- TITLE SCREEN ---------------- #
def show_title_screen(root, start_game_callback):
    """Display the title screen with difficulty buttons."""
    for widget in root.winfo_children():
        widget.destroy()  # remove any existing widgets

    title = tk.Label(root, text="UNO", font=("Arial", 48, "bold"))
    title.pack(pady=40)

    # Button to start game with Easy AI
    btn_easy = tk.Button(root, text="Easy", font=("Arial", 22),
                         command=lambda: start_game_callback(root, "easy"))
    btn_easy.pack(pady=8)

    # Button to start game with Medium AI
    btn_med = tk.Button(root, text="Medium", font=("Arial", 22),
                        command=lambda: start_game_callback(root, "medium"))
    btn_med.pack(pady=8)

    # Button to start game with Hard AI
    btn_hard = tk.Button(root, text="Hard", font=("Arial", 22),
                         command=lambda: start_game_callback(root, "hard"))
    btn_hard.pack(pady=8)

# ---------------- START GAME ---------------- #
def start_uno_game(root, difficulty):
    """Initialize the UNO game UI and start the game."""
    global window
    window = root
    for widget in window.winfo_children():
        widget.destroy()
    initialize_game_ui(difficulty)

# ---------------- GAME SETTINGS ---------------- #
color = ['red', 'yellow', 'green', 'blue']  # available colors
number = ['0', '1', '1', '2', '2', '3', '3', '4', '4', '5', '5',
          '6', '6', '7', '7', '8', '8', '9', '9']  # number cards
action = ['skip', 'reverse', 'draw two']  # action cards
wild = ['wild', 'wild draw four']        # wild cards

# ---------------- CARD CLASS ---------------- #
class Card:
    """Represents an Uno card and handles its UI interactions."""
    def __init__(self, color, text):
        self.color = color
        self.text = text
        self.is_played = False
        self.widget = None
        self.x = 0
        self.y = 0

    def create_widget(self):
        """Create a Tkinter Label for the card if it doesn't exist."""
        if self.widget is None:
            self.widget = tk.Label(window, text=self.text, bg=self.color,
                                   font=tkfont.Font(size=10, weight="bold"),
                                   width=8, height=5, bd=2, relief="raised")
            # Bind mouse events for drag-and-drop
            self.widget.bind("<Button-1>", self.on_click)
            self.widget.bind("<B1-Motion>", self.drag_motion)
            self.widget.bind("<ButtonRelease-1>", self.on_release)

    def place(self, **kwargs):
        """Place the card widget at a specific position."""
        self.create_widget()
        self.widget.place(**kwargs)
        if 'x' in kwargs: self.x = kwargs['x']
        if 'y' in kwargs: self.y = kwargs['y']

    def on_click(self, event):
        """Store initial click coordinates for drag."""
        self.widget.startX = event.x
        self.widget.startY = event.y

    def drag_motion(self, event):
        """Handle card being dragged across the window."""
        new_widget = event.widget
        new_widget.tkraise()
        x = new_widget.winfo_x() + (event.x - new_widget.startX)
        y = new_widget.winfo_y() + (event.y - new_widget.startY)
        new_widget.place(x=x, y=y)

    def on_release(self, event):
        """Handle card release; attempt to play it if valid."""
        global game_manager, current_card
        if not game_manager or game_manager.current_player != 'human':
            self.reset_position()
            return

        if self.is_inside_discard() and game_manager.is_card_valid(self):
            self.is_played = True
            if self in game_manager.human.hand: game_manager.human.hand.remove(self)
            game_manager.discard_pile.add_card(self)
            game_manager.AI.discard_history.append(self)
            game_manager.AI.opponent_hand_size = len(game_manager.human.hand)
            game_manager.AI.deck_size = len(game_manager.deck)
            game_manager.human.turn = False
            game_manager.human.card_button.place_forget()

            if len(game_manager.human.hand) == 0:
                messagebox.showinfo("Game Over", "You Win!")
                window.quit()
                return

            game_manager.end_turn(self)
            layout_player_hand(game_manager.human)

            if game_manager.current_player == 'AI':
                window.after(200, game_manager.turns)
        else:
            self.reset_position()

    def reset_position(self):
        """Return card to player's hand if not played."""
        owner_hand = game_manager.human.hand if game_manager and game_manager.human else None
        if owner_hand and self in owner_hand:
            layout_player_hand(game_manager.human)

    def is_inside_discard(self):
        """Check if card is inside discard pile area."""
        x, y = self.widget.winfo_x(), self.widget.winfo_y()
        w, h = self.widget.winfo_width(), self.widget.winfo_height()
        return (250 <= x <= 550 and 160 <= y <= 340)

# ---------------- PLAYER ---------------- #
class Player:
    """Represents a human player in the game."""
    def __init__(self, name, deck, hand):
        self.name = name
        self.deck = deck
        self.hand = hand
        self.turn = False
        self.card_button = tk.Button(window, text="Draw Card", command=self.draw_card_button)
        self.uno_button = tk.Button(window, text="Say UNO", command=self.say_UNO)
        self.uno_button.place(x=700, y=250)

    def start_turn(self):
        """Enable player's turn and show draw card button."""
        self.turn = True
        self.card_button.place(x=700, y=200)

    def draw_card_button(self):
        """Allow player to draw a card from the deck manually."""
        if not self.turn: return
        if self.deck:
            drawn = self.deck.pop()
            self.hand.append(drawn)
            drawn.create_widget()
            layout_player_hand(self)

        # Check if player can play any card after drawing
        playable = any(game_manager.is_card_valid(c) for c in self.hand)
        if not playable:
            self.end_turn_after_draw()

    def end_turn_after_draw(self):
        """End the player's turn after drawing if no playable cards."""
        self.turn = False
        self.card_button.place_forget()
        game_manager.switch_player()
        window.after(200, game_manager.turns)

    def draw_card_silent(self):
        """Draw a card without user interaction (used for AI)."""
        if self.deck:
            drawn = self.deck.pop()
            self.hand.append(drawn)
            drawn.create_widget()
            layout_player_hand(self)

    def say_UNO(self):
        """Display a message when the player calls UNO."""
        if len(self.hand) == 1:
            messagebox.showinfo("UNO!", f"{self.name} has 1 card left!")
        else:
            messagebox.showwarning("Invalid UNO", f"You can only call UNO when you have 1 card!\nYou have {len(self.hand)} cards.")

# ---------------- DISCARD PILE ---------------- #
class Discard_Pile:
    """Represents the discard pile area in the game UI."""
    def __init__(self):
        self.frame = tk.Frame(window, width=200, height=150, bg='grey')
        self.frame.place(x=300, y=180)
        self.cards = []

    def add_card(self, card):
        """Add a card to the discard pile and update its UI."""
        card.widget.place(x=350, y=200, width=100, height=120)
        # Remove interactivity once card is discarded
        card.widget.unbind("<Button-1>")
        card.widget.unbind("<B1-Motion>")
        card.widget.unbind("<ButtonRelease-1>")
        card.widget.tkraise()
        self.cards.append(card)

# ---------------- GAME MANAGER ---------------- #
class GameManager:
    """Controls game flow, player turns, and game rules."""
    def __init__(self, human, AI, deck):
        self.human = human
        self.AI = AI
        self.deck = deck
        self.current_player = 'AI'
        self.discard_pile = Discard_Pile()
        self.locked = False  # prevents overlapping AI/human turns

    def start(self):
        """Start the game loop."""
        window.after(300, self.turns)

    def turns(self):
        """Handle the current player's turn."""
        global current_card
        if self.locked: return
        if self.current_player == 'human':
            self.human.start_turn()
        else:
            self.locked = True
            window.after(50, self._ai_make_move)

    def _ai_make_move(self):
        """AI selects a card to play or draws if no playable cards."""
        global current_card
        self.AI.is_AI_turn = True
        chosen = self.AI.choose_card(self.AI.hand, current_card)
        if chosen is None:
            if self.deck:
                drawn = self.deck.pop()
                self.AI.hand.append(drawn)
                update_ai_hand_label(self)
            self.AI.is_AI_turn = False
            self.locked = False
            self.switch_player()
            window.after(200, self.turns)
            return

        if not hasattr(chosen, 'widget') or chosen.widget is None:
            chosen.create_widget()
        self.discard_pile.add_card(chosen)
        if chosen in self.AI.hand: self.AI.hand.remove(chosen)

        self.AI.opponent_hand_size = len(self.human.hand)
        self.AI.deck_size = len(self.deck)
        self.AI.discard_history.append(chosen)
        update_ai_hand_label(self)

        if len(self.AI.hand) == 0:
            messagebox.showinfo("Game Over", "AI Wins!")
            window.quit()
            return

        self.end_turn(chosen)
        self.AI.is_AI_turn = False
        self.locked = False
        window.after(200, self.turns)

    def end_turn(self, played_card):
        """Resolve the effect of the played card and advance turn."""
        global current_card
        current_card = played_card
        text = played_card.text

        if text in number:
            self.switch_player()
        elif text == 'skip': self.skip()
        elif text == 'reverse': self.reverse()
        elif text == 'draw two': self.draw_two()
        elif text == 'wild': self.wild()
        elif text == 'wild draw four': self.wild_draw_four()

    def switch_player(self):
        """Switch turn to the other player."""
        self.current_player = 'AI' if self.current_player == 'human' else 'human'

    def is_card_valid(self, card):
        """Check if a card can be legally played on the current discard."""
        global current_card
        if not current_card: return True
        if card.color == current_card.color or card.text == current_card.text: return True
        if card.text in wild: return True
        return False

    def reverse(self):
        """Reverse effect (switch twice to maintain game flow)."""
        self.switch_player()
        self.switch_player()
        window.after(200, self.turns)

    def skip(self):
        """Skip opponent's turn (switch twice)."""
        self.switch_player()
        self.switch_player()
        window.after(200, self.turns)

    def draw_two(self):
        """Handle 'draw two' effect depending on who played it."""
        if self.current_player == 'human':
            # human played -> AI draws 2 silently
            for _ in range(2):
                self.AI.draw_card_silent(self.deck)
            update_ai_hand_label(self)
            self.switch_player()
        else:
            # AI played -> human draws 2 silently
            self.human.draw_card_silent()
            self.human.draw_card_silent()
            self.switch_player()
        window.after(200, self.turns)

    def wild(self):
        """Handle 'wild' card: player chooses a color."""
        global current_card
        if self.current_player == 'human':
            choice = simpledialog.askstring("Choose Color", "Enter a color (red, yellow, green, blue):")
            if choice in color:
                current_card.color = choice
                current_card.widget.config(bg=choice)
            else:
                current_card.color = 'red'
                current_card.widget.config(bg='red')
        else:
            current_card.color = self.AI.choose_color()
            current_card.widget.config(bg=current_card.color)
        self.switch_player()
        window.after(200, self.turns)

    def wild_draw_four(self):
        """Handle 'wild draw four' card effect for both players."""
        global current_card
        if self.current_player == 'human':
            choice = simpledialog.askstring("Choose Color", "Enter a color (red, yellow, green, blue):")
            if choice in color:
                current_card.color = choice
                current_card.widget.config(bg=choice)
            else:
                current_card.color = 'red'
                current_card.widget.config(bg='red')
            # AI draws 4 silently
            for _ in range(4):
                self.AI.draw_card_silent(self.deck)
            update_ai_hand_label(self)
        else:
            current_card.color = self.AI.choose_color()
            current_card.widget.config(bg=current_card.color)
            # Human draws 4 silently
            for _ in range(4):
                self.human.draw_card_silent()
        self.switch_player()
        window.after(200, self.turns)

# ---------------- HELPERS ---------------- #
def spawn_deck():
    """Create a shuffled deck of Uno cards."""
    deck = []
    for c in color:
        for n in number:
            deck.append(Card(c, n))
    for c in color:
        for a in action:
            deck.append(Card(c, a))
            deck.append(Card(c, a))
    for _ in range(4):
        for w in wild:
            deck.append(Card('gray40', w))
    random.shuffle(deck)
    return deck

def spawn_hands(deck, hand_size=7):
    """Draw a starting hand for a player from the deck."""
    hands = random.sample(deck, hand_size)
    for i in hands: deck.remove(i)
    return hands

def layout_player_hand(player):
    """Arrange the player's hand cards visually on the UI."""
    hand = player.hand
    if not hand: return
    area_width, y = 700, 440
    n = len(hand)
    card_width = 100
    spacing = max(10, min(120, (area_width - card_width)//max(1,n-1)))
    total_width = card_width + spacing*(n-1)
    start_x = max(50, (800-total_width)//2)
    for idx, card in enumerate(hand):
        x = start_x + idx*spacing
        card.place(x=x, y=y, width=100, height=120)

def update_ai_hand_label(manager):
    """Update the label showing the AI's hand size."""
    global ai_hand_label
    if ai_hand_label and manager and manager.AI:
        ai_hand_label.config(text=f"AI Hand: {len(manager.AI.hand)} cards")

# ---------------- INITIALIZATION ---------------- #
def initialize_game_ui(difficulty):
    """Set up the main game interface and start the GameManager."""
    global game_manager, current_card, window, ai_hand_label
    deck = spawn_deck()
    human_hand = spawn_hands(deck)
    for c in human_hand: c.create_widget()
    current_card = deck.pop()
    while current_card.text not in number:
        deck.append(current_card)
        random.shuffle(deck)
        current_card = deck.pop()
    current_card.create_widget()
    current_card.place(x=350, y=200, width=100, height=120)
    ai_hand_label = tk.Label(window, text="AI Hand: 0 cards", font=("Arial",14))
    ai_hand_label.place(x=300, y=10, width=200)
    player = Player("Player 1", deck, human_hand)
    ai = AI_bot("AI", deck, spawn_hands(deck), difficulty=difficulty)
    layout_player_hand(player)
    game_manager = GameManager(player, ai, deck)
    update_ai_hand_label(game_manager)
    game_manager.start()

# ---------------- MAIN ---------------- #
if __name__ == "__main__":
    root = tk.Tk()
    root.title("UNO")
    root.geometry("800x600")
    show_title_screen(root, start_uno_game)
    root.mainloop()
