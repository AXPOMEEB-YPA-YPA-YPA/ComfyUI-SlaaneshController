import random
import re

# ==========================================
# 色孽の单人性爱控制 (SlaaneshSoloSexControl) V3.6
# 1. 修复 UI 键名修改导致的参数获取失败 BUG
# 2. 修正 DETAILS_CONFIG 中部分选项资源池映射错误的 BUG
# ==========================================

# ... import 部分 ...

# 【新增】全局 UI 映射字典：存储 "中文短名" -> "完整数据字符串" 的对应关系
GLOBAL_OPTS_MAP = {}

def register_opt(full_text):
    """
    辅助函数：将完整字符串注册到映射表，并返回简洁的中文名
    输入: "01.大腿分开[legs_apart],{m_legs}"
    输出: "01.大腿分开" (同时将映射存入 GLOBAL_OPTS_MAP)
    """
    if not full_text or full_text == "(不指定)":
        return "(不指定)"
    
    # 截取 [ 之前的内容作为短名
    short_name = full_text.split('[')[0].strip()
    
    # 如果没有 [，说明本身就是短名或者格式不对，直接存
    if short_name == full_text:
        GLOBAL_OPTS_MAP[full_text] = full_text
        return full_text
    
    # 存入映射表
    GLOBAL_OPTS_MAP[short_name] = full_text
    return short_name

# ... COMMON_TAGS 定义 ...
# 1. 通用资源池 (Common Tags)
COMMON_TAGS = {
    # --- 手部资源池 ---
    "H01": "01.放额头上[facepalm, hand on own forehead],{arms around neck, w arms}", 
    "H02": "02.放奶子上[hands on own chest],{arms around neck}", 
    "H03": "03.双手抬起[w arms, hands up],{arms around neck}", 
    "H04": "04.抓紧床单[sheet grab],{arms around neck}", 
    "H05": "05.双手比耶[double v, hands up],{arms around neck}", 
    "H06": "06.抬起手臂[arms up, armpits],{arms around neck, w arms}", 
    "H07": "07.放肚子上[hands on own stomach],{arms around neck, w arms}", 
    "H08": "08.手放两侧[arms at side],{arms around neck, hands up, w arms}", 
    "H09": "09.自己开阴[(female masturbation:1.3), (spreading own pussy:1.2)],{arms around neck, fingering}", 
    "H10": "10.环抱脖颈[(arms around neck:1.1)],{w arms}", 
    "H11": "11.锁扣环抱[(arms around neck, hug:1.1), (leg lock:1.1), (knees up:1.1)],{w arms}", 
    "H12": "12.等待受种[(grabbing own thigh:1.1), folded, knees to chest, legs up, spread legs],{arms around neck}", 
    "H13": "13.手放腿上[hands on own thighs],{arms around neck}", 
    "H14": "14.手臂支撑[arm support],{arms around neck, w arms}", 
    "H15": "15.手肘支撑[elbow rest, arm support],{arms around neck, w arms}", 
    "H16": "16.十指相扣[(interlocked fingers:1.1)],{arms around neck}", 
    "H17": "17.被抓手腕[wrist grab, arms at side],{arms around neck}", 
    "H18": "18.被向后拉[arm held back],{arms around neck}", 
    "H19": "19.腿间自慰[female masturbation, hand between legs]", 
    "H20": "20.撸动肉棒[handjob, hand up]", 
    "H21": "21.抚摸睾丸[caressing testicles, hand up]", 
    "H22": "22.双手爱抚[handjob, caressing testicles, hands up]", 
    "H23": "23.撩动头发[hand in hair, tucking hair]", 
    "H24": "24.抓自己奶[grabbing own breast]", 
    "H25": "25.抓自己臀[grabbing own ass]", 
    "H26": "26.双手叉腰[hands on hips]", 
    "H27": "27.手放背后[arm behind back]", 
    "H28": "28.双手捧碗[cupping hands, hand to mouth]",
    
    # --- 腿部资源池 ---
    "L01": "01.大腿分开[legs apart],{legs together, m legs}", 
    "L02": "02.罗圈开腿[bowlegged pose, legs apart],{legs together, m legs}", 
    "L03": "03.M字开腿[m legs, spread legs],{legs together}", 
    "L04": "04.单腿抬高[leg up, spread legs],{legs together}", 
    "L05": "05.种付开腿[(folded:1.1), spread legs, knees to chest, legs up],{legs together}", 
    "L06": "06.双腿环住[(leg lock:1.1), (knees up:1.1)],{legs together}", 
    "L07": "07.大腿并拢[legs together],{legs apart}", 
    "L08": "08.双腿劈叉[(standing split:1.2)],{legs together}", 
    "L09": "09.内八姿势[knees together feet apart],{legs together}", 
    "L10": "10.单膝抬高[knee up, spread legs],{legs together}", 
    "L11": "11.双膝抬高[knees up, spread legs],{legs together}", 
    "L12": "12.鸭子坐姿[wariza]", 
    "L13": "13.双膝跪下[kneeling, legs together]", 
    "L14": "14.正常坐下[sitting, legs together],{kneeling, wariza}", 
    "L15": "15.四肢着地[kneeling, all fours, leaning forward, arched back],{kneeling, wariza}", 
    "L16": "16.侧卧斜躺[(reclining:1.1), on side],{kneeling, wariza}", 
    "L17": "17.分腿站立[standing, legs apart]", 
    "L18": "18.身体前倾[leaning forward, arm support]", 
    "L19": "19.身体后仰[leaning back, legs apart]", 
}

