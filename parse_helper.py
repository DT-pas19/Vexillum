import re
from typing import List, Tuple, Dict

import audio_helper
from Entities.song import *

time_re = re.compile(r'((?P<hours>\d{1,2}):)?(?P<minutes>\d{1,2}):(?P<seconds>\d{1,2})')
pattern_re = re.compile(r'(%\{track|artist|title|duration\}(?P<delim>[ .-/]))*')


def parse_tracks(file_path: str, pattern: str, track_list: str, general_artist: str='') -> List[Tuple[str, Song]]:
    tracks = track_list.split('\n')
    pattern_info = parse_pattern(pattern)
    songs = []
    tmp_info_list = []

    for track in tracks:
        track = track.strip()
        if track == str():
            continue
        track_info = parse_track(pattern_info, track)
        if track_info == dict():
            continue
        if track_info.get("artist", None) is None:
            track_info["artist"] = general_artist
        tmp_info_list.append(track_info)

    timestamp_marker = timedelta(0)
    # if has_timestamp:
    #     tmp_info_list.append({"timestamp": audio_helper.get_audio_length(file_path)})
    for index in range(len(tmp_info_list)):
        track_info = tmp_info_list[index]
        track_number = track_info.get("track", 0)
        if track_number != 0:
            track_info.pop("track")

        if "timestamp" in track_info.keys():
            if index < len(tmp_info_list) - 1:
                duration = tmp_info_list[index + 1].get("timestamp") - track_info["timestamp"]
            else:
                duration = timedelta(0)
            if duration < timedelta(0):
                duration = timedelta(0)
            track_info["duration"] = duration
        elif "duration" in track_info.keys():
            track_info["timestamp"] = timestamp_marker
            timestamp_marker += track_info["duration"]

        songs.append((track_number, Song(**track_info)))
    return songs


def parse_track(pattern: List[Tuple[str, str]], track: str) -> Dict[str, str or timedelta]:
    """
    Parses track according to pattern
    :param pattern: шаблон, обработанный функцией parse_track()
    :param track: наименование
    :return:
    """
    # TODO parse w/out dots - "3. Timing X 04:02" & "%{track}. %{title} %{timestamp}",
    # TODO parsing with misc symbols '1. "CCCP"   2:21'

    i = 0
    block_index = 0
    song_info = {}
    while i < len(track):
        if pattern[block_index] in ["track", "artist", "title", "duration", "timestamp"]:
            if len(pattern) - 1 == block_index:
                ind = len(track)
            else:
                delim = pattern[block_index + 1]
                ind = track[i:].find(delim)

            if i != -1:
                tag = track[i: i + ind].strip()
            else:
                tag = track[i:]
            if pattern[block_index] == "duration" or pattern[block_index] == "timestamp":
                time_piece_span = time_re.search(tag).span()
                if time_piece_span[0] > 0:
                    pre_tag = tag[:time_piece_span[0]]
                    prev_tag_type = pattern[block_index - 2]
                    prev_delim = pattern[block_index - 1]
                    song_info[prev_tag_type] += prev_delim + pre_tag
                    song_info[prev_tag_type] = song_info[prev_tag_type].strip()
                    tag = tag[time_piece_span[0]:time_piece_span[1]]
                    ind = len(tag)
                tag = parse_time(tag)
            song_info[pattern[block_index]] = tag
            i += ind + len(delim)
        block_index += 1
        if block_index >= len(pattern):
            break
    return song_info


def parse_pattern(pattern: str) -> List[Tuple[str, str]]:
    track_i = []
    i = 0
    while i < len(pattern):
        if pattern[i] == "%":
            sub_index = pattern[i:].find("}")
            sub = pattern[i + 2: i + sub_index]
            track_i.append(sub)
            track_i.append('')
            i += sub_index + 1
        else:
            track_i[-1] += pattern[i]
            i += 1
    track_i = list(filter(lambda x: x != '', track_i))
    # for track_ipiece in track_i:
    #     is_consisted_of_spaces = (True for s in set(track_ipiece) if str.isspace(s))
    #     if any(is_consisted_of_spaces):
    #         track_ipiece = track_ipiece.strip()
    #     if track_ipiece == str():
    #         track_i.remove(track_ipiece)
    return track_i


def parse_time(val: str)-> timedelta:
    """
    Parses time string
    :param val:
    :return:

    >>> parse_time("08:10")
    timedelta(minutes=8, seconds=10)
    """
    parts = time_re.match(val)
    if not parts:
        return timedelta()
    parts = parts.groupdict()
    time_parts = {}
    for name, param in parts.items():
        if param:
            time_parts[name] = int(param)
    return timedelta(**time_parts)


def timedelta_str(td: timedelta) -> str:
    minutes = (td.seconds - td.seconds % 60) / 60
    hours = minutes / 60
    timespan = {
        'seconds': int(td.seconds % 60),
        'minutes': int(minutes % 60),
        'hours': int(hours)
    }
    result = '{0[hours]:02}:{0[minutes]:02}:{0[seconds]:02}'.format(timespan)
    return result
