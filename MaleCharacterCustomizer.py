import random
import re

# ==========================================
# 色孽の丑男杆役定制器 (SlaaneshMaleCharacterCustomizer) V2.1
# 1. UI优化：下拉菜单只显示中文，后台自动映射完整Prompt
# 2. 逻辑适配：支持短名输入 -> 长名解析
# ==========================================

# ==============================================================================
# UI 映射辅助系统
# ==============================================================================
# 全局映射字典：存储 "中文短名" -> "完整数据字符串"
GLOBAL_OPTS_MAP = {}

def register_opt(full_text):
    """
    解析并注册选项
    输入: "油腻大叔: [male...]" 或 "1人：[1boy]"
    输出: "油腻大叔" (并将映射存入 GLOBAL_OPTS_MAP)
    """
    if not full_text or full_text == "(不指定)":
        return "(不指定)"
    
    # 策略1：中文冒号分割 (针对 count)
    if "：" in full_text:
        short_name = full_text.split("：", 1)[0].strip()
    # 策略2：英文冒号分割 (针对其他)
    elif ":" in full_text:
        short_name = full_text.split(":", 1)[0].strip()
    # 备用：尝试用 "[" 分割
    elif "[" in full_text:
        short_name = full_text.split("[", 1)[0].strip()
    else:
        short_name = full_text
        
    # 存入映射表
    GLOBAL_OPTS_MAP[short_name] = full_text
    return short_name

# --------------------------------------------------------------------------------
# 数据配置区域
# --------------------------------------------------------------------------------

MALE_CHARACTER_DATA = {
    "count": [
        "(不指定)", 
        "1人：[1boy]", 
        "2人：[2boys, multiple boys]", 
        "3人：[3boys, multiple boys]", 
        "4人：[4boys, multiple boys]", 
        "5人：[5boys, multiple boys]", 
        "6人：[6+boys, multiple boys]"
    ],
    "race": [
        "(不指定)", 
        "油腻大叔: [male, dark-skinned male, ugly man, fat man, stubble, tall, sparse hair, body hair]", 
        "黑人肌霸: [male, dark-skinned male, black skin, muscular, tall, stubble, bald, body hair]", 
        "兽人: [male, orc, ugly man, multicolored skin, tusks, fat man, stubble, tall, bald, body hair]", 
        "哥布林: [male, multicolored skin, goblin, pointed nose, size difference]", 
        "牛头人: [male, minotaur, multicolored skin, fur, muscular, tall]"
    ],
    "face_visibility": [
        "不可见: (不指定)", 
        "可见: [faceless male]"
    ],
    "penis_visibility": [
        "不可见: (不指定)", 
        "可见: [huge penis, veiny penis, dark penis, male pubic hair, large testicles]"
    ],
    "action1": [
        "(不指定)", 
        "抓奶: [grabbing another's breast, open hand]", 
        "掐奶头: [nipple tweak]", 
        "抓腰: [torso grab]", 
        "抓腿: [leg grab]", 
        "打屁股: [spanking]", 
        "抓屁股: [grabbing another's ass]", 
        "绞首: [strangling]", 
        "按脑袋: [head grab]", 
        "抓头发: [grabbing another's hair]"
    ],
    "action2": [
        "(不指定)", 
        "抓奶: [grabbing another's breast, open hand]", 
        "掐奶头: [nipple tweak]", 
        "抓腰: [torso grab]", 
        "抓腿: [holding another's leg]", 
        "打屁股: [spanking]", 
        "抓屁股: [grabbing another's ass]", 
        "绞首: [strangling]", 
        "按脑袋: [head grab]", 
        "抓头发: [grabbing another's hair]"
    ],
}

# 结构: (key, UI显示名, 部分随机模式下的触发概率)
CONFIGURATION = [
    ("count", "人数", 0.0), # 人数永远不随机，必须手动选
    ("race", "种族", 1.0),
    ("face_visibility", "面部可见", 0.5),
    ("penis_visibility", "阴茎可见", 0.5),
    ("action1", "动作1", 0.7),
    ("action2", "动作2", 0.4),
]

