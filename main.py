"""Точка входа в игру «airplane good game»."""
from src.app import App


def main():
    """Создает экземпляр приложения и запускает игровой цикл."""
    app = App()
    app.run()


if __name__ == '__main__':
    main()
