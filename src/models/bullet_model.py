"""Модель ракеты, выпускаемой кораблем."""
import math
from src.models.asteroid_model import GameObject


class BulletModel(GameObject):
    """Класс ракеты с постоянной скоростью и ограниченным временем жизни."""

    MISSILE_SPEED = 9.0
    MISSILE_RADIUS = 5
    MAX_LIFESPAN = 52

    def __init__(self, x, y, angle, ship_vx, ship_vy, screen_w, screen_h):
        """Создает ракету в точке носа корабля."""
        rad = math.radians(angle)
        vx = ship_vx + math.cos(rad) * self.MISSILE_SPEED
        vy = ship_vy + math.sin(rad) * self.MISSILE_SPEED

        super().__init__(
            x=x, y=y, vx=vx, vy=vy, angle=angle, angular_vel=0.0,
            radius=self.MISSILE_RADIUS, screen_w=screen_w, screen_h=screen_h,
        )
        self.age = 0

    def update(self):
        """Двигает ракету и увеличивает счетчик возраста."""
        super().update()
        self.age += 1

    def is_expired(self):
        """Проверяет, истекло ли время жизни ракеты."""
        return self.age >= self.MAX_LIFESPAN
