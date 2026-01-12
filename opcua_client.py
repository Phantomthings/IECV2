from asyncua import Client
import logging

logger = logging.getLogger(__name__)

class OPCUAClient:
    def __init__(self, url: str):
        self.url = url
        self.client = None
        self.connected = False
    
    async def connect(self):
        try:
            self.client = Client(url=self.url)
            await self.client.connect()
            self.connected = True
            logger.info(f"✅ Connecté à {self.url}")
        except Exception as e:
            logger.error(f"❌ Erreur connexion: {e}")
            raise
    
    async def disconnect(self):
        if self.client:
            await self.client.disconnect()
            self.connected = False
            logger.info("Déconnecté")
    
    async def read_variable(self, node_id: str):
        try:
            node = self.client.get_node(node_id)
            value = await node.read_value()
            return value
        except Exception as e:
            logger.error(f"Erreur lecture {node_id}: {e}")
            raise
    
    async def write_variable(self, node_id: str, value):
        try:
            node = self.client.get_node(node_id)
            await node.write_value(value)
            logger.info(f"✅ Écriture {node_id} = {value}")
        except Exception as e:
            logger.error(f"Erreur écriture {node_id}: {e}")
            raise