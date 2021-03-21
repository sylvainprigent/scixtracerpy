# -*- coding: utf-8 -*-
"""SciXtracer request.

This module implements the request to query the database

Classes
-------
Request

"""

import os
import re
from .utils import Observable, SciXtracerError, format_date
from .factory import requestServices
from .containers import (Experiment, RawData, ProcessedData, Dataset,
                         METADATA_TYPE_RAW)
from .query import SearchContainer, query_list_single


class Request(Observable):
    """Implements the requests to the database

    """
    def __init__(self):
        Observable.__init__(self)
        self.service = requestServices.get("LOCAL")

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

        return self.service.create_experiment(name, author, format_date(date),
                                              tag_keys, destination)

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

        return self.service.get_experiment(uri)

    def update_experiment(self, experiment):
        """Write an experiment to the database

        Parameters
        ----------
        experiment: Experiment
            Container of the experiment metadata
        """

        self.service.update_experiment(experiment)

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

        return self.service.import_data(experiment, data_path, name, author,
                                        format_, format_date(date), tags, copy)

    def import_dir(self, experiment, dir_uri, filter_, author, format_, date,
                   copy_data):
        """Import data from a directory to the experiment

        This method import with or without copy data contained
        in a local folder into an experiment. Imported data are
        considered as RawData for the experiment

        Parameters
        ----------
        experiment: Experiment
            Container of the experiment metadata
        dir_uri: str
            URI of the directory containing the data to be imported
        filter_: str
            Regular expression to filter which files in the folder
            to import
        author: str
            Name of the person who created the data
        format_: str
            Format of the image (ex: tif)
        date: str
            Date when the data where created
        copy_data: bool
            True to copy the data to the experiment, false otherwise. If the
            data are not copied, an absolute link to dir_uri is kept in the
            experiment metadata. The original data directory must then not be
            changed for the experiment to find the data.
        """

        files = os.listdir(dir_uri)
        count = 0
        for file in files:
            count += 1
            r1 = re.compile(filter_)  # re.compile(r'\.tif$')
            if r1.search(file):
                self.notify_observers(int(100 * count / len(files)), file)
                data_url = os.path.join(dir_uri, file)
                self.import_data(experiment, data_url, file, author, format_,
                                 date, {}, copy_data)

    def tag_from_name(self, experiment, tag, values):
        """Tag an experiment raw data using raw data file names

        Parameters
        ----------
        experiment: Experiment
            Container of the experiment metadata
        tag: str
            The name (or key) of the tag to add to the data
        values: list
            List of possible values (str) for the tag to find in the filename
        """

        experiment.set_tag_key(tag)
        self.update_experiment(experiment)
        _rawdataset = self.get_rawdataset(experiment)
        for uri in _rawdataset.uris:
            _rawdata = self.get_rawdata(uri.md_uri)
            for value in values:
                if value in _rawdata.name:
                    _rawdata.set_tag(tag, value)
                    self.update_rawdata(_rawdata)
                    break

    def tag_using_separator(self, experiment, tag, separator, value_position):
        """Tag an experiment raw data using file name and separator

        Parameters
        ----------
        experiment: Experiment
            Container of the experiment metadata
        tag: str
            The name (or key) of the tag to add to the data
        separator: str
            The character used as a separator in the filename (ex: _)
        value_position: int
            Position of the value to extract with respect to the separators
        """

        experiment.set_tag_key(tag)
        self.update_experiment(experiment)
        _rawdataset = self.get_rawdataset(experiment)
        for uri in _rawdataset.uris:
            _rawdata = self.get_rawdata(uri.md_uri)
            basename = os.path.splitext(os.path.basename(_rawdata.uri))[0]
            splited_name = basename.split(separator)
            value = ''
            if len(splited_name) > value_position:
                value = splited_name[value_position]
            _rawdata.set_tag(tag, value)
            self.update_rawdata(_rawdata)

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

        return self.service.get_rawdata(uri)

    def update_rawdata(self, rawdata):
        """Read a raw data from the database

        Parameters
        ----------
        rawdata: RawData
            Container with the rawdata metadata
        """

        self.service.update_rawdata(rawdata)

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

        return self.service.get_processeddata(uri)

    def update_processeddata(self, processeddata):
        """Read a processed data from the database

        Parameters
        ----------
        processeddata: ProcessedData
            Container with the processeddata metadata
        """

        self.service.update_processeddata(processeddata)

    def get_dataset_from_uri(self, uri):
        """Read a dataset from the database using it URI

        Parameters
        ----------
        uri: str
            URI if the dataset

        Returns
        -------
        Dataset object containing the dataset metadata
        """

        return self.service.get_dataset(uri)

    def update_dataset(self, dataset):
        """Read a processed data from the database

        Parameters
        ----------
        dataset: Dataset
            Container with the dataset metadata
        """

        self.service.update_dataset(dataset)

    def get_rawdataset(self, experiment):
        """Read the raw dataset from the database

        Parameters
        ----------
        experiment: Experiment
            Container of the experiment metadata

        Returns
        -------
        Dataset object containing the dataset metadata

        """
        return self.get_dataset_from_uri(experiment.rawdataset.url)

    def get_parent(self, processeddata):
        """Get the metadata of the parent data.

        The parent data can be a RawData or a ProcessedData
        depending on the process chain

        Parameters
        ----------
        processeddata: ProcessedData
            Container of the processed data URI

        Returns
        -------
        parent
            Parent data (RawData or ProcessedData)

        """

        if len(processeddata.inputs) > 0:
            if processeddata.inputs[0].type == METADATA_TYPE_RAW():
                return self.get_rawdata(processeddata.inputs[0].uri)
            else:
                return self.get_processeddata(processeddata.inputs[0].uri)
        return None

    def get_origin(self, processed_data):
        """Get the first metadata of the parent data.

        The origin data is a RawData. It is the first data that have
        been seen in the raw dataset

        Parameters
        ----------
        processeddata: ProcessedData
            Container of the processed data URI

        Returns
        -------
        the origin data in a RawData object
        """

        if len(processed_data.inputs) > 0:
            if processed_data.inputs[0].type == METADATA_TYPE_RAW():
                return self.get_rawdata(processed_data.inputs[0].uri)
            else:
                return self.get_origin(
                           self.get_processeddata(processed_data.inputs[0].uri))

    def get_dataset(self, experiment, name):
        """Query a dataset from it name

        Parameters
        ----------
        experiment: Experiment
            Object containing the experiment metadata
        name: str
            Name of the dataset to query

        Returns
        -------
        a Dataset containing the dataset metadata. None is return if the dataset
        is not found
        """

        if name == 'data':
            return self.get_dataset_from_uri(experiment.rawdataset.url)
        else:
            for dataset_name in experiment.processeddatasets:
                pdataset = self.get_dataset_from_uri(dataset_name.url)
                if pdataset.name == name:
                    return pdataset
        return None

    def get_data(self, dataset, query='', origin_output_name=''):
        """Query data from a dataset

        Parameters
        ----------
        dataset: Dataset
            Object containing the dataset metadata
        query
            String query with the key=value format.
        origin_output_name
            Name of the output origin (ex: -o) in the case of ProcessedDataset
            search

        Returns
        -------
        list
            List of selected data (list of RawData or ProcessedData objects)
        """

        if len(dataset.uris) < 1:
            return list()

        # search the dataset
        queries = re.split(' AND ', query)

        # initially all the raw data are selected
        #  first_data = self.get_rawdata(dataset.uris[0].md_uri)
        selected_list = []
        # raw dataset
        if dataset.name == 'data':
            for data_info in dataset.uris:
                data_container = self.get_rawdata(data_info.md_uri)
                selected_list.append(self._rawdata_to_search_container(
                    data_container))
        # processed dataset
        else:
            pre_list = []
            for data_info in dataset.uris:
                p_con = self.get_processeddata(data_info.md_uri)
                pre_list.append(self._processed_data_to_search_container(p_con))
            # remove the data where output origin is not the asked one
            if origin_output_name != '':
                for pdata in pre_list:
                    data = self.get_processeddata(pdata.uri())
                    if data.output["name"] == origin_output_name:
                        selected_list.append(pdata)
            else:
                selected_list = pre_list

        # run all the AND queries on the preselected dataset
        if query != '':
            for q in queries:
                selected_list = query_list_single(selected_list, q)

        # convert SearchContainer list to uri list
        out = []
        for d in selected_list:
            if dataset.name == 'data':
                out.append(self.get_rawdata(d.uri()))
            else:
                out.append(self.get_processeddata(d.uri()))
        return out

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

        return self.service.create_dataset(experiment, dataset_name)

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

        return self.service.create_run(dataset, run_info)

    def get_run(self, uri):
        """Read a run metadata from the data base

        Parameters
        ----------
        uri
            URI of the run entry in the database

        Returns
        -------
        Run: object containing the run metadata
        """

        return self.service.get_run(uri)

    def create_data(self, dataset, run, processed_data):
        """Create a new processed data for a given dataset

        Parameters
        ----------
        dataset: Dataset
            Object of the dataset metadata
        run: Run
            Metadata of the run
        processed_data: ProcessedData
            Object containing the new processed data. md_uri is ignored and
            created automatically by this method

        Returns
        -------
        ProcessedData object with the metadata and the new created md_uri
        """

        return self.service.create_data(dataset, run, processed_data)

    @staticmethod
    def _rawdata_to_search_container(rawdata):
        """convert a RawData to SearchContainer

        Parameters
        ----------
        rawdata: RawData
            Object containing the rawdata

        Returns
        -------
        SearchContainer object
        """

        info = SearchContainer()
        info.data['name'] = rawdata.name
        info.data["uri"] = rawdata.md_uri
        info.data['tags'] = rawdata.tags
        return info

    def _processed_data_to_search_container(self, processeddata):
        """convert a ProcessedData to SearchContainer

        Parameters
        ----------
        processeddata: ProcessedData
            Object containing the processeddata

        Returns
        -------
        SearchContainer object
        """

        container = None
        try:
            origin = self.get_origin(processeddata)
            if origin is not None:
                container = self._rawdata_to_search_container(origin)
            else:
                container = SearchContainer()
        except SciXtracerError:
            container = SearchContainer()
        container.data['name'] = processeddata.name
        container.data['uri'] = processeddata.md_uri
        container.data['uuid'] = processeddata.uuid
        return container
