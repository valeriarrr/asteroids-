"""Обработчик событий клавиатуры и мыши."""


class Controls:
    """Связывает нажатия клавиш и клики мыши с логикой игры."""

    def __init__(self, root, canvas, app):
        """Настраивает привязки событий для окна и холста."""
        self.app = app
        self.root = root
        self.canvas = canvas

        root.bind('<KeyPress-Left>', lambda e: setattr(self.app.player, 'rotating_left', True))
        root.bind('<KeyRelease-Left>', lambda e: setattr(self.app.player, 'rotating_left', False))
        root.bind('<KeyPress-Right>', lambda e: setattr(self.app.player, 'rotating_right', True))
        root.bind('<KeyRelease-Right>', lambda e: setattr(self.app.player, 'rotating_right', False))
        root.bind('<KeyPress-Up>', lambda e: setattr(self.app.player, 'thrusting', True))
        root.bind('<KeyRelease-Up>', lambda e: setattr(self.app.player, 'thrusting', False))
        root.bind('<KeyPress-space>', self._on_space_press)
        root.bind('<KeyRelease-space>', lambda e: setattr(self.app.player, 'shooting', False))

        canvas.bind('<Button-1>', self._on_canvas_click)
        canvas.bind('<Motion>', self._on_canvas_motion)
        root.focus_force()

    def _on_space_press(self, event):
        """Обрабатывает нажатие пробела для одиночного выстрела."""
        if self.app.in_game and not self.app.player.shooting:
            self.app.fire_missile()
        self.app.player.shooting = True

    def _on_canvas_motion(self, event):
        """Только визуально подсвечивает кнопку запуска при наведении курсора."""
        if not self.app.in_game:
            cx = self.app.SCREEN_WIDTH / 2
            cy = self.app.SCREEN_HEIGHT / 2
            self.app.hover_launch = (
                (cx - 175 <= event.x <= cx + 175)
                and (cy + 88 <= event.y <= cy + 138)
            )

    def _on_canvas_click(self, event):
        """Обрабатывает клики на заставке: сначала выбор темы, затем старт игры."""
        if not self.app.in_game:
            if self.app.handle_theme_click(event.x, event.y):
                return

            if self.app.theme_selected:
                cx = self.app.SCREEN_WIDTH / 2
                cy = self.app.SCREEN_HEIGHT / 2
                if (cx - 175 <= event.x <= cx + 175) and (cy + 88 <= event.y <= cy + 138):
                    self.app.start_game()
