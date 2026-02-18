import random
import re

# ==============================================================================
# 色孽の女角色饰品定制器 (SlaaneshAccessoryCustomizer) V1.1
# 更新日志:
# 1. 新增输出 [面部提示词]: 单独输出化妆相关Tag。
# 2. 新增输出 [手部提示词]: 单独输出手饰、手套、指甲油相关Tag。
# ==============================================================================

GLOBAL_OPTS_MAP = {}

def register_opt(full_text):
    if not full_text or full_text == "(不指定)":
        return None
    
    if ":" in full_text:
        short_name = full_text.split(":", 1)[0].strip()
    elif "[" in full_text:
        short_name = full_text.split("[", 1)[0].strip()
    else:
        short_name = full_text
        
    GLOBAL_OPTS_MAP[short_name] = full_text
    return short_name

# ==============================================================================
# 数据字典配置 (Accessory 专用)
# ==============================================================================

FEMALE_CHARACTER_DATA = {
    "makeup": [
        "(不指定)", "唇彩: [lipstick]", "红唇: [lipstick, red lips]", "眼影: [red eyeshadow]", "全妆: [makeup, red eyeshadow, lipstick]", "眉间印记: [forehead mark]", "眉间印记全妆: [makeup, red eyeshadow, lipstick, forehead mark]"
    ],
    "nailpolish": [
        "(不指定)",
        "🔴红色: [red nails]", "🔴深红色: [darkred nails]", "🔴绯红色: [crimson nails]",
        "🟠橙色: [orange nails]", "🟡黄色: [yellow nails]",
        "🟢绿色: [green nails]", "🟢墨绿色: [darkgreen nails]",
        "🔵蓝色: [blue nails]", "🔵天蓝色: [skyblue nails]", "🔵深蓝色: [darkblue nails]", "🔵水蓝色: [aqua nails]",
        "🟣紫色: [purple nails]", "🟣淡紫色: [lavender nails]",
        "🩷粉色: [pink nails]", "🩷深粉色: [deep pink nails]", "🩷亮粉色: [hot pink nails]", "🩷淡粉色: [light pink nails]",
        "🟤棕色: [brown nails]", "🟤米色: [beige nails]",
        "⚫黑色: [black nails]", "⚪白色: [white nails]", "🩶灰色: [gray nails]", "⚪🩶银色: [silver nails]", "✨金色: [gold nails]",

    ],
    "tattoo": [ "(不指定)", "淫纹: [(small glowing pink heart stomach tattoo:1.15)]" ],
    "nippleextra": [ "(不指定)", "乳钉: [nipple piercing]", "乳环: [nipple ring]" ],
    "hairwear1": [
        "(不指定)", "小蝴蝶结: [hair ribbon]", "大蝴蝶结: [hair bow]", "发饰: [hair ornament]", "头花: [hair flower]", "X发饰: [x hair ornament]", "心形发饰: [heart hair ornament]", "蝴蝶发饰: [butterfly hair ornament]", "星星发饰: [star hair ornament]", "月牙发饰: [crescent hair ornament]", "十字发饰: [cross hair ornament]", "小发角: [hairpods]", "雪花发饰: [snowflake hair ornament]", "发卡: [hairclip]", "发管: [hair tubes]", "中式发簪: [hair stick]", "日式发簪: [kanzashi]", "花环: [head wreath]", "月桂冠: [laurel crown]", "皇冠: [crown]", "迷你皇冠: [mini crown]", "头冠: [tiara]", "头环: [circlet]", "发箍: [hairband]", "洛丽塔发带: [lolita hairband]", "蕾丝边饰发带: [lace-trimmed hairband]", "女仆头饰: [maid headdress]", "头纱: [veil]", "面纱: [mouth veil]", "护额: [forehead protector]", "耳罩: [earmuffs]", "耳机: [headphones]", "头上别着护目镜: [goggles on head]", 
    ],
    "hairwear2": [
        "(不指定)", "小蝴蝶结: [hair ribbon]", "大蝴蝶结: [hair bow]", "发饰: [hair ornament]", "头花: [hair flower]", "X发饰: [x hair ornament]", "心形发饰: [heart hair ornament]", "蝴蝶发饰: [butterfly hair ornament]", "星星发饰: [star hair ornament]", "月牙发饰: [crescent hair ornament]", "十字发饰: [cross hair ornament]", "小发角: [hairpods]", "雪花发饰: [snowflake hair ornament]", "发卡: [hairclip]", "发管: [hair tubes]", "发簪: [hair stick]", "发铃: [hair bell]", "兔子饰品: [bunny hair ornament]", "花环: [head wreath]", "月桂冠: [laurel crown]", "皇冠: [crown]", "迷你皇冠: [mini crown]", "头冠: [tiara]", "头环: [circlet]", "发箍: [hairband]", "洛丽塔发带: [lolita hairband]", "蕾丝边饰发带: [lace-trimmed hairband]", "女仆头饰: [maid headdress]", "头纱: [veil]", "面纱: [mouth veil]", "护额: [forehead protector]", "耳罩: [earmuffs]", "耳机: [headphones]", "头上别着护目镜: [goggles on head]", 
    ],
    "hat": [
        "(不指定)", "迷你礼帽: [mini top hat]", "钟形女帽: [cloche hat]", "贝雷帽: [beret]", "驻军帽: [garrison cap]", "侦探帽: [cabbie hat]", "草帽: [straw hat]", "泡泡帽: [bobblehat]", "鸭舌帽: [flat cap]", "反带帽: [backwards hat]", "水手帽: [sailor hat]", "大盖帽: [peaked cap]", "魔女帽: [witch hat]", "宽檐帽: [wide brim hat]", 
    ],
    "eyewear": [
        "(不指定)", "眼镜别头上: [eyewear on head]", "有框眼镜: [under-rim eyewear]", "半框眼镜: [semi-rimless eyewear]", "无框眼镜: [rimless eyewear]", "墨镜: [sunglasses]", "护目镜: [goggles]"
    ],
    "earrings": [
        "(不指定)", "十字耳环: [cross earrings]", "水晶耳环: [crystal earrings]", "花耳环: [flower earrings]", "心形耳环: [heart earrings]", "环状耳环: [hoop earrings]", "流苏耳环: [tassel earrings]", "星形耳环: [star earrings]", "耳钉: [stud earrings]", "珍珠耳环: [pearl earrings]", "耳骨夹: [ear cuff]"
    ],
    "neckwear": [
        "(不指定)", "方巾: [kerchief]", "格子围巾: [plaid scarf]", "条纹围巾: [striped scarf]", "印花围巾: [print scarf]", "菱形围巾: [argyle scarf]", "皮草围巾: [fur scarf]", "脖子上护目镜: [goggles around neck]", "脖子上的耳机: [headphones around neck]", "领带: [necktie]", "领结: [bowtie]", "十字项链: [cross necklace]", "珍珠项链: [pearl necklace]", "新月项链: [crescent necklace]", "宝石项链: [gem necklace]", "颈丝带: [ribbon choker]", "项部装饰: [choker]", "皮带项圈: [belt collar]", "金属项圈: [metal collar]", "蕾丝项圈: [lace choker]", "钉刺项圈: [spiked choker]"
    ],
    "handwear": [
        "(不指定)", "珠子手链: [bead bracelet]", "手镯: [bracelet]", "花手镯: [flower bracelet]", "带钉手镯: [spiked bracelet]", "腕带: [wristband]", "手套: [gloves]", "单手套: [single glove]", "单手戴着过肘的手套: [single elbow glove]", "长手套: [elbow gloves]", "短手套: [half gloves]", "露指手套: [fingerless gloves]", "部分露指手套: [partially fingerless gloves]", "毛爪手套: [paw gloves]", "毛边手套: [fur-trimmed gloves]", "乳胶手套: [latex gloves]", "蕾丝边手套: [lace-trimmed gloves]", "花边手套: [frilled gloves]", "皮手套: [leather gloves]", "戒指: [ring]", "婚戒: [wedding ring]", "新娘长手套: [bridal gauntlets]", "袖口: [wrist cuffs]", 
    ],
}

