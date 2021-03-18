"""Serialize the containers

Methods
-------
serialize_rawdata

"""

from .containers import RawData, ProcessedData, Dataset, Run, Experiment


def serialize_data(data):
    """Serialize a data

    Parameters
    ----------
    data: Data
        Container of data metadata

    Returns
    -------
    str containing the serialized container
    """

    content = 'name = ' + data.name + '\n'
    content += 'author = ' + data.author + '\n'
    content += 'date = ' + data.date + '\n'
    content += 'format = ' + data.format + '\n'
    content += 'uri = ' + data.uri + '\n'
    return content


def serialize_rawdata(rawdata):
    """Serialize a rawdata

    Parameters
    ----------
    rawdata: RawData
        Container of raw data metadata

    Returns
    -------
    str containing the serialized container
    """

    content = 'RawData:\n'
    content += serialize_data(rawdata)
    content += 'tags = {'
    for tag in rawdata.tags:
        content += rawdata.tags[tag] + ':' + rawdata.tags[tag] + ','
    content = content[:-1] + '}'
    return content


def serialize_processeddata(processeddata):
    """Serialize a processeddata

    Parameters
    ----------
    processeddata: ProcessedData
        Container of processed data metadata

    Returns
    -------
    str containing the serialized container
    """

    content = 'ProcessedData:\n'
    content += serialize_data(processeddata)
    content += 'run_uri = ' + processeddata.run_uri + '\n'
    content += 'inputs = [ \n'
    for input_ in processeddata.inputs:
        content += 'name:' + input_.name + ', uri:' + input_.uri + '\n'
    content += (
            'output={name:'
            + processeddata.output['name']
            + ', label:'
            + processeddata.output['label']
            + '}'
    )
    return content


def serialize_dataset(dataset):
    """Serialize a dataset

    Parameters
    ----------
    dataset: Dataset
        Container of dataset metadata

    Returns
    -------
    str containing the serialized container
    """

    content = 'Dataset:\n'
    content += 'name = ' + dataset.name
    content += 'uris = \n'
    for uri in dataset.uris:
        content += '\t' + uri
    content += '\n'
    return content


def serialize_experiment(experiment):
    """Serialize an experiment

    Parameters
    ----------
    experiment: Experiment
        Container of experiment metadata

    Returns
    -------
    str containing the serialized container
    """

    content = 'Experiment:\n'
    content += 'uuid = ' + experiment.uuid + '\n'
    content += 'name = ' + experiment.name + '\n'
    content += 'author = ' + experiment.author + '\n'
    content += 'date = ' + experiment.date + '\n'
    content += 'rawdataset = ' + '\n'
    content += '\t{\n'
    content += '\t\tname: ' + experiment.rawdataset.name + ',\n'
    content += '\t\tuuid: ' + experiment.rawdataset.uuid + ',\n'
    content += '\t\turl: ' + experiment.rawdataset.url + ',\n'
    content += '\t}\n'
    content += 'processeddatasets = [ \n'
    for dataset in experiment.processeddatasets:
        content += '\t{\n'
        content += '\t\tname: ' + dataset.name + ',\n'
        content += '\t\tuuid: ' + dataset.uuid + ',\n'
        content += '\t\turl: ' + dataset.url + ',\n'
        content += '\t}\n'
    content += '] \n'
    content += 'tags = [ \n'
    for tag in experiment.tag_keys:
        content += '\t' + tag + '\n'
    content += ']'
    return content


def serialize_run(run):
    """Serialize a run

    Parameters
    ----------
    run: Run
        Container of run metadata

    Returns
    -------
    str containing the serialized container
    """

    content = 'Experiment:\n'
    content += '{\n\t"process":{\n'
    content += '\t\t"name": "' + run.process_name + '",\n'
    content += '\t\t"uri": "' + run.process_uri + '"\n'
    content += '\t}\n\t"processeddataset": "' + run.processeddataset + \
               '",\n'
    content += '\t"parameters": [\n '
    for param in run.parameters:
        content += '\t\t{\n'
        content += '\t\t\t"name": "' + param.name + '",\n'
        content += '\t\t\t"value": "' + param.value + '"\n'
        content += '\t\t},\n'
    content = content[:-3] + '\n'
    content += '\t]\n'
    content += '\t"inputs": [\n '
    for input_ in run.inputs:
        content += '\t\t{\n'
        content += '\t\t\t"name": "' + input_.name + '",\n'
        content += '\t\t\t"dataset": "' + input_.dataset + '",\n'
        content += '\t\t\t"query": "' + input_.query + '",\n'
        content += (
                '\t\t\t"origin_output_name": "' + input_.origin_output_name +
                '"\n'
        )
        content += '\t\t},\n'
    content = content[:-3] + '\n'
    content += '\t]\n'
    content += '}'
    return content
