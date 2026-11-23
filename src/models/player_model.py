"""Модель космического корабля игрока с инерцией и вращением."""
import math
from src.models.asteroid_model import GameObject


class PlayerModel(GameObject):
    """Класс корабля игрока с ускорением и сопротивлением среды."""

    ROTATION_SPEED = 5.0
    THRUST_ACCEL = 0.25
    FRICTION = 0.985
    SHIP_RADIUS = 22
    INITIAL_LIVES = 3

    def __init__(self, screen_w, screen_h):
        """Инициализирует корабль в центре экрана."""
        super().__init__(
            x=screen_w / 2, y=screen_h / 2, vx=0.0, vy=0.0,
            angle=0.0, angular_vel=0.0, radius=self.SHIP_RADIUS,
            screen_w=screen_w, screen_h=screen_h,
        )
        self.lives = self.INITIAL_LIVES
        self.rotating_left = False
        self.rotating_right = False
        self.thrusting = False
        self.shooting = False

    def reset_position(self):
        """Возрождает корабль неподвижным в центре игрового поля."""
        self.x = self.screen_w / 2
        self.y = self.screen_h / 2
        self.vx = 0.0
        self.vy = 0.0
        self.angle = 0.0
        self.thrusting = False

    def update(self):
        """Обновляет поворот, вектор скорости и координаты корабля."""
        if self.rotating_left:
            self.angle = (self.angle - self.ROTATION_SPEED) % 360
        if self.rotating_right:
            self.angle = (self.angle + self.ROTATION_SPEED) % 360

        if self.thrusting:
            rad = math.radians(self.angle)
            self.vx += math.cos(rad) * self.THRUST_ACCEL
            self.vy += math.sin(rad) * self.THRUST_ACCEL

        self.vx *= self.FRICTION
        self.vy *= self.FRICTION

        if math.hypot(self.vx, self.vy) < 0.02 and not self.thrusting:
            self.vx = 0.0
            self.vy = 0.0

        super().update()

    def get_nose_position(self):
        """Возвращает координаты носа корабля для запуска ракеты."""
        rad = math.radians(self.angle)
        return (
            self.x + math.cos(rad) * (self.radius + 6),
            self.y + math.sin(rad) * (self.radius + 6),
        )