COLOR_DATA = {
    "hat_col": [
        "(不指定)", "⚫黑色: [black]", "⚪白色: [white]", "🩶灰色: [gray]", "🔴红色: [red]", "🔵蓝色: [blue]", "🟤棕色: [brown]", "🩷粉色: [pink]", "🟢绿色: [green]", "🟣紫色: [purple]", "🟡黄色: [yellow]", "🟠橙色: [orange]", "🟤米色: [beige]", "🔷藏青: [navy blue]"
    ]
}

CONSOLIDATED_DATA = {
    "FEMALE_CHARACTER_DATA": FEMALE_CHARACTER_DATA,
    "hat_col": COLOR_DATA["hat_col"]
}

# ==============================================================================
# 饰品配置列表
# ==============================================================================
ACCESSORY_CONFIG = [
    ("makeup", "化妆", None, None, None),
    ("tattoo", "纹身/淫纹", None, None, None),
    ("nippleextra", "乳饰", None, None, None), 
    ("hat", "帽子", "hat_col", "帽子颜色", "hat_col"),
    ("hairwear1", "发饰1", None, None, None),
    ("hairwear2", "发饰2", None, None, None),
    ("eyewear", "眼镜", None, None, None),
    ("earrings", "耳环", None, None, None), 
    ("neckwear", "颈饰", None, None, None),
    ("handwear", "手饰/手套", None, None, None),
    ("nailpolish", "指甲油", None, None, None),
]

