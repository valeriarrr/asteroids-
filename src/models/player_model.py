"""Модель космического корабля игрока."""
import math
from src.models.asteroid_model import GameObject


class PlayerModel(GameObject):
    """Класс корабля игрока с вращением, ускорением и трением среды."""

    ROTATION_SPEED = 5.0      # Скорость поворота (градусов за кадр)
    THRUST_ACCEL = 0.25       # Ускорение при включенном двигателе
    FRICTION = 0.985          # Коэффициент сопротивления среды (замедление)
    SHIP_RADIUS = 22          # Радиус хитбокса корабля
    INITIAL_LIVES = 3         # Начальное количество жизней

    def __init__(self, screen_w, screen_h):
        """Инициализирует корабль в центре экрана."""
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

        # Флаги управления с клавиатуры
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
        """Обновляет угол поворота, вектор скорости и координаты корабля."""
        # Вращение вокруг своего центра
        if self.rotating_left:
            self.angle = (self.angle - self.ROTATION_SPEED) % 360
        if self.rotating_right:
            self.angle = (self.angle + self.ROTATION_SPEED) % 360

        # Ускорение по направлению ориентации корабля
        if self.thrusting:
            rad = math.radians(self.angle)
            self.vx += math.cos(rad) * self.THRUST_ACCEL
            self.vy += math.sin(rad) * self.THRUST_ACCEL

        # Сопротивление среды при выключенных (и включенных) двигателях
        self.vx *= self.FRICTION
        self.vy *= self.FRICTION

        # Остановка при околонулевой скорости
        if math.hypot(self.vx, self.vy) < 0.02 and not self.thrusting:
            self.vx = 0.0
            self.vy = 0.0

        # Перемещение с учетом тороидальной геометрии
        super().update()
        return self.shooting

    def get_nose_position(self):
        """Возвращает координаты (x, y) носа корабля для запуска ракеты."""
        rad = math.radians(self.angle)
        nose_x = self.x + math.cos(rad) * (self.radius + 6)
        nose_y = self.y + math.sin(rad) * (self.radius + 6)
        return nose_x, nose_y
