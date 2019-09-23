import unittest
from time import sleep

from ox_profile.core.launchers import SimpleLauncher


def one_second_running_function():
    sleep(1)


def three_seconds_running_function():
    sleep(3)


class OxProfileIntegrationTestCase(unittest.TestCase):

    def test_simple_launcher_sampler_query(self):
        launcher = SimpleLauncher(interval=.001)
        launcher.start()
        launcher.unpause()

        one_second_running_function()

        launcher.is_alive()
        launcher.cancel()
        query, total_records = launcher.sampler.my_db.query(max_records=None)
        self.assertGreater(total_records, 0)

        query_result = [(i.name, i.hits) for i in query if "one_second_running_function" in i.name]
        self.assertEqual(len(query_result), 1)
        name, hits = query_result.pop()
        self.assertGreater(hits, 0)

    def test_simple_launcher_sampler_query_calls(self):
        launcher = SimpleLauncher(interval=.001)
        launcher.start()
        launcher.unpause()

        one_second_running_function()
        three_seconds_running_function()

        launcher.is_alive()
        launcher.cancel()
        query, total_records = launcher.sampler.my_db.query(max_records=None)
        self.assertGreater(total_records, 0)

        one_second_running_function_result = next(
            ((i.name, i.hits) for i in query if "one_second_running_function" in i.name), None
        )
        three_seconds_running_function_result = next(
            ((i.name, i.hits) for i in query if "three_seconds_running_function" in i.name), None
        )

        self.assertIsNotNone(one_second_running_function_result)
        self.assertIsNotNone(three_seconds_running_function_result)
        one_second_running_function_calls = one_second_running_function_result[1]
        three_seconds_running_function_calls = three_seconds_running_function_result[1]
        self.assertGreater(three_seconds_running_function_calls, one_second_running_function_calls)


if __name__ == '__main__':
    unittest.main()
