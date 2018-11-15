import asyncio

class Gateway_Info(object):

    uuid = None
    firmwareVersion = None
    hardwareVersion = None
    _request = None

    def __init__(self, request):
        self._request = request
   
    def get_name(self):
        return self.uuid
    
    def get_software(self):
        return self.firmwareVersion

    def get_hardware(self):
        return self.hardwareVersion

    async def update(self):
        result = await self._request('/gateway/uuid')
        self.uuid = result['value']
        result = await self._request('/gateway/versionFirmware')
        self.firmwareVersion = result['value']
        result = await self._request('/gateway/versionHardware')
        self.hardwareVersion = result['value']
       # self.firmwareVersion = await self._request('/gateway/firmwareVersion')
       # self.hardwareVersion = await self._request('/gateway/hardawreVersion')
