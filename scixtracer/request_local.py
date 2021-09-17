# -*- coding: utf-8 -*-
"""SciXtracer request local.

Local implementation of the request service

Classes
-------
LocalRequest

"""

import os
import json
from shutil import copyfile
import uuid

from .utils import SciXtracerError
from .containers import (METADATA_TYPE_RAW, METADATA_TYPE_PROCESSED, RawData,
                         ProcessedData, Dataset, DatasetInfo, Container,
                         Experiment, Run, ProcessedDataInputContainer,
                         RunInputContainer, RunParameterContainer)


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
    def _generate_uuid():
        return str(uuid.uuid4())

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

    @staticmethod
    def md_file_path(md_uri):
        """get metadata file directory path

        Parameters
        ----------
        md_uri: str
            URI of the metadata

        Returns
        ----------
        str
            The name of the metadata file directory path
        """
        abspath = os.path.abspath(md_uri)
        return os.path.dirname(abspath)

    @staticmethod
    def relative_path(file: str, reference_file: str):
        """convert file absolute path to a relative path wrt reference_file
        Parameters
        ----------
        reference_file
            Reference file
        file
            File to get absolute path
        Returns
        -------
        relative path of uri wrt md_uri
        """
        separator = os.sep
        file = file.replace(separator + separator, separator)
        reference_file = reference_file.replace(separator + separator,
                                                separator)

        common_part = ''
        for i in range(len(file)):
            common_part = reference_file[0:i]
            if common_part not in file:
                break

        last_separator = common_part.rfind(separator)

        short_reference_file = reference_file[last_separator + 1:]

        number_of_sub_folder = short_reference_file.count(separator)
        short_file = file[last_separator + 1:]
        for i in range(number_of_sub_folder):
            short_file = '..' + separator + short_file

        return short_file

    @staticmethod
    def absolute_path(file: str, reference_file: str):
        """convert file relative to reference_file into an absolute path
        Parameters
        ----------
        reference_file
            Reference file
        file
            File to get absolute path
        Returns
        -------
        absolute path of file
        """
        if os.path.isfile(file):
            return os.path.abspath(file)

        separator = os.sep
        last_separator = reference_file.rfind(separator)
        canonical_path = reference_file[0: last_separator + 1]
        return LocalRequestService.simplify_path(canonical_path + file)

    @staticmethod
    def simplify_path(path: str) -> str:
        """Simplify a path by removing ../"""

        if path.find('..') < 0:
            return path

        separator = os.sep
        keep_folders = path.split(separator)

        found = True
        while found:
            pos = -1
            folders = keep_folders
            for i in range(len(folders)):
                if folders[i] == '..':
                    pos = i
                    break
            if pos > -1:
                keep_folders = []
                for i in range(0, pos - 1):
                    keep_folders.append(folders[i])
                for i in range(pos + 1, len(folders)):
                    keep_folders.append(folders[i])
            else:
                found = False

        clean_path = ''
        for i in range(len(keep_folders)):
            clean_path += keep_folders[i]
            if i < len(keep_folders) - 1:
                clean_path += separator
        return clean_path

    @staticmethod
    def normalize_path_sep(path: str) -> str:
        """Normalize the separators of a path

        Parameters
        ----------
        path: str
            Path to normalize

        Returns
        -------
        path normalized
        """
        p1 = path.replace('/', os.sep).replace('\\\\', os.sep)
        return p1

    @staticmethod
    def to_unix_path(path: str) -> str:
        """Transform a path to unix path
        Parameters
        ----------
        path: str
            Path to unixify
        Returns
        -------
        Path with unix separator
        """
        return path.replace('\\\\', '/').replace('\\', '/')

    def create_experiment(self, name, author, date='now', tag_keys=None,
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

        if tag_keys is None:
            tag_keys = []
        container = Experiment()
        container.uuid = self._generate_uuid()
        container.name = name
        container.author = author
        container.date = date
        container.tag_keys = tag_keys

        # check the destination dir
        uri = os.path.abspath(destination)
        if not os.path.exists(uri):
            raise SciXtracerError(
                'Cannot create Experiment: the destination '
                'directory does not exists'
            )

        uri = os.path.abspath(uri)

        # create the experiment directory
        filtered_name = name.replace(' ', '')
        experiment_path = os.path.join(uri, filtered_name)
        if not os.path.exists(experiment_path):
            os.mkdir(experiment_path)
        else:
            raise SciXtracerError(
                'Cannot create Experiment: the experiment '
                'directory already exists'
            )

        # create an empty raw dataset
        rawdata_path = os.path.join(experiment_path, 'data')
        rawdataset_md_url = os.path.join(rawdata_path, 'rawdataset.md.json')
        if os.path.exists(experiment_path):
            os.mkdir(rawdata_path)
        else:
            raise SciXtracerError(
                'Cannot create Experiment raw dataset: the experiment '
                'directory does not exists'
            )

        rawdataset = Dataset()
        rawdataset.uuid = self._generate_uuid()
        rawdataset.md_uri = rawdataset_md_url
        rawdataset.name = 'data'
        self.update_dataset(rawdataset)
        container.rawdataset = DatasetInfo(rawdataset.name, rawdataset_md_url,
                                           rawdataset.uuid)

        # save the experiment.md.json metadata file
        container.md_uri = os.path.join(experiment_path, 'experiment.md.json')
        self.update_experiment(container)
        return container

    def get_experiment(self, md_uri):
        """Read an experiment from the database

        Parameters
        ----------
        md_uri: str
            URI of the experiment. For local use case, the URI is either the
            path of the experiment directory, or the path of the
            experiment.md.json file

        Returns
        -------
        Experiment container with the experiment metadata
        """

        md_uri = os.path.abspath(md_uri)
        if os.path.isfile(md_uri):
            metadata = self._read_json(md_uri)
            container = Experiment()
            container.uuid = metadata['uuid']
            container.md_uri = md_uri
            container.name = metadata['information']['name']
            container.author = metadata['information']['author']
            container.date = metadata['information']['date']

            rawdataset_url = LocalRequestService.absolute_path(
                LocalRequestService.normalize_path_sep(
                    metadata['rawdataset']['url']), md_uri)
            container.rawdataset = DatasetInfo(metadata['rawdataset']['name'],
                                               rawdataset_url,
                                               metadata['rawdataset']['uuid'])
            for dataset in metadata['processeddatasets']:
                processeddataset_url = LocalRequestService.absolute_path(
                    LocalRequestService.normalize_path_sep(
                        dataset['url']), md_uri)

                container.processeddatasets.append(
                    DatasetInfo(dataset['name'],
                                processeddataset_url,
                                dataset['uuid']))
            for tag in metadata['tags']:
                container.tag_keys.append(tag)
            return container
        raise SciXtracerError('Cannot find the experiment metadata from the '
                              'given URI')

    def update_experiment(self, experiment):
        """Write an experiment to the database

        Parameters
        ----------
        experiment: Experiment
            Container of the experiment metadata
        """

        md_uri: str = os.path.abspath(experiment.md_uri)
        metadata = dict()
        metadata['uuid'] = experiment.uuid
        metadata['information'] = {}
        metadata['information']['name'] = experiment.name
        metadata['information']['author'] = experiment.author
        metadata['information']['date'] = experiment.date

        tmp_url = LocalRequestService.to_unix_path(
            LocalRequestService.relative_path(experiment.rawdataset.url,
                                              md_uri))
        metadata['rawdataset'] = {"name": experiment.rawdataset.name,
                                  "url": tmp_url,
                                  "uuid": experiment.rawdataset.uuid}
        metadata['processeddatasets'] = []
        for dataset in experiment.processeddatasets:
            tmp_url = LocalRequestService.to_unix_path(
                          LocalRequestService.relative_path(dataset.url,
                                                            md_uri))
            metadata['processeddatasets'].append(
                {"name": dataset.name, "url": tmp_url, "uuid": dataset.uuid}
                )
        metadata['tags'] = []
        for tag in experiment.tag_keys:
            metadata['tags'].append(tag)
        self._write_json(metadata, md_uri)

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

        rawdataset_uri = os.path.abspath(experiment.rawdataset.url)
        data_dir_path = os.path.dirname(rawdataset_uri)

        # create the new data uri
        data_base_name = os.path.basename(data_path)
        filtered_name = data_base_name.replace(' ', '')
        filtered_name, ext = os.path.splitext(filtered_name)
        md_uri = os.path.join(data_dir_path, filtered_name + '.md.json')

        # create the container
        metadata = RawData()
        metadata.uuid = self._generate_uuid()
        metadata.md_uri = md_uri
        metadata.name = name
        metadata.author = author
        metadata.format = format_
        metadata.date = date
        metadata.tags = tags

        # import data
        if copy:
            copied_data_path = os.path.join(data_dir_path, data_base_name)
            copyfile(data_path, copied_data_path)
            metadata.uri = copied_data_path
        else:
            metadata.uri = data_path
        self.update_rawdata(metadata)

        # add data to experiment RawDataSet
        rawdataset_container = self.get_dataset(rawdataset_uri)
        raw_c = Container(md_uri=metadata.md_uri, uuid=metadata.uuid)
        rawdataset_container.uris.append(raw_c)
        self.update_dataset(rawdataset_container)

        # add tags keys to experiment
        for key in tags:
            experiment.set_tag_key(key)
        self.update_experiment(experiment)

        return metadata

    def get_rawdata(self, md_uri):
        """Read a raw data from the database

        Parameters
        ----------
        md_uri: str
            URI if the rawdata

        Returns
        -------
        RawData object containing the raw data metadata
        """

        md_uri = os.path.abspath(md_uri)
        if os.path.isfile(md_uri) and md_uri.endswith('.md.json'):
            metadata = LocalRequestService._read_json(md_uri)
            container = RawData()
            container.uuid = metadata['uuid']
            container.md_uri = md_uri
            container.type = metadata['origin']['type']
            container.name = metadata['common']['name']
            container.author = metadata['common']['author']
            container.date = metadata['common']['date']
            container.format = metadata['common']['format']
            # copy the url if absolute, append md_uri path otherwise
            container.uri = LocalRequestService.absolute_path(
                LocalRequestService.normalize_path_sep(
                    metadata['common']['url']), md_uri)
            if 'tags' in metadata:
                for key in metadata['tags']:
                    container.tags[key] = metadata['tags'][key]
            return container
        raise SciXtracerError('Metadata file format not supported')

    def update_rawdata(self, rawdata):
        """Read a raw data from the database

        Parameters
        ----------
        rawdata: RawData
            Container with the rawdata metadata
        """

        md_uri = os.path.abspath(rawdata.md_uri)
        metadata = dict()
        metadata['uuid'] = rawdata.uuid
        metadata['origin'] = dict()
        metadata['origin']['type'] = METADATA_TYPE_RAW()

        metadata['common'] = dict()
        metadata['common']['name'] = rawdata.name
        metadata['common']['author'] = rawdata.author
        metadata['common']['date'] = rawdata.date
        metadata['common']['format'] = rawdata.format
        metadata['common']['url'] = LocalRequestService.to_unix_path(
            LocalRequestService.relative_path(rawdata.uri, md_uri))

        metadata['tags'] = dict()
        for key in rawdata.tags:
            metadata['tags'][key] = rawdata.tags[key]

        self._write_json(metadata, md_uri)

    def get_processeddata(self, md_uri):
        """Read a processed data from the database

        Parameters
        ----------
        md_uri: str
            URI if the processeddata

        Returns
        -------
        ProcessedData object containing the raw data metadata
        """

        md_uri = os.path.abspath(md_uri)
        if os.path.isfile(md_uri) and md_uri.endswith('.md.json'):
            metadata = self._read_json(md_uri)
            container = ProcessedData()
            container.uuid = metadata['uuid']
            container.md_uri = md_uri
            container.name = metadata['common']['name']
            container.author = metadata['common']['author']
            container.date = metadata['common']['date']
            container.format = metadata['common']['format']
            container.uri = LocalRequestService.absolute_path(
                LocalRequestService.normalize_path_sep(
                    metadata['common']['url']), md_uri)
            # origin run
            container.run = Container(LocalRequestService.absolute_path(
                LocalRequestService.normalize_path_sep(
                    metadata['origin']['run']["url"]), md_uri),
                metadata['origin']['run']["uuid"])
            # origin input
            for input_ in metadata['origin']['inputs']:
                container.inputs.append(
                    ProcessedDataInputContainer(
                        input_['name'],
                        LocalRequestService.absolute_path(
                            LocalRequestService.normalize_path_sep(
                                input_['url']), md_uri),
                        input_['uuid'],
                        input_['type'],
                    )
                )
            # origin output
            if 'name' in metadata['origin']['output']:
                container.output['name'] = metadata['origin']['output']["name"]
            if 'label' in metadata['origin']['output']:
                container.output['label'] = \
                    metadata['origin']['output']['label']

            return container
        raise SciXtracerError('Metadata file format not supported')

    def update_processeddata(self, processeddata):
        """Read a processed data from the database

        Parameters
        ----------
        processeddata: ProcessedData
            Container with the processeddata metadata
        """

        md_uri = os.path.abspath(processeddata.md_uri)
        metadata = dict()
        metadata['uuid'] = processeddata.uuid
        # common
        metadata['common'] = dict()
        metadata['common']['name'] = processeddata.name
        metadata['common']['author'] = processeddata.author
        metadata['common']['date'] = processeddata.date
        metadata['common']['format'] = processeddata.format
        metadata['common']['url'] = LocalRequestService.to_unix_path(
            LocalRequestService.relative_path(processeddata.uri, md_uri))
        # origin type
        metadata['origin'] = dict()
        metadata['origin']['type'] = METADATA_TYPE_PROCESSED()
        # run url
        run_url = LocalRequestService.to_unix_path(
            LocalRequestService.relative_path(processeddata.run.md_uri, md_uri))
        metadata['origin']['run'] = {"url": run_url,
                                     "uuid": processeddata.run.uuid}
        # origin inputs
        metadata['origin']['inputs'] = list()
        for input_ in processeddata.inputs:
            metadata['origin']['inputs'].append(
                {
                    'name': input_.name,
                    'url': LocalRequestService.to_unix_path(
                        LocalRequestService.relative_path(input_.uri, md_uri)),
                    'uuid': input_.uuid,
                    'type': input_.type,
                }
            )
        # origin ouput
        metadata['origin']['output'] = {
            'name': processeddata.output['name'],
            'label': processeddata.output['label'],
        }

        self._write_json(metadata, md_uri)

    def get_dataset(self, md_uri):
        """Read a dataset from the database using it URI

        Parameters
        ----------
        md_uri: str
            URI if the dataset

        Returns
        -------
        Dataset object containing the dataset metadata
        """

        md_uri = os.path.abspath(md_uri)
        if os.path.isfile(md_uri) and md_uri.endswith('.md.json'):
            metadata = self._read_json(md_uri)
            container = Dataset()
            container.uuid = metadata["uuid"]
            container.md_uri = md_uri
            container.name = metadata['name']
            for uri in metadata['urls']:
                container.uris.append(
                    Container(LocalRequestService.absolute_path(
                        LocalRequestService.normalize_path_sep(uri['url']),
                        md_uri),
                        uri['uuid']))

            return container
        raise SciXtracerError('Dataset not found')

    def update_dataset(self, dataset):
        """Read a processed data from the database

        Parameters
        ----------
        dataset: Dataset
            Container with the dataset metadata
        """

        md_uri = os.path.abspath(dataset.md_uri)
        metadata = dict()
        metadata['uuid'] = dataset.uuid
        metadata['name'] = dataset.name
        metadata['urls'] = list()
        for uri in dataset.uris:
            tmp_url = LocalRequestService.to_unix_path(
                LocalRequestService.relative_path(uri.md_uri, md_uri))
            metadata['urls'].append({"uuid": uri.uuid, 'url': tmp_url})
        self._write_json(metadata, md_uri)

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

        # create the dataset metadata
        experiment_md_uri = os.path.abspath(experiment.md_uri)
        experiment_dir = LocalRequestService.md_file_path(experiment_md_uri)
        dataset_dir = os.path.join(experiment_dir, dataset_name)
        if not os.path.isdir(dataset_dir):
            os.mkdir(dataset_dir)
        processeddataset_uri = os.path.join(
            experiment_dir, dataset_name, 'processeddataset.md.json'
        )
        container = Dataset()
        container.uuid = self._generate_uuid()
        container.md_uri = processeddataset_uri
        container.name = dataset_name
        self.update_dataset(container)

        # add the dataset to the experiment
        tmp_url = LocalRequestService.to_unix_path(processeddataset_uri)
        experiment.processeddatasets.append(
            DatasetInfo(dataset_name, tmp_url, container.uuid)
            )
        self.update_experiment(experiment)

        return container

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

        # create run URI
        dataset_md_uri = os.path.abspath(dataset.md_uri)
        dataset_dir = LocalRequestService.md_file_path(dataset_md_uri)
        run_md_file_name = "run.md.json"
        runid_count = 0
        while os.path.isfile(os.path.join(dataset_dir, run_md_file_name)):
            runid_count += 1
            run_md_file_name = "run_" + str(runid_count) + ".md.json"
        run_uri = os.path.join(dataset_dir, run_md_file_name)

        # write run
        run_info.processeddataset = dataset
        run_info.uuid = self._generate_uuid()
        run_info.md_uri = run_uri
        self._write_run(run_info)
        return run_info

    def get_run(self, md_uri):
        """Read a run metadata from the data base

        Parameters
        ----------
        md_uri
            URI of the run entry in the database

        Returns
        -------
        Run: object containing the run metadata
        """

        md_uri = os.path.abspath(md_uri)
        if os.path.isfile(md_uri):
            metadata = self._read_json(md_uri)
            container = Run()
            container.uuid = metadata['uuid']
            container.md_uri = md_uri
            container.process_name = metadata['process']['name']
            container.process_uri = LocalRequestService.normalize_path_sep(
                metadata['process']['url'])
            container.processeddataset = Container(
                LocalRequestService.absolute_path(
                    LocalRequestService.normalize_path_sep(
                        metadata['processeddataset']['url']),
                    md_uri),
                metadata['processeddataset']['uuid']
            )
            for input_ in metadata['inputs']:
                container.inputs.append(
                    RunInputContainer(
                        input_['name'],
                        input_['dataset'],
                        input_['query'],
                        input_['origin_output_name'],
                    )
                )
            for parameter in metadata['parameters']:
                container.parameters.append(
                    RunParameterContainer(parameter['name'], parameter['value'])
                )
            return container
        raise SciXtracerError('Run not found')

    def _write_run(self, run):
        """Write a run metadata to the data base
        Parameters
        ----------
        run
            Object containing the run metadata
        """

        metadata = dict()
        metadata['uuid'] = run.uuid

        metadata['process'] = {}
        metadata['process']['name'] = run.process_name
        metadata['process']['url'] = LocalRequestService.to_unix_path(
            run.process_uri)
        dataset_rel_url = LocalRequestService.to_unix_path(
            LocalRequestService.relative_path(run.processeddataset.md_uri,
                                              run.md_uri))
        metadata['processeddataset'] = {"uuid": run.processeddataset.uuid,
                                        "url": dataset_rel_url}
        metadata['inputs'] = []
        for input_ in run.inputs:
            metadata['inputs'].append(
                {
                    'name': input_.name,
                    'dataset': input_.dataset,
                    'query': input_.query,
                    'origin_output_name': input_.origin_output_name,
                }
            )
        metadata['parameters'] = []
        for parameter in run.parameters:
            metadata['parameters'].append(
                {'name': parameter.name, 'value': parameter.value}
            )

        self._write_json(metadata, run.md_uri)

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

        md_uri = os.path.abspath(dataset.md_uri)
        dataset_dir = LocalRequestService.md_file_path(md_uri)

        # create the data metadata
        data_md_file = os.path.join(dataset_dir, processed_data.name
                                    + '.md.json')
        processed_data.uuid = self._generate_uuid()
        processed_data.md_uri = data_md_file

        processed_data.run = run

        self.update_processeddata(processed_data)

        # add the data to the dataset
        dataset.uris.append(Container(data_md_file, processed_data.uuid))
        self.update_dataset(dataset)

        return processed_data
