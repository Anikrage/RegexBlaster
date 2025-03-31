class GameState:
    """Manage the state of the game."""
    
    def __init__(self):
        """Initialize game state."""
        self.attack_string = None
        self.noncomb_string = None
        self.last_defense = ""
        self.score = 0
        self.message = 'Welcome to Regex Blaster! Type a regex to defend against the attack.'
        self.attack_history = []
        self.noncomb_history = []
        self.attack_limit = 5
        self.noncomb_limit = 3
        self.game_over = False
