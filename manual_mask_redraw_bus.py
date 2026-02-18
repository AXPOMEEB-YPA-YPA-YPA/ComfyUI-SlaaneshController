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

class ManualMaskRedrawSettings:
    """
    节点7：手动蒙版重绘-参数设置 (Bus)
    """
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                # 兼容性必须项
                "ckpt_name": (folder_paths.get_filename_list("checkpoints"), ),
                
                # 基础采样参数
                "Steps": ("INT", {"default": 25, "min": 1, "max": 10000, "step": 1}),
                "CFG": ("FLOAT", {"default": 5.0, "min": 0.0, "max": 100.0, "step": 0.1}),
                "采样器": (SAMPLER_LIST, ),
                "调度器": (SCHEDULER_LIST, ),
                
                # 重绘特有参数
                "降噪度": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "是否自动修复": ("BOOLEAN", {"default": False}),
                "是否保存图像": ("BOOLEAN", {"default": True}),
            }
        }

    # 输出端口
    RETURN_TYPES = ("MANUAL_MASK_BUS", any_type)
    RETURN_NAMES = ("节点束", "模型名称")
    
    FUNCTION = "pack_params"
    CATEGORY = "CustomConfig"

    def pack_params(self, **kwargs):
        # 打包所有参数到字典，并单独提取 ckpt_name 用于直连
        return (kwargs, kwargs.get("ckpt_name"))


class ManualMaskRedrawUnpacker:
    """
    节点8：手动蒙版重绘-数据展开 (Unpack)
    """
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "节点束": ("MANUAL_MASK_BUS",),
            }
        }

    RETURN_TYPES = (
        "INT",            # Steps
        "FLOAT",          # CFG
        "SAMPLER_NAME",   # sampler
        "SCHEDULER_NAME", # scheduler
        "FLOAT",          # denoise
        "BOOLEAN",        # 是否自动修复
        "BOOLEAN"         # 是否保存图像
    )
    
    RETURN_NAMES = (
        "Steps", 
        "CFG", 
        "sampler_name采样器", 
        "scheduler调度器",
        "denoise降噪度",
        "是否自动修复",
        "是否保存图像"
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
            节点束.get("降噪度"),
            节点束.get("是否自动修复"),
            节点束.get("是否保存图像"),
        )