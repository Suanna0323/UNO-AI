# ai_performance_test.py
import random
from AI_uno import AI_bot, GameState
from main_game import spawn_deck, spawn_hands, color, number, action, wild

NUM_GAMES = 1000
DIFFICULTIES = ['easy', 'medium', 'hard']

# ---------------- MINIMAL CARD CLASS ---------------- #
class Card:
    """Minimal card class for simulation."""
    def __init__(self, color, text):
        self.color = color
        self.text = text

# ---------------- SIMPLE SIMULATED PLAYER ---------------- #
class RandomPlayer:
    """Simulates a typical player that plays any valid card randomly."""
    def __init__(self, hand):
        self.hand = hand

    def choose_card(self, current_card):
        valid_cards = [card for card in self.hand if
                       card.color == current_card.color or
                       card.text == current_card.text or
                       card.text in ['wild', 'wild draw four']]
        if valid_cards:
            return random.choice(valid_cards)
        return None

# ---------------- GAME SIMULATION ---------------- #
def simulate_single_game(difficulty):
    deck = spawn_deck()
    ai_hand = spawn_hands(deck)
    player_hand = spawn_hands(deck)

    # Convert main_game.Card objects to minimal Card objects
    ai_hand = [Card(c.color, c.text) for c in ai_hand]
    player_hand = [Card(c.color, c.text) for c in player_hand]

    # Initialize AI and random player
    ai = AI_bot("AI", deck.copy(), ai_hand.copy(), difficulty=difficulty)
    player = RandomPlayer(player_hand.copy())

    # Initialize starting card
    current_card_obj = deck.pop()
    while current_card_obj.text not in number:
        deck.append(current_card_obj)
        random.shuffle(deck)
        current_card_obj = deck.pop()
    current_card = Card(current_card_obj.color, current_card_obj.text)

    # Game loop
    current_player = 'ai'  # AI starts
    while len(ai.hand) > 0 and len(player.hand) > 0:
        if current_player == 'ai':
            chosen = ai.choose_card(ai.hand, current_card)
            if chosen:
                ai.hand.remove(chosen)
                current_card = chosen
            else:
                if deck:
                    c = deck.pop()
                    current_card = Card(c.color, c.text)
                    ai.hand.append(current_card)
            current_player = 'player'
        else:
            chosen = player.choose_card(current_card)
            if chosen:
                player.hand.remove(chosen)
                current_card = chosen
            else:
                if deck:
                    c = deck.pop()
                    current_card = Card(c.color, c.text)
                    player.hand.append(current_card)
            current_player = 'ai'

    return 'ai' if len(ai.hand) == 0 else 'player'

# ---------------- RUN SIMULATION ---------------- #
if __name__ == "__main__":
    for difficulty in DIFFICULTIES:
        wins = 0
        for _ in range(NUM_GAMES):
            winner = simulate_single_game(difficulty)
            if winner == 'ai':
                wins += 1
        win_rate = wins / NUM_GAMES * 100
        print(f"Difficulty: {difficulty.capitalize()} - AI Win Rate: {win_rate:.2f}%")
