"""Главный модуль приложения «airplane good game»."""
import tkinter as tk
from src.models.asteroid_model import AsteroidModel, ExplosionModel
from src.models.bullet_model import BulletModel
from src.models.player_model import PlayerModel
from src.renderers.renderer import Renderer
from src.widgets.controls import Controls


class App:
    """Управляет окном, состоянием игры, столкновениями и игровым циклом."""

    # Глобальные параметры игры
    GAME_TITLE = 'AIRPLANE GOOD GAME'
    SCREEN_WIDTH = 800          # Ширина игрового поля (пикс.)
    SCREEN_HEIGHT = 600         # Высота игрового поля (пикс.)
    FPS_DELAY_MS = 20           # Интервал обновления кадра (~50 FPS)
    ASTEROID_COUNT = 5          # Количество астероидов на поле
    ASTEROID_SPAWN_MS = 1200    # Частота генерации новых астероидов (мс)
    SPLASH_WIDTH = 520          # Ширина тактической заставки
    SPLASH_HEIGHT = 360         # Высота тактической заставки

    def __init__(self):
        """Инициализирует окно Tkinter, модели и рендерер."""
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

        # Состояние игры и выбранная тема ('night' или 'day')
        self.in_game = False
        self.theme = 'night'
        self.theme_selected = False
        self.hover_launch = False
        self.splash_tick = 0
        self.score = 0
        self.last_spawn_time = 0

        # Игровые сущности
        self.player = PlayerModel(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.bullets = []
        self.asteroids = []
        self.explosions = []

        self.renderer = Renderer(self.canvas, self)
        self.controls = Controls(self.root, self.canvas, self)

    def run(self):
        """Запускает главный цикл приложения."""
        self._game_loop()
        self.root.mainloop()

    def is_click_on_splash(self, click_x, click_y):
        """Проверяет, попал ли клик мыши внутрь прямоугольника заставки."""
        cx = self.SCREEN_WIDTH / 2
        cy = self.SCREEN_HEIGHT / 2
        half_w = self.SPLASH_WIDTH / 2
        half_h = self.SPLASH_HEIGHT / 2
        return (cx - half_w <= click_x <= cx + half_w) and (cy - half_h <= click_y <= cy + half_h)

    def handle_theme_click(self, click_x, click_y):
        """Переключает режим ДЕНЬ / НОЧЬ и разрешает запуск игры."""
        cx = self.SCREEN_WIDTH / 2
        cy = self.SCREEN_HEIGHT / 2
        if cy + 30 <= click_y <= cy + 68:
            if cx - 210 <= click_x <= cx - 15:
                self.theme = 'day'
                self.theme_selected = True
                return True
            if cx + 15 <= click_x <= cx + 210:
                self.theme = 'night'
                self.theme_selected = True
                return True
        return False

    def start_game(self):
        """Начинает новую игру при щелчке по заставке."""
        self.in_game = True
        self.score = 0
        self.player.lives = PlayerModel.INITIAL_LIVES
        self.player.reset_position()

        self.bullets.clear()
        self.asteroids.clear()
        self.explosions.clear()

        # Генерируем 5 начальных астероидов
        for _ in range(self.ASTEROID_COUNT):
            self.asteroids.append(
                AsteroidModel(
                    self.SCREEN_WIDTH,
                    self.SCREEN_HEIGHT,
                    safe_x=self.player.x,
                    safe_y=self.player.y,
                )
            )
        self.last_spawn_time = self.root.tk.call('clock', 'milliseconds')

    def fire_missile(self):
        """Выпускает ракету из носа корабля."""
        nose_x, nose_y = self.player.get_nose_position()
        missile = BulletModel(
            x=nose_x,
            y=nose_y,
            angle=self.player.angle,
            ship_vx=self.player.vx,
            ship_vy=self.player.vy,
            screen_w=self.SCREEN_WIDTH,
            screen_h=self.SCREEN_HEIGHT,
        )
        self.bullets.append(missile)

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
        # 1. Столкновение ракеты и астероида (+1 очко, взрыв на месте астероида)
        for ast in self.asteroids[:]:
            for missile in self.bullets[:]:
                if ast.collides_with(missile):
                    self.bullets.remove(missile)
                    self.asteroids.remove(ast)
                    self.explosions.append(ExplosionModel(ast.x, ast.y))
                    self.score += 1
                    break

        # 2. Столкновение корабля и астероида (-1 жизнь, возрождение корабля в центре)
        for ast in self.asteroids[:]:
            if ast.collides_with(self.player):
                self.asteroids.remove(ast)
                self.explosions.append(ExplosionModel(ast.x, ast.y))
                self.player.lives -= 1
                self.player.reset_position()

                if self.player.lives <= 0:
                    self._end_game()
                    return

    def _end_game(self):
        """Завершает игру при потере всех жизней и возвращает заставку."""
        self.in_game = False
        self.asteroids.clear()
        self.bullets.clear()
        self.explosions.clear()

    def _game_loop(self):
        """Основной игровой цикл: обновление физики и перерисовка экрана."""
        if self.in_game:
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
