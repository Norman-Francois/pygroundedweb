from enum import Enum

class DistortionModel(str, Enum):
    RADIAL_EXTENDED = "RadialExtended"
    RADIAL_BASIC = "RadialBasic"
    FRASER = "Fraser"
    FRASER_BASIC = "FraserBasic"
    FISHEYE_EQUI = "FishEyeEqui"
    HEMI_EQUI = "HemiEqui"
    AUTO_CAL = "AutoCal"
    FIGEE = "Figee"

class ZoomFinal(str, Enum):
    QUICK_MAC = "QuickMac"
    MIC_MAC = "MicMac"
    BIG_MAC = "BigMac"

class TapiocaMode(str, Enum):
    ALL = "All"
    MULSCALE = "MulScale"
