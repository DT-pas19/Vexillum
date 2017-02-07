from typing import Tuple, List
import datetime
from playlist import Playlist
from song import Song

if __name__ == "__main__":
    songs = [
        Song("Привет, Москва!", "Александр Барабашев и Ночной Проспект", datetime.timedelta(minutes=3, seconds=15, milliseconds=590)),
        Song("На разных квартирах", "Александр Барабашев и Ночной Проспект", datetime.timedelta(minutes=2, seconds=12, milliseconds=310))
    ]

    play = Playlist("Александр Барабашев и Ночной Проспект.flac",
                    title="Привет, Москва!",
                    performer="Александр Барабашев и Ночной Проспект",
                    date=1987,
                    songs=songs)
    print(play)