import logging
from config import VARIABLES, SYNOPTIQUE_VARIABLES
from offline_data import get_offline_value, simulate_dynamic_value, OFFLINE_DATA, SYNOPTIQUE_OFFLINE_DATA

logger = logging.getLogger(__name__)

class OfflineProvider:
    def __init__(self, url: str = None):
        self.url = url
        self.connected = False
        self.data_cache = {}
        self._init_cache()

    def _init_cache(self):
        all_vars = {**VARIABLES, **SYNOPTIQUE_VARIABLES}
        for var_name, node_id in all_vars.items():
            value = get_offline_value(var_name)
            if value is not None:
                self.data_cache[node_id] = value

    async def connect(self):
        self.connected = True
        logger.info("🟡 MODE OFFLINE - Pas de connexion OPC UA")

    async def disconnect(self):
        self.connected = False
        logger.info("🟡 MODE OFFLINE - Déconnexion simulée")

    async def read_variable(self, node_id: str):
        if node_id not in self.data_cache:
            logger.warning(f"Variable {node_id} non trouvée en mode offline")
            return None

        current_value = self.data_cache[node_id]

        var_name = self._get_var_name(node_id)
        if var_name:
            new_value = simulate_dynamic_value(var_name, current_value)
            self.data_cache[node_id] = new_value
            return new_value

        return current_value

    async def write_variable(self, node_id: str, value):
        if node_id in self.data_cache:
            self.data_cache[node_id] = value
            logger.info(f"🟡 MODE OFFLINE - Écriture simulée {node_id} = {value}")
        else:
            logger.warning(f"🟡 MODE OFFLINE - Variable {node_id} inconnue pour écriture")

    def _get_var_name(self, node_id: str):
        all_vars = {**VARIABLES, **SYNOPTIQUE_VARIABLES}
        for var_name, nid in all_vars.items():
            if nid == node_id:
                return var_name
        return None
