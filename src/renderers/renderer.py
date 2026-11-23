"""Модуль графической отрисовки игры «airplane good game»."""
from collections import deque
import os
import random
from PIL import Image, ImageDraw, ImageFilter, ImageTk
import math

class Renderer:
    """Отвечает за обработку спрайтов, генерацию фонов День/Ночь и отрисовку кадров."""

    EXPLOSION_FRAMES = 24
    EXPLOSION_SIZE = 88
    ASTEROID_SIZE = 64
    SHIP_SIZE = (56, 56)
    DEBRIS_SPEED = 1.2

    def __init__(self, canvas, app):
        """Инициализирует рендерер и подготавливает графические ресурсы."""
        self.canvas = canvas
        self.app = app
        self.debris_x = 0.0
        self._tk_cache = []

        self.asteroid_pils = self._load_asteroid_sprites()
        self.ship_base_pil = self._load_ship_sprite(thrust=False)
        self.ship_thrust_pil = self._load_ship_sprite(thrust=True)
        self.missile_pil = self._create_missile_sprite()

        self.bg_night_img = self._create_nebula_bg(is_day=False)
        self.bg_day_img = self._create_nebula_bg(is_day=True)
        self.bg_debris_img = self._create_debris_layer(self.asteroid_pils)

        self.explosion_night_frames = self._create_explosion_frames(is_day=False)
        self.explosion_day_frames = self._create_explosion_frames(is_day=True)

    def _remove_background_auto(self, img):
        """Удаляет внешний фон вокруг контура, сохраняя белый цвет внутри объекта."""
        rgba = img.convert('RGBA')
        w, h = rgba.size
        pixels = rgba.load()

        _, _, _, a_tl = rgba.getpixel((0, 0))
        _, _, _, a_tr = rgba.getpixel((w - 1, 0))
        _, _, _, a_bl = rgba.getpixel((0, h - 1))
        _, _, _, a_br = rgba.getpixel((w - 1, h - 1))

        if a_tl < 20 and a_tr < 20 and a_bl < 20 and a_br < 20:
            bbox = rgba.getbbox()
            return rgba.crop(bbox) if bbox else rgba

        top_colors = {rgba.getpixel((x, 0))[:3] for x in range(min(w, 40))}
        is_checkerboard = (
            len(top_colors) >= 2
            and all(abs(r - g) < 12 and abs(g - b) < 12 and r > 180 for (r, g, b) in top_colors)
        )

        bottom_strip_h = int(h * 0.08)
        dark_bottom = sum(
            1 for x in range(w) for y in range(h - bottom_strip_h, h)
            if max(rgba.getpixel((x, y))[:3]) < 45
        )
        if dark_bottom > (w * bottom_strip_h * 0.7):
            for x in range(w):
                for y in range(h - bottom_strip_h, h):
                    pixels[x, y] = (0, 0, 0, 0)

        visited = set()
        queue = deque()
        for x in range(w):
            queue.append((x, 0))
            queue.append((x, h - 1))
        for y in range(h):
            queue.append((0, y))
            queue.append((w - 1, y))

        bg_r, bg_g, bg_b, _ = rgba.getpixel((0, 0))

        def is_bg_pixel(r, g, b, a):
            if a < 20:
                return True
            if is_checkerboard:
                return abs(r - g) < 15 and abs(g - b) < 15 and r > 185
            return (abs(r - bg_r) + abs(g - bg_g) + abs(b - bg_b)) < 65

        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) in visited or not (0 <= cx < w and 0 <= cy < h):
                continue
            visited.add((cx, cy))

            r, g, b, a = pixels[cx, cy]
            if is_bg_pixel(r, g, b, a):
                pixels[cx, cy] = (0, 0, 0, 0)
                queue.append((cx + 1, cy))
                queue.append((cx - 1, cy))
                queue.append((cx, cy + 1))
                queue.append((cx, cy - 1))

        bbox = rgba.getbbox()
        return rgba.crop(bbox) if bbox else rgba

    def _load_ship_sprite(self, thrust=False):
        """Загружает ваш шаттл из images/ship.png, убирает внешний фон и поворачивает носом вправо."""
        ship_w, ship_h = self.SHIP_SIZE
        ship_path = None
        for name in ('ship.png', 'ship.jpg', 'ship.jpeg'):
            candidate = os.path.join('images', name)
            if os.path.exists(candidate):
                ship_path = candidate
                break

        if ship_path:
            raw = Image.open(ship_path)
            clean = self._remove_background_auto(raw)
            clean = clean.rotate(-90, expand=True)
            base = clean.resize((ship_w, ship_h), Image.Resampling.LANCZOS)
        else:
            base = Image.new('RGBA', (ship_w, ship_h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(base)
            draw.polygon(
                [(ship_w - 4, ship_h // 2), (10, 8), (16, ship_h // 2), (10, ship_h - 8)],
                fill='#ffffff', outline='#000000', width=3,
            )

        if not thrust:
            return base

        canvas_img = Image.new('RGBA', (ship_w + 14, ship_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas_img)
        cy = ship_h // 2
        draw.polygon([(0, cy), (16, cy - 9), (16, cy + 9)], fill='#ff6600')
        draw.polygon([(4, cy), (16, cy - 5), (16, cy + 5)], fill='#ffff66')
        canvas_img.paste(base, (12, 0), base)
        return canvas_img

    def _load_asteroid_sprites(self):
        """Загружает картинки астероидов из папки images/ и удаляет с них фон."""
        excluded = {
            'ship.png', 'ship.jpg', 'ship.jpeg',
            'ship_thrust.png', 'missile.png',
            'bg_static.png', 'bg_debris.png', 'splash.png', 'explosion.png'
        }
        sprites = []
        if os.path.exists('images'):
            for fname in sorted(os.listdir('images')):
                if fname.lower().endswith(('.png', '.jpg', '.jpeg')) and fname not in excluded:
                    try:
                        raw_img = Image.open(os.path.join('images', fname))
                        clean_img = self._remove_background_auto(raw_img)
                        clean_img = clean_img.resize(
                            (self.ASTEROID_SIZE, self.ASTEROID_SIZE),
                            Image.Resampling.LANCZOS,
                        )
                        sprites.append(clean_img)
                    except Exception as exc:
                        print(f'Не удалось загрузить {fname}: {exc}')

        if not sprites:
            img = Image.new('RGBA', (self.ASTEROID_SIZE, self.ASTEROID_SIZE), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.ellipse(
                (4, 4, self.ASTEROID_SIZE - 4, self.ASTEROID_SIZE - 4),
                fill='#888892', outline='#44444c', width=3,
            )
            sprites.append(img)

        return sprites

    def _create_nebula_bg(self, is_day=False):
        """Создает фон как на скриншотах 1-2 (Ночь — темный космос, День — розово-голубой с желтым)."""
        w, h = self.app.SCREEN_WIDTH, self.app.SCREEN_HEIGHT
        base_color = (245, 195, 225) if is_day else (10, 8, 18)
        bg = Image.new('RGBA', (w, h), base_color + (255,))

        # Слой мягких туманностей
        nebula = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        ndraw = ImageDraw.Draw(nebula)
        rng = random.Random(101 if is_day else 202)

        if is_day:
            cloud_colors = [
                (255, 130, 190, 130),  # Розовый
                (120, 210, 255, 135),  # Голубой
                (255, 235, 120, 125),  # Желтый
                (210, 160, 255, 115),  # Сиреневый
            ]
        else:
            cloud_colors = [
                (140, 45, 25, 115),    # Оранжево-красная туманность
                (35, 45, 125, 110),    # Темно-синяя туманность
                (95, 30, 75, 95),      # Фиолетовая дымка
                (160, 75, 35, 85),     # Теплое свечение
            ]

        for _ in range(38):
            cx = rng.randint(-80, w + 80)
            cy = rng.randint(-80, h + 80)
            rx = rng.randint(90, 230)
            ry = rng.randint(70, 180)
            col = rng.choice(cloud_colors)
            ndraw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=col)

        nebula = nebula.filter(ImageFilter.GaussianBlur(radius=38))
        bg = Image.alpha_composite(bg, nebula)

        # Яркая центральная звезда с лучами
        star_layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(star_layer)
        sx, sy = int(w * 0.46), int(h * 0.34)
        glow_col = (255, 250, 170, 160) if is_day else (90, 160, 255, 150)
        sdraw.ellipse((sx - 45, sy - 45, sx + 45, sy + 45), fill=glow_col)
        star_layer = star_layer.filter(ImageFilter.GaussianBlur(radius=16))
        bg = Image.alpha_composite(bg, star_layer)

        # Лучи и россыпь блесток / звезд
        draw = ImageDraw.Draw(bg)
        ray_col = (255, 255, 240, 220) if is_day else (200, 235, 255, 220)
        draw.line((sx - 42, sy, sx + 42, sy), fill=ray_col, width=2)
        draw.line((sx, sy - 42, sx, sy + 42), fill=ray_col, width=2)
        draw.ellipse((sx - 6, sy - 6, sx + 6, sy + 6), fill=(255, 255, 255, 255))

        sparkle_colors = (
            [(255, 255, 255), (255, 245, 130), (130, 230, 255), (255, 140, 210)]
            if is_day else
            [(255, 255, 255), (255, 110, 160), (110, 190, 255), (255, 220, 150)]
        )
        for _ in range(190):
            x = rng.randint(0, w)
            y = rng.randint(0, h)
            r = rng.choice((1, 2, 3))
            col = rng.choice(sparkle_colors)
            draw.ellipse((x - r, y - r, x + r, y + r), fill=col + (240,))
            if r >= 2 and rng.random() < 0.35:
                draw.line((x - 5, y, x + 5, y), fill=(255, 255, 255, 210), width=1)
                draw.line((x, y - 5, x, y + 5), fill=(255, 255, 255, 210), width=1)

        return ImageTk.PhotoImage(bg.convert('RGB'))

    def _create_debris_layer(self, asteroid_sprites):
        """Создает полупрозрачный слой из очищенных астероидов для движения влево."""
        w, h = self.app.SCREEN_WIDTH, self.app.SCREEN_HEIGHT
        layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        rng = random.Random(77)

        for _ in range(28):
            src = rng.choice(asteroid_sprites)
            sz = rng.randint(16, 34)
            mini = src.resize((sz, sz), Image.Resampling.LANCZOS)
            mini = mini.rotate(rng.randint(0, 360), expand=True)

            r, g, b, a = mini.split()
            a = a.point(lambda p: int(p * 0.45))
            mini = Image.merge('RGBA', (r, g, b, a))

            x = rng.randint(0, w - sz)
            y = rng.randint(0, h - sz)
            layer.paste(mini, (x, y), mini)

        return ImageTk.PhotoImage(layer)

    def _create_missile_sprite(self):
        """Создает спрайт ракеты."""
        img = Image.new('RGBA', (20, 8), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse((0, 1, 19, 7), fill='#ff3300')
        draw.ellipse((5, 2, 17, 6), fill='#ffff88')
        return img

    def _create_explosion_frames(self, is_day=False):
        """Создает 24 кадра анимации взрыва: темно-сине-фиолетовые для Дня и бело-желто-голубые для Ночи."""
        frames = []
        if is_day:
            outer_col = (45, 20, 130)
            mid_col = (120, 35, 185)
            core_col = (75, 95, 235)
        else:
            outer_col = (130, 215, 255)
            mid_col = (255, 240, 110)
            core_col = (255, 255, 255)

        for i in range(self.EXPLOSION_FRAMES):
            img = Image.new('RGBA', (self.EXPLOSION_SIZE, self.EXPLOSION_SIZE), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            progress = i / self.EXPLOSION_FRAMES
            max_r = self.EXPLOSION_SIZE // 2
            alpha = int(255 * (1.0 - progress))
            cx, cy = max_r, max_r

            r1 = int(max_r * (0.25 + 0.75 * progress))
            r2 = int(r1 * 0.72)
            r3 = int(r1 * 0.42)

            draw.ellipse((cx - r1, cy - r1, cx + r1, cy + r1), fill=outer_col + (alpha,))
            draw.ellipse((cx - r2, cy - r2, cx + r2, cy + r2), fill=mid_col + (alpha,))
            draw.ellipse((cx - r3, cy - r3, cx + r3, cy + r3), fill=core_col + (alpha,))
            frames.append(ImageTk.PhotoImage(img))

        return frames

    def _draw_rotated_sprite(self, pil_img, x, y, angle):
        """Поворачивает PIL-изображение по часовой стрелке и рисует по центру (x, y)."""
        rotated = pil_img.rotate(-angle, resample=Image.Resampling.BICUBIC, expand=True)
        tk_img = ImageTk.PhotoImage(rotated)
        self._tk_cache.append(tk_img)
        self.canvas.create_image(x, y, image=tk_img, anchor='center')

    def _draw_splash_screen(self):
        """Рисует футуристический голографический терминал запуска по центру экрана."""
        self.app.splash_tick = (getattr(self.app, 'splash_tick', 0) + 1) % 3600
        tick = self.app.splash_tick

        cx = self.app.SCREEN_WIDTH // 2
        cy = self.app.SCREEN_HEIGHT // 2
        hw = self.app.SPLASH_WIDTH // 2
        hh = self.app.SPLASH_HEIGHT // 2
        cut = 24  # Размер скошенных sci-fi углов

        is_day = self.app.theme == 'day'
        # Палитра терминала подстраивается под выбранный сектор (День или Ночь)
        panel_bg = '#1b0f2e' if is_day else '#091124'
        panel_inner = '#281545' if is_day else '#0d1b38'
        accent = '#ff55b8' if is_day else '#00f5d4'
        accent_alt = '#ffd166' if is_day else '#3a86ff'
        text_main = '#ffffff'

        # 1. Внешний светящийся контур со скошенными углами (восьмиугольник)
        outer_pts = [
            cx - hw + cut, cy - hh,
            cx + hw - cut, cy - hh,
            cx + hw, cy - hh + cut,
            cx + hw, cy + hh - cut,
            cx + hw - cut, cy + hh,
            cx - hw + cut, cy + hh,
            cx - hw, cy + hh - cut,
            cx - hw, cy - hh + cut,
        ]
        self.canvas.create_polygon(outer_pts, fill=panel_bg, outline=accent, width=3)

        # Внутренняя рамка с отступом
        pad = 8
        inner_pts = [
            cx - hw + cut + pad, cy - hh + pad,
            cx + hw - cut - pad, cy - hh + pad,
            cx + hw - pad, cy - hh + cut + pad,
            cx + hw - pad, cy + hh - cut - pad,
            cx + hw - cut - pad, cy + hh - pad,
            cx - hw + cut + pad, cy + hh - pad,
            cx - hw + pad, cy + hh - cut - pad,
            cx - hw + pad, cy - hh + cut + pad,
        ]
        self.canvas.create_polygon(inner_pts, fill=panel_inner, outline=accent_alt, width=1)

        # 2. Декоративные «ушки»-засечки по бокам терминала
        self.canvas.create_rectangle(cx - hw - 6, cy - 35, cx - hw + 2, cy + 35, fill=accent, outline='')
        self.canvas.create_rectangle(cx + hw - 2, cy - 35, cx + hw + 6, cy + 35, fill=accent, outline='')

        # 3. Верхняя строка телеметрии
        self.canvas.create_text(
            cx, cy - hh + 24,
            text='// ORBITAL DEFENSE SYSTEM v2.6 • SECTOR READY //',
            fill=accent_alt,
            font=('Consolas', 9, 'bold'),
        )

        # 4. Заголовок игры с неоновой тенью
        self.canvas.create_text(
            cx + 2, cy - hh + 56,
            text=self.app.GAME_TITLE,
            fill=accent,
            font=('Arial', 23, 'bold'),
        )
        self.canvas.create_text(
            cx, cy - hh + 54,
            text=self.app.GAME_TITLE,
            fill=text_main,
            font=('Arial', 23, 'bold'),
        )

        # 5. Живой голографический радар по центру с вращающимся кораблем
        radar_y = cy - 32
        r_outer = 46
        self.canvas.create_oval(
            cx - r_outer, radar_y - r_outer, cx + r_outer, radar_y + r_outer,
            outline=accent_alt, width=1, dash=(4, 4),
        )
        self.canvas.create_oval(
            cx - 30, radar_y - 30, cx + 30, radar_y + 30,
            outline=accent, width=1,
        )

        # Вращающийся луч сканера радара
        scan_rad = math.radians(tick * 4)
        lx = cx + math.cos(scan_rad) * r_outer
        ly = radar_y + math.sin(scan_rad) * r_outer
        self.canvas.create_line(cx, radar_y, lx, ly, fill=accent, width=2)

        # Вращающийся предпросмотр вашего шаттла в центре радара
        preview_angle = (tick * 1.5) % 360
        self._draw_rotated_sprite(self.ship_base_pil, cx, radar_y, preview_angle)

        # Подсказка по управлению по бокам от радара
        self.canvas.create_text(
            cx - 145, radar_y - 10,
            text='[ ◄ ► ] ROTATE\n[  ▲  ] THRUST',
            fill='#b8c4e0',
            font=('Consolas', 9),
            justify='left',
        )
        self.canvas.create_text(
            cx + 145, radar_y - 10,
            text='[ SPACE ] FIRE\n[  5x   ] TARGETS',
            fill='#b8c4e0',
            font=('Consolas', 9),
            justify='right',
        )

        # 6. Тактические тумблеры выбора сектора: ДЕНЬ / НОЧЬ
        selected = getattr(self.app, 'theme_selected', False)
        btn_y1, btn_y2 = cy + 30, cy + 68

        # Левый тумблер: ДЕНЬ
        day_active = selected and is_day
        day_fill = '#ff66c4' if day_active else '#141d38'
        day_outline = '#ffffff' if day_active else '#ff66c4'
        self.canvas.create_polygon(
            [cx - 200, btn_y1, cx - 15, btn_y1, cx - 25, btn_y2, cx - 210, btn_y2],
            fill=day_fill, outline=day_outline, width=2 if day_active else 1,
        )
        self.canvas.create_text(
            cx - 112, (btn_y1 + btn_y2) // 2,
            text='☀ DAY SECTOR (ДЕНЬ)',
            fill='#120724' if day_active else '#d0d8ff',
            font=('Arial', 10, 'bold'),
        )

        # Правый тумблер: НОЧЬ
        night_active = selected and not is_day
        night_fill = '#00b4d8' if night_active else '#141d38'
        night_outline = '#ffffff' if night_active else '#00b4d8'
        self.canvas.create_polygon(
            [cx + 15, btn_y1, cx + 200, btn_y1, cx + 210, btn_y2, cx + 25, btn_y2],
            fill=night_fill, outline=night_outline, width=2 if night_active else 1,
        )
        self.canvas.create_text(
            cx + 112, (btn_y1 + btn_y2) // 2,
            text='☾ NIGHT SECTOR (НОЧЬ)',
            fill='#04101e' if night_active else '#d0d8ff',
            font=('Arial', 10, 'bold'),
        )

        # 7. Главная кнопка запуска миссии (активна только после выбора темы)
        hover = getattr(self.app, 'hover_launch', False) and selected
        launch_y1, launch_y2 = cy + 88, cy + 138
        if selected:
            launch_fill = accent if hover else accent_alt
            launch_outline = '#ffffff'
            launch_text = '► INITIATE LAUNCH • НАЧАТЬ ИГРУ ◄'
            launch_text_col = '#090b1a'
        else:
            launch_fill = '#1b2440'
            launch_outline = '#4a5a80'
            launch_text = '⚠ SELECT SECTOR FIRST • ВЫБЕРИТЕ ТЕМУ ⚠'
            launch_text_col = '#8899bb'

        self.canvas.create_polygon(
            [
                cx - 160, launch_y1,
                cx + 160, launch_y1,
                cx + 175, (launch_y1 + launch_y2) // 2,
                cx + 160, launch_y2,
                cx - 160, launch_y2,
                cx - 175, (launch_y1 + launch_y2) // 2,
            ],
            fill=launch_fill,
            outline=launch_outline,
            width=2 if hover else 1,
        )
        self.canvas.create_text(
            cx, (launch_y1 + launch_y2) // 2,
            text=launch_text,
            fill=launch_text_col,
            font=('Arial', 11, 'bold'),
        )

    def draw(self):
        """Отрисовывает полный кадр игры."""
        self.canvas.delete('all')
        self._tk_cache.clear()

        is_day = self.app.theme == 'day'

        # 1. Неподвижный фон (День или Ночь)
        bg_img = self.bg_day_img if is_day else self.bg_night_img
        self.canvas.create_image(0, 0, image=bg_img, anchor='nw')

        # 2. Динамический фон: полупрозрачные астероиды движутся влево с постоянной скоростью
        self.debris_x = (self.debris_x - self.DEBRIS_SPEED) % self.app.SCREEN_WIDTH
        self.canvas.create_image(self.debris_x, 0, image=self.bg_debris_img, anchor='nw')
        self.canvas.create_image(
            self.debris_x - self.app.SCREEN_WIDTH, 0, image=self.bg_debris_img, anchor='nw'
        )

        # 3. Игровые объекты (рисуются ТОЛЬКО во время активной игры)
        if self.app.in_game:
            # Астероиды (5 штук)
            for ast in self.app.asteroids:
                if ast.image_index is None:
                    ast.image_index = random.randint(0, len(self.asteroid_pils) - 1)
                sprite = self.asteroid_pils[ast.image_index]
                self._draw_rotated_sprite(sprite, ast.x, ast.y, ast.angle)

            # Ракеты
            for missile in self.app.bullets:
                self._draw_rotated_sprite(self.missile_pil, missile.x, missile.y, missile.angle)

            # Корабль (с пламенем при ускорении)
            ship_sprite = (
                self.ship_thrust_pil if self.app.player.thrusting else self.ship_base_pil
            )
            self._draw_rotated_sprite(
                ship_sprite, self.app.player.x, self.app.player.y, self.app.player.angle
            )

            # Анимация взрывов (цвет зависит от Дня или Ночи)
            exp_frames = self.explosion_day_frames if is_day else self.explosion_night_frames
            for exp in self.app.explosions:
                if exp.current_frame < len(exp_frames):
                    self.canvas.create_image(
                        exp.x, exp.y,
                        image=exp_frames[exp.current_frame],
                        anchor='center',
                    )
        else:
            # 4. Заставка по центру экрана
            self._draw_splash_screen()

        # 5. Интерфейс: Жизни и Очки (контрастный цвет для Дня и Ночи)
        hud_color = '#1a0033' if is_day else '#00ff00'
        self.canvas.create_text(
            40, 25,
            text=f'Lives: {self.app.player.lives}',
            fill=hud_color,
            anchor='nw',
            font=('Arial', 20, 'bold'),
        )
        self.canvas.create_text(
            self.app.SCREEN_WIDTH - 40, 25,
            text=f'Score: {self.app.score}',
            fill=hud_color,
            anchor='ne',
            font=('Arial', 20, 'bold'),
        )
