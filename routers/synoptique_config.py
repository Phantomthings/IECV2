from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Module:
    id: str
    vdc: float = 0.0
    idc: float = 0.0
    status: int = 0
    
    @property
    def status_color(self) -> str:
        if self.status == 6:
            return "rgb(192, 255, 192)"
        elif self.status == 2:
            return "rgb(255, 192, 192)"
        return "white"


@dataclass
class PoleGroupe:
    id: str
    modules: List[str] = field(default_factory=list)
    position_x: int = 0
    position_y: int = 0
    status: int = 0
    color_id: int = -1
    id_prise: int = 0
    
    @property
    def status_color(self) -> str:
        if self.status in [2, 3]:
            return "rgb(192, 255, 192)"
        elif self.status == 4:
            return "rgb(255, 192, 192)"
        return "white"
    
    @property
    def prise_color(self) -> str:
        colors = {
            -1: "white",
            1: "rgb(176, 224, 230)",
            2: "rgb(250, 250, 210)",
            3: "rgb(255, 228, 225)",
            4: "rgb(255, 229, 180)"
        }
        return colors.get(self.color_id, "white")


@dataclass
class Contacteur:
    id: str
    position_x: int = 0
    position_y: int = 0
    status: int = 1
    label: str = ""
    
    @property
    def status_color(self) -> str:
        if self.status == 17:
            return "rgb(255, 192, 192)"
        elif self.status == 6:
            return "rgb(192, 255, 192)"
        elif self.status == 2:
            return "white"
        return "gray"


@dataclass
class PDCStatus:
    id: str
    position_x: int = 0
    position_y: int = 0
    color_status: int = 0
    text_status: str = ""
    
    @property
    def status_color(self) -> str:
        colors = {
            0: "white",
            1: "rgb(192, 255, 192)",
            2: "rgb(128, 255, 255)",
            3: "rgb(255, 192, 192)"
        }
        return colors.get(self.color_status, "white")


MODULES: Dict[str, Module] = {
    "M1": Module(id="M1"),
    "M2": Module(id="M2"),
    "M3": Module(id="M3"),
    "M4": Module(id="M4"),
    "M5": Module(id="M5"),
    "M6": Module(id="M6"),
    "M7": Module(id="M7"),
    "M8": Module(id="M8"),
    "M9": Module(id="M9"),
    "M10": Module(id="M10"),
    "M11": Module(id="M11"),
    "M12": Module(id="M12"),
    "M13": Module(id="M13"),
    "M14": Module(id="M14"),
}

POLE_GROUPES: Dict[str, PoleGroupe] = {
    "G8": PoleGroupe(id="G8", modules=["M1", "M2"], position_x=500, position_y=20),
    "G1": PoleGroupe(id="G1", modules=["M3"], position_x=50, position_y=140),
    "G5": PoleGroupe(id="G5", modules=["M4", "M5"], position_x=160, position_y=140),
    "G2": PoleGroupe(id="G2", modules=["M6"], position_x=310, position_y=140),
    "G6": PoleGroupe(id="G6", modules=["M7", "M8"], position_x=420, position_y=140),
    "G3": PoleGroupe(id="G3", modules=["M9"], position_x=620, position_y=140),
    "G7": PoleGroupe(id="G7", modules=["M10", "M11"], position_x=730, position_y=140),
    "G4": PoleGroupe(id="G4", modules=["M12"], position_x=930, position_y=140),
    "G9": PoleGroupe(id="G9", modules=["M13"], position_x=200, position_y=320),
    "G10": PoleGroupe(id="G10", modules=["M14"], position_x=780, position_y=320),
}

CONTACTEURS_KM: Dict[str, Contacteur] = {
    "K1": Contacteur(id="K1", label="212/KM1-2", position_x=70, position_y=260),
    "K2": Contacteur(id="K2", label="212/KM3-4", position_x=150, position_y=260),
    "K3": Contacteur(id="K3", label="213/KM1-2", position_x=290, position_y=260),
    "K4": Contacteur(id="K4", label="213/KM3-4", position_x=430, position_y=260),
    "K5": Contacteur(id="K5", label="214/KM1-2", position_x=600, position_y=260),
    "K6": Contacteur(id="K6", label="214/KM3-4", position_x=740, position_y=260),
    "K7": Contacteur(id="K7", label="215/KM1-2", position_x=880, position_y=260),
    "K8": Contacteur(id="K8", label="215/KM3-4", position_x=960, position_y=260),
    "K9": Contacteur(id="K9", label="212/KM5-6", position_x=130, position_y=420),
    "K10": Contacteur(id="K10", label="213/KM5-6", position_x=330, position_y=420),
    "K11": Contacteur(id="K11", label="214/KM5-6", position_x=710, position_y=420),
    "K12": Contacteur(id="K12", label="215/KM5-6", position_x=910, position_y=420),
}

CONTACTEURS_P: Dict[str, Contacteur] = {
    "P1": Contacteur(id="P1", position_x=70, position_y=420),
    "P2": Contacteur(id="P2", position_x=400, position_y=420),
    "P3": Contacteur(id="P3", position_x=640, position_y=420),
    "P4": Contacteur(id="P4", position_x=980, position_y=420),
}

PDC_STATUS_LIST: Dict[str, PDCStatus] = {
    "PDC1": PDCStatus(id="PDC1", position_x=50, position_y=550),
    "PDC2": PDCStatus(id="PDC2", position_x=300, position_y=550),
    "PDC3": PDCStatus(id="PDC3", position_x=600, position_y=550),
    "PDC4": PDCStatus(id="PDC4", position_x=900, position_y=550),
}