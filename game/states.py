from enum import Enum, auto


class GameState(Enum):
    START = auto()
    STORY = auto()
    SETTINGS = auto()
    LEVEL_SELECT = auto()
    PLAY = auto()
    GAMEOVER = auto()
    COMPLETE = auto()
    CUTSCENE_LEFT_CONTROLLER = auto()
    CUTSCENE_RIGHT_CONTROLLER = auto()
    CUTSCENE_SCREEN = auto()
    VICTORY_CUTSCENE = auto()
    CONGRATULATIONS = auto()
