# -*- coding: utf-8 -*-
"""SciXtracer request local.

Local implementation of the request service

Classes
-------
LocalRequest

"""

import os
import json


class RequestLocalServiceBuilder:
    """Service builder for the metadata service"""

    def __init__(self):
        self._instance = None

    def __call__(self, **_ignored):
        if not self._instance:
            self._instance = LocalRequestService()
        return self._instance


class LocalRequestService:
    """Service for local metadata management"""

    def __init__(self):
        self.service_name = 'LocalMetadataService'

    @staticmethod
    def _read_json(md_uri: str):
        """Read the metadata from the a json file"""
        if os.path.getsize(md_uri) > 0:
            with open(md_uri) as json_file:
                return json.load(json_file)

    @staticmethod
    def _write_json(metadata: dict, md_uri: str):
        """Write the metadata to the a json file"""
        with open(md_uri, 'w') as outfile:
            json.dump(metadata, outfile, indent=4)

    def create_experiment(self, name, author, date='now', tag_keys=[],
                          destination=''):
        """Create a new experiment

        Parameters
        ----------
        name: str
            Name of the experiment
        author: str
            username of the experiment author
        date: str
            Creation date of the experiment
        tag_keys: list
            List of keys used for the experiment vocabulary
        destination: str
            Destination where the experiment is created. It is a the path of the
            directory where the experiment will be created for local use case

        Returns
        -------
        Experiment container with the experiment metadata
        """

        return None

    def get_experiment(self, uri):
        """Read an experiment from the database

        Parameters
        ----------
        uri: str
            URI of the experiment. For local use case, the URI is either the
            path of the experiment directory, or the path of the
            experiment.md.json file

        Returns
        -------
        Experiment container with the experiment metadata
        """

        return None

    def update_experiment(self, experiment):
        """Write an experiment to the database

        Parameters
        ----------
        experiment: Experiment
            Container of the experiment metadata
        """

        return None

    def import_data(self, experiment, data_path, name, author, format_,
                    date='now', tags=dict, copy=True):
        """import one data to the experiment

        The data is imported to the rawdataset

        Parameters
        ----------
        experiment: Experiment
            Container of the experiment metadata
        data_path: str
            Path of the accessible data on your local computer
        name: str
            Name of the data
        author: str
            Person who created the data
        format_: str
            Format of the data (ex: tif)
        date: str
            Date when the data where created
        tags: dict
            Dictionary {key:value, key:value} of tags
        copy: bool
            True to copy the data to the Experiment database
            False otherwise

        Returns
        -------
        class RawData containing the metadata

        """

    def get_rawdata(self, uri):
        """Read a raw data from the database

        Parameters
        ----------
        uri: str
            URI if the rawdata

        Returns
        -------
        RawData object containing the raw data metadata
        """

        return None

    def update_rawdata(self, rawdata):
        """Read a raw data from the database

        Parameters
        ----------
        rawdata: RawData
            Container with the rawdata metadata
        """

        pass

    def get_processeddata(self, uri):
        """Read a processed data from the database

        Parameters
        ----------
        uri: str
            URI if the processeddata

        Returns
        -------
        ProcessedData object containing the raw data metadata
        """

        return None

    def update_processeddata(self, processeddata):
        """Read a processed data from the database

        Parameters
        ----------
        processeddata: ProcessedData
            Container with the processeddata metadata
        """

        pass

    def get_dataset(self, uri):
        """Read a dataset from the database using it URI

        Parameters
        ----------
        uri: str
            URI if the dataset

        Returns
        -------
        Dataset object containing the dataset metadata
        """

        return None

    def update_dataset(self, dataset):
        """Read a processed data from the database

        Parameters
        ----------
        dataset: Dataset
            Container with the dataset metadata
        """

        pass

    def create_dataset(self, experiment, dataset_name):
        """Create a processed dataset in an experiment

        Parameters
        ----------
        experiment: Experiment
            Object containing the experiment metadata
        dataset_name: str
            Name of the dataset

        Returns
        -------
        Dataset object containing the new dataset metadata

        """

        return None

    def create_run(self, dataset, run_info):
        """Create a new run metadata

        Parameters
        ----------
        dataset: Dataset
            Object of the dataset metadata
        run_info: Run
            Object containing the metadata of the run. md_uri is ignored and
            created automatically by this method

        Returns
        -------
        Run object with the metadata and the new created md_uri
        """

        return None

    def create_data(self, dataset, processed_data):
        """Create a new processed data for a given dataset

        Parameters
        ----------
        dataset: Dataset
            Object of the dataset metadata
        processed_data: ProcessedData
            Object containing the new processed data. md_uri is ignored and
            created automatically by this method

        Returns
        -------
        ProcessedData object with the metadata and the new created md_uri
        """

        return None