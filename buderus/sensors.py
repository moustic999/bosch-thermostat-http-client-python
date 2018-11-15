class Sensors(object):
    items = []
    def __init__(self, request):
        self._request = request
       
    
    async def update(self):
        for item in self.items:
            await item.update()

    def registerSensor(self, name ,path):
        item = Sensor(self._request, name, path)
        self.items.append(item)




class Sensor(object):
    
    _path = None
    _request = None 
    name =  None
    value = None
    type = None
    unitOfMeasure = None

    def __init__(self, request, name, path):
        self._request = request
        self._path = path
        self.name = name


    def getName(self):
        return self.getName()

    def getValue(self):
        return self.getValue()    

    async def update(self):
        data = await self._request(self._path)
        self.value = data['value']
        self.type = data['type']
        self.unitOfMeasure = data['unitOfMeasure']

