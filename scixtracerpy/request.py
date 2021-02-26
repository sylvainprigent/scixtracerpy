# -*- coding: utf-8 -*-
"""SciXtracer request.

This module implements the request to query the database

Classes
-------
Request

"""

import os
import re
from .factory import requestServices
from .containers import Experiment


class Request:
    """Implements the requests to the database

    """
    def __init__(self):
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

        return self.service.create_experiment(name, author,  date, tag_keys,
                                              destination)

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

        self.service.import_data(experiment, data_path, name, author, format_,
                                 date, tags, copy)

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
        self.import_data(experiment, data_url, file, author, format_, date, {},
                         copy_data)

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

        experiment.set_tag(tag, False)
        self.update_experiment(experiment)
        _rawdataset = self.get_rawdataset(experiment)
        for uri in _rawdataset.uris:
            _rawdata = self.get_rawdata(uri)
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
        
        experiment.set_tag(tag, False)
        self.update_experiment(experiment)
        _rawdataset = self.get_rawdataset(experiment)
        for uri in _rawdataset.uris:
            _rawdata = self.get_rawdata(uri)
            basename = os.path.splitext(os.path.basename(_rawdata.uri))[0]
            splited_name = basename.split(separator)
            value = ''
            if len(splited_name) > value_position:
                value = splited_name[value_position]
            _rawdata.set_tag(tag, value)
            self.update_rawdata(_rawdata)
