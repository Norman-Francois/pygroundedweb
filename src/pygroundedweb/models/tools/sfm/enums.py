from enum import Enum

class DistortionModel(str, Enum):
    """Enum décrivant les modèles de distorsion optique supportés par MicMac."""
    RADIAL_EXTENDED = "RadialExtended"
    RADIAL_BASIC = "RadialBasic"
    FRASER = "Fraser"
    FRASER_BASIC = "FraserBasic"
    FISHEYE_EQUI = "FishEyeEqui"
    HEMI_EQUI = "HemiEqui"
    AUTO_CAL = "AutoCal"
    FIGEE = "Figee"

class ZoomFinal(str, Enum):
    """Enum décrivant les valeurs du paramètre zoom final de MicMac."""
    QUICK_MAC = "QuickMac"
    MIC_MAC = "MicMac"
    BIG_MAC = "BigMac"

class TapiocaMode(str, Enum):
    """Enum décrivant les valeurs possible du paramètre tapioca de MicMac."""
    ALL = "All"
    MULSCALE = "MulScale"
