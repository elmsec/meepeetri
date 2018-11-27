import sys
import re
import time
import logging
import threading
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from ui_meepeetri import Ui_Meepeetri

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG)

# create logger
logger = logging.getLogger(__name__)

# fh handler
fh = logging.FileHandler('all.log')
fh.setLevel(logging.INFO)
fh.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(fh)

MSG_URL_WARNING = (
    "Please check the URL field, it should contain a YouTube video URL that "
    "not used in this session before."
)


class Meepeetri:
    def __init__(self):
        self.tasks = dict()
        self.is_running = False

    def add_task(
            self, url, artist=None, title=None, album=None,
            embed_lyrics=None, embed_thumbnail=None):

        # Try to get the video ID from the URL
        video_id = self.get_video_id(url)

        # Create a new task if there is no such
        if (not video_id) or (video_id and video_id in self.tasks):
            logger.info(MSG_URL_WARNING)
            return

        task = dict(
            video_id=video_id,
            url=url,
            artist=artist,
            title=title,
            album=album,
            embed_thumbnail=embed_thumbnail,
            embed_lyrics=embed_lyrics,
            )
        # Add new task
        self.tasks.update({video_id: task})
        self.start_task(task)
        return 1

    def get_video_id(self, url):
        try:
            video_id = re.search('watch\\?v=([A-Za-z0-9_-]*)', url).group(1)
            return video_id
        except Exception:
            return

    def start_task(self, task):
        if self.is_running:
            pass
        else:
            job = threading.Thread(
                target=self.download_song, name=task['video_id'], args=(task,))
            job.start()

    def task_loop(self):
        pass

    def download_song(self, task):
        # IDEA:
        print('Download started for task {}!'.format(task['video_id']))
        time.sleep(3)
        print('Download finished for task {}'.format(task['video_id']))


class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Meepeetri()
        self.ui.setupUi(self)
        self.setWindowTitle('Meepeetri')

        # Definitions
        self.meepeetri = Meepeetri()

        # Boolean definition
        self.is_embed_lyrics, self.is_embed_thumbnail = [0]*2

        # Connect all signals
        self.connect_signals()

        # Show the app window
        self.show()

    def connect_signals(self):
        self.ui.add_button.pressed.connect(self.on_add_button)
        self.ui.embed_lyrics.stateChanged.connect(self.on_embed_lyrics)
        self.ui.embed_thumbnail.stateChanged.connect(self.on_embed_thumbnail)

    def show_message(self, title, text, icon=None):
        self.message_box = QMessageBox()
        self.message_box.setWindowTitle(title)
        self.message_box.setText(text)
        self.message_box.setIcon(icon)
        self.message_box.show()

    def update_task_list(self, tasks=None):
        if tasks is None:
            tasks = self.meepeetri.tasks

        task_list = list()
        for video_id, task in tasks.items():
            task_item = '{song_artist} - {song_title}'.format(
                song_artist=task['artist'], song_title=task['title']
            )

            if not task['artist'] or not task['title']:
                task_item = '{song_url}'.format(song_url=task['url'])

            task_list.append(task_item)
        self.ui.tasks.clear()
        self.ui.tasks.addItems(task_list)

    def on_add_button(self):
        add_task = self.meepeetri.add_task(
            url=self.ui.video_url.text(),
            artist=self.ui.song_artist.text(),
            title=self.ui.song_title.text(),
            album=self.ui.song_album.text(),
            embed_thumbnail=self.is_embed_thumbnail,
            embed_lyrics=self.is_embed_lyrics,
        )

        self.ui.video_url.clear()
        self.ui.song_title.clear()
        if not add_task:
            self.show_message(
                'Uh...', MSG_URL_WARNING, QMessageBox.Warning)
            return
        self.update_task_list()

    def on_embed_lyrics(self, is_checked):
        self.is_embed_lyrics = is_checked

    def on_embed_thumbnail(self, is_checked):
        self.is_embed_thumbnail = is_checked


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = AppWindow()
    w.show()
    sys.exit(app.exec_())
