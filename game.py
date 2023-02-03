from player import Player
from credits import Credits
from minerals import Minerals
from experience import Experience

class Game:
    def __init__(self):
        self.player1 = Player()
        self.player2 = None
        self.player3 = None
        self.player4 = None
        self.mission_type = None
        self.mission_name = None
        self.difficulty = None
        self.complexity = None
        self.length = None
        self.modifiers = None
        self.mission_time = None
        self.credits = Credits()
        self.minerals = Minerals()
        self.xp = Experience()
