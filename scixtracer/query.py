"""Implements internal query methods


"""

from .utils import SciXtracerError


class SearchContainer:
    """Container for data queries on tag
    Parameters
    ----------
    data
        Data are stored in dict as
            data['name'] = 'file.tif'
            data['uuid'] = 'hkamocnna-cinlncdce-flndcdsa223'
            data['uri'] = '/url/of/the/metadata/file.md.json'
            data['tags'] = {'tag1'='value1', 'tag2'='value2'}
    """

    def __init__(self):
        self.data = dict()
        self.data['name'] = ''
        self.data['uri'] = ''
        self.data['uuid'] = ''
        self.data['tags'] = {}

    def uri(self):
        """Returns the data metadata file uri"""
        if 'uri' in self.data:
            return self.data['uri']

    def set_uri(self, uri: str):
        """Set the data metadata file uri"""
        self.data['uri'] = uri

    def set_uuid(self, uuid: str):
        """Set the data metadata file uuid"""
        self.data['uuid'] = uuid

    def set_name(self, name: str):
        self.data['name'] = name

    def name(self):
        return self.data['name']

    def is_tag(self, key: str):
        """Check if a tag exists
        Returns
        -------
        True if the tag exists, False otherwise
        """
        if key in self.data['tags']:
            return True
        return False

    def tag(self, key: str):
        """Get a tag value
        Parameters
        ----------
        key
            Tag key
        Returns
        -------
        value
            Value of the tag
        """
        if key in self.data['tags']:
            return self.data['tags'][key]
        return ''


def query_list_single(search_list, query):
    """query internal function
    Search if the query is on the search_list

    Parameters
    ----------
    search_list: list
        data search list (list of SearchContainer)
    query: str
        String query with the key=value format. No 'AND', 'OR'...

    Returns
    -------
    list
        list of selected SearchContainer
    """

    selected_list = list()

    if 'name' in query:
        split_query = query.split('=')
        if len(split_query) != 2:
            raise SciXtracerError(
                'Error: the query ' + query +
                ' is not correct. Must be (key<=value)'
            )
        value = split_query[1]
        for i in range(len(search_list)):
            if value in search_list[i].name():
                selected_list.append(search_list[i])
        return selected_list

    if "<=" in query:
        split_query = query.split('<=')
        if len(split_query) != 2:
            raise SciXtracerError(
                'Error: the query ' + query +
                ' is not correct. Must be (key<=value)'
            )
        key = split_query[0]
        value = float(split_query[1].replace(' ', ''))
        for i in range(len(search_list)):
            if (
                search_list[i].is_tag(key)
                and float(search_list[i].tag(key).replace(' ', '')) <= value
            ):
                selected_list.append(search_list[i])

    elif ">=" in query:
        split_query = query.split('>=')
        if len(split_query) != 2:
            raise SciXtracerError(
                'Error: the query ' + query +
                ' is not correct. Must be (key>=value)'
            )
        key = split_query[0]
        value = split_query[1]
        for i in range(len(search_list)):
            if search_list[i].is_tag(key) and \
                    float(search_list[i].tag(key)) >= float(
                value
            ):
                selected_list.append(search_list[i])
    elif "=" in query:
        split_query = query.split('=')
        if len(split_query) != 2:
            raise SciXtracerError(
                'Error: the query ' + query +
                ' is not correct. Must be (key=value)'
            )
        key = split_query[0]
        value = split_query[1]
        for i in range(len(search_list)):
            if search_list[i].is_tag(key) and search_list[i].tag(key) == value:
                selected_list.append(search_list[i])
    elif "<" in query:
        split_query = query.split('<')
        if len(split_query) != 2:
            raise SciXtracerError(
                'Error: the query ' + query +
                ' is not correct. Must be (key<value)'
            )
        key = split_query[0]
        value = split_query[1]
        for i in range(len(search_list)):
            if search_list[i].is_tag(key) and \
                    float(search_list[i].tag(key)) < float(
                value
            ):
                selected_list.append(search_list[i])
    elif ">" in query:
        split_query = query.split('>')
        if len(split_query) != 2:
            raise SciXtracerError(
                'Error: the query ' + query +
                ' is not correct. Must be (key>value)'
            )
        key = split_query[0]
        value = split_query[1]
        for i in range(len(search_list)):
            if search_list[i].is_tag(key) and \
                    float(search_list[i].tag(key)) > float(
                value
            ):
                selected_list.append(search_list[i])

    return selected_list