# 2. 自动细节资源池 (Auto Details)
# [重要] 请在此处填入您的提示词，如果留空则不会生成对应细节
AUTO_DETAILS = {
    # --- 1. 插入位置(必须手动) (Group 1 & 4) ---
    "INSERTION_POS": {
        "小穴": "[vaginal],{anal}", # 示例: "01.阴道性交[vaginal_sex],{anal_sex}"
        "菊穴": "[anal],{vaginal}",
        "未插入": "[imminent penetration]", 
    },
    # --- 2. 重度插入(必须手动) (Group 1 & 4) ---
    "HEAVY_INSERTION": {
        "宫颈穿透": "[stomach bulge]", 
    },
    # --- 3. 眼神1 (All Groups) ---
    "EYES_1": {
        "看向观众": "[looking at viewer]", 
        "向下看": "[looking down]", 
        "向上看": "[looking up]", 
        "看向别处": "[looking away]", 
        "回眸": "[looking back]", 
        "啊嘿颜": "[ahegao]",
        "哦齁颜": "[ohogao]", 
        "瞳孔缩小": "[wide-eyed]", 
        "翻白眼": "[rolling eyes]", 
        "空洞双眼": "[empty eyes]", 
        "半闭眼": "[half-closed eyes]",
        "半眯眼": "[narrowed eyes]", 
        "斗鸡眼": "[cross-eyed]", 
        "爱心眼": "[heart-shaped pupils]", 
        "闭一只眼": "[one eye closed]",
        "闭眼": "[(closed eyes:1.1)]"
    },
    # --- 4. 眼神2 (All Groups) ---
    "EYES_2": {
        "看向观众": "[looking at viewer]", 
        "向下看": "[looking down]", 
        "向上看": "[looking up]", 
        "看向别处": "[looking away]", 
        "回眸": "[looking back]", 
        "啊嘿颜": "[ahegao]",
        "哦齁颜": "[ohogao]", 
        "瞳孔缩小": "[wide-eyed]", 
        "翻白眼": "[rolling eyes]", 
        "空洞双眼": "[empty eyes]", 
        "半闭眼": "[half-closed eyes]",
        "半眯眼": "[narrowed eyes]", 
        "斗鸡眼": "[cross-eyed]", 
        "爱心眼": "[heart-shaped pupils]", 
        "闭一只眼": "[one eye closed]",
        "闭眼": "[(closed eyes:1.1)]"
    },
    # --- 5. 表情 (All Groups, 特定屏蔽) ---
    "EXPRESSION": {
        "害羞微笑": "[shy, smile, closed mouth]", 
        "魅惑微笑": "[seductive smile, parted lips]", 
        "张嘴娇喘": "[moaning, gasping, open mouth]", 
        "张嘴吐舌娇喘": "[moaning, gasping, open mouth, tongue out, uvula]", 
        "o型嘴娇喘": "[:o]", 
        "o型嘴吐舌娇喘": "[:o, tongue out]",
        "嘟嘴": "[puckered lips, :o]", 
        "栗子嘴": "[chestnut mouth]", 
        "被操傻笑": "[(fucked silly:1.2), open mouth, crazy smile]", 
        "傻笑吐舌": "[(fucked silly:1.2), open mouth, crazy smile, tongue out, uvula]", 
        "毫无感觉": "[expressionless, parted lips]", 
        "闭嘴忍耐": "[closed mouth, homu]", 
        "微微忍耐": "[parted lips, teeth]", 
        "强行忍耐": "[parted lips, teeth, clenched teeth]", 
        "咬牙切齿": "[disgust, clenched teeth]"
    },
    # --- 5.5. 眉毛 (All Groups) ---
    "EYEBROWS": {
        "V字眉": "[v-shaped eyebrows]", 
        "八字眉": "[raised eyebrows]", 
    },
    # --- 6. 乳摇 (All Groups) ---
    "BREAST_SHAKE": {
        "乳摇": "[bouncing breasts]", 
    },
    # --- 8. 脸红 (All Groups) ---
    "BLUSH": {
        "一点脸红": "[light blush]", 
        "脸红": "[blush]", 
        "更加脸红": "[blush, nose blush]", 
        "满脸红晕": "[full-face blush, nose blush, ear blush]",
    },
    # --- 9. 眼泪口水 (All Groups) ---
    "FLUIDS_FACE": {
        "眼泪": "[tears, teardrop]",
        "口水": "[saliva, drooling]",
        "眼泪口水": "[tears, teardrop, saliva, drooling]",
    },
    # --- 10. 性交射精(必须手动) (Group 1 & 4) ---
    "EJAC_SEX": {
        "小穴射精": "[cum in pussy]", 
        "菊穴射精": "[cum in ass]", 
        "体外射精": "[(projectile cum:1.1), cum on body]", 
        "口内射精": "[cum in mouth]", 
        "口内强力射精": "[cum in mouth, cheek bulge]", 
        "体外颜射": "[facial, bukkake, cum on hair, cum on breasts]", 
    },
    # --- 12. 过量射精(必须手动) (Group 1, 2, 4 - 连锁触发) ---
    "EJAC_EXCESS": {
        "巨量射精": "[excessive cum]", 
    },
    # --- 13. 汗水 (All Groups) ---
    "SWEAT": {
        "还没出汗": "{embedding:lazywet, sweat, sweat drop}", 
        "微微出汗": "[sweat, sweat drop]", 
        "香汗淋漓": "[(very sweaty:1.2), (shiny skin:1.2), (steaming body:1.2), wet, sweat, sweat drop]", 
    },
    # --- 14. 淫水 (All Groups) ---
    "JUICES": {
        "丝丝缕缕": "[pussy juice]", 
        "淫水汩汩": "[pussy juice, (pussy juice trail：1.2), (pussy juice stain:1.1), pussy juice puddle]", 
    },
    # --- 15. 潮吹(必须手动) (All Groups) ---
    "SQUIRT": {
        "盛大潮吹(必须手动)": "[female ejaculation, female orgasm]", 
    },
    # --- 16. 娇颤 (All Groups) ---
    "TWITCH": {
        "娇颤不止": "[twitching, trembling]", 
    },
    # --- 17. 螓首(必须手动) (All Groups) ---
    "HEAD": {
        "歪头": "[head tilt]", 
        "侧头": "[profile]", 
        "仰头": "[(head back:1.2)]", 
    },
    # --- 18. 画面 (All Groups) ---
    "EFFECT": {
        "运动线": "[motion lines, speed lines]", 
        "运动模糊": "[motion blur]",
        "拟声词": "[(sound effects:1.2)]", 
        "特效全家桶": "[(sound effects only:1.2), motion lines, speed lines, motion blur]", 
    },
}

