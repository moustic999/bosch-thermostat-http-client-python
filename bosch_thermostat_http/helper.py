""" Helper functions. """

from .const import GET, NAME, PATH


async def crawl(url, _list, deep, get):
    resp = await get(url)
    if (("references" not in resp or deep == 0) and "id" in resp):
        _list.append(resp)
    else:
        if "references" in resp:
            for uri in resp["references"]:
                if "id" in uri and deep > 0:
                    await crawl(uri["id"], _list, deep-1, get)
    return _list


class BoschEntities:
    """
    Main object to deriver sensors and circuits.
    """
    def __init__(self, requests):
        """
        :param dic requests: { GET: get function, SUBMIT: submit function}
        """
        self._items = []
        self._requests = requests

    async def retrieve_from_module(self, deep, path):
        return await crawl(path, [], deep, self._requests[GET])

    def get_items(self):
        """ Get items. """
        return self._items

    async def update(self):
        """ Update all heating circuits. """
        for item in self._items:
            await item.update()


class BoschSingleEntity:

    def __init__(self, name, data, path=None):
        self._main_data = {
            NAME: name,
            PATH: path
        }
        self._data = data

    def get_property(self, property_name):
        if property_name in self._data:
            return self._data[property_name]
        return None

    @property
    def name(self):
        """ Name of Bosch entity. """
        return self._main_data[NAME]

    @property
    def path(self):
        return self._main_data[PATH]
