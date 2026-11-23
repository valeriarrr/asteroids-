"""Модели игровых объектов: базовое физическое тело и астероид."""
import math
import random


class GameObject:
    """Базовый класс для движущихся объектов в тороидальном пространстве."""

    def __init__(self, x, y, vx, vy, angle, angular_vel, radius, screen_w, screen_h):
        """Инициализация параметров физического тела."""
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.angle = float(angle)
        self.angular_vel = float(angular_vel)
        self.radius = float(radius)
        self.screen_w = screen_w
        self.screen_h = screen_h

    def update(self):
        """Обновляет координаты и угол поворота с учетом зацикленного экрана."""
        self.x = (self.x + self.vx) % self.screen_w
        self.y = (self.y + self.vy) % self.screen_h
        self.angle = (self.angle + self.angular_vel) % 360

    def collides_with(self, other):
        """Проверяет столкновение двух круглых объектов."""
        distance = math.hypot(self.x - other.x, self.y - other.y)
        return distance < (self.radius + other.radius)


class AsteroidModel(GameObject):
    """Класс астероида со случайной линейной и угловой скоростью."""

    MIN_SPEED = 0.8
    MAX_SPEED = 2.5
    MAX_ANGULAR_SPEED = 3.0
    ASTEROID_RADIUS = 28

    def __init__(self, screen_w, screen_h, safe_x=None, safe_y=None):
        """Создает астероид в случайной точке, не пересекающейся с центром."""
        while True:
            x = random.uniform(0, screen_w)
            y = random.uniform(0, screen_h)
            if safe_x is None or math.hypot(x - safe_x, y - safe_y) > 120:
                break

        speed = random.uniform(self.MIN_SPEED, self.MAX_SPEED)
        move_angle = random.uniform(0, 2 * math.pi)
        vx = math.cos(move_angle) * speed
        vy = math.sin(move_angle) * speed
        angular_vel = random.uniform(-self.MAX_ANGULAR_SPEED, self.MAX_ANGULAR_SPEED)

        super().__init__(
            x=x,
            y=y,
            vx=vx,
            vy=vy,
            angle=random.uniform(0, 360),
            angular_vel=angular_vel,
            radius=self.ASTEROID_RADIUS,
            screen_w=screen_w,
            screen_h=screen_h,
        )
        self.image_index = None

class ExplosionModel:
    """Класс покадровой анимации взрыва на месте уничтоженного астероида."""

    def __init__(self, x, y, total_frames=24):
        """Инициализация взрыва в заданных координатах."""
        self.x = x
        self.y = y
        self.current_frame = 0
        self.total_frames = total_frames
        self.finished = False

    def update(self):
        """Переключает кадр анимации взрыва."""
        self.current_frame += 1
        if self.current_frame >= self.total_frames:
            self.finished = True