# 3. 核心逻辑树 (Logic Tree) - [已包含 Group 1-4 完整数据]
SOLO_LOGIC_TREE = {
    # ================= Group 1: 插入正戏 =================
    "Group1": {
        "name": "💞插入正戏",
        "poses": {
            # --- 体位 1: 正常位 ---
            "正戏-正常位1234[(missionary:1.2), lying, on back, leaning back, sex, hetero],{gangbang, group sex}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H02","H03","H04","H06","H08","H09","H10","H11","H12","H15"], 
                        "allow_legs": ["L02","L03","L04","L05","L06"]
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H01","H02","H03","H04","H05","H06","H07","H08","H09","H12","H15","H16","H17"], 
                        "allow_legs": ["L02","L03","L04","L05"]
                    },
                    "3.镜头颠倒[(upside-down:1.2)]": {
                        "allow_hands": ["H02","H03","H06","H16"], 
                        "allow_legs": ["L01","L03","L05"] 
                    },
                   "4.正常位第一人称[(pov crotch:1.2), pov, from above]": {
                        "allow_hands": ["H01","H02","H03","H04","H05","H06","H07","H08","H09","H12","H16","H17"], 
                        "allow_legs": ["L02","L03","L04","L05"] 
                    }
                }
            },           
            # --- 体位 2: 弓腰正常位 ---
            "正戏-弓腰正常位124[(missionary:1.2), (body bridge:1.25), arched back, lying, on back, leaning back, sex, hetero],{gangbang, group sex}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H03","H04","H06","H08","H09","H11","H15"], 
                        "allow_legs": ["L02","L03"]
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H01","H03","H04","H06","H08","H09","H15","H16","H17"], 
                        "allow_legs": ["L02","L03"]
                    },
                    "4.正常位第一人称[(pov crotch:1.2), pov, from above]": {
                        "allow_hands": ["H03","H04","H05","H06","H08","H09","H12","H16","H17"], 
                        "allow_legs": ["L02","L03"] 
                    }
                }
            },  
            # --- 体位 3: 侧面位 ---
            "正戏-侧面位15[lying, on side, leaning, sex, hetero],{gangbang, group sex}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H02","H05","H06","H07","H09","H14"], 
                        "allow_legs": ["L03","L04","L07"]
                    },
                    "5.镜头在后仰视[(from below:1.2), (from behind:1.2), (ass focus:1.2)]": {
                        "allow_hands": ["H02","H05","H07","H08","H09","H14"], 
                        "allow_legs": ["L04","L07"]
                    }
                }
            },
            # --- 体位 4: 俯卧位 ---
            "正戏-俯卧位126[(prone bone:1.1), on stomach, sex, hetero], {gangbang, group sex}": {
                "views": {
                    "6.正面镜头[(straight-on:1.2), face focus]": {
                        "allow_hands": ["H02","H03","H04","H18"], 
                        "allow_legs": ["L07"]
                    },
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H02","H03","H04","H18"], 
                        "allow_legs": ["L07"]
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H02","H03","H04","H18"], 
                        "allow_legs": ["L07"]
                    },
                }
            },    
            # --- 体位 5: 狗爬式 ---
            "正戏-狗爬式125678[(doggystyle:1.2), sex from behind, on stomach, kneeling, top-down bottom-up, sex, hetero],{gangbang, group sex, all fours}": {
                "views": {
                    "6.正面镜头[(straight-on:1.2), face focus]": {
                        "allow_hands": ["H02","H03","H04","H18"], 
                        "allow_legs": ["L01"]
                    },
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H03","H04","H18"], 
                        "allow_legs": ["L01"]
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H02","H03","H04","H18"], 
                        "allow_legs": ["L01"]
                    },
                    "5.镜头在后仰视[(from below:1.2), (from behind:1.2), (ass focus:1.2)]": {
                        "allow_hands": ["H03"], 
                        "allow_legs": ["L01"]
                    },
                    "7.正面镜头仰视[(from below:1.2), straight-on, face focus]": {
                        "allow_hands": ["H03","H04","H18"], 
                        "allow_legs": ["L01"]
                    },
                    "8.后入式第一人称[(pov crotch:1.2), pov, ass focus, from behind, from above, backboob]": {
                        "allow_hands": ["H03","H04","H08","H18"], 
                        "allow_legs": ["L01"] 
                    }
                }
            },       
            # --- 体位 6: 后入式 ---
            "正戏-后入式12678[(sex from behind:1.2), doggystyle, kneeling, sex, hetero],{gangbang, group sex}": {
                "views": {
                    "6.正面镜头[(straight-on:1.2), face focus]": {
                        "allow_hands": ["H14","H18"], 
                        "allow_legs": ["L01"]
                    },
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H14","H18"], 
                        "allow_legs": ["L01"]
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H14","H18"], 
                        "allow_legs": ["L01"]
                    },
                    "7.正面镜头仰视[(from below:1.2), straight-on, face focus]": {
                        "allow_hands": ["H14","H18"], 
                        "allow_legs": ["L01"]
                    },
                    "8.后入式第一人称[(pov crotch:1.2), pov, ass focus, from behind, from above, backboob]": {
                        "allow_hands": ["H14","H18"], 
                        "allow_legs": ["L01"] 
                    }
                }
            },    
            # --- 体位 7: 正面骑乘位前倾 ---
            "正戏-正面骑乘位前倾1259[(cowgirl position:1.2), girl on top, leaning forward, sex, hetero],{gangbang, group sex, squatting}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H14","H16"], 
                        "allow_legs": ["L01"]
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H14","H16"], 
                        "allow_legs": ["L01"]
                    },
                    "5.镜头在后仰视[(from below:1.2), (from behind:1.2), (ass focus:1.2)]": {
                        "allow_hands": ["H14"], 
                        "allow_legs": ["L01"]
                    },
                    "9.骑乘位第一人称[(pov crotch:1.2), pov, from below, straight-on]": {
                        "allow_hands": ["H14","H16"], 
                        "allow_legs": ["L01"] 
                    }
                }
            },   
            # --- 体位 8: 正面骑乘位后仰 ---
            "正戏-正面骑乘位后仰19[(cowgirl position:1.2), girl on top, leaning back, arched back, sex, hetero],{gangbang, group sex, squatting}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H05","H09","H14"], 
                        "allow_legs": ["L01"]
                    },
                    "9.骑乘位第一人称[(pov crotch:1.2), pov, from below, straight-on]": {
                        "allow_hands": ["H05","H09","H14"], 
                        "allow_legs": ["L01"] 
                    }
                }
            },   
            # --- 体位 9: 蹲姿骑乘位前倾 ---
            "正戏-蹲姿骑乘位前倾1259[(squatting cowgirl position:1.2), girl on top, leaning forward, sex, hetero],{gangbang, group sex}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H13","H14","H16"], 
                        "allow_legs": ["L01"]
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H13","H14","H16"], 
                        "allow_legs": ["L01"]
                    },
                    "5.镜头在后仰视[(from below:1.2), (from behind:1.2), (ass focus:1.2)]": {
                        "allow_hands": ["H14"], 
                        "allow_legs": ["L01"]
                    },
                    "9.骑乘位第一人称[(pov crotch:1.2), pov, from below, straight-on]": {
                        "allow_hands": ["H13","H14","H16"], 
                        "allow_legs": ["L01"] 
                    }
                }
            },            
            # --- 体位 10: 蹲姿骑乘位后仰 ---
            "正戏-蹲姿骑乘位后仰19[(squatting cowgirl position:1.2), girl on top, leaning back, sex, hetero],{gangbang, group sex}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H05","H09","H14"], 
                        "allow_legs": ["L01"]
                    },
                    "9.骑乘位第一人称[(pov crotch:1.2), pov, from below, straight-on]": {
                        "allow_hands": ["H05","H09","H14"], 
                        "allow_legs": ["L01"] 
                    }
                }
            },               
            # --- 体位 11: 站立正常位 ---
            "正戏-站立正常位15[(standing missionary:1.3), standing sex, standing, standing on one leg, face-to-face, sex, hetero],{gangbang, group sex}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H08","H10","H14"], 
                        "allow_legs": ["L04","L10"]
                    },
                    "5.镜头在后仰视[(from below:1.2), (from behind:1.2), (ass focus:1.2)]": {
                        "allow_hands": ["H08","H10","H14"], 
                        "allow_legs": ["L10"]
                    },
                }
            },    
            # --- 体位 12: 站立后背位 ---
            "正戏-站立后背位1278[(standing sex:1.2), sex from behind, standing, leaning forward, arched back, sex, hetero],{gangbang, group sex}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H03","H06","H08","H13","H14","H18"], 
                        "allow_legs": ["L01","L02","L07","L10"]
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H03","H06","H08","H13","H14","H18"], 
                        "allow_legs": ["L01","L02","L07","L10"]
                    },
                    "7.正面镜头仰视[(from below:1.2), straight-on, face focus]": {
                        "allow_hands": ["H03","H06","H08","H13","H14","H18"], 
                        "allow_legs": ["L01","L02","L07","L10"]
                    },
                    "8.后入式第一人称[(pov crotch:1.2), pov, ass focus, from behind, from above, backboob]": {
                        "allow_hands": ["H14","H18"], 
                        "allow_legs": ["L07"] 
                    }
                }
            },  
            # --- 体位 13: 观音坐莲 ---
            "正戏-观音坐莲127[(suspended congress:1.3), (upright straddle:1.1), sitting, sex, hetero],{gangbang, group sex}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H11"], 
                        "allow_legs": []
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H11"], 
                        "allow_legs": []
                    },
                    "7.正面镜头仰视[(from below:1.2), straight-on, face focus]": {
                        "allow_hands": ["H11"], 
                        "allow_legs": []
                    },
                }
            },  
            # --- 体位 14: 逆观音坐莲 ---
            "正戏-逆观音坐莲1267[(reverse suspended congress:1.3), (reverse upright straddle:1.1), sitting, leaning back, sex, hetero],{gangbang, group sex}": {
                "views": {
                    "6.正面镜头[(straight-on:1.2), face focus]": {
                        "allow_hands": ["H01","H02","H03","H05","H06","H07","H08","H09"], 
                        "allow_legs": ["L03"]
                    }, 
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H01","H02","H03","H05","H06","H07","H08","H09"], 
                        "allow_legs": ["L03"]
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H01","H02","H03","H05","H06","H07","H08","H09"], 
                        "allow_legs": ["L03"]
                    },
                    "7.正面镜头仰视[(from below:1.2), straight-on, face focus]": {
                        "allow_hands": ["H01","H02","H03","H05","H06","H07","H08","H09"], 
                        "allow_legs": ["L03"]
                    },
                }
            },  
            # --- 体位 15: 火车便当 ---
            "正戏-火车便当125[(suspended congress:1.3), standing sex, face-to-face, sex, hetero],{gangbang, group sex}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H10"], 
                        "allow_legs": ["L06","L11"]
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H10"], 
                        "allow_legs": ["L06","L11"]
                    },
                    "5.镜头在后仰视[(from below:1.2), (from behind:1.2), (ass focus:1.2)]": {
                        "allow_hands": ["H10"], 
                        "allow_legs": ["L11"]
                    },
                }
            },  
            # --- 体位 16: 逆火车便当 ---
            "正戏-逆火车便当167[(reverse suspended congress:1.3), standing sex, sex from behind, leaning back, sex, hetero],{full nelson, gangbang, group sex}": {
                "views": {
                    "6.正面镜头[(straight-on:1.2), face focus]": {
                        "allow_hands": ["H01","H02","H03","H05","H06","H08","H09"], 
                        "allow_legs": ["L03"]
                    }, 
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H01","H02","H03","H05","H06","H08","H09"], 
                        "allow_legs": ["L03"]
                    },
                    "7.正面镜头仰视[(from below:1.2), straight-on, face focus]": {
                        "allow_hands": ["H01","H02","H03","H05","H06","H08","H09"], 
                        "allow_legs": ["L03"]
                    },
                }
            },  
            # --- 体位 17: 纳尔逊锁 ---
            "正戏-纳尔逊锁167[(full nelson:1.2), reverse suspended congress, standing sex, sex from behind, sex, hetero],{gangbang, group sex}": {
                "views": {
                    "6.正面镜头[(straight-on:1.2), face focus]": {
                        "allow_hands": [], 
                        "allow_legs": ["L05"]
                    }, 
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": [], 
                        "allow_legs": ["L05"]
                    },
                    "7.正面镜头仰视[(from below:1.2), straight-on, face focus]": {
                        "allow_hands": [], 
                        "allow_legs": ["L05"]
                    },
                }
            },  
            # --- 体位 18: 种付位 ---
            "正戏-种付位12356[(mating press:1.3), lying, on back, boy on top, top-down bottom-up, sex, hetero],{gangbang, group sex}": {
                "views": {
                    "6.正面镜头[(straight-on:1.2), face focus]": {
                        "allow_hands": [], 
                        "allow_legs": ["L05"]
                    }, 
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H06","H12"], 
                        "allow_legs": ["L05"]
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H06","H12"], 
                        "allow_legs": ["L05"]
                    },
                    "5.镜头在后仰视[(from below:1.2), (from behind:1.2), (ass focus:1.2)]": {
                        "allow_hands": ["H12"], 
                        "allow_legs": ["L05"]
                    },
                    "3.镜头颠倒[(upside-down:1.2)]": {
                        "allow_hands": ["H06","H12"], 
                        "allow_legs": ["L05"]
                    },
                }
            },   
        }
    },
    # ================= Group 2: 女方侍奉 (示例) =================
    "Group2": {
        "name": "🫦女方侍奉",
        "poses": {
             "侍奉-即将口交14[penis on face, imminent fellatio],{gangbang, group sex}": {
                 "views": {
                     "1.镜头在侧[(from side:1.2)]": {
                         "allow_hands": ["H02","H03","H19","H20","H21","H22","H23","H28"], 
                         "allow_legs": ["L12","L13","L14","L15"]
                     },
                     "4.正常位第一人称[(pov crotch:1.2), pov, from above]": {
                        "allow_hands": ["H02","H03","H14","H20","H23"], 
                        "allow_legs": ["L12","L13","L14","L15","L16"] 
                     }
                 }
             },
             "侍奉-舔舐龟头14[licking penis],{gangbang, group sex}": {
                 "views": {
                     "1.镜头在侧[(from side:1.2)]": {
                         "allow_hands": ["H02","H03","H19","H20","H21","H22","H23"], 
                         "allow_legs": ["L12","L13","L14","L15"]
                     },
                     "4.正常位第一人称[(pov crotch:1.2), pov, from above]": {
                        "allow_hands": ["H02","H03","H14","H20","H23"], 
                        "allow_legs": ["L12","L13","L14","L15","L16"] 
                     }
                 }
             },
             "侍奉-口交含弄14[oral, fellatio],{:>=, gangbang, group sex}": {
                 "views": {
                     "1.镜头在侧[(from side:1.2)]": {
                         "allow_hands": ["H02","H03","H19","H20","H21","H22","H23"], 
                         "allow_legs": ["L12","L13","L14","L15"]
                     },
                     "4.正常位第一人称[(pov crotch:1.2), pov, from above]": {
                        "allow_hands": ["H02","H03","H14","H20","H23"], 
                        "allow_legs": ["L12","L13","L14","L15","L16"] 
                     }
                 }
             },
             "侍奉-鼓嘴口交14[cheek bulge, oral, fellatio],{:>=, gangbang, group sex}": {
                 "views": {
                     "1.镜头在侧[(from side:1.2)]": {
                         "allow_hands": ["H02","H03","H19","H20","H21","H22","H23"], 
                         "allow_legs": ["L12","L13","L14","L15"]
                     },
                     "4.正常位第一人称[(pov crotch:1.2), pov, from above]": {
                        "allow_hands": ["H02","H03","H14","H20","H23"], 
                        "allow_legs": ["L12","L13","L14","L15","L16"] 
                     }
                 }
             },
             "侍奉-强力口交14[:>=, oral, fellatio],{gangbang, group sex}": {
                 "views": {
                     "1.镜头在侧[(from side:1.2)]": {
                         "allow_hands": ["H02","H03","H19","H20","H21","H22","H23"], 
                         "allow_legs": ["L12","L13","L14","L15"]
                     },
                     "4.正常位第一人称[(pov crotch:1.2), pov, from above]": {
                        "allow_hands": ["H02","H03","H14","H20","H23"], 
                        "allow_legs": ["L12","L13","L14","L15","L16"] 
                     }
                 }
             },
             "侍奉-深喉口交14[deepthroat, irrumatio, oral, fellatio],{gangbang, group sex}": {
                 "views": {
                     "1.镜头在侧[(from side:1.2)]": {
                         "allow_hands": ["H03","H19","H21"], 
                         "allow_legs": ["L12","L13","L14","L15"]
                     },
                     "4.正常位第一人称[(pov crotch:1.2), pov, from above]": {
                        "allow_hands": ["H03","H14"], 
                        "allow_legs": ["L12","L13","L14","L15"] 
                     }
                 }
             },
             "侍奉-喂奶撸管1[nursing handjob, breast sucking],{gangbang, group sex}": {
                 "views": {
                     "1.镜头在侧[(from side:1.2)]": {
                         "allow_hands": ["H20"], 
                         "allow_legs": ["L14","L16"]
                     }
                 }
             },
             "侍奉-常规乳交24[paizuri, upper body],{gangbang, group sex}": {
                 "views": {
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H02","H03","H24"], 
                        "allow_legs": ["L13"]
                    },
                    "4.正常位第一人称[(pov crotch:1.2), pov, from above]": {
                        "allow_hands": ["H02","H03","H24"], 
                        "allow_legs": ["L13"] 
                    }
                 }
             },
             "侍奉-乳交舔弄24[paizuri, licking penis, upper body],{gangbang, group sex}": {
                 "views": {
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H02","H03","H24"], 
                        "allow_legs": ["L13"]
                    },
                    "4.正常位第一人称[(pov crotch:1.2), pov, from above]": {
                        "allow_hands": ["H02","H03","H24"], 
                        "allow_legs": ["L13"] 
                    }
                 }
             },
             "侍奉-乳交口交24[paizuri, oral, fellatio, upper body],{gangbang, group sex}": {
                 "views": {
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H02","H03","H24"], 
                        "allow_legs": ["L13"]
                    },
                    "4.正常位第一人称[(pov crotch:1.2), pov, from above]": {
                        "allow_hands": ["H02","H03","H24"], 
                        "allow_legs": ["L13"] 
                    }
                 }
             },
             "侍奉-跨骑乳交134[(straddling paizuri:1.3), lying, on back, boy on top, upper body],{gangbang, group sex}": {
                 "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H02","H03"], 
                        "allow_legs": []
                    },
                    "3.镜头颠倒[(upside-down:1.2)]": {
                        "allow_hands": ["H02","H03","H06"], 
                        "allow_legs": []
                    },
                    "4.正常位第一人称[(pov crotch:1.2), pov, from above]": {
                        "allow_hands": ["H02","H03","H06"], 
                        "allow_legs": []
                    }
                 }
             },
             "侍奉-垂直乳交1[(perpendicular paizuri:1.2), upper body],{gangbang, group sex}": {
                 "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H02","H03","H24"], 
                        "allow_legs": ["L13"]
                    },
                 }
             },   
             "侍奉-69式没口交156[(69:1.2), cunnilingus, licking pussy, girl on top, all fours, sitting on face],{fellatio, gangbang, group sex}": {
                 "views": {
                    "6.正面镜头[(straight-on:1.2), face focus]": {
                        "allow_hands": ["H02","H03","H14","H20","H23","H25"], 
                        "allow_legs": []
                    }, 
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H02","H03","H14","H20","H23","H25"], 
                        "allow_legs": []
                    },
                    "5.镜头在后仰视[(from below:1.2), (from behind:1.2), (ass focus:1.2)]": {
                        "allow_hands": ["H14","H20","H23","H25"], 
                        "allow_legs": []
                    }
                 }
             },   
             "侍奉-69式口交156[(69:1.2), cunnilingus, licking pussy, girl on top, all fours, sitting on face, oral, fellatio],{gangbang, group sex}": {
                 "views": {
                    "6.正面镜头[(straight-on:1.2), face focus]": {
                        "allow_hands": ["H02","H03","H14","H20","H23","H25"], 
                        "allow_legs": []
                    }, 
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H02","H03","H14","H20","H23","H25"], 
                        "allow_legs": []
                    },
                    "5.镜头在后仰视[(from below:1.2), (from behind:1.2), (ass focus:1.2)]": {
                        "allow_hands": ["H14","H20","H23","H25"], 
                        "allow_legs": []
                    }
                 }
             }, 
             "侍奉-坐着足交210[footjob, girl on top, sitting, leaning back],{gangbang, group sex}": {
                 "views": {
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": [], 
                        "allow_legs": ["L01","L09"]
                    },
                    "10.足交特写[from below, from behind, (foot focus:1.2)]": {
                        "allow_hands": [], 
                        "allow_legs": ["L01","L09"]
                    },
                 }
             },  
             "侍奉-站着足交10[footjob, girl on top, standing, knee up],{gangbang, group sex}": {
                 "views": {
                    "10.足交特写[from below, from behind, (foot focus:1.2)]": {
                        "allow_hands": ["H03","H08","H26"], 
                        "allow_legs": []
                    },
                 }
             },     
        }
    },
    # ================= Group 3: 前戏爱抚 (示例) =================
    "Group3": {
        "name": "🖕🏿前戏爱抚",
        "poses": {
             "前戏-手指爱抚1567[clitoral stimulation, fingering],{gangbang, group sex}": {
                 "views": {
                    "6.正面镜头[(straight-on:1.2), face focus]": {
                         "allow_hands": [], 
                         "allow_legs": ["L15","L17","L19"]
                    },
                    "1.镜头在侧[(from side:1.2)]": {
                         "allow_hands": [], 
                         "allow_legs": ["L15","L17","L18","L19"]
                    },
                    "5.镜头在后仰视[(from below:1.2), (from behind:1.2), (ass focus:1.2)]": {
                         "allow_hands": [], 
                         "allow_legs": ["L15","L17","L18"]
                    },
                    "7.正面镜头仰视[(from below:1.2), straight-on, face focus]": {
                         "allow_hands": [], 
                         "allow_legs": ["L17","L19"]
                    },
                 }
             },
             "前戏-手指插入1567[fingering],{gangbang, group sex}": {
                 "views": {
                    "6.正面镜头[(straight-on:1.2), face focus]": {
                         "allow_hands": [], 
                         "allow_legs": ["L15","L17","L19"]
                    },
                    "1.镜头在侧[(from side:1.2)]": {
                         "allow_hands": [], 
                         "allow_legs": ["L15","L17","L18","L19"]
                    },
                    "5.镜头在后仰视[(from below:1.2), (from behind:1.2), (ass focus:1.2)]": {
                         "allow_hands": [], 
                         "allow_legs": ["L15","L17","L18"]
                    },
                    "7.正面镜头仰视[(from below:1.2), straight-on, face focus]": {
                         "allow_hands": [], 
                         "allow_legs": ["L17","L19"]
                    },
                 }
             },
             "前戏-玩具爱抚1567[nipple stimulation, clitoral stimulation, holding vibrator, vibrator, hitachi magic wand, vaginal object insertion, anal beads, anal object insertion, egg vibrator],{gangbang, group sex}": {
                 "views": {
                    "6.正面镜头[(straight-on:1.2), face focus]": {
                         "allow_hands": [], 
                         "allow_legs": ["L15","L17","L19"]
                    },
                    "1.镜头在侧[(from side:1.2)]": {
                         "allow_hands": [], 
                         "allow_legs": ["L15","L17","L18","L19"]
                    },
                    "5.镜头在后仰视[(from below:1.2), (from behind:1.2), (ass focus:1.2)]": {
                         "allow_hands": [], 
                         "allow_legs": ["L15","L17","L18"]
                    },
                    "7.正面镜头仰视[(from below:1.2), straight-on, face focus]": {
                         "allow_hands": [], 
                         "allow_legs": ["L17","L19"]
                    },
                 }
             },
             "前戏-吮吸阴蒂1567[cunnilingus, licking pussy],{gangbang, group sex}": {
                 "views": {
                    "6.正面镜头[(straight-on:1.2), face focus]": {
                         "allow_hands": [], 
                         "allow_legs": ["L17","L19"]
                    },
                    "1.镜头在侧[(from side:1.2)]": {
                         "allow_hands": [], 
                         "allow_legs": ["L15","L17","L18","L19"]
                    },
                    "5.镜头在后仰视[(from below:1.2), (from behind:1.2), (ass focus:1.2)]": {
                         "allow_hands": [], 
                         "allow_legs": ["L18"]
                    },
                    "7.正面镜头仰视[(from below:1.2), straight-on, face focus]": {
                         "allow_hands": [], 
                         "allow_legs": ["L15","L17","L19"]
                    },
                 }
             },
             "前戏-亵玩奶子167[grabbing another's breast, nipple stimulation, breast sucking, licking nipple, nipple tweak],{gangbang, group sex}": {
                 "views": {
                    "6.正面镜头[(straight-on:1.2), face focus]": {
                         "allow_hands": [], 
                         "allow_legs": ["L17","L19"]
                    },
                    "1.镜头在侧[(from side:1.2)]": {
                         "allow_hands": [], 
                         "allow_legs": ["L17","L19"]
                    },
                    "7.正面镜头仰视[(from below:1.2), straight-on, face focus]": {
                         "allow_hands": [], 
                         "allow_legs": ["L17","L19"]
                    },
                 }
             },
        }
    },
    # ================= Group 4: 拘束捆绑 (示例) =================
    "Group4": {
        "name": "🔗拘束捆绑",
        "poses": {
            "🪢捆绑绳缚-正常位1234[(shibari:1.1), breast bondage, bound arms, bound legs, frogtie, missionary, metal collar, bound wrists, lying, on back, leaning back, sex, hetero],{gangbang, group sex}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H06","H27"], 
                        "allow_legs": ["L03"]
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H06","H27"], 
                        "allow_legs": ["L03"]
                    },
                    "3.镜头颠倒[(upside-down:1.2)]": {
                        "allow_hands": ["H06","H27"], 
                        "allow_legs": ["L03"]
                    },
                    "4.正常位第一人称[(pov crotch:1.2), pov, from above]": {
                        "allow_hands": ["H06","H27"], 
                        "allow_legs": ["L03"]
                    }
                }
            },   
            "🩹捆绑胶带-正常位1234[(tape:1.1), breast bondage, bound arms, bound legs, frogtie, missionary, metal collar, bound wrists, lying, on back, leaning back, sex, hetero],{rope, gangbang, group sex}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H06","H27"], 
                        "allow_legs": ["L03"]
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H06","H27"], 
                        "allow_legs": ["L03"]
                    },
                    "3.镜头颠倒[(upside-down:1.2)]": {
                        "allow_hands": ["H06","H27"], 
                        "allow_legs": ["L03"]
                    },
                    "4.正常位第一人称[(pov crotch:1.2), pov, from above]": {
                        "allow_hands": ["H06","H27"], 
                        "allow_legs": ["L03"]
                    }
                }
            },   
            "⛓️捆绑锁链-正常位1234[(chain, chained:1.1), breast bondage, bound arms, bound legs, frogtie, missionary, metal collar, bound wrists, lying, on back, leaning back, sex, hetero],{rope, gangbang, group sex}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H06","H27"], 
                        "allow_legs": ["L03"]
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H06","H27"], 
                        "allow_legs": ["L03"]
                    },
                    "3.镜头颠倒[(upside-down:1.2)]": {
                        "allow_hands": ["H06","H27"], 
                        "allow_legs": ["L03"]
                    },
                    "4.正常位第一人称[(pov crotch:1.2), pov, from above]": {
                        "allow_hands": ["H06","H27"], 
                        "allow_legs": ["L03"]
                    }
                }
            },  
            "⛓️捆绑锁链-完全固定种付位1256[restrained, stationary restraints, bound ankles, bound wrists, bound arms, bound legs, frogtie, missionary, metal collar, mating press, lying, on back, boy on top, top-down bottom-up, sex, hetero],{rope, gangbang, group sex}": {
                "views": {
                    "6.正面镜头[(straight-on:1.2), face focus]": {
                        "allow_hands": ["H06"], 
                        "allow_legs": ["L05"]
                    }, 
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H06"], 
                        "allow_legs": ["L05"]
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H06"], 
                        "allow_legs": ["L05"]
                    },
                    "5.镜头在后仰视[(from below:1.2), (from behind:1.2), (ass focus:1.2)]": {
                        "allow_hands": ["H06"], 
                        "allow_legs": ["L05"]
                    }
                }
            },            
            "🪢捆绑绳缚-后入式125678[(shibari:1.1), breast bondage, bound wrists, bound arms, sex from behind, doggystyle, kneeling, sex, hetero],{gangbang, group sex}": {
            "views": {
                    "6.正面镜头[(straight-on:1.2), face focus]": {
                        "allow_hands": ["H27"], 
                        "allow_legs": ["L01","L07"]
                    },
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H27"], 
                        "allow_legs": ["L01","L07"]
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H27"], 
                        "allow_legs": ["L01","L07"]
                    },
                    "5.镜头在后仰视[(from below:1.2), (from behind:1.2), (ass focus:1.2)]": {
                        "allow_hands": ["H27"], 
                        "allow_legs": ["L01","L07"]
                    },
                    "7.正面镜头仰视[(from below:1.2), straight-on, face focus]": {
                        "allow_hands": ["H27"], 
                        "allow_legs": ["L01","L07"]
                    },
                    "8.后入式第一人称[(pov crotch:1.2), pov, ass focus, from behind, from above, backboob]": {
                        "allow_hands": ["H27"], 
                        "allow_legs": ["L01","L07"]
                    }
                }
            },   
            "⛓️捆绑锁链-后入式125678[(chain, chained:1.1), breast bondage, bound wrists, bound arms, sex from behind, doggystyle, kneeling, sex, hetero],{rope, gangbang, group sex}": {
            "views": {
                    "6.正面镜头[(straight-on:1.2), face focus]": {
                        "allow_hands": ["H27"], 
                        "allow_legs": ["L01","L07"]
                    },
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H27"], 
                        "allow_legs": ["L01","L07"]
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H27"], 
                        "allow_legs": ["L01","L07"]
                    },
                    "5.镜头在后仰视[(from below:1.2), (from behind:1.2), (ass focus:1.2)]": {
                        "allow_hands": ["H27"], 
                        "allow_legs": ["L01","L07"]
                    },
                    "7.正面镜头仰视[(from below:1.2), straight-on, face focus]": {
                        "allow_hands": ["H27"], 
                        "allow_legs": ["L01","L07"]
                    },
                    "8.后入式第一人称[(pov crotch:1.2), pov, ass focus, from behind, from above, backboob]": {
                        "allow_hands": ["H27"], 
                        "allow_legs": ["L01","L07"]
                    }
                }
            },   
            "⛓️捆绑锁链-首枷固定后入式127[(pillory:1.2), stationary restraints, sex from behind, doggystyle, kneeling, sex, hetero],{rope, gangbang, group sex}": {
            "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H03"], 
                        "allow_legs": ["L01","L07"]
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H03"], 
                        "allow_legs": ["L01","L07"]
                    },
                    "7.正面镜头仰视[(from below:1.2), straight-on, face focus]": {
                        "allow_hands": ["H03"], 
                        "allow_legs": ["L01","L07"]
                    },
                }
            },   
            "🪢捆绑绳缚-绳缚悬空后入式127[(shibari:1.1), (suspension:1.1), stationary restraints, breast bondage, bound arms, bound legs, frogtie, sex from behind, metal collar, bound wrists, sex, hetero],{gangbang, group sex}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H27"], 
                        "allow_legs": ["L03"]
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H27"], 
                        "allow_legs": ["L03"]
                    },
                    "7.正面镜头仰视[(from below:1.2), straight-on, face focus]": {
                        "allow_hands": ["H27"], 
                        "allow_legs": ["L03"]
                    },
                }
            }, 
            "⛓️捆绑锁链-锁链悬空后入式127[(chain, chained:1.1), (suspension:1.1), stationary restraints, breast bondage, bound arms, bound legs, frogtie, sex from behind, metal collar, bound wrists, sex, hetero],{rope, gangbang, group sex}": {
                "views": {
                    "1.镜头在侧[(from side:1.2)]": {
                        "allow_hands": ["H27"], 
                        "allow_legs": ["L03"]
                    },
                    "2.镜头在上[(from above:1.2)]": {
                        "allow_hands": ["H27"], 
                        "allow_legs": ["L03"]
                    },
                    "7.正面镜头仰视[(from below:1.2), straight-on, face focus]": {
                        "allow_hands": ["H27"], 
                        "allow_legs": ["L03"]
                    },
                }
            },             
        }
    },
}
# ==============================================================================
# 辅助函数：UI 选项生成
# ==============================================================================
def get_all_options(tree):
    groups = [data["name"] for key, data in tree.items()]
    poses = ["(不指定)"]
    views = ["(不指定)"]
    hands_keys = set()
    legs_keys = set()
    
    for g_data in tree.values():
        for p_key, p_data in g_data["poses"].items():
            # 【修改】注册并添加短名
            poses.append(register_opt(p_key)) 
            for v_key, v_data in p_data["views"].items():
                # 【修改】注册并添加短名
                views.append(register_opt(v_key))
                for h in v_data.get("allow_hands", []): hands_keys.add(h)
                for l in v_data.get("allow_legs", []): legs_keys.add(l)
    
    # 【修改】手部和腿部也经过 register_opt 处理
    hands_list = ["(不指定)"] + [register_opt(COMMON_TAGS[k]) for k in hands_keys if k in COMMON_TAGS]
    legs_list = ["(不指定)"] + [register_opt(COMMON_TAGS[k]) for k in legs_keys if k in COMMON_TAGS]
    
    return sorted(list(set(groups))), list(dict.fromkeys(poses)), list(dict.fromkeys(views)), sorted(hands_list), sorted(legs_list)

