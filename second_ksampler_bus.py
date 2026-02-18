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

class SecondKSamplerSettings:
    """
    节点3：二采润色-参数设置 (Bus)
    """
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                # 兼容性必须项 (Easy-Use 等加载器需要)
                "ckpt_name": (folder_paths.get_filename_list("checkpoints"), ),
                
                # 基础采样参数
                "Steps": ("INT", {"default": 25, "min": 1, "max": 60, "step": 1}),
                "CFG": ("FLOAT", {"default": 5.0, "min": 0.0, "max": 30.0, "step": 0.1}),
                
                # === 修改处：参数名改为中文 ===
                "采样器": (SAMPLER_LIST, ),
                "调度器": (SCHEDULER_LIST, ),
                
                # === 二采特有参数 ===
                "降噪度": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.01}),
                "是否开启放大": ("BOOLEAN", {"default": False}),
                "放大倍率": ("FLOAT", {"default": 1.5, "min": 1.0, "max": 2.0, "step": 0.05}),
                "是否开启图像选择弹窗": ("BOOLEAN", {"default": False}),
            }
        }

    # 输出端口
    RETURN_TYPES = ("SECOND_PASS_BUS", any_type)
    RETURN_NAMES = ("节点束", "模型名称")
    
    FUNCTION = "pack_params"
    CATEGORY = "CustomConfig"

    def pack_params(self, **kwargs):
        # 打包所有参数到字典，并单独提取 ckpt_name 用于直连
        return (kwargs, kwargs.get("ckpt_name"))


class SecondKSamplerUnpacker:
    """
    节点4：二采润色-数据展开 (Unpack)
    """
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "节点束": ("SECOND_PASS_BUS",),
            }
        }

    RETURN_TYPES = (
        "INT",            # Steps
        "FLOAT",          # CFG
        "SAMPLER_NAME",   # sampler
        "SCHEDULER_NAME", # scheduler
        "FLOAT",          # 降噪度
        "BOOLEAN",        # 是否开启放大
        "FLOAT",          # 放大倍率
        "BOOLEAN",        # 是否开启图像选择弹窗
    )
    
    RETURN_NAMES = (
        "Steps", 
        "CFG", 
        "sampler_name采样器", 
        "scheduler调度器",
        "denoise降噪度",
        "是否开启放大",
        "放大倍率",
        "是否开启图像选择弹窗"
    )

    FUNCTION = "unpack_params"
    CATEGORY = "CustomConfig"

    def unpack_params(self, 节点束):
        # 从字典中提取数据（使用修改后的中文键名）
        return (
            节点束.get("Steps"),
            节点束.get("CFG"),
            节点束.get("采样器"), # 修改为读取中文键
            节点束.get("调度器"), # 修改为读取中文键
            节点束.get("降噪度"),
            节点束.get("是否开启放大"),
            节点束.get("放大倍率"),
            节点束.get("是否开启图像选择弹窗"),
        )