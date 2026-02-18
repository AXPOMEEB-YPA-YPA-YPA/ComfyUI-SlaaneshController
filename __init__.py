# ==========================================
# 色孽の提示词控制
# ==========================================

from .PoseControl import SlaaneshPoseControl       # 色孽の常规姿势控制
from .SoloSexControl import SlaaneshSoloSexControl # 色孽の单人性爱控制
from .GroupSexControl import SlaaneshGroupSexControl # 色孽の群交轮奸控制
from .MaleCharacterCustomizer import SlaaneshMaleCharacterCustomizer # 色孽の丑男杆役定制器
from .SceneControl import SlaaneshSceneControl # 色孽の地点场景控制
from .BodyCustomizer import SlaaneshBodyCustomizer # 色孽の地点场景控制
from .CostumeCustomizer import SlaaneshCostumeCustomizer # 
from .AccessoryCustomizer import SlaaneshAccessoryCustomizer # 


NODE_CLASS_MAPPINGS = {
    "SlaaneshPoseControl": SlaaneshPoseControl,     # 常规姿势控制
    "SlaaneshSoloSexControl": SlaaneshSoloSexControl, # 单人性爱控制
    "SlaaneshGroupSexControl": SlaaneshGroupSexControl, # 群交轮奸控制
    "SlaaneshMaleCharacterCustomizer": SlaaneshMaleCharacterCustomizer, # 丑男杆役定制器
    "SlaaneshSceneControl": SlaaneshSceneControl, # 地点场景控制
    "SlaaneshBodyCustomizer": SlaaneshBodyCustomizer, # 地点场景控制
    "SlaaneshCostumeCustomizer": SlaaneshCostumeCustomizer,
    "SlaaneshAccessoryCustomizer": SlaaneshAccessoryCustomizer

}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SlaaneshPoseControl": "色孽の常规姿势控制", 
    "SlaaneshSoloSexControl": "色孽の单人性爱控制", 
    "SlaaneshGroupSexControl": "色孽の群交轮奸控制", 
    "SlaaneshMaleCharacterCustomizer": "色孽の丑男杆役定制器", 
    "SlaaneshSceneControl": "色孽の地点场景控制", 
    "SlaaneshBodyCustomizer": "色孽の女角色外观定制器",
    "SlaaneshCostumeCustomizer": "色孽の女角色服装定制器",
    "SlaaneshAccessoryCustomizer": "色孽の女角色饰品定制器"

}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]