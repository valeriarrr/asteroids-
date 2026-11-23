"""Главный модуль приложения (Этап 1: базовый цикл и физика)."""
import tkinter as tk
from src.models.asteroid_model import AsteroidModel
from src.models.player_model import PlayerModel
from src.renderers.renderer import Renderer


class App:
    """Управляет окном и базовым обновлением координат."""

    GAME_TITLE = 'AIRPLANE GOOD GAME'
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    FPS_DELAY_MS = 20
    ASTEROID_COUNT = 5

    def __init__(self):
        """Инициализирует окно, игрока и 5 астероидов."""
        self.root = tk.Tk()
        self.root.title(self.GAME_TITLE)
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(
            self.root, width=self.SCREEN_WIDTH, height=self.SCREEN_HEIGHT, bg='#090b1a'
        )
        self.canvas.pack()

        self.score = 0
        self.player = PlayerModel(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.asteroids = [
            AsteroidModel(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.player.x, self.player.y)
            for _ in range(self.ASTEROID_COUNT)
        ]
        self.renderer = Renderer(self.canvas, self)

    def run(self):
        """Запускает главный цикл приложения."""
        self._game_loop()
        self.root.mainloop()

    def _game_loop(self):
        """Обновляет позиции объектов и перерисовывает кадр."""
        for ast in self.asteroids:
            ast.update()
        self.renderer.draw()
        self.root.after(self.FPS_DELAY_MS, self._game_loop)
