import pydub
import os
import datetime


def get_audio_length(track_path: str) -> datetime.timedelta:
    """
    Returns length of an audio file
    :param track_path: path to file
    :return: length given in timedelta structure
    """
    exists = isinstance(track_path, str) and os.path.exists(track_path) and os.path.isfile(track_path)
    if not exists:
        return datetime.timedelta()
    track = pydub.AudioSegment.from_file(track_path)
    return datetime.timedelta(milliseconds=len(track))