def extract_tag(text, target="pos"):
    if not text or "(不指定)" in text or "🎲" in text: return ""
    if target == "pos":
        match = re.search(r'\[(.*?)\]', text)
        return match.group(1).strip() if match else ""
    else:
        match = re.search(r'\{(.*?)\}', text)
        return match.group(1).strip() if match else ""

def enforce_str(tag):
    return tag if tag else ""

class SlaaneshAccessoryCustomizer:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        required_inputs = {
            "总开关": ("BOOLEAN", {"default": True, "label_on": "节点开启", "label_off": "节点关闭", "display": "toggle"}), 
            "模式选择": (["🔒 手动指定", "🎲 部分随机(手动优先)", "🔓 完全随机"], {"default": "🎲 部分随机(手动优先)"}),
            "出图模式": (["头像 (Portrait)", "上半身 (Upper Body)", "胸像 (Breast Focus)", "中景 (Cowboy Shot)", "下半身 (Lower Body)", "全身 (Full Body)"], {"default": "全身 (Full Body)"}),
        }

        for item_en_key, item_cn_key, color_en_key, color_cn_key, color_data_source in ACCESSORY_CONFIG:
            required_inputs[f"启用_{item_cn_key}"] = ("BOOLEAN", {"default": False, "label_on": "开启", "label_off": "关闭"})
            
            raw_list = FEMALE_CHARACTER_DATA.get(item_en_key, ["(不指定)"])
            clean_list = [x for x in raw_list if x != "(不指定)"]
            ui_list = ["🎲 随机"] + [register_opt(x) for x in clean_list if x]
            required_inputs[item_cn_key] = (ui_list,)
            
            if color_cn_key:
                raw_color_list = CONSOLIDATED_DATA.get(color_data_source, ["(不指定)"])
                clean_color_list = [x for x in raw_color_list if x != "(不指定)"]
                ui_color_list = ["🎲 随机"] + [register_opt(x) for x in clean_color_list if x]
                required_inputs[color_cn_key] = (ui_color_list,)

        return {
            "required": required_inputs,
            "optional": {
                "构图提示词_Link": ("STRING", {"forceInput": True}),
            }
        }

    # [修改] 增加了第3、第4个输出类型
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    # [修改] 增加了第3、第4个输出名称
    RETURN_NAMES = ("正面提示词", "负面提示词", "面部提示词", "手部提示词")
    FUNCTION = "process_accessory"
    CATEGORY = "slaaneshcontroller/character"

    @classmethod
    def IS_CHANGED(s, **kwargs):
        if kwargs.get("总开关") or kwargs.get("模式选择") != "🔒 手动指定":
            return float("nan") 
        return False

    def process_accessory(self, **kwargs):
        # [修改] 返回值增加空占位
        if not kwargs.get("总开关", False): return ("", "", "", "")

        pos_parts = []
        neg_parts = []
        face_parts = [] # [新增] 用于存储面部提示词
        hand_parts = [] # [新增] 用于存储手部提示词
        
        mode = kwargs.get("模式选择", "🔒 手动指定")
        
        # 联动逻辑
        shot_mode = kwargs.get("出图模式", "全身 (Full Body)")
        framing_input = kwargs.get("构图提示词_Link", "")
        
        if framing_input and isinstance(framing_input, str) and framing_input.strip() != "":
            if "face" in framing_input or "close-up" in framing_input:
                shot_mode = "头像 (Portrait)"
            elif "upper body" in framing_input:
                shot_mode = "上半身 (Upper Body)"
            elif "breast focus" in framing_input:
                shot_mode = "胸像 (Breast Focus)"
            elif "cowboy shot" in framing_input:
                shot_mode = "中景 (Cowboy Shot)"
            elif "lower body" in framing_input:
                shot_mode = "下半身 (Lower Body)"
            elif "full body" in framing_input:
                shot_mode = "全身 (Full Body)"

        # 智能屏蔽列表
        blocked_slots = []
        if "头像" in shot_mode:
            # 头像屏蔽手饰和指甲
            blocked_slots = ["handwear", "nailpolish"]
        # 其他模式暂不需要严格屏蔽头部饰品(如上半身/胸像)，
        # 但如果是“下半身”模式，通常应该屏蔽头部饰品：
        if "下半身" in shot_mode or "胸像" in shot_mode:
            blocked_slots.extend(["makeup", "hat", "hairwear1", "hairwear2", "eyewear", "earrings", "neckwear"])

        for item_en_key, item_cn_key, color_en_key, color_cn_key, color_data_source in ACCESSORY_CONFIG:
            
            is_enabled = kwargs.get(f"启用_{item_cn_key}", False)
            if not is_enabled: continue

            if item_en_key in blocked_slots: continue

            item_val = kwargs.get(item_cn_key, "🎲 随机")
            item_manual = GLOBAL_OPTS_MAP.get(item_val, item_val)
            
            raw_text = ""
            force_random = (mode == "🔓 完全随机")
            
            if not force_random and item_manual != "🎲 随机":
                raw_text = item_manual
            else:
                item_pool = FEMALE_CHARACTER_DATA.get(item_en_key, ["(不指定)"])
                valid_items = [x for x in item_pool if x != "(不指定)"]
                if valid_items:
                    raw_text = random.choice(valid_items)

            raw_color = ""
            if color_en_key:
                color_val = kwargs.get(color_cn_key, "🎲 随机")
                color_manual = GLOBAL_OPTS_MAP.get(color_val, color_val)
                
                if not force_random and color_manual != "🎲 随机":
                    raw_color = color_manual
                elif raw_text:
                    color_pool = CONSOLIDATED_DATA.get(color_data_source, ["(不指定)"])
                    valid_colors = [x for x in color_pool if x != "(不指定)"]
                    if valid_colors:
                        raw_color = random.choice(valid_colors)

            p_item = extract_tag(raw_text, "pos")
            p_color = extract_tag(raw_color, "pos")
            combined = f"{p_color} {p_item}" if (p_color and p_item) else (p_color or p_item)
            
            if combined: 
                combined_str = enforce_str(combined)
                pos_parts.append(combined_str)
                
                # [新增] 分类逻辑
                if item_en_key == "makeup":
                    face_parts.append(combined_str)
                elif item_en_key in ["handwear", "nailpolish"]:
                    hand_parts.append(combined_str)

            n_item = extract_tag(raw_text, "neg")
            n_color = extract_tag(raw_color, "neg")
            if n_item: neg_parts.append(n_item)
            if n_color: neg_parts.append(n_color)

        final_pos = ", ".join(filter(None, pos_parts))
        final_neg = ", ".join(filter(None, neg_parts))
        final_face = ", ".join(filter(None, face_parts)) # [新增]
        final_hand = ", ".join(filter(None, hand_parts)) # [新增]
        
        if final_pos: final_pos += ", "
        if final_neg: final_neg += ", "
        if final_face: final_face += ", "
        if final_hand: final_hand += ", "

        # [修改] 返回增加 final_face, final_hand
        return (final_pos, final_neg, final_face, final_hand)

NODE_CLASS_MAPPINGS = { 
    "SlaaneshAccessoryCustomizer": SlaaneshAccessoryCustomizer
}
NODE_DISPLAY_NAME_MAPPINGS = { 
    "SlaaneshAccessoryCustomizer": "色孽の女角色饰品定制器"
}