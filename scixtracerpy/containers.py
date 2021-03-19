# -*- coding: utf-8 -*-
"""SciXtracerPy data containers.

Implements data containers defined in SciXTracer

Classes
-------
Container
Data
RawData
ProcessedData
Dataset
Experiment
Run

"""


def METADATA_TYPE_RAW():
    """Type for matadata for raw data"""
    return "raw"


def METADATA_TYPE_PROCESSED():
    """Type for matadata for processed data"""
    return "processed"


class Container:
    """Interface fo all scixtracer containers

    Containers are classes to store and interact with dedicated
    types of metadata

    Attributes
    ----------
    md_uri: str
        URI of the metadata in the database or file system depending on backend
    uuid: str
        Unique identifier of the metadata
    """
    def __init__(self, md_uri='', uuid=''):
        self.md_uri = md_uri
        self.uuid = uuid


class Data(Container):
    """Interface for data container

    Data container aims at manipulating the metadata of a single data

    Attributes
    ----------
    name
        Name of the data
    author
        Author of the data
    date
        Date when the data is created
    format
        Data format (txt, csv, tif, ...)
    uri
        URI of the data as stored in the database

    """

    def __init__(self):
        Container.__init__(self)
        self.name = ''
        self.author = ''
        self.date = ''
        self.format = ''
        self.uri = ''


class RawData(Data):
    """Container for a Raw data

    Attributes
    ----------
    tags
        Dictionary containing the tags (key=value)

    """

    def __init__(self):
        Data.__init__(self)
        self.tags = dict()

    def set_tag(self, key, value):
        self.tags[key] = value


class ProcessedDataInputContainer:
    """Container for processed data origin input

    Attributes
    ----------
    name
        Name of the input (the unique name in the process)
    uri
        The uri of the input metadata
    """

    def __init__(self, name: str = '', uri: str = '', uuid: str = '',
                 type_: str = METADATA_TYPE_RAW()):
        self.name = name
        self.uri = uri
        self.uuid = uuid
        self.type = type_


class ProcessedData(Data):
    """Container for processed data

    Attributes
    ----------
    run_uri
        URI of the Run metadata file
    inputs
        Information about the inputs that generated
        this processed data. It is a list of ProcessedDataInputContainer
    output
        Information about how the output is referenced
        in the process that generates this processed data
        ex: {"name": "o", "label": "Processed image"}

    """

    def __init__(self):
        Data.__init__(self)
        self.run_uri = ''
        self.inputs = list()
        self.output = dict()

    def add_input(self, name: str, uri: str, uuid: str, type_: str):
        self.inputs.append(ProcessedDataInputContainer(name, uri, uuid, type_))

    def set_output(self, name: str, label: str):
        self.output = {'name': name, 'label': label}


class Dataset(Container):
    """Container for a dataset metadata

    Attributes
    ----------
    name
        Name of the dataset
    uris
        List of the URIs of the data (metadata) in the URIs
    """

    def __init__(self):
        Container.__init__(self)
        self.name = ''
        self.uris = list()  # list of containers


class RunParameterContainer:
    """Container for a run parameter

    Attributes
    ----------
    name
        Name of the parameter
    value
        Value of the parameter
    """

    def __init__(self, name: str = '', value: str = ''):
        self.name = name
        self.value = value


class RunInputContainer:
    """Container for a run input

    Attributes
    ----------
    name
        Name of the input (ex -i)
    dataset
        Name of the dataset containing the inputs (ex 'data')
    query
        Query used to select images in the dataset (ex 'name=image.tif')
    origin_output_name
        Name of the output in the parent run if run on a processed dataset

    """
    def __init__(
        self,
        name: str = '',
        dataset: str = '',
        query: str = '',
        origin_output_name: str = '',
    ):
        self.name = name
        self.dataset = dataset
        self.query = query
        self.origin_output_name = origin_output_name


class Run(Container):
    """Container for a run (processing or job execution)

    Attributes
    ----------
    process_name
        Name of the process (ex: ndsafir)
    process_uri
        Unique URI of the process (ex: github url)
    processeddataset
        URI of the processed dataset
    parameters
        List of parameters using the RunParameterContainer object
    inputs
        List of the run inputs using RunInputContainer object

    """

    def __init__(self):
        Container.__init__(self)
        self.process_name = ''
        self.process_uri = ''
        self.processeddataset = None  # Container
        self.parameters = []  # list of RunParameterContainer
        self.inputs = []  # list of RunInputContainer


class DatasetInfo:
    """Contains the info of a dataset

    Attributes
    ----------
    name: str
        Name of the dataset
    url: str
        URL of the metadata file
    uuid: str
        Unique ID of the dataset
    """
    def __init__(self, name, url, uuid):
        self.name = name
        self.url = url
        self.uuid = uuid


class Experiment(Container):
    """Container for an experiment

    Attributes
    ----------
    name
        Name of the experiment
    author
        Username of the experiment author
    date
        Creation date of the experiment
    rawdataset:
        URI of the raw dataset
    processeddatasets
        URIs of the processed datasets
    tag_keys
        List of vocabulary keys used in the experiment

    """

    def __init__(self):
        Container.__init__(self)
        self.name = ''
        self.author = ''
        self.date = ''
        self.rawdataset = None  # DatasetInfo
        self.processeddatasets = []  # list of DatasetInfo
        self.tag_keys = []

    def set_tag_key(self, key):
        if key not in self.tag_keys:
            self.tag_keys.append(key)
