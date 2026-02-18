import comfy.samplers

class IterativeUpscaleSettings:
    """
    节点1：迭代放大-参数设置 (Bus)
    功能：设置所有参数，并将其打包成一个字典（Bus）输出。
    """
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "Steps": ("INT", {"default": 25, "min": 1, "max": 60}),
                "CFG": ("FLOAT", {"default": 5.0, "min": 0.0, "max": 30.0, "step": 0.1}),
                "采样器": (comfy.samplers.KSampler.SAMPLERS,),
                "调度器": (comfy.samplers.KSampler.SCHEDULERS,),
                "降噪度": ("FLOAT", {"default": 0.3, "min": 0.0, "max": 1.0, "step": 0.01}),
                "放大倍率": ("FLOAT", {"default": 1.5, "min": 1.0, "max": 2.0, "step": 0.05}),
                "迭代轮数": ("INT", {"default": 3, "min": 1, "max": 5}),
                "细节增强强度": ("FLOAT", {"default": 0.75, "min": 0.0, "max": 1.0, "step": 0.01}),
                "WaveSpeed加速开关": ("BOOLEAN", {"default": True}),
                "负面提示词加速开关": ("BOOLEAN", {"default": True}),
                "负面提示词生效范围": ("FLOAT", {"default": 0.8, "min": 0.0, "max": 1.0, "step": 0.01}),
                "是否保存图像": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("UPSCALE_SETTINGS_BUS",)
    RETURN_NAMES = ("节点束",)
    FUNCTION = "pack_settings"
    CATEGORY = "CustomConfig"

    def pack_settings(self, **kwargs):
        # 将所有参数打包成一个字典
        return (kwargs,)


class IterativeUpscaleUnpacker:
    """
    节点2：迭代放大-数据展开 (Unpack)
    功能：接收总线（Bus），将其拆解为独立的输出端口。
    """
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "节点束": ("UPSCALE_SETTINGS_BUS",),
            }
        }

    RETURN_TYPES = (
        "INT",            # steps
        "FLOAT",          # cfg
        "SAMPLER_NAME",   # sampler_name
        "SCHEDULER_NAME", # scheduler
        "FLOAT",          # denoise
        "FLOAT",          # upscale_by
        "INT",            # iterations
        "FLOAT",          # detail_enhancement
        "BOOLEAN",        # wavespeed_accel
        "BOOLEAN",        # neg_prompt_accel
        "FLOAT",          # neg_accel_range
        "BOOLEAN"         # save_image
    )
    
    RETURN_NAMES = (
        "Steps", 
        "CFG", 
        "sampler_name采样器", 
        "scheduler调度器", 
        "denoise降噪度", 
        "upscale_factor放大倍率", 
        "iteration_steps迭代轮数", 
        "start_end_strength细节增强强度", 
        "WaveSpeed加速开关", 
        "负面提示词加速开关", 
        "负面提示词生效范围", 
        "是否保存图像"
    )

    FUNCTION = "unpack_settings"
    CATEGORY = "CustomConfig"

    def unpack_settings(self, 节点束):
        # 解包字典（使用修改后的中文键名）
        return (
            节点束.get("Steps"),
            节点束.get("CFG"),
            节点束.get("采样器"),
            节点束.get("调度器"),
            节点束.get("降噪度"),
            节点束.get("放大倍率"),
            节点束.get("迭代轮数"),
            节点束.get("细节增强强度"),
            节点束.get("WaveSpeed加速开关"),
            节点束.get("负面提示词加速开关"),
            节点束.get("负面提示词生效范围"),
            节点束.get("是否保存图像"),
        )