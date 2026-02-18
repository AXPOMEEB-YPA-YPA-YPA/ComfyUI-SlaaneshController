import folder_paths
import comfy.samplers

# ==============================================================================
# 定义万能类型 (Any Type)
# ==============================================================================
class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False

any_type = AnyType("*")

class PartialRedrawSettings:
    """
    节点5：局部重绘-参数设置 (Bus)
    功能：整合模型选择、采样参数、特殊的字符串参数以及加速开关。
    """
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                # 1. 兼容性必须项 (Easy-Use 等加载器需要)
                "ckpt_name": (folder_paths.get_filename_list("checkpoints"), ),
                
                # 2. 基础采样参数
                "Steps": ("INT", {"default": 25, "min": 1, "max": 100, "step": 1}),
                "CFG": ("FLOAT", {"default": 5.0, "min": 0.0, "max": 100.0, "step": 0.1}),
                "采样器": (comfy.samplers.KSampler.SAMPLERS, ),
                "调度器": (comfy.samplers.KSampler.SCHEDULERS, ),
                
                # 3. 局部重绘特有参数 (字符串类型)
                "降噪度": ("STRING", {"default": "0.3|0.3|0.2|0.3", "multiline": False}),
                "置信度": ("STRING", {"default": "0.35|0.5|0.5|0.35", "multiline": False}),
                
                # 4. 加速与保存控制 (源自 Iterative Upscale)
                "WaveSpeed加速开关": ("BOOLEAN", {"default": True}),
                "负面提示词加速开关": ("BOOLEAN", {"default": True}),
                "负面提示词生效范围": ("FLOAT", {"default": 0.8, "min": 0.0, "max": 1.0, "step": 0.05}),
                "是否保存图像": ("BOOLEAN", {"default": True}),
            }
        }

    # 输出端口: 节点束用于传参，模型名称用于直连
    RETURN_TYPES = ("PARTIAL_REDRAW_BUS", any_type)
    RETURN_NAMES = ("节点束", "模型名称")
    
    FUNCTION = "pack_params"
    CATEGORY = "CustomConfig"

    def pack_params(self, **kwargs):
        # 打包所有参数到字典，并单独提取 ckpt_name 用于直连
        return (kwargs, kwargs.get("ckpt_name"))


class PartialRedrawUnpacker:
    """
    节点6：局部重绘-数据展开 (Unpack)
    """
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "节点束": ("PARTIAL_REDRAW_BUS",),
            }
        }

    RETURN_TYPES = (
        "INT",            # Steps
        "FLOAT",          # CFG
        "SAMPLER_NAME",   # sampler
        "SCHEDULER_NAME", # scheduler
        "STRING",         # 降噪度
        "STRING",         # 置信度
        "BOOLEAN",        # WaveSpeed加速开关
        "BOOLEAN",        # 负面提示词加速开关
        "FLOAT",          # 负面提示词生效范围
        "BOOLEAN"         # 是否保存图像
    )
    
    RETURN_NAMES = (
        "Steps", 
        "CFG", 
        "sampler_name采样器", 
        "scheduler调度器",
        "降噪度",
        "置信度",
        "WaveSpeed加速开关",
        "负面提示词加速开关",
        "负面提示词生效范围",
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
            节点束.get("置信度"),
            节点束.get("WaveSpeed加速开关"),
            节点束.get("负面提示词加速开关"),
            节点束.get("负面提示词生效范围"),
            节点束.get("是否保存图像"),
        )