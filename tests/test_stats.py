import unittest

from main import demo_records, make_roast, player_record, summarize


class TestRiftRoast(unittest.TestCase):
    def test_stats(self):
        summary = summarize(demo_records())
        self.assertEqual(summary["played"], 5)
        self.assertEqual(summary["win_rate"], 20)
        self.assertAlmostEqual(summary["avg_deaths"], 9)
        self.assertAlmostEqual(summary["kda"], 54 / 45)

    def test_player_record(self):
        match = {"info": {"participants": [
            {"puuid": "someone_else", "kills": 0},
            {"puuid": "mine", "championName": "Ashe", "win": True,
             "kills": 4, "deaths": 2, "assists": 9}
        ]}}
        self.assertEqual(player_record(match, "mine")["champion"], "Ashe")
        self.assertIsNone(player_record(match, "missing"))

    def test_zero_deaths(self):
        summary = summarize([{"champion": "Lux", "win": True,
                              "kills": 10, "deaths": 0, "assists": 5}])
        self.assertIsNone(summary["kda"])
        self.assertIsInstance(make_roast(summary), str)


if __name__ == "__main__":
    unittest.main()
