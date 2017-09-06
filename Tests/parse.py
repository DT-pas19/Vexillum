import unittest

from datetime import timedelta

from Entities.song import Song
from parse_helper import timedelta_str, parse_time, parse_track, parse_pattern, parse_tracks


class ParserTestCase(unittest.TestCase):
    def test_timedelta_to_str_conversion(self):
        to_str_cases = [
            (timedelta(seconds=20), '00:00:20'),
            (timedelta(seconds=60), '00:01:00'),
            (timedelta(minutes=2, seconds=20), '00:02:20'),
            (timedelta(seconds=183), '00:03:03'),
            (timedelta(hours=1, seconds=20), '01:00:20')
        ]
        [self.assertEqual(timedelta_str(case[0]), case[1]) for case in to_str_cases]

    def test_timedelta_from_str_convention(self):
        from_str_cases = [
            ('00:00:20', timedelta(seconds=20)),
            ('00:01:00', timedelta(seconds=60)),
            ('00:02:20', timedelta(minutes=2, seconds=20)),
            ('00:03:03', timedelta(seconds=183)),
            ('01:00:20', timedelta(hours=1, seconds=20)),
            ('08:10', timedelta(minutes=8, seconds=10)),
            ('68:15', timedelta(hours=1, minutes=8, seconds=15)),
        ]
        [self.assertEqual(parse_time(case[0]), case[1]) for case in from_str_cases]

    def test_parse_track(self):
        patterns = [
            "%{artist} - %{track} %{title} - %{duration}",
            "%{artist} - %{track} %{title} - %{timestamp}",
            "%{track} %{title} - %{duration}",
            "%{track} %{title} - %{timestamp}",
            "%{track}. %{title}",
            "%{track} - %{title}",
            "%{track}. %{title}. %{duration}",
            "%{track} - %{artist} - %{title}",
        ]
        pattern_infos = [parse_pattern(pattern) for pattern in patterns]
        case_1 = parse_track(pattern_infos[-1], "02 - Bajaga - Mali Slonovi")
        case_2 = parse_track(pattern_infos[4], "02. Vitosha")
        case_3 = parse_track(pattern_infos[5], "02 - Vitosha")
        self.assertEqual(case_1, dict(track='02', artist='Bajaga', title='Mali Slonovi'))
        self.assertEqual(case_2, dict(track='02', title= 'Vitosha'))
        self.assertEqual(case_3, dict(track='02', title='Vitosha'))

        track_list = '1. Hoćemo Cenzuru. 3:05\n' \
                     '2. Vajk Na Bolje. 2:31\n' \
                     '3. Preživjeti (We Remember Marjeto). 2:38'
        case_4 = parse_tracks('', patterns[-2], track_list)
        case_5 = parse_tracks('', patterns[-2], track_list, 'KUD Idijoti')

        results = [
            ('1', Song('Hoćemo Cenzuru', '', timedelta(minutes=3, seconds=5))),
            ('2', Song('Vajk Na Bolje', '', timedelta(minutes=2, seconds=31))),
            ('3', Song('Preživjeti (We Remember Marjeto)', '', timedelta(minutes=2, seconds=38))),
        ]
        self.assertEqual(case_4, results)
        for r in results:
            r[1].performer = 'KUD Idijoti'
        self.assertEqual(case_5, results)

    def test_pattern_parsing_cases(self):
        patterns = [
            "%{track}. %{title} %{timestamp}",
            "%{track}. \"%{title}\" %{timestamp}",
            "%{artist} - %{track} %{title} - %{duration}",
            "%{artist} - %{track} %{title} - %{timestamp}",
            "%{track} %{title} - %{duration}",
            "%{track} %{title} - %{timestamp}",
            "%{track}. %{title}",
            "%{track} - %{title}",
            "%{track}. %{title}. %{duration}",
            "%{track} - %{artist} - %{title}",
        ]
        pattern_infos = [parse_pattern(pattern) for pattern in patterns]
        expected_results = [
            ['track', '. ', 'title', ' ', 'timestamp'],
            ['track', '. "', 'title', '" ', 'timestamp'],
            ['artist', ' - ', 'track', ' ', 'title', ' - ', 'duration'],
            ['artist', ' - ', 'track', ' ', 'title', ' - ', 'timestamp'],
            ['track', ' ', 'title', ' - ', 'duration'],
            ['track', ' ', 'title', ' - ', 'timestamp'],
            ['track', '. ', 'title'],
            ['track', ' - ', 'title'],
            ['track', '. ', 'title', '. ', 'duration'],
            ['track', ' - ', 'artist', ' - ', 'title']]

        [self.assertEqual(exp, case) for case, exp in zip(pattern_infos, expected_results)]

    def test_parse_odd_cases(self):
        patterns = [
            "%{track}. %{title} %{timestamp}",
            "%{track}. \"%{title}\" %{timestamp}",
        ]
        pattern_infos = [parse_pattern(pattern) for pattern in patterns]
        case_1 = parse_track(pattern_infos[0], '3. Timing X 04:02')
        case_2 = parse_track(pattern_infos[1], '1. "CCCP"   2:21')
        case_3 = parse_track(pattern_infos[0], '2. Clockout 01:15')
        case_4 = parse_track(pattern_infos[1], '3. "Mi Ami? (Remiscelata)"   2:48')
        self.assertEqual(case_1, dict(track='3', title='Timing X', timestamp=timedelta(minutes=4, seconds=2)))
        self.assertEqual(case_2, dict(track='1', title='CCCP', timestamp=timedelta(minutes=2, seconds=21)))
        self.assertEqual(case_3, dict(track='2', title='Clockout', timestamp=timedelta(minutes=1, seconds=15)))
        self.assertEqual(case_4, dict(track='3', title='Mi Ami? (Remiscelata)', timestamp=timedelta(minutes=2, seconds=48)))

    def test_blank_lines_behaviour(self):
        case = "1. Devo Corporate Anthem 00:00\n" \
               "2. Clockout 01:15\n" \
               "\n" \
               "11. Secret Agent Man 26:27\n" \
               "\n"
        pattern = '%{track}. %{title} %{timestamp}'
        results = parse_tracks('', pattern, case, 'DEVO')

        expected_results = [
            ('1', Song('Devo Corporate Anthem', 'DEVO', duration=timedelta(minutes=1, seconds=15))),
            ('2', Song('Clockout', 'DEVO', duration=timedelta(minutes=25, seconds=12))),
            ('11', Song('Secret Agent Man', 'DEVO', duration=timedelta(seconds=0))),
        ]
        self.assertEqual(expected_results, results)


if __name__ == '__main__':
    unittest.main()
