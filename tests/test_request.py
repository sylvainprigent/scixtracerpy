import unittest
import os
import os.path
import filecmp

from scixtracerpy import Request
from scixtracerpy.serialize import serialize_experiment
from tests.metadata import create_experiment


class TestRequest(unittest.TestCase):
    def setUp(self):
        self.request = Request()
        self.ref_experiment_uri = \
            os.path.join('tests', 'test_metadata_local', 'experiment.md.json')

    def tearDown(self):
        pass

    def test_get_experiment(self):
        experiment = self.request.get_experiment(self.ref_experiment_uri)
        ref_experiment = create_experiment()

        print(serialize_experiment(experiment))
        print(serialize_experiment(ref_experiment))

        self.assertEqual(serialize_experiment(experiment),
                         serialize_experiment(ref_experiment))
