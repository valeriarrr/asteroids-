"""Обработчик клавиатуры для управления кораблем и стрельбы."""


class Controls:
    """Связывает нажатия клавиш со свойствами корабля."""

    def __init__(self, root, canvas, app):
        """Настраивает привязки клавиш."""
        self.app = app
        root.bind('<KeyPress-Left>', lambda e: setattr(self.app.player, 'rotating_left', True))
        root.bind('<KeyRelease-Left>', lambda e: setattr(self.app.player, 'rotating_left', False))
        root.bind('<KeyPress-Right>', lambda e: setattr(self.app.player, 'rotating_right', True))
        root.bind('<KeyRelease-Right>', lambda e: setattr(self.app.player, 'rotating_right', False))
        root.bind('<KeyPress-Up>', lambda e: setattr(self.app.player, 'thrusting', True))
        root.bind('<KeyRelease-Up>', lambda e: setattr(self.app.player, 'thrusting', False))
        root.bind('<KeyPress-space>', self._on_space_press)
        root.bind('<KeyRelease-space>', lambda e: setattr(self.app.player, 'shooting', False))
        root.focus_force()

    def _on_space_press(self, event):
        """Выпускает одиночную ракету при нажатии пробела."""
        if not self.app.player.shooting:
            self.app.fire_missile()
        self.app.player.shooting = True