def get_detail_options(key):
    pool = AUTO_DETAILS.get(key, {})
    return ["(不指定)"] + sorted(list(pool.keys()))

UI_GROUPS, UI_POSES, UI_VIEWS, UI_HANDS, UI_LEGS = get_all_options(SOLO_LOGIC_TREE)

# ==============================================================================
# 核心节点类定义：SlaaneshSoloSexControl
# ==============================================================================
class SlaaneshSoloSexControl:
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "总开关": ("BOOLEAN", {"default": True, "label_on": "节点开启", "label_off": "节点关闭", "display": "toggle"}), 
                "模式选择": (["🔒 手动指定", "🎲 部分随机(手动优先)", "🔓 完全随机"], {"default": "🎲 部分随机(手动优先)"}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF, "step": 1}),
                "玩法选择(必选)": (UI_GROUPS, {"default": UI_GROUPS[0] if UI_GROUPS else ""}),
                
                # --- 级联菜单 ---
                "体位(可选)": (UI_POSES,),
                "视角(不可单选)": (UI_VIEWS,),
                "手部(不可单选)": (UI_HANDS,),
                "腿部(不可单选)": (UI_LEGS,),
                
                # --- 新增：随机细节 (手动可覆盖) ---
                "插入位置(必须手动)": (get_detail_options("INSERTION_POS"),),
                "重度插入(必须手动)": (get_detail_options("HEAVY_INSERTION"),),
                "眼神1": (get_detail_options("EYES_1"),),
                "眼神2": (get_detail_options("EYES_2"),),
                "表情": (get_detail_options("EXPRESSION"),),
                "眉毛": (get_detail_options("EYEBROWS"),),
                "螓首(必须手动)": (get_detail_options("HEAD"),),
                "乳摇(必须手动)": (get_detail_options("BREAST_SHAKE"),),
                "脸红": (get_detail_options("BLUSH"),),
                "眼泪口水": (get_detail_options("FLUIDS_FACE"),),
                "性交射精(必须手动)": (get_detail_options("EJAC_SEX"),),
                "过量射精(必须手动)": (get_detail_options("EJAC_EXCESS"),),
                "汗水": (get_detail_options("SWEAT"),),
                "淫水": (get_detail_options("JUICES"),),
                "潮吹(必须手动)": (get_detail_options("SQUIRT"),),
                "娇颤": (get_detail_options("TWITCH"),),
                "画面(必须手动)": (get_detail_options("EFFECT"),),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("正面提示词", "负面提示词", "面部提示词")
    FUNCTION = "generate" 
    CATEGORY = "slaaneshcontroller/sex"

    @classmethod
    def IS_CHANGED(s, **kwargs):
        if kwargs.get("总开关") and kwargs.get("模式选择") != "🔒 手动指定":
            return int(kwargs.get("seed", 0))
        return False
    
