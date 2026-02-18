import folder_paths
import comfy.samplers

# ==============================================================================
# 定义万能类型 (Any Type)
# ==============================================================================
class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False

any_type = AnyType("*")

# ==============================================================================
# 获取 ComfyUI 内置列表
# ==============================================================================
SAMPLER_LIST = comfy.samplers.KSampler.SAMPLERS
SCHEDULER_LIST = comfy.samplers.KSampler.SCHEDULERS

class FirstKSamplerSettings:
    """
    节点1：一采预测-参数设置 (Bus)
    """
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                # ⚠️【关键修正】
                # Easy-Use 加载器强制要求上游节点必须有一个参数叫 "ckpt_name"。
                "ckpt_name": (folder_paths.get_filename_list("checkpoints"), ),
                
                # 原有参数
                "Steps": ("INT", {"default": 25, "min": 1, "max": 60, "step": 1}),
                "CFG": ("FLOAT", {"default": 5.0, "min": 0.0, "max": 30.0, "step": 0.1}),
                "采样器": (SAMPLER_LIST, ),
                "调度器": (SCHEDULER_LIST, ),
                
                # === 新增参数 ===
                "Token规格化": (["none", "mean", "length", "length+mean"], {"default": "length+mean"}),
                "权重插值方式": (["comfy", "A1111", "comfy++", "compel", "fixed attention"], {"default": "comfy++"}),
                "批次大小": ("INT", {"default": 1, "min": 1, "max": 10, "step": 1}),
                "A1111提示词风格": ("BOOLEAN", {"default": False}),
                
                # === 本次新增：高CFG模式 ===
                "一采二采高CFG模式(自动翻倍当前CFG)": ("BOOLEAN", {"default": False}),
            }
        }

    # 输出端口
    RETURN_TYPES = ("FIRST_PASS_BUS", any_type)
    RETURN_NAMES = ("节点束", "模型名称")
    
    FUNCTION = "pack_params"
    CATEGORY = "CustomConfig"

    def pack_params(self, **kwargs):
        # 打包所有参数到字典，并单独提取 ckpt_name 用于直连
        # kwargs 会自动包含 INPUT_TYPES 里定义的所有新参数
        return (kwargs, kwargs.get("ckpt_name"))


class FirstKSamplerUnpacker:
    """
    节点2：一采预测-数据展开 (Unpack)
    """
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "节点束": ("FIRST_PASS_BUS",),
            }
        }

    RETURN_TYPES = (
        "INT",            
        "FLOAT",          
        "SAMPLER_NAME",   
        "SCHEDULER_NAME",
        # === 新增输出类型 ===
        "STRING",  # Token规格化
        "STRING",  # 权重插值方式
        "INT",     # 批次大小
        "BOOLEAN", # A1111提示词风格
        "BOOLEAN"  # 本次新增：高CFG模式
    )
    
    RETURN_NAMES = (
        "Steps", 
        "CFG", 
        "sampler_name采样器", 
        "scheduler调度器",
        # === 新增输出名称 ===
        "Token规格化",
        "权重插值方式",
        "批次大小",
        "A1111提示词风格",
        "高CFG模式" # 本次新增输出名称
    )

    FUNCTION = "unpack_params"
    CATEGORY = "CustomConfig"

    def unpack_params(self, 节点束):
        # 从字典中提取数据
        return (
            节点束.get("Steps"),
            节点束.get("CFG"),
            节点束.get("采样器"),
            节点束.get("调度器"),
            # === 提取新增数据 ===
            节点束.get("Token规格化"),
            节点束.get("权重插值方式"),
            节点束.get("批次大小"),
            节点束.get("A1111提示词风格"),
            # === 提取本次新增数据 ===
            节点束.get("一采二采高CFG模式(自动翻倍当前CFG)"),
        )