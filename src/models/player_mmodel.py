"""Базовая модель корабля игрока."""
from src.models.asteroid_model import GameObject


class PlayerModel(GameObject):
    """Класс корабля игрока в центре экрана."""

    SHIP_RADIUS = 22
    INITIAL_LIVES = 3

    def __init__(self, screen_w, screen_h):
        """Инициализирует корабль неподвижным в центре экрана."""
        super().__init__(
            x=screen_w / 2,
            y=screen_h / 2,
            vx=0.0,
            vy=0.0,
            angle=0.0,
            angular_vel=0.0,
            radius=self.SHIP_RADIUS,
            screen_w=screen_w,
            screen_h=screen_h,
        )
        self.lives = self.INITIAL_LIVES