class SlaaneshMaleCharacterCustomizer:
    @classmethod
    def INPUT_TYPES(cls):
        required = {
            "总开关": ("BOOLEAN", {"default": True, "label_on": "节点开启", "label_off": "节点关闭", "display": "toggle"}),
            "模式选择": (["🔒 手动指定", "🎲 部分随机(手动优先)", "🔓 完全随机"], {"default": "🎲 部分随机(手动优先)"}),
            "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF, "step": 1}),
        }
        
        # 动态生成 UI 列表 (应用 register_opt)
        for en_key, cn_key, _ in CONFIGURATION:
            raw_list = MALE_CHARACTER_DATA[en_key]
            # 注册并转换为短名列表
            ui_list = [register_opt(x) for x in raw_list]
            required[cn_key] = (ui_list, {"default": ui_list[0]})
        
        return {"required": required}

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("正面提示词", "负面提示词")
    FUNCTION = "generate_prompt"
    CATEGORY = "slaaneshcontroller/character"

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # 只要不是纯手动模式，就强制刷新
        if kwargs.get("总开关") and kwargs.get("模式选择") != "🔒 手动指定":
            return int(kwargs.get("seed", 0))
        return False

    def generate_prompt(self, **kwargs):
        if not kwargs.get("总开关"):
            return ("", "")

        mode = kwargs.get("模式选择")
        seed = int(kwargs.get("seed", 0))
        rng = random.Random(seed)
        pos_parts = []
        neg_parts = []

        def extract(text, target="pos"):
            if not text or "(不指定)" in text: return ""
            if target == "pos":
                match = re.search(r'\[(.*?)\]', text)
                return match.group(1).strip() if match else ""
            else:
                match = re.search(r'\{(.*?)\}', text)
                return match.group(1).strip() if match else ""

        for en_key, cn_key, prob in CONFIGURATION:
            data_list = MALE_CHARACTER_DATA[en_key]
            
            # [关键修改] 获取UI输入(中文短名) -> 映射回完整字符串
            manual_val_short = kwargs.get(cn_key)
            manual_val_full = GLOBAL_OPTS_MAP.get(manual_val_short, manual_val_short)
            
            # 判断是否为手动选择了有效项 (使用完整字符串判断)
            is_manually_set = manual_val_full and "(不指定)" not in manual_val_full
            final_tag_raw = ""

            # --- 逻辑分支 ---
            if mode == "🔓 完全随机":
                # 如果是完全随机，且该项允许随机(prob > 0)，则强制从非默认选项中选一个
                if prob > 0:
                    final_tag_raw = rng.choice(data_list[1:])
                else:
                    # 像“人数”这种 prob 为 0 的，依然遵循手动选择
                    final_tag_raw = manual_val_full

            elif mode == "🎲 部分随机(手动优先)":
                if is_manually_set:
                    final_tag_raw = manual_val_full
                elif prob > 0 and rng.random() < prob:
                    final_tag_raw = rng.choice(data_list[1:])

            else: # 🔒 手动指定
                final_tag_raw = manual_val_full

            # --- 标签提取 ---
            if final_tag_raw:
                p = extract(final_tag_raw, "pos")
                n = extract(final_tag_raw, "neg")
                if p: pos_parts.append(p)
                if n: neg_parts.append(n)

        final_pos = ", ".join(filter(None, pos_parts))
        final_neg = ", ".join(filter(None, neg_parts))
        
        if final_pos: final_pos += ", "
        if final_neg: final_neg += ", "

        return (final_pos, final_neg)

NODE_CLASS_MAPPINGS = {"SlaaneshMaleCharacterCustomizer": SlaaneshMaleCharacterCustomizer}
NODE_DISPLAY_NAME_MAPPINGS = {"SlaaneshMaleCharacterCustomizer": "色孽の丑男杆役定制器 V2.1"}
