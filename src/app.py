"""Главный модуль приложения (Этап 3: спрайты, параллакс-фон и взрывы)."""
import tkinter as tk
from src.models.asteroid_model import AsteroidModel, ExplosionModel
from src.models.bullet_model import BulletModel
from src.models.player_model import PlayerModel
from src.renderers.renderer import Renderer
from src.widgets.controls import Controls


class App:
    """Управляет окном, игровым циклом, столкновениями и анимацией взрывов."""

    GAME_TITLE = 'AIRPLANE GOOD GAME'
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    FPS_DELAY_MS = 20
    ASTEROID_COUNT = 5
    ASTEROID_SPAWN_MS = 1200

    def __init__(self):
        """Инициализирует окно Tkinter, модели и графический рендерер."""
        self.root = tk.Tk()
        self.root.title(self.GAME_TITLE)
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(
            self.root,
            width=self.SCREEN_WIDTH,
            height=self.SCREEN_HEIGHT,
            bg='#090b1a',
            highlightthickness=0,
        )
        self.canvas.pack()

        # На Этапе 3 игра запускается сразу (меню появится на Этапе 4)
        self.in_game = True
        self.theme = 'night'
        self.score = 0
        self.last_spawn_time = 0

        self.player = PlayerModel(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.bullets = []
        self.explosions = []
        self.asteroids = [
            AsteroidModel(
                self.SCREEN_WIDTH,
                self.SCREEN_HEIGHT,
                safe_x=self.player.x,
                safe_y=self.player.y,
            )
            for _ in range(self.ASTEROID_COUNT)
        ]

        self.renderer = Renderer(self.canvas, self)
        self.controls = Controls(self.root, self.canvas, self)

    def run(self):
        """Запускает главный цикл приложения."""
        self.last_spawn_time = self.root.tk.call('clock', 'milliseconds')
        self._game_loop()
        self.root.mainloop()

    def fire_missile(self):
        """Выпускает ракету из носа корабля."""
        nose_x, nose_y = self.player.get_nose_position()
        self.bullets.append(
            BulletModel(
                x=nose_x,
                y=nose_y,
                angle=self.player.angle,
                ship_vx=self.player.vx,
                ship_vy=self.player.vy,
                screen_w=self.SCREEN_WIDTH,
                screen_h=self.SCREEN_HEIGHT,
            )
        )

    def _spawn_asteroids_periodically(self):
        """Поддерживает количество астероидов равным ASTEROID_COUNT."""
        current_time = self.root.tk.call('clock', 'milliseconds')
        if (
            len(self.asteroids) < self.ASTEROID_COUNT
            and current_time - self.last_spawn_time >= self.ASTEROID_SPAWN_MS
        ):
            self.asteroids.append(
                AsteroidModel(
                    self.SCREEN_WIDTH,
                    self.SCREEN_HEIGHT,
                    safe_x=self.player.x,
                    safe_y=self.player.y,
                )
            )
            self.last_spawn_time = current_time

    def _handle_collisions(self):
        """Обрабатывает столкновения ракет с астероидами и корабля с астероидами."""
        for ast in self.asteroids[:]:
            for missile in self.bullets[:]:
                if ast.collides_with(missile):
                    self.bullets.remove(missile)
                    self.asteroids.remove(ast)
                    self.explosions.append(ExplosionModel(ast.x, ast.y))
                    self.score += 1
                    break

        for ast in self.asteroids[:]:
            if ast.collides_with(self.player):
                self.asteroids.remove(ast)
                self.explosions.append(ExplosionModel(ast.x, ast.y))
                self.player.lives -= 1
                self.player.reset_position()

                if self.player.lives <= 0:
                    self._reset_game()
                    return

    def _reset_game(self):
        """Перезапускает сессию при потере всех жизней (до появления стартового меню)."""
        self.score = 0
        self.player.lives = PlayerModel.INITIAL_LIVES
        self.player.reset_position()
        self.bullets.clear()
        self.explosions.clear()
        self.asteroids = [
            AsteroidModel(
                self.SCREEN_WIDTH,
                self.SCREEN_HEIGHT,
                safe_x=self.player.x,
                safe_y=self.player.y,
            )
            for _ in range(self.ASTEROID_COUNT)
        ]

    def _game_loop(self):
        """Основной игровой цикл: обновление физики, взрывов и перерисовка."""
        self._spawn_asteroids_periodically()
        self.player.update()

        for missile in self.bullets[:]:
            missile.update()
            if missile.is_expired():
                self.bullets.remove(missile)

        for ast in self.asteroids:
            ast.update()

        self._handle_collisions()

        for exp in self.explosions[:]:
            exp.update()
            if exp.finished:
                self.explosions.remove(exp)

        self.renderer.draw()
        self.root.after(self.FPS_DELAY_MS, self._game_loop)
