"""
Auto Sort Script

Автоматический скрипт для сортировки файлов в папке Downloads по типам.
Использует библиотеку watchdog для мониторинга файловой системы в реальном времени.
"""

import os
import time
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Конфигурация
DOWNLOADS_DIR = os.path.expanduser("~/Downloads")
EXTENSION_MAP = {
    "Images": (".jpg", ".jpeg", ".png", ".gif", ".svg", ".bmp", ".webp"),
    "Documents": (".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx", ".csv"),
    "Archives": (".zip", ".rar", ".7z", ".tar", ".gz"),
    "Video": (".mp4", ".mov", ".avi", ".mkv", ".wmv"),
    "Audio": (".mp3", ".wav", ".flac", ".m4a"),
    "Executables": (".exe", ".msi", ".dmg"),
}


class SortingHandler(FileSystemEventHandler):
    """
    Обработчик событий файловой системы для автоматической сортировки файлов.

    Наследуется от FileSystemEventHandler и обрабатывает события изменения
    в папке Downloads, автоматически сортируя файлы по категориям.
    """

    def on_modified(self, event):
        """
        Обработчик события изменения файла или директории.

        Args:
            event: Событие файловой системы от watchdog
        """
        if not event.is_directory:
            self.sort_files()

    def sort_files(self):
        """
        Сортирует все файлы в папке Downloads по соответствующим категориям.

        Пропускает директории и скрытые файлы (начинающиеся с точки).
        """
        for filename in os.listdir(DOWNLOADS_DIR):
            file_path = os.path.join(DOWNLOADS_DIR, filename)
            if os.path.isdir(file_path) or filename.startswith('.'):
                continue
            self.move_file(filename, file_path)

    def get_unique_path(self, target_dir, filename):
        """
        Создает уникальное имя файла, если файл с таким именем уже существует.

        Если файл существует, добавляет номер в скобках перед расширением.
        Например: image.jpg -> image(1).jpg -> image(2).jpg

        Args:
            target_dir (str): Целевая директория для файла
            filename (str): Имя файла

        Returns:
            str: Уникальный путь к файлу
        """
        base, extension = os.path.splitext(filename)
        counter = 1
        unique_path = os.path.join(target_dir, filename)

        while os.path.exists(unique_path):
            unique_filename = f"{base}({counter}){extension}"
            unique_path = os.path.join(target_dir, unique_filename)
            counter += 1

        return unique_path

    def move_file(self, filename, file_path):
        """
        Перемещает файл в соответствующую категорию на основе его расширения.

        Определяет категорию файла по расширению из EXTENSION_MAP,
        создает целевую директорию если её нет, и перемещает файл.
        Обрабатывает дубликаты, создавая уникальные имена.

        Args:
            filename (str): Имя файла
            file_path (str): Полный путь к файлу
        """
        extension = os.path.splitext(filename)[1].lower()

        for folder_name, extensions in EXTENSION_MAP.items():
            if extension in extensions:
                target_dir = os.path.join(DOWNLOADS_DIR, folder_name)

                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)

                # Получаем уникальный путь (с учетом дубликатов)
                final_destination = self.get_unique_path(target_dir, filename)

                try:
                    # Небольшая пауза, чтобы файл полностью записался на диск
                    time.sleep(1)
                    shutil.move(file_path, final_destination)
                    print(f"Перемещен: {filename} -> {os.path.basename(final_destination)}")
                except Exception as e:
                    print(f"Ошибка при перемещении {filename}: {e}")
                break


def main():
    """
    Основная функция для запуска мониторинга папки Downloads.

    Создает обработчик событий и наблюдатель, запускает мониторинг
    до получения сигнала прерывания (Ctrl+C).
    """
    event_handler = SortingHandler()
    observer = Observer()
    observer.schedule(event_handler, DOWNLOADS_DIR, recursive=False)

    print(f"Мониторинг запущен в: {DOWNLOADS_DIR}")
    print("Логика обработки дубликатов: ВКЛЮЧЕНА")
    print("Для остановки нажмите Ctrl+C\n")

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nОстановка мониторинга...")
        observer.stop()
    observer.join()
    print("Мониторинг остановлен.")


if __name__ == "__main__":
    main()