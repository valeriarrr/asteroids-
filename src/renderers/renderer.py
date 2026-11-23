"""Рендерер Этапа 2: добавлены ракеты и индикация тяги двигателя."""
import math


class Renderer:
    """Отрисовывает примитивы корабля, ракет и астероидов."""

    def __init__(self, canvas, app):
        """Сохраняет ссылки на холст и приложение."""
        self.canvas = canvas
        self.app = app

    def draw(self):
        """Отрисовывает кадр игры."""
        self.canvas.delete('all')

        for ast in self.app.asteroids:
            r = ast.radius
            self.canvas.create_oval(
                ast.x - r, ast.y - r, ast.x + r, ast.y + r, outline='#aaaaaa', width=2
            )

        for missile in self.app.bullets:
            r = missile.radius
            self.canvas.create_oval(
                missile.x - r, missile.y - r, missile.x + r, missile.y + r, fill='#ff4400', outline=''
            )

        p = self.app.player
        rad = math.radians(p.angle)
        nose = (p.x + math.cos(rad) * 24, p.y + math.sin(rad) * 24)
        left = (p.x + math.cos(rad + 2.4) * 18, p.y + math.sin(rad + 2.4) * 18)
        right = (p.x + math.cos(rad - 2.4) * 18, p.y + math.sin(rad - 2.4) * 18)
        self.canvas.create_polygon([nose, left, right], fill='#ffffff', outline='#00ffcc')

        if p.thrusting:
            tail = (p.x - math.cos(rad) * 26, p.y - math.sin(rad) * 26)
            self.canvas.create_line(p.x, p.y, tail[0], tail[1], fill='#ff9900', width=4)

        self.canvas.create_text(
            40, 25, text=f'Lives: {p.lives}', fill='#00ff00', anchor='nw', font=('Arial', 20, 'bold')
        )
        self.canvas.create_text(
            self.app.SCREEN_WIDTH - 40, 25,
            text=f'Score: {self.app.score}', fill='#00ff00', anchor='ne', font=('Arial', 20, 'bold')
        )
