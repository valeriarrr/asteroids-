"""Модель ракеты, выпускаемой кораблем."""
import math
from src.models.asteroid_model import GameObject


class BulletModel(GameObject):
    """Класс ракеты, летящей с постоянной скоростью и ограниченным временем жизни."""

    MISSILE_SPEED = 9.0
    MISSILE_RADIUS = 5
    # Меньшее измерение экрана = 600 пикс. При скорости 9 пикс/кадр
    # время жизни 52 кадра дает дальность 468 пикс (< 600 пикс).
    MAX_LIFESPAN = 52

    def __init__(self, x, y, angle, ship_vx, ship_vy, screen_w, screen_h):
        """Создает ракету в точке носа корабля с учетом его ориентации."""
        rad = math.radians(angle)
        vx = ship_vx + math.cos(rad) * self.MISSILE_SPEED
        vy = ship_vy + math.sin(rad) * self.MISSILE_SPEED

        super().__init__(
            x=x,
            y=y,
            vx=vx,
            vy=vy,
            angle=angle,
            angular_vel=0.0,
            radius=self.MISSILE_RADIUS,
            screen_w=screen_w,
            screen_h=screen_h,
        )
        self.age = 0

    def update(self):
        """Двигает ракету по тороидальному полю и увеличивает счетчик времени жизни."""
        super().update()
        self.age += 1

    def is_expired(self):
        """Возвращает True, если время жизни ракеты истекло."""
        return self.age >= self.MAX_LIFESPAN