# ==============================================================================
    # 核心生成逻辑函数 (修复版)
    # ==============================================================================
    def generate(self, **kwargs):
        
        # --- 工具函数 ---
        def parse_tag(text):
            if not text or text == "(不指定)": return "", ""
            pos_match = re.search(r'\[(.*?)\]', text)
            pos = pos_match.group(1).strip() if pos_match else ""
            neg_match = re.search(r'\{(.*?)\}', text) 
            neg = neg_match.group(1).strip() if neg_match else ""
            if not pos and not neg and ":" not in text: pos = text
            return pos, neg

        if not kwargs.get("总开关", True): return ("", "", "")

        mode = kwargs.get("模式选择")
        seed = int(kwargs.get("seed", 0))
        rng = random.Random(seed)
        # [关键修复] 获取参数名必须与 INPUT_TYPES 中定义的完全一致
        selected_group_name = kwargs.get("玩法选择(必选)")
        final_pos_list = []
        final_neg_list = []
        face_pos_list = [] # 新增：面部提示词列表

        # --- 基础逻辑: 确定 Group ---
        current_group_key = None
        for k, v in SOLO_LOGIC_TREE.items():
            if v["name"] == selected_group_name:
                current_group_key = k
                break
        
        if not current_group_key:
            return ("Error: Group Not Found", "", "")
            
        group_data = SOLO_LOGIC_TREE[current_group_key]
        poses_pool = group_data["poses"]

        # === Step 1: 确定体位 (Pose) ===
        if not poses_pool:
            return ("Error: Pose Pool is empty for this group!", "", "")

        selected_pose_key = None
        manual_pose_short = kwargs.get("体位(可选)", "(不指定)")
        # 【新增】通过短名查回完整 Key
        manual_pose_full = GLOBAL_OPTS_MAP.get(manual_pose_short, manual_pose_short)
        
        # 【修改】使用完整 Key 进行判断
        is_manual_pose_valid = manual_pose_full in poses_pool

        if mode == "🔒 手动指定":
            if is_manual_pose_valid: selected_pose_key = manual_pose_full # 赋值完整 Key
        elif mode == "🎲 部分随机(手动优先)":
            if is_manual_pose_valid: selected_pose_key = manual_pose_full
            else: selected_pose_key = rng.choice(list(poses_pool.keys()))
        else: # "💀 完全随机"
            selected_pose_key = rng.choice(list(poses_pool.keys()))

        if not selected_pose_key:
            return ("", "", "")

        p, n = parse_tag(selected_pose_key)
        if p: final_pos_list.append(p)
        if n: final_neg_list.append(n)

        pose_node = poses_pool[selected_pose_key]
        views_pool = pose_node.get("views", {})

        # === Step 2: 确定视角 (View) ===
        if not views_pool:
             selected_view_key = None
        else:
            selected_view_key = None
            manual_view_short = kwargs.get("视角(不可单选)", "(不指定)")
            # 【新增】查回完整 Key
            manual_view_full = GLOBAL_OPTS_MAP.get(manual_view_short, manual_view_short)
            
            is_manual_view_valid = manual_view_full in views_pool
            
            if mode == "🔒 手动指定":
                if is_manual_view_valid: selected_view_key = manual_view_full
            elif mode == "🎲 部分随机(手动优先)":
                if is_manual_view_valid: selected_view_key = manual_view_full
                elif views_pool: selected_view_key = rng.choice(list(views_pool.keys()))
            else:
                if views_pool: selected_view_key = rng.choice(list(views_pool.keys()))

        view_node = None
        if selected_view_key:
            p, n = parse_tag(selected_view_key)
            if p: final_pos_list.append(p)
            if n: final_neg_list.append(n)
            view_node = views_pool[selected_view_key]

        # === Step 3: 确定细节 (Hands/Legs) ===
        skip_legs = False 

        if view_node:
            allowed_hands_keys = view_node.get("allow_hands", [])
            allowed_legs_keys = view_node.get("allow_legs", [])

            # --------- 处理手部 (Hands) ---------
            manual_hand_short = kwargs.get("手部(不可单选)", "(不指定)")
            # 【新增】查回完整 Value
            manual_hand_full = GLOBAL_OPTS_MAP.get(manual_hand_short, manual_hand_short)
            
            manual_hand_key = None
            for k, v in COMMON_TAGS.items():
                if v == manual_hand_full: # 【修改】对比完整字符串
                    manual_hand_key = k
                    break
            
            is_hand_valid = manual_hand_key in allowed_hands_keys
            final_hand_str = ""

            if mode == "🔒 手动指定":
                if is_hand_valid: final_hand_str = manual_hand_full # 【修改】使用完整字符串
            elif mode == "🎲 部分随机(手动优先)":
                if is_hand_valid: final_hand_str = manual_hand_full
                elif allowed_hands_keys and rng.random() < 1: 
                    k = rng.choice(allowed_hands_keys)
                    final_hand_str = COMMON_TAGS[k]
            else: 
                if allowed_hands_keys and rng.random() < 1:
                    k = rng.choice(allowed_hands_keys)
                    final_hand_str = COMMON_TAGS[k]
            
            p, n = parse_tag(final_hand_str)
            if p: final_pos_list.append(p)
            if n: final_neg_list.append(n)

            # [精准避让] 只有抓大腿、锁腿、膝盖贴胸才会跳过腿部
            if p and ("leg_lock" in p or "knees_to_chest" in p or "grabbing_own_thigh" in p):
                skip_legs = True

            # --------- 处理腿部 (Legs) ---------
            if not skip_legs:
                # [关键修复] 获取参数名必须与 INPUT_TYPES 中定义的完全一致
                manual_leg_short = kwargs.get("腿部(不可单选)", "(不指定)")
                # 【新增】查回完整 Value
                manual_leg_full = GLOBAL_OPTS_MAP.get(manual_leg_short, manual_leg_short)
            
                manual_leg_key = None
                for k, v in COMMON_TAGS.items():
                    if v == manual_leg_full: # 【修改】对比完整字符串
                        manual_leg_key = k
                        break
                
                is_leg_valid = manual_leg_key in allowed_legs_keys
                final_leg_str = ""

                # [修复] 修正了这里的缩进和逻辑嵌套错误
                if mode == "🔒 手动指定":
                    if is_leg_valid: final_leg_str = manual_leg_full 
                elif mode == "🎲 部分随机(手动优先)":
                    if is_leg_valid: final_leg_str = manual_leg_full # [修复] 使用 _full 变量
                    elif allowed_legs_keys and rng.random() < 1:
                        k = rng.choice(allowed_legs_keys)
                        final_leg_str = COMMON_TAGS[k]
                else:
                    if allowed_legs_keys and rng.random() < 1:
                        k = rng.choice(allowed_legs_keys)
                        final_leg_str = COMMON_TAGS[k]

                p, n = parse_tag(final_leg_str)
                if p: final_pos_list.append(p)
                if n: final_neg_list.append(n)

        # ----------------------------------------------------------------
        # 4. 增强逻辑: 细节随机 (Auto Details)
        # ----------------------------------------------------------------
        
        # 定义配置表 (key_in_kwargs, pool_key, prob, forbidden_words)
        # 概率为 0 表示必须手动指定，不参与随机
        DETAILS_CONFIG = [
            ("插入位置(必须手动)", "INSERTION_POS", 0, []),
            ("重度插入(必须手动)", "HEAVY_INSERTION", 0, []),
            ("眼神1", "EYES_1", 0.75, []),
            ("眼神2", "EYES_2", 0.75, []),
            ("表情", "EXPRESSION", 0.5, ["fellatio", "kissing penis", "licking_penis"]),
            ("眉毛", "EYEBROWS", 0.5, []),
            ("螓首(必须手动)", "HEAD", 0, []), 
            ("乳摇(必须手动)", "BREAST_SHAKE", 0, []),
            ("脸红", "BLUSH", 0.3, []),
            ("眼泪口水", "FLUIDS_FACE", 0.3, []),
            ("性交射精(必须手动)", "EJAC_SEX", 0, []),
            ("过量射精(必须手动)", "EJAC_EXCESS", 0, []),
            ("汗水", "SWEAT", 0.3, []),
            ("淫水", "JUICES", 0.3, []),
            ("潮吹(必须手动)", "SQUIRT", 0, []),
            ("娇颤", "TWITCH", 0.3, []), 
            ("画面(必须手动)", "EFFECT", 0, []), 
        ]
        
        # 定义需要提取到面部提示词的 Pool Key
        FACE_KEYS = ["EYES_1", "EYES_2", "EXPRESSION", "EYEBROWS", "BLUSH", "FLUIDS_FACE"]

        current_pos_str = ",".join(final_pos_list)
        
        # --- 通用处理循环 ---
        for ui_key, pool_key, prob, forbidden in DETAILS_CONFIG:
            # 1. 检查手动输入
            manual_val = kwargs.get(ui_key, "(不指定)")
            pool = AUTO_DETAILS.get(pool_key, {})
            
            found_val = None
            
            # 2. 手动指定 (最高优先级)
            if manual_val != "(不指定)" and manual_val in pool:
                found_val = pool[manual_val] # 获取实际提示词

            # 3. 如果没手动指定 -> 检查是否允许随机
            elif mode != "🔒 手动指定":
                # 4. 检查屏蔽词
                if not (forbidden and any(w in current_pos_str for w in forbidden)):
                    # 5. 随机触发
                    if rng.random() < prob and pool:
                        keys = list(pool.keys())
                        if keys: # 确保有 Key 可选
                            rand_key = rng.choice(keys)
                            found_val = pool[rand_key]

            # 统一处理找到的提示词
            if found_val:
                p, n = parse_tag(found_val)
                if p: 
                    final_pos_list.append(p)
                    # [新增] 如果属于面部特征，添加到面部提示词列表
                    if pool_key in FACE_KEYS:
                        face_pos_list.append(p)
                        
                if n: final_neg_list.append(n)

        # --- 最终组合 ---
        pos_str = ", ".join(filter(None, final_pos_list))
        neg_str = ", ".join(filter(None, final_neg_list))
        face_str = ", ".join(filter(None, face_pos_list))

        if pos_str: pos_str += ", "
        if neg_str: neg_str += ", "
        if face_str: face_str += ", "

        return (pos_str, neg_str, face_str)

# 注册节点类映射
NODE_CLASS_MAPPINGS = {"SlaaneshSoloSexControl": SlaaneshSoloSexControl}
# 注册节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {"SlaaneshSoloSexControl": "色孽の单人性爱控制V3.7"}
