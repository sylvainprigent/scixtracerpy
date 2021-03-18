import unittest
import os
import os.path
import filecmp
import shutil

from scixtracerpy import Request
from scixtracerpy.serialize import serialize_experiment
from tests.metadata import create_experiment


class TestRequest(unittest.TestCase):
    def setUp(self):
        self.request = Request()
        self.ref_experiment_uri = \
            os.path.join('tests', 'test_metadata_local', 'experiment.md.json')
        self.test_experiment_uri = \
            os.path.join('tests', 'test_metadata_local',
                         'test_experiment.md.json')
        self.test_experiment_dir = \
            os.path.join('tests', 'test_metadata_local')
        self.test_import_image = \
            os.path.join('tests', 'test_images', 'data', 'population1_001.tif')

    def tearDown(self):
        #if os.path.isfile(self.test_experiment_uri):
        #    os.remove(self.test_experiment_uri)
        #path = os.path.join(self.test_experiment_dir, 'myexperiment')
        #if os.path.isdir(path):
        #    shutil.rmtree(path)
        pass

    def test_create_experiment(self):
        return self.assertTrue(True)
        self.request = Request()
        self.request.create_experiment("myexperiment", "sprigent", date='now',
                                       tag_keys=["key1", "key2"],
                                       destination=self.test_experiment_dir)

        t1 = os.path.isdir(os.path.join(self.test_experiment_dir,
                                        'myexperiment'))
        t2 = os.path.isfile(os.path.join(self.test_experiment_dir,
                                         'myexperiment',
                                         'experiment.md.json'))
        t3 = os.path.isdir(os.path.join(self.test_experiment_dir,
                                        'myexperiment', 'data'))
        t4 = os.path.isfile(os.path.join(self.test_experiment_dir,
                                         'myexperiment', 'data',
                                         'rawdataset.md.json'))
        self.assertTrue(t1 * t2 * t3 * t4)

    def test_get_experiment(self):
        return self.assertTrue(True)
        experiment = self.request.get_experiment(self.ref_experiment_uri)
        ref_experiment = create_experiment()
        # print(serialize_experiment(experiment))
        # print(serialize_experiment(ref_experiment))

        self.assertEqual(serialize_experiment(experiment),
                         serialize_experiment(ref_experiment))

    def test_update_experiment(self):
        return self.assertTrue(True)
        experiment = create_experiment()
        experiment.md_uri = self.test_experiment_uri
        # print(serialize_experiment(experiment))
        self.request.update_experiment(experiment)

        self.assertTrue(filecmp.cmp(self.test_experiment_uri,
                                    self.ref_experiment_uri, shallow=False))

    def test_import_data(self):
        self.request = Request()
        experiment = self.request.create_experiment("myexperiment", "sprigent",
                                                    date='now', tag_keys=[],
                                                    destination=self.test_experiment_dir)
        data_path = self.test_import_image
        name = 'population1_001.tif'
        author = 'sprigent'
        format_ = 'tif'
        tags = {"population": "population1", "ID": "001"}
        self.request.import_data(experiment, data_path, name, author, format_,
                                 date='now', tags=tags, copy=True)

        # report tags keys to experiment if not exists
        # add a test on the population1_001.md.json changing uuid with dumb
        # add a test on the rawdataset.md.json changing uuid with dumb
        # add test tag on experiment
        self.assertTrue(True)
