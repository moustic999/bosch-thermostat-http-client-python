import asyncio

HEATING_CIRCUITS = '/heatingCircuits' # get all heating Circuits



class HeatingCircuits(object):
    items = []
    def __init__(self, request):
        self._request = request        
       
    async def initialize(self):
        circuitsJson = await self._request(HEATING_CIRCUITS)
        print(circuitsJson)
        circuits = circuitsJson['references']
        for circuitId in circuits:
            name = circuitId['id'].split('/').pop()
            heatingCircuit = HeatingCircuit(self._request, name)
            self.items.append(heatingCircuit)

    async def update(self):
        for item in self.items:
            await item.update()

class HeatingCircuit(object):
    name = None
    operationMode = None
    operationList = []
    currentSetPoint = None
    currentTemperature = None

    def __init__(self, request, hc_name):
        self._request = request
        self.name = hc_name

    async def update(self):
        path = '/heatingCircuits/{}/roomtemperature'.format(self.name)
        result =  await self._request(path)
        self.currentTemperature = result['value']
        path =  '/heatingCircuits/{}/currentRoomSetpoint'.format(self.name)
        result =  await self._request(path)
        self.currentSetPoint = result['value']
        path = '/heatingCircuits/{}/operationMode'.format(self.name)
        result =  await self._request(path)
        self.operationMode = result['value']
        self.operationList = result['allowedValues']
