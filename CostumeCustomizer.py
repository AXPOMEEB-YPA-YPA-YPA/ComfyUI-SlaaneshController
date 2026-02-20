import random
import re

# ==============================================================================
# 色孽の女角色服装定制器 (SlaaneshCostumeCustomizer) V7.4
# 最终逻辑版: 
# 1. 移除概率，开关即必出。
# 2. 颜色提示词逻辑优化 (后缀模式: red dress / blue shoes)。
# 3. UI顺序调整 (服装优先，配饰在后)。
# ==============================================================================

# ==============================================================================
# UI 映射辅助系统
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
# 数据字典配置 (主要服装专用)
# ==============================================================================

FEMALE_CHARACTER_DATA = {
    "legwear": [
        "(不指定)", 
        "连裤袜: [pantyhose]", 
        "单腿连裤袜: [single leg pantyhose]", 
        "渔网连裤袜: [fishnet pantyhose]", 
        "单腿渔网连裤袜: [fishnet pantyhose, single leg pantyhose]", 
        "丝袜: [thighhighs]", 
        "单腿丝袜: [single thighhigh]", 
        "渔网丝袜: [fishnet thighhighs]", 
        "单腿渔网丝袜: [single thighhigh, fishnets]", 
        "吊带袜: [thighhighs, garter straps]", 
        "渔网吊带袜: [thighhighs, fishnet thighhighs, garter straps]", 
        "中筒袜: [kneehighs]", 
        "泡泡袜: [socks, loose socks]", 
        "短袜: [socks]", 
    ],
    "shoes": [
        "(不指定)", 
        "小皮鞋: [loafers]", 
        "厚底鞋: [platform footwear]", 
        "高跟鞋: [high heels]", 
        "尖头细高跟: [high heels, pointy footwear, stiletto heels], {strappy heels, ankle strap}", 
        "带束带的尖头细高跟: [high heels, pointy footwear, strappy heels, stiletto heels]", 
        "厚底高跟鞋: [platform heels]", 
        "露趾细高跟: [toeless heels, strappy heels, stiletto heels]", 
        "交叉系带鞋: [cross-laced footwear]", 
        "珍妮鞋: [mary janes]", 
        "运动鞋: [sneakers]", 
        "大腿靴: [thigh boots]", 
        "尖头细高跟靴: [thigh boots, high heel boots, pointy footwear, stiletto heels]", 
        "尖头高跟靴: [thigh boots, high heel boots, pointy footwear]", 
        "系带靴: [thigh boots, lace-up boots]", 
        "毛边靴: [thigh boots, fur-trimmed boots]", 
        "马丁靴: [doc martens, platform heels]"
    ],
    "outfits": [
        "(不指定)", 
        "魔法少女1白色: [white dress, (lightpink dress:0.9), magical girl, star hair ornament, wing hair ornament, frilled, detached collar, neck ruff, bowtie, bare shoulders__HEAD__detached sleeves, juliet sleeves, elbow gloves, strapless shirt, navel cutout, backless outfit, two-tone dress__UPPER__layered skirt, miniskirt, frilled skirt, white skirt, back bow, pink bow, thigh boots, white shoes__LEG__high heel boots]",
        "魔法少女1黑色: [black dress, (red dress:0.9), magical girl, star hair ornament, wing hair ornament, frilled, detached collar, neck ruff, bowtie, bare shoulders__HEAD__detached sleeves, juliet sleeves, elbow gloves, strapless shirt, navel cutout, backless outfit, two-tone dress__UPPER__layered skirt, miniskirt, frilled skirt, black skirt, back bow, red bow, thigh boots, black shoes__LEG__high heel boots]",
        "魔法少女1随机颜色: [magical girl, star hair ornament, wing hair ornament, frilled, detached collar, neck ruff, bowtie, bare shoulders__HEAD__detached sleeves, juliet sleeves, elbow gloves, strapless shirt, navel cutout, backless outfit, two-tone dress__UPPER__layered skirt, miniskirt, frilled skirt, back bow, thigh boots__LEG__high heel boots]",
        "魔法少女2白色: [white dress, (lightpink dress:0.9), magical girl, star hair ornament, wing hair ornament, frilled, standing collar, sleeveless shirt__HEAD__detached sleeves, juliet sleeves, elbow gloves, sleeveless dress, cleavage cutout, navel cutout, backless outfit, two-tone dress__UPPER__pleated skirt, miniskirt, white skirt, back bow, pink bow, thigh boots, white shoes__LEG__high heel boots]",
        "魔法少女2黑色: [black dress, (red dress:0.9), magical girl, star hair ornament, wing hair ornament, frilled, standing collar, sleeveless shirt__HEAD__detached sleeves, juliet sleeves, elbow gloves, sleeveless dress, cleavage cutout, navel cutout, backless outfit, two-tone dress__UPPER__pleated skirt, miniskirt, black dress, back bow, red bow, thigh boots, black shoes__LEG__high heel boots]",
        "魔法少女2随机颜色: [magical girl, star hair ornament, wing hair ornament, frilled, standing collar, sleeveless shirt__HEAD__detached sleeves, juliet sleeves, elbow gloves, sleeveless dress, cleavage cutout, navel cutout, backless outfit, two-tone dress__UPPER__pleated skirt, miniskirt, back bow, thigh boots__LEG__high heel boots]",
        "地雷系辣妹: [jirai kei, choker, frilled shirt, frilled bib, pink shirt, bolo tie__HEAD__shoulder cutout, puffy long sleeves, belt, shirt tucked in__UPPER__black skirt, frilled skirt, layered skirt, black pantyhose__LEG__platform heels]",
        "JK辣妹: [choker, open shirt, collared shirt, white shirt__HEAD__tied shirt, crop top, midriff, sleeves rolled up, leopard print, bikini top only__UPPER__microskirt, pleated skirt, darkblue skirt, highleg panties__LEG__loose socks, white socks, loafers, platform heels]",
        "JK夏季校服短袜: [summer uniform, school uniform, bowtie, collared shirt, white shirt__HEAD__short sleeves, shirt tucked in__UPPER__pleated skirt, checkered skirt, darkblue skirt__LEG__white socks, loafers]", 
        "JK夏季校服白丝: [summer uniform, school uniform, bowtie, collared shirt, white shirt__HEAD__short sleeves, shirt tucked in__UPPER__pleated skirt, checkered skirt, darkblue skirt, white thighhighs__LEG__loafers]", 
        "JK夏季校服黑丝: [summer uniform, school uniform, bowtie, collared shirt, white shirt__HEAD__short sleeves, shirt tucked in__UPPER__pleated skirt, checkered skirt, darkblue skirt, black thighhighs__LEG__loafers]", 
        "JK冬季校服白丝: [winter uniform, school uniform, lapels, necktie, collared shirt, white shirt, blazer__HEAD__long sleeves__UPPER__pleated skirt, checkered skirt, darkblue skirt, white thighhighs__LEG__loafers]", 
        "JK冬季校服黑丝: [winter uniform, school uniform, lapels, necktie, collared shirt, white shirt, blazer__HEAD__long sleeves__UPPER__pleated skirt, checkered skirt, darkblue skirt, black thighhighs__LEG__loafers]", 
        "JK冬季校服白丝裤袜: [winter uniform, school uniform, lapels, necktie, collared shirt, white shirt, blazer__HEAD__long sleeves__UPPER__pleated skirt, checkered skirt, darkblue skirt, white pantyhose__LEG__loafers]", 
        "JK冬季校服黑丝裤袜: [winter uniform, school uniform, lapels, necktie, collared shirt, white shirt, blazer__HEAD__long sleeves__UPPER__pleated skirt, checkered skirt, darkblue skirt, black pantyhose__LEG__loafers]", 
        "涩涩体操服: [gym uniform, round collar, white shirt__HEAD__wristband, short sleeves, shirt tucked in__UPPER__buruma, darkblue bloomers, thighs__LEG__white socks, sneakers]",   
        "涩涩网球服: [tennis uniform, polo shirt, white shirt__HEAD__wristband, short sleeves, midriff__UPPER__pleated skirt, white skirt, thighs__LEG__sneakers]", 
        "处男杀手毛衣米色: [virgin killer sweater, beige sweater, turtleneck__HEAD__aran sweater, sideboob, backless outfit, detached sleeves, long sleeves, sleeves past wrists__UPPER__no panties, ribbed thighhighs, beige thighhighs__LEG__no shoes], {cleavage cutout}",  
        "处男杀手毛衣黑色: [virgin killer sweater, black sweater, turtleneck__HEAD__aran sweater, sideboob, backless outfit, detached sleeves, long sleeves, sleeves past wrists__UPPER__no panties, ribbed thighhighs, black thighhighs__LEG__no shoes], {cleavage cutout}",         
        "处男毁灭毛衣米色: [virgin destroyer sweater, beige sweater, turtleneck__HEAD__sideboob, backless outfit, detached sleeves, long sleeves, sleeves past wrists__UPPER__ribbed panties, highleg panties, ribbed thighhighs, beige thighhighs__LEG__no shoes], {cleavage cutout}", 
        "处男毁灭毛衣黑色: [virgin destroyer sweater, black sweater, turtleneck__HEAD__sideboob, backless outfit, detached sleeves, long sleeves, sleeves past wrists__UPPER__ribbed panties, highleg panties, ribbed thighhighs, black thighhighs__LEG__no shoes], {cleavage cutout}", 
        "裸体围裙: [naked apron, white apron, frilled apron, shoulder strap__HEAD__backless outfit, sideboob__UPPER__no panties__LEG__slippers]", 
        "SM女王: [dominatrix, latex, standing collar, shrug (clothing), belt collar__HEAD__breastless clothes, chest harness, between breasts, belt, corset, elbow gloves, garter straps__UPPER__no panties, thigh boots, belt boots__LEG__high heel boots, pointy footwear, stiletto heel]", 
        "哥特萝莉白色: [gothic lolita, lolita fashion, white dress, frilled bib, lace trim, frilled, bonnet, hair flower, lightblue_flower, neck ruff, blue_gemstone, bolo tie, cleavage cutout__HEAD__bustier, cross-laced clothes, juliet sleeves, half gloves, lace-trimmed gloves, white gloves__UPPER__short dress, frilled dress, layered dress, petticoat, garter straps__LEG__platform heels, white shoes]", 
        "哥特萝莉黑色: [gothic lolita, lolita fashion, black dress, frilled bib, lace trim, frilled, bonnet, hair flower, darkred_flower, neck ruff, red_gemstone, bolo tie, see-through cleavage__HEAD__bustier, cross-laced clothes, juliet sleeves, half gloves, lace-trimmed gloves, black gloves__UPPER__short dress, frilled dress, layered dress, petticoat, garter straps, black thighhighs__LEG__platform heels, black shoes]", 
        "哥特萝莉红色: [gothic lolita, lolita fashion, red dress, frilled bib, lace trim, frilled, bonnet, hair flower, black_flower, neck ruff, green_gemstone, bolo tie, see-through cleavage__HEAD__bustier, cross-laced clothes, juliet sleeves, half gloves, lace-trimmed gloves, black gloves__UPPER__short dress, frilled dress, layered dress, petticoat, garter straps, black thighhighs__LEG__platform heels, black shoes]", 
        "涩涩护士白色: [white dress, nurse, nurse cap, standing collar, breastless clothes, cross print__HEAD__short sleeves, bikini top only, eyepatch bikini, lightpink bikini__UPPER__pencil dress, white pantyhose, see-through legwear__LEG__high heels, pointy footwear, stiletto heel, lightpink shoes], {strappy heels, ankle strap}",
        "涩涩护士黑色: [black dress, nurse, nurse cap, standing collar, breastless clothes, cross print__HEAD__short sleeves, bikini top only, eyepatch bikini, white bikini__UPPER__pencil dress__LEG__high heels, pointy footwear, stiletto heels, black shoes], {strappy heels, ankle strap}",
        "赛博紧身衣: [cyberpunk, science fiction, headgear, bodysuit, neon trim, pink trim, shrug (clothing), two-tone bodysuit, black bodysuit, (grey bodysuit:0.9), see-through cleavage, v-neck__HEAD__plunging neckline__UPPER__black gloves__LEG__high heels]",
        "潜入搜查官: [black bodysuit, latex bodysuit, standing collar, open collar, choker, v-neck__HEAD__plunging neckline, latex gloves, zipper__UPPER__gloves__LEG__high heels, pointy footwear, stiletto heel]",
        "涩涩女教师: [teacher, collared shirt, white shirt, open collar, long sleeves__HEAD__sleeves rolled up, shirt tucked in__UPPER__pencil skirt, black skirt, black pantyhose__LEG__high heels, pointy footwear, stiletto heel, black shoes], {strappy heels, ankle strap}",
        "涩涩OL藏青: [office lady, lapels, collared shirt, white shirt, blazer, darkblue_blazer, lanyard__HEAD__id card, sleeve rolled up__UPPER__pencil skirt, darkblue_skirt, brown pantyhose__LEG__high heels, pointy footwear, stiletto heel, black shoes], {shirt tucked in, strappy heels, ankle strap}",
        "涩涩OL米色: [office lady, lapels, collared shirt, white shirt, blazer, beige_blazer, lanyard__HEAD__id card, sleeve rolled up__UPPER__pencil skirt, beige_skirt, brown pantyhose__LEG__high heels, pointy footwear, stiletto heel, black shoes], {shirt tucked in, strappy heels, ankle strap}",
        "涩涩女警: [policewoman, police uniform, police hat, collared shirt, lightblue_shirt, open collar__HEAD__lace bra, shirt tucked in, short sleeves, fingerless gloves, belt__UPPER__pencil skirt, darkblue_skirt, brown pantyhose__LEG__high heels, pointy footwear, stiletto heel, black shoes], {strappy heels, ankle strap}", 
        "德式黑色军服: [military uniform, military hat, black_uniform, standing collar, lapels, gold trim, epaulettes, cleavage cutout__HEAD__belt, double-breasted, white gloves__UPPER__pencil skirt, black skirt, side slit, black pantyhose, thigh boots, black_boots, leather boots__LEG__high heels, pointy footwear, stiletto heel]",
        "德式啤酒娘: [dirndl, bavarian_costume, german_clothes, frilled, frilled choker, bolo tie, shoulder cutout__HEAD__underbust, short sleeves, juliet sleeves, brown corset, apron__UPPER__frilled skirt, layered skirt, checkered skirt, red skirt, white thighhighs, frilled thighhighs, ribbon-trimmed thighhighs__LEG__strappy heels, high heels, brown shoes]",
        "涩涩空姐: [stewardess, garrison cap, darkblue_cap, ascot, collared shirt, sleeveless shirt, white shirt__HEAD__sideboob, backless outfit, high-waist skirt, half gloves, white gloves__UPPER__pencil skirt, side slit, darkblue_skirt, pantyhose__LEG__high heels, pointy footwear, stiletto heel, black shoes], {strappy heels, ankle strap}",
        "黑色涩涩女仆: [maid, maid headdress, frilled, frilled choker, black_bowtie, frilled shirt, low neckline__HEAD__juliet sleeves, short sleeves, black_sleeves, wrist cuffs, corset, black corset, maid apron__UPPER__frilled skirt, layered skirt, black skirt, white thighhighs, frilled thighhighs, ribbon-trimmed thighhighs__LEG__strappy heels, high heels, black shoes]",
        "粉色涩涩女仆: [maid, maid headdress, frilled, frilled choker, pink_bowtie, frilled shirt, low neckline__HEAD__juliet sleeves, short sleeves, pink_sleeves, wrist cuffs, corset, pink corset, maid apron__UPPER__frilled skirt, layered skirt, pink skirt, white thighhighs, frilled thighhighs, ribbon-trimmed thighhighs__LEG__strappy heels, high heels, pink shoes]",
        "涩涩修女白色: [nun, nun headdress, (white dress:1.1), turtleneck, standing collar, cross necklace__HEAD__breast curtains, breastless clothes, juliet sleeves, cross print, gold trim__UPPER__side slit, highleg, white garter straps, white thighhighs, pelvic curtain__LEG__high heels, pointy footwear, stiletto heel, black shoes], {strappy heels, ankle strap}",
        "涩涩修女黑色: [nun, nun headdress, turtleneck, standing collar, cross necklace, black dress__HEAD__breast curtains, breastless clothes, juliet sleeves, cross print, gold trim__UPPER__side slit, highleg, pelvic curtain, white garter straps, white thighhighs__LEG__high heels, pointy footwear, stiletto heel, black shoes], {strappy heels, ankle strap}",
        "涩涩巫女: [nontraditional miko, japanese clothes, v-neck__HEAD__plunging neckline, sideboob, detached sleeves, long sleeves, wide sleeves, red sash, obi__UPPER__hakama_short_skirt, red_skirt, cross-laced skirt, white thighhighs__LEG__platform heels, flip-flops, black shoes]", 
        "短款和服粉色: [pink kimono, print kimono, sakura_print, japanese clothes, off-shoulder kimono, bare shoulders__HEAD__furisode, long sleeves, wide sleeves, obi, black sash__UPPER__short kimono, gradient_kimono, purple kimono, white thighhighs__LEG__platform heels, flip-flops, black shoes]",
        "短款和服黑色: [black kimono, print kimono, snowflake print, japanese clothes, off-shoulder kimono, bare shoulders__HEAD__furisode, long sleeves, wide sleeves, obi, red sash__UPPER__short kimono, gradient_kimono, darkblue_kimono, black thighhighs__LEG__platform heels, flip-flops, black shoes]",
        "涩涩女忍: [ninja, purple kimono, (black kimono:0.8), japanese clothes, black scarf, v-neck, sleeveless kimono, see-through cleavage, fishnet top, leotard under clothes__HEAD__sideboob, japanese armor, fingerless gloves, black gloves, arm armor, single_shoulder_armor, black sash, obi__UPPER__pelvic curtain, black pantyhose, fishnet pantyhose, thigh_strap__LEG__leg armor, shin guards, thigh boots]",
        "涩涩圣诞: [santa costume, santa hat, fur-trimmed cape, red cape, green bowtie, bell__HEAD__red bikini, highleg bikini, black corset, elbow gloves, black gloves, wrist cuffs, black garter straps__UPPER__black thighhighs__LEG__high heels, pointy footwear, stiletto heel, red shoes], {strappy heels, ankle strap}",
        "涩涩海盗: [pirate costume, pirate hat, black collared coat, standing collar, detached collar, ascot, epaulettes, gold trim__HEAD__long sleeves, white bustier, midriff, belt__UPPER__frilled skirt, layered skirt, black skirt__LEG__knee boots, high heel boots, lace-up boots]",
        "兔女郎黑色裤袜: [playboy bunny, black_clothes, fake animal ears, rabbit ears, detached collar, bare shoulders, bowtie__HEAD__highleg leotard, straples leotard, black leotard, wrist cuffs__UPPER__black pantyhose__LEG__high heels, pointy footwear, stiletto heel, black shoes], {strappy heels, ankle strap}",
        "兔女郎黑色渔网袜: [playboy bunny, black_clothes, fake animal ears, rabbit ears, detached collar, bare shoulders, bowtie__HEAD__highleg leotard, straples leotard, black leotard, wrist cuffs__UPPER__black pantyhose, fishnet pantyhose__LEG__high heels, pointy footwear, stiletto heel, black shoes], {strappy heels, ankle strap}",
        "兔女郎白色裤袜: [playboy bunny, white_clothes, fake animal ears, rabbit ears, detached collar, bare shoulders, bowtie__HEAD__highleg leotard, straples leotard, white leotard, wrist cuffs__UPPER__white pantyhose__LEG__high heels, pointy footwear, stiletto heel, white shoes], {strappy heels, ankle strap}",
        "兔女郎白色渔网袜: [playboy bunny, white_clothes, fake animal ears, rabbit ears, detached collar, bare shoulders, bowtie__HEAD__highleg leotard, straples leotard, white leotard, wrist cuffs__UPPER__white pantyhose, fishnet pantyhose__LEG__high heels, pointy footwear, stiletto heel, white shoes], {strappy heels, ankle strap}",
        "兔女郎水蓝裤袜: [playboy bunny, skyblue_clothes, fake animal ears, rabbit ears, detached collar, bare shoulders, bowtie__HEAD__highleg leotard, straples leotard, skyblue_leotard, wrist cuffs__UPPER__black pantyhose__LEG__high heels, pointy footwear, stiletto heel, skyblue shoes], {strappy heels, ankle strap}",
        "兔女郎水蓝渔网袜: [playboy bunny, skyblue_clothes, fake animal ears, rabbit ears, detached collar, bare shoulders, bowtie__HEAD__highleg leotard, straples leotard, skyblue_leotard, wrist cuffs__UPPER__black pantyhose, fishnet pantyhose__LEG__high heels, pointy footwear, stiletto heel, skyblue shoes], {strappy heels, ankle strap}",
        "兔女郎粉色裤袜: [playboy bunny, pink_clothes, fake animal ears, rabbit ears, detached collar, bare shoulders, bowtie__HEAD__highleg leotard, straples leotard, pink leotard, wrist cuffs__UPPER__white pantyhose__LEG__high heels, pointy footwear, stiletto heel, pink shoes], {strappy heels, ankle strap}",
        "兔女郎粉色渔网袜: [playboy bunny, pink_clothes, fake animal ears, rabbit ears, detached collar, bare shoulders, bowtie__HEAD__highleg leotard, straples leotard, pink leotard, wrist cuffs__UPPER__white pantyhose, fishnet pantyhose__LEG__high heels, pointy footwear, stiletto heel, pink shoes], {strappy heels, ankle strap}",
        "逆兔女郎黑色裤袜: [reverse bunnysuit, black_clothes, fake animal ears, rabbit ears, black_shrug_(clothing), bowtie__HEAD__heart_maebari, wrist cuffs__UPPER__heart_pasties, highleg, black pantyhose__LEG__high heels, pointy footwear, stiletto heel, black shoes], {strappy heels, ankle strap}",
        "逆兔女郎黑色渔网袜: [reverse bunnysuit, black_clothes, fake animal ears, rabbit ears, black_shrug_(clothing), bowtie__HEAD__heart_maebari, wrist cuffs__UPPER__heart_pasties, highleg, black pantyhose, fishnet pantyhose__LEG__high heels, pointy footwear, stiletto heel, black shoes], {strappy heels, ankle strap}",
        "逆兔女郎白色裤袜: [reverse bunnysuit, white_clothes, fake animal ears, rabbit ears, white_shrug_(clothing), bowtie__HEAD__heart_maebari, wrist cuffs__UPPER__heart_pasties, highleg, white pantyhose__LEG__high heels, pointy footwear, stiletto heel, white shoes], {strappy heels, ankle strap}",
        "逆兔女郎白色渔网袜: [reverse bunnysuit, white_clothes, fake animal ears, rabbit ears, white_shrug_(clothing), bowtie__HEAD__heart_maebari, wrist cuffs__UPPER__heart_pasties, highleg, white pantyhose, fishnet pantyhose__LEG__high heels, pointy footwear, stiletto heel, white shoes], {strappy heels, ankle strap}",
        "逆兔女郎水蓝裤袜: [reverse bunnysuit, skyblue_clothes, fake animal ears, rabbit ears, skyblue_shrug_(clothing), bowtie__HEAD__heart_maebari, wrist cuffs__UPPER__heart_pasties, highleg, black pantyhose__LEG__high heels, pointy footwear, stiletto heel, skyblue shoes], {strappy heels, ankle strap}",
        "逆兔女郎水蓝渔网袜: [reverse bunnysuit, skyblue_clothes, fake animal ears, rabbit ears, skyblue_shrug_(clothing), bowtie__HEAD__heart_maebari, wrist cuffs__UPPER__heart_pasties, highleg, black pantyhose, fishnet pantyhose__LEG__high heels, pointy footwear, stiletto heel, skyblue shoes], {strappy heels, ankle strap}",
        "逆兔女郎粉色裤袜: [reverse bunnysuit, pink_clothes, fake animal ears, rabbit ears, pink_shrug_(clothing), bowtie__HEAD__heart_maebari, wrist cuffs__UPPER__heart_pasties, highleg, white pantyhose__LEG__high heels, pointy footwear, stiletto heel, pink shoes], {strappy heels, ankle strap}",
        "逆兔女郎粉色渔网袜: [reverse bunnysuit, pink_clothes, fake animal ears, rabbit ears, pink_shrug_(clothing), bowtie__HEAD__heart_maebari, wrist cuffs__UPPER__heart_pasties, highleg, white pantyhose, fishnet pantyhose__LEG__high heels, pointy footwear, stiletto heel, pink shoes], {strappy heels, ankle strap}",
        "赛车女郎1: [race queen, black leotard, two-tone leotard, white leotard, detached collar, criss-cross halter, low neckline, strapless leotard__HEAD__backless leotard, elbow gloves, bridal gauntlets, highleg leotard, navel cutout, see-through navel__UPPER__miniskirt, pleated skirt, thighhighs, thighhighs under boots, thigh boots__LEG__high heels, pointy footwear, stiletto heel]",
        "赛车女郎2: [race queen, darkblue_leotard, detached collar, low neckline, strapless leotard__HEAD__backless leotard, elbow gloves, bridal gauntlets__UPPER__miniskirt, pencil skirt, thigh boots__LEG__high heels, pointy footwear, stiletto heel]",
        "赛车女郎3: [race queen, choker, lapels, shrug (clothing), standing collar, open collar, chest harness__HEAD__bikini top only, micro bikini, sleeve rolled up, fingerless gloves, highleg bikini__UPPER__microskirt, pencil skirt, lowleg_skirt, side slit, thigh belt, thigh boots__LEG__high heels, pointy footwear, stiletto heel]",
        "涩涩旗袍白色: [cheongsam, print cheongsam, flower_print, white dress, china dress, chinese clothes, chinese style, standing collar, turtleneck, sleeveless dress, gold trim, chinese knot, cleavage cutout__HEAD__medium dress__UPPER__pelvic curtain, side slit__LEG__high heels, pointy footwear, stiletto heel, white shoes], {strappy heels, ankle strap}",
        "涩涩旗袍黑色: [cheongsam, print cheongsam, dragon_print, black dress, china dress, chinese clothes, chinese style, standing collar, turtleneck, sleeveless dress, gold trim, chinese knot, cleavage cutout__HEAD__medium dress__UPPER__pelvic curtain, side slit__LEG__high heels, pointy footwear, stiletto heel, black shoes], {strappy heels, ankle strap}",
        "涩涩旗袍水蓝: [cheongsam, print cheongsam, flower_print, lightblue_dress, china dress, chinese clothes, chinese style, standing collar, turtleneck, sleeveless dress, gold trim, chinese knot, cleavage cutout__HEAD__medium dress__UPPER__pelvic curtain, side slit__LEG__high heels, pointy footwear, stiletto heel, lightblue shoes], {strappy heels, ankle strap}",
        "涩涩旗袍淡粉: [cheongsam, print cheongsam, flower_print, pink dress, china dress, chinese clothes, chinese style, standing collar, turtleneck, sleeveless dress, gold trim, chinese knot, cleavage cutout__HEAD__medium dress__UPPER__pelvic curtain, side slit__LEG__high heels, pointy footwear, stiletto heel, pink shoes], {strappy heels, ankle strap}",
        "涩涩僵尸: [jiangshi costume, qingdai guanmao, standing collar, china dress, chinese clothes, chinese style, darkblue_cheongsam, darkblue_dress, breastless clothes, two-tone dress, sleeveless dress, chinese knot, ofuda__HEAD__detached sleeves, wide sleeves, long sleeves, breast curtains, black sash, obi__UPPER__pelvic curtain, medium dress, white thighhighs__LEG__no shoes]",
        "涩涩新娘1: [bride, bridal veil, tiara, wedding dress, white dress, necklace, off-shoulder dress, bare shoulders__HEAD__elbow gloves, wedding ring, frilled dress, layered dress__UPPER__garter straps, white thighhighs, back bow__LEG__high heels, pointy footwear, stiletto heel, white shoes], {strappy heels, ankle strap}",
        "涩涩新娘2: [bride, bridal veil, tiara, wedding dress, white dress, necklace, off-shoulder dress, bare shoulders, sleeveless dress, strapless dress__HEAD__elbow gloves, wedding ring, taut dress__UPPER__side slit, bare legs__LEG__high heels, pointy footwear, stiletto heel, white shoes], {strappy heels, ankle strap}",
        "机娘: [mecha musume, science fiction, headgear, pauldrons, armored dress, cleavage cutout, see-through cleavage__HEAD__breastplate, bodysuit under clothes, mechanical wings, detached wings, highleg leotard, mechanical arms__UPPER__pantyhose, faulds, armored dress, armored boots, mechanical legs__LEG__mechanical shoes, high heel boots, pointy footwear, stiletto heel]",
        "骑士姬白色: [knight, tiara, turtleneck, standing collar, full armor, white dress, white armor, cleavage cutout, pauldrons, armored dress, gold trim__HEAD__gauntlets, armored gloves, underbust__UPPER__faulds, waist cape, frilled skirt, layered skirt, garter straps, thighhighs, thighhighs under boots, greaves, armored boots, thigh boots__LEG__high heel boots, pointy footwear, stiletto heel]",
        "骑士姬黑色: [knight, tiara, turtleneck, standing collar, full armor, black dress, black armor, cleavage cutout, pauldrons, armored dress, gold trim__HEAD__gauntlets, armored gloves, underbust__UPPER__faulds, waist cape, frilled skirt, layered skirt, garter straps, thighhighs, thighhighs under boots, greaves, armored boots, thigh boots__LEG__high heel boots, pointy footwear, stiletto heel]",
        "骑士姬随机颜色: [knight, tiara, turtleneck, standing collar, full armor, cleavage cutout, pauldrons, armored dress, gold trim__HEAD__gauntlets, armored gloves, underbust__UPPER__faulds, waist cape, frilled skirt, layered skirt, garter straps, thighhighs, thighhighs under boots, greaves, armored boots, thigh boots__LEG__high heel boots, pointy footwear, stiletto heel]",
        "比基尼盔甲白色: [knight, tiara, white armor, chest harness, halterneck, bikini armor, pauldrons, gold trim__HEAD__gauntlets, armored gloves, midriff__UPPER__faulds, highleg bikini, greaves, armored boots, thigh boots__LEG__high heel boots, pointy footwear, stiletto heel]",
        "比基尼盔甲黑色: [knight, tiara, black armor, chest harness, halterneck, bikini armor, pauldrons, gold trim__HEAD__gauntlets, armored gloves, midriff__UPPER__faulds, highleg bikini, greaves, armored boots, thigh boots__LEG__high heel boots, pointy footwear, stiletto heel]",
        "比基尼盔甲随机颜色: [knight, tiara, chest harness, halterneck, bikini armor, pauldrons, gold trim__HEAD__gauntlets, armored gloves, midriff__UPPER__faulds, highleg bikini, greaves, armored boots, thigh boots__LEG__high heel boots, pointy footwear, stiletto heel]",
        "涩涩牛仔: [cowboy western, cowboy hat, red bandana, plaid shirt, collared shirt, open skirt, red shirt__HEAD__tied shirt, sleeves rolled up, leather gloves, fingerless gloves__UPPER__highleg panties, denim shorts, belt pouch__LEG__high heel boots, knee boots]",
        "埃及舞娘: [usekh collar, circlet, harem outfit, white dress__HEAD__arm garter, bracelet, underbust, sideboob, midriff__UPPER__leg garter, white loincloth, white thighhighs__LEG__stirrup legwear, no shoes]",
        "涩涩女巫: [witch, witch hat, lace choker, gemstone, halter dress, halter top, halterneck, shoulder strap, black dress, gold trim, gold chain, gold_string, v-neck, bare shoulders__HEAD__lace-trimmed gloves, elbow gloves, sideless outfit, sideboob, revealing clothes, plunging neckline, sideless outfit, navel cutout, shawl, fur shawl, black shawl__UPPER__pelvic curtain, thigh strap, no panties__LEG__anklet, high heels, pointy footwear, stiletto heel, black shoes], {strappy heels, ankle strap}",
        "涩涩女巫不戴帽子: [witch, lace choker, gemstone, halter dress, halter top, halterneck, shoulder strap, black dress, gold trim, gold chain, gold_string, v-neck, bare shoulders__HEAD__lace-trimmed gloves, elbow gloves, sideless outfit, sideboob, revealing clothes, plunging neckline, sideless outfit, navel cutout, shawl, fur shawl, black shawl__UPPER__pelvic curtain, thigh strap, no panties__LEG__anklet, high heels, pointy footwear, stiletto heel, black shoes], {strappy heels, ankle strap}",
        "奶牛比基尼: [cow ears, cow horns, cowbell, collar, halterneck, cow_print_bikini__HEAD__cow print gloves, elbow gloves, microbikini__UPPER__highleg bikini, cow print thighhighs__LEG__high heels, pointy footwear, stiletto heel, black shoes], {strappy heels, ankle strap}",
        "三点式比基尼: [front-tie bikini top, micro bikini, halterneck__HEAD____UPPER__side-tie bikini bottom, highleg bikini__LEG__sandals, high heels]",
        "交叉吊带泳衣: [micro bikini, criss-cross halter, o-ring top__HEAD____UPPER__o-ring bottom, highleg bikini__LEG__sandals, high heels]",
        "V字泳衣: [micro bikini, slingshot swimsuit, halterneck__HEAD____UPPER____LEG__sandals, high heels]", 
        "贝壳泳衣: [micro bikini, shell bikini, halterneck__HEAD____UPPER__highleg bikini__LEG__sandals, high heels]",
        "薄纱睡衣白色: [babydoll, halter top, halterneck, shoulder strap, see-through dress, white dress, lace-trimmed dress, v-neck__HEAD__plunging neckline__UPPER__no panties, short dress__LEG__no shoes, barefoot]",
        "薄纱睡衣黑色: [babydoll, halter top, halterneck, shoulder strap, see-through dress, black dress, lace-trimmed dress, v-neck__HEAD__plunging neckline__UPPER__no panties, short dress__LEG__no shoes, barefoot]",
        "薄纱睡衣粉色: [babydoll, halter top, halterneck, shoulder strap, see-through dress, pink dress, lace-trimmed dress, v-neck__HEAD__plunging neckline__UPPER__no panties, short dress__LEG__no shoes, barefoot]",
        "情趣内衣白色: [lace choker, white bra, halterneck, shoulder strap, underwear only__HEAD__cupless bra, lace-trimmed bra, lace bra__UPPER__white garter straps, white panties, crotchless panties, lace-trimmed panties, lace panties, white thighhighs, lace-trimmed thighhighs__LEG__no shoes]",
        "情趣内衣黑色: [lace choker, black bra, halterneck, shoulder strap, underwear only__HEAD__cupless bra, lace-trimmed bra, lace bra__UPPER__black garter straps, black panties, crotchless panties, lace-trimmed panties, lace panties, black thighhighs, lace-trimmed thighhighs__LEG__no shoes]",
        "情趣内衣红色: [lace choker, red bra, halterneck, shoulder strap, underwear only__HEAD__cupless bra, lace-trimmed bra, lace bra__UPPER__red garter straps, red panties, crotchless panties, lace-trimmed panties, lace panties, red thighhighs, lace-trimmed thighhighs__LEG__no shoes]",
        "开胸猫猫内衣白色: [cat lingerie, fake animal ears, cat ears, bell, choker, belt collar, shoulder strap__HEAD__keyhole bra, white bra__UPPER__white panties, side-tie panties, white thighhighs, cat tail__LEG__no shoes]",
        "开胸猫猫内衣黑色: [cat lingerie, fake animal ears, cat ears, bell, choker, belt collar, shoulder strap__HEAD__keyhole bra, black bra__UPPER__black panties, side-tie panties, black thighhighs, cat tail__LEG__no shoes]",
        "死库水: [school swimsuit, new school swimsuit, darkblue swimsuit, shoulder strap__HEAD____UPPER__one-piece swimsuit__LEG__barefoot, no shoes]",

        
    ],
    # 33. G3 Cosplay模式 - 特定角色扮演 __HEAD__ __UPPER__ __LEG__
    "cosplay": [
        "(不指定)", 
        "天女兽cos: [cosplay, angewomon (cosplay), digimon, head wings__HEAD__multiple belts, navel cutout, hagoromo, single elbow glove, feathered wings, multiple wings, white wings__UPPER__asymmetrical clothes:1.2, asymmetrical legwear:1.2, thigh belt__LEG__ankle cuffs, white shoes], {(winged helmet:1.2)}",
        "尼尔2Bcos: [cosplay, 2b (nier:automata) (cosplay), nier (series), black hairband, turtleneck, black dress__HEAD__cleavage cutout, juliet sleeves, white bracer, black gloves__UPPER__side slit, short dress, white highleg leotard, black thighhighs, thighhighs under boots, black thigh boots__LEG__high heel boots]",
        "尼尔2Bcos不带裙子: [cosplay, 2b (nier:automata) (cosplay), nier (series), black hairband, turtleneck, black shirt__HEAD__cleavage cutout, juliet sleeves, white bracer, black gloves__UPPER__white highleg leotard, black thighhighs, thighhighs under boots, black thigh boots__LEG__high heel boots]",
        "尼尔凯妮内衣cos: [ccosplay, kaine (nier:automata) (cosplay), nier (series), lingerie, negligee, bandaged neck, aqua dress, single bandaged arm__HEAD__bracer, black gloves__UPPER__white panties, simgle bandaged leg, thigh strap__LEG__high heels, strappy heels]",
        "尼尔寄叶指挥官cos: [cosplay, commander (nier:automata) (cosplay), nier (series), turtleneck, white dress__HEAD__see-through dress, bracer, white gloves__UPPER__side slit, short dress, white highleg leotard, white thighhighs, thighhighs under boots, white thigh boots__LEG__high heel boots]",
        "火舞cos: [cosplay, shiranui mai (cosplay), the king of fighters, ninja, japanese clothes, revealing clothes, red clothes, v-neck__HEAD__plunging neckline, black sash, obi, pelvic curtain, wrist guards, back bow, white bow__UPPER__no panties__LEG__tabi]",   
        "霞cos: [cosplay, kasumi (doa) (cosplay), dead or alive, japanese clothes, revealing clothes, blue clothes, v-neck, puffy short sleeves__HEAD__plunging neckline, white sash, pelvic curtain, wrist guards, white arm warmers__UPPER__no panties, white thighhighs__LEG__tabi, shin guards, slippers]", 
        "春丽cos: [cosplay, chun-li (street fighter) (cosplay), street fighter, china dress, blue dress, puffy short sleeves__HEAD__white sash, spiked bracelet__UPPER__pelvic curtain, brown pantyhose__LEG__lace-up boots, knee boots, high heel boots, white shoes]",  
        "伊莎贝拉cos: [cosplay, isabella valentine (cosplay), soulcalibur, purple dress, single pauldron, armor, cleavage cutout__HEAD__highleg leotard, underboob, single gauntlet, revealing clothes, underbust, navel cutout, elbow glove__UPPER__garter straps, thigh boots__LEG__high heel boots, pointy footwear, stiletto heel]",   
        "贝优妮塔cos: [cosplay, bayonetta (cosplay), bayonetta (series), standing collar, shrug (clothing), bodysuit, cleavage cutout__HEAD__white gloves, elbow gloves, arm belt__UPPER__backless outfit__LEG__high heel boots, stiletto heel]",   
        "ZEROcos: [cosplay, zero (drag-on dragoon) (cosplay), drag-on dragoon, popped collar, v-neck, bare shoulder, white dress, white cape__HEAD__elbow gloves, white gloves, single gauntlet, black armor, cleavage cutout__UPPER__backless outfit__LEG__white kneehighs, high heels, stiletto heels, strappy heels]",   
        "莫莉卡cos: [cosplay, morrigan aensland (cosplay), darkstalkers, strapless leotard, bare shoulders, head wings, bat wings, purple wings__HEAD__bridal gauntlets, elbow gloves, orange gloves, plunging neckline, highleg leotard, purple pantyhose, bat print__UPPER__low wings__LEG__knee boots, high heel boots, stiletto heels]", 
        "雅儿贝德cos: [cosplay, albedo (overlord) (cosplay), demon horns, white horns, standing collar, detached collar, bare shoulders__HEAD__white dress, white gloves__UPPER__hip vent__LEG__high heels, pointy footwear, stiletto heel, white shoes], {strappy heels, ankle strap}", 
        "蒂法cos: [cosplay, tifa lockhart (cosplay), final fantasy, sleeveless shirt, round collar__HEAD__crop top, midriff, elbow gloves, fingerless gloves, vambraces__UPPER__black skirt, suspender skirt, black thighhighs__LEG__combat boots, lace-up boots, red shoes]",   
        "蒂法晚礼服cos: [cosplay, tifa lockhart (refined dress) (cosplay), final fantasy, frilled choker, bolo tie, crescent earrings, purple dress, blue dress, sleeveless dress, bare shoulders__HEAD__plunging neckline__UPPER__short dress__LEG__high heels, pointy footwear, stiletto heel, black shoes]",   
        "约尔cos: [cosplay, yor briar (cosplay), spy x family, gold hairband, hair flower, black dress, bare shoulders__HEAD__black gloves, fingerless gloves__UPPER__pencil dress, waist cape, black thigh boots__LEG__high heel boots, pointy footwear, stiletto heel, black shoes]", 
        "游戏王黑魔导女孩cos: [cosplay, dark magician girl (cosplay), yu-gi-oh!, wizard hat, choker, red gemstone, bare shoulders__HEAD__vambraces, capelet, pentacle__UPPER__waist cape__LEG__blue footwear]", 
        "游戏王白银城拉比林丝cos: [cosplay, lovely labrynth of the silver castle (cosplay), yu-gi-oh!, demon horns, white horns, demon wings, detached collar, frilled collar, neck ruff, bare shoulders__HEAD__strapless dress, detached sleeves, juliet sleeves, faulds, frilled gloves__UPPER__highleg leotard, leotard under clothes, see-through dress, long dress, petticoat, pelvic curtain, garter straps, white thighhighs, low wings, transparent wings, multiple wings__LEG__high heels, pointy footwear, stiletto heel, strappy heels, white shoes]", 
        "碧蓝天狼星奶盖旗袍cos: [cosplay, sirius (azure horizons) (azur lane) (cosplay), hair flower, standing collar, china dress, grey dress, bare shoulders, breast curtains, ribbon between breasts, revealing clothes__HEAD__white gloves, half gloves__UPPER__pelvic curtain, garter straps, white thighhighs__LEG__high heels, pointy footwear, stiletto heel, white shoes], {strappy heels, ankle strap}",
        "碧蓝圣路易斯礼服cos: [cosplay, st. louis (luxurious wheels) (azur lane) (cosplay), hairclip, necklace, earrings, silver dress, halter dress, bare shoulders, grey dress, evening gown__HEAD__revealing clothes, backless dress, plunging neckline, bracelet__UPPER__side slit, no panties__LEG__high heels, sandals, stiletto heel, strappy heels, silver shoes]",
        "碧蓝巴尔的摩赛车女王cos: [cosplay, baltimore (finish line flagbearer) (cosplay), azur lane, race queen, peaked cap, blue hat, blue headwear, black choker, popped collar, cropped jacket, open jacket, blue jacket, chest harness__HEAD__long sleeves, blue bikini, sleeve rolled up, single glove, black gloves__UPPER__highleg bikini, black bikini, mismatched bikini, micro shorts, blue shorts, thigh strap, thigh boots, blue footwear__LEG__high heel boots]",
        "碧蓝大凤赛车女王cos: [cosplay, taihou (enraptured companion) (azur lane) (cosplay), race queen, black choker, halter top, sunglasses, eyewear on head, bare shoulders__HEAD__open jacket, long sleeves, off shoulder, red jacket, black bikini, underburst__UPPER__multi-strapped bikini bottom, highleg bikini, thigh boots__LEG__high heel boots]",
        "碧蓝大凤旗袍cos: [cosplay, taihou (phoenix's spring song) (azur lane) (cosplay), china dress, red dress, standing collar, sleeveless dress, cleavage cutout, bare shoulders__HEAD__bridal gauntlets, elbow gloves, lace-trimmed gloves, black gloves, low neckline__UPPER__pelvic curtain, garter straps, black thighhighs, fishnet thighhighs, lace-trimmed thighhighs__LEG__high heels, pointy footwear, stiletto heel, red shoes], {strappy heels, ankle strap}",
        "碧蓝大凤礼服cos: [cosplay, taihou (forbidden feast) (azur lane) (cosplay), red choker, hair ornament, red dress, halter dress, bare shoulders__HEAD__cocktail dress, plunging neckline__UPPER__long dress, side slit, black thighhighs__LEG__high heels, pointy footwear, stiletto heel, red shoes], {strappy heels, ankle strap}",
        "碧蓝大凤婚纱cos: [cosplay, taihou (temptation on the sea breeze) (azur lane) (cosplay), hair ornament, earrings, necklace, white dress, halter dress, sleeveless dress, wedding dress, evening gown, see-through dress, bare shoulders__HEAD__plunging neckline__UPPER__side slit, garter straps, white thighhighs, lace-trimmed thighhighs__LEG__high heels, pointy footwear, stiletto heel, white shoes], {strappy heels, ankle strap}",
        "碧蓝大凤原皮cos: [cosplay, taihou (azur lane) (cosplay), hair ornament, off-shoulder kimono, japanese clothes, red kimono, bare shoulders__HEAD__print kimono, furisode, long sleeves, wide sleeves, obi, black sash__UPPER__pleated skirt, red skirt, black thighhighs__LEG__rudder footwear, high heels, platform heels]",
        "碧蓝高雄原皮cos: [cosplay, takao (azur lane) (cosplay), standing collar, military uniform__HEAD__long sleeves, double-breasted__UPPER__pleated skirt, black pantyhose__LEG__black loafers]",
        "碧蓝怨仇原皮cos: [cosplay, implacable (azur lane) (cosplay), nun, habit, veil, fake horns, white horns, standing collar, bare shoulders__HEAD__breast cutout, between breasts, revealing clothes, black gloves, half gloves, detached sleeves, long sleeves, wide sleeves__UPPER__pelvic curtain, white thighhighs__LEG__high heels, pointy footwear, stiletto heel, black shoes], {strappy heels, ankle strap}",
        "康口雷岛风cos: [cosplay, shimakaze (kancolle) (cosplay), fake animal ears, rabbit ears, sailor collar, black necktie, sleeveless shirt__HEAD__serafuku, crop top, midriff, double-breasted, elbow gloves, white gloves__UPPER__pleated skirt, highleg panties, black panties, horizontal-striped thighhighs__LEG__rudder footwear, high heels]",
        "原神雷电将军cos: [cosplay, raiden shogun (cosplay), hair ornament, shrug (clothing), standing collar, breast cutout, purple kimono, japanese clothes, off-shoulder__HEAD__furisode, sash, obi, bridal gauntlets__UPPER__short kimono, thighhighs__LEG__high heels, platform heels, flip-flops, brown shoes]",  
        "原神申鹤cos: [cosplay, shenhe (genshin impact) (cosplay), hair ornament, standing collar, sleeveless dress, china dress__HEAD__puffy detached sleeves, bracer, bridal gauntlets, black gloves, breast curtain, black bodysuit__UPPER__hip vent__LEG__high heels, platform heels, toeless boots, silver shoes]", 
        "原神优菈cos: [cosplay, eula (genshin impact) (cosplay), black hairband, hair ornament, standing collar__HEAD__leg cutout, long sleeves, gloves__UPPER__thigh boots__LEG__high heel boots]",    
        "fate斯卡哈lancercos: [cosplay, scathach (fate) (cosplay), black veil, standing collar, purple bodysuit__HEAD__gold pauldrons, capelet, multicolored bodysuit__UPPER____LEG__high heels, stiletto heels, armored boots]",  
        "fate斯卡哈斯卡蒂cos: [cosplay, scathach skadi (fate) (cosplay), tiara, detached collar, strapless dress, purple dress, off-shoulder dress, bare shoulders__HEAD__fur-trimmed dress, long sleeves__UPPER__long dress, purple pantyhose__LEG__high heels, pointy footwear, stiletto heels, strappy heels, purple shoes]",
        "fate开膛手杰克cos: [cosplay, cosplay, jack the ripper (fate/apocrypha) (cosplay), standing collar, sleeveless shirt__HEAD__arm belt, single gauntlet, bandaged arm, cleavage cutout, midriff__UPPER__thong, lowleg panties, black thighhighs__LEG__purple shoes]",      
        "fate南丁格尔不给治就捣蛋cos: [cosplay, cosplay, florence nightingale (trick or treatment) (fate) (cosplay), black nurse cap, standing collar, black shrug clothing__HEAD__short sleeves, green bikini, revealing clothes, green gloves, purple bikini, layered bikini__UPPER__black microskirt, highleg bikini, multi-strapped bikini, black garter straps, green thighhighs, thighhighs under boots, thigh boots__LEG__high heel boots, pointy footwear, stiletto heels]", 
        "fate黑枪呆皇家糖霜cos: [cosplay, artoria pendragon (royal icing) (fate) (cosplay), lace choker, black choker, necklace, lingerie, halter dress, bare shoulders__HEAD__babydoll, revealing clothes, plunging neckline, lace-trimmed gloves, black gloves__UPPER__garter straps, black thighhighs, lace-trimmed thighhighs__LEG__no shoes]", 
        "fate玛修危险野兽cos: [cosplay, mash kyrielight (dangerous beast) (cosplay), fake animal ears, wolf ears, fur collar, halloween costume, bare shoulders__HEAD__revealing clothes, elbow gloves, fur-trimmed gloves, claws, purple gloves__UPPER__fur-trimmed legwear, purple thighhighs__LEG__no shoes]",   
        "怪猎麒麟套cos: [cosplay, kirin (armor), monster hunter (character), alternate costume, single horn, hairband, fur-trimmed jacket, sleeveless jacket__HEAD__white bandeau, midriff, cropped jacket, elbow gloves, fur-trimmed gloves, detached sleeves, vambraces__UPPER__belt, multiple belts, faulds, pelvic curtain, black thighhighs__LEG__knee boots, fur-trimmed boots]", 
        "高达seedD米娅cos: [cosplay, meer campbell (cosplay), star hair ornament, standing collar, white capelet, gold trim__HEAD__(highleg leotard, two-tone leotard, purple leotard, white leotard), white gloves__UPPER__long skirt, purple skirt, high-waist skirt__LEG__high heels, pointy footwear, stiletto heel, white shoes], {strappy heels, ankle strap}",  
        "美少女战士火星cos: [cosplay, magical girl, sailor senshi (cosplay), circlet, earrings, sailor collar, sleeveless shirt, bowite, purple bow, choker__HEAD__elbow gloves__UPPER__pleated skirt, darkred skirt__LEG__high heels, pointy footwear, stiletto heel, red shoes], {strappy heels, ankle strap}",
        "美少女战士水星cos: [cosplay, magical girl, sailor senshi (cosplay), circlet, earrings, sailor collar, sleeveless shirt, bowite, darkblue bow, choker__HEAD__elbow gloves__UPPER__pleated skirt, blue skirt__LEG__knee boots, high heel boots, pointy footwear, stiletto heel, blue shoes]",
        "美少女战士木星cos: [cosplay, magical girl, sailor senshi (cosplay), circlet, earrings, sailor collar, sleeveless shirt, bowite, pink bow, choker__HEAD__elbow gloves__UPPER__pleated skirt, darkgreen_skirt__LEG__ankle boots, high heel boots, lace-up boots, green shoes]",
        "美少女战士金星cos: [cosplay, magical girl, sailor senshi (cosplay), circlet, earrings, sailor collar, sleeveless shirt, bowite, darkblue bow, choker__HEAD__elbow gloves__UPPER__pleated skirt, orange skirt__LEG__high heels, pointy footwear, stiletto heel, strappy heels, orange shoes]",
        "女超人cos: [cosplay, supergirl (cosplay), superhero costume, choker, round collar, red cape, blue skirt__HEAD__crop top, midriff, long sleeves__UPPER__sailor dress, red skirt, thigh boots, red shoes__LEG__high heel boots, pointy footwear, stiletto heel]",
        "超能女孩cos: [cosplay, power girl (cosplay), superhero costume, standing collar, red cape, cleavage cutout, white leotard__HEAD__long sleeves, blue gloves__UPPER__highleg leotard, belt__LEG__knee boots, high heel boots, pointy footwear, stiletto heel, blue shoes]",
        "神奇女侠cos: [cosplay, wonder woman (cosplay), superhero costume, circlet, bare shoulders, strapless leotard__HEAD__vambraces__UPPER__pleated skirt, blue skirt__LEG__knee boots, high heel boots, pointy footwear, stiletto heel, red shoes]",
        "艾达王cos: [cosplay, ada wong (cosplay), standing collar, red sweater, ribbed sweater, chest harness__HEAD__long sleeves, fingerless gloves__UPPER__pencil dress, black pantyhose, thigh boots, thigh holster__LEG__high heel boots, pointy footwear, stiletto heels]",
        "初音未来cos: [cosplay, hatsune miku (cosplay), collared shirt, sleeveless shirt, necktie__HEAD__detached sleeves__UPPER__pleated skirt, layered skirt, thigh boots__LEG__high heel boots]",
    ],
    "dress": [ 
        "(不指定)", 
        "露肩褶边连衣短裙 [off-shoulder dress, frilled dress, criss-cross halter, low neckline, short dress]", 
        "露肩褶边连衣中裙 [off-shoulder dress, frilled dress, criss-cross halter, low neckline, medium dress]", 
        "裸肩低胸包臀裙 [strapless dress, pencil dress, low neckline]",
        "裸肩深V包臀裙 [strapless dress, pencil dress, plunging neckline]", 
        "鸡尾酒礼服交叉肩带: [cocktail dress, halter dress, backless dress, criss-cross halter, evening gown, plunging neckline, jewelry]", 
        "鸡尾酒礼服常规肩带: [cocktail dress, halter dress, backless dress, shoulder strap, halterneck, evening gown, plunging neckline, jewelry]", 
        "吊带无袖连衣短裙: [sundress, summer dress, halter dress, shoulder strap, v-neck, short dress]", 
        "吊带无袖连衣中裙: [sundress, summer dress, halter dress, shoulder strap, v-neck, medium dress]", 
        "吊带无袖连衣长裙: [sundress, summer dress, halter dress, shoulder strap, v-neck, long dress]", 
        "水手连衣裙: [sailor dress, sailor collar, sleeveless dress, bowtie]",  
        "高领阿兰毛衣连衣裙: [aran sweater, sweater dress, long sleeves, turtleneck]", 
        "露肩阿兰毛衣连衣裙: [aran sweater, sweater dress, off-shoulder sweater, strapless dress, bare shoulders, long sleeves]", 
        "高领罗纹毛衣连衣裙: [ribbed sweater, sweater dress, long sleeves, turtleneck]", 
        "露肩罗纹毛衣连衣裙: [ribbed sweater, sweater dress, off-shoulder sweater, strapless dress, bare shoulders, long sleeves]", 
        "后妈裙: [dongtan dress, low neckline, long sleeves, side slit, long dress]"
    ],  
    "topwear": [ 
        "(不指定)", 
        "长袖衬衫: [collared shirt, long sleeves]", 
        "短袖衬衫: [collared shirt, short sleeves]", 
        "无袖衬衫: [collared shirt, sleeveless]", 
        "长袖水手服: [sailor shirt, sailor collar, long sleeves]", 
        "短袖水手服: [sailor shirt, sailor collar, short sleeves]", 
        "无袖水手服: [sailor shirt, sailor collar, sleeveless]", 
        "长袖圆领T恤: [T-shirts, round collar, long sleeve]", 
        "短袖圆领T恤: [T-shirts, round collar, short sleeve,]", 
        "长袖露肩褶边上衣: [off-shoulder shirt, frilled shirt, puffy long sleeves, bare shoulders]", 
        "短袖露肩褶边上衣: [off-shoulder shirt, frilled shirt, puffy short sleeves, bare shoulders]", 
        "长袖褶边上衣: [frilled shirt, standing collar, frilled bib, long sleeves, long sleeves]", 
        "短袖褶边上衣: [frilled shirt, standing collar, frilled bib, long sleeves, short sleeves]", 
        "无袖褶边上衣: [frilled shirt, standing collar, sleeveless]", 
        "长袖卫衣: [hoodie]", 
        "无袖卫衣: [sleeveless hoodie]", 
        "长袖格子衬衫: [plaid shirt, collared shirt, long sleeves]", 
        "短袖格子衬衫: [plaid shirt, collared shirt, short sleeves]", 
        "无袖格子衬衫: [plaid shirt, collared shirt, sleeveless]", 
        "短袖Polo衫: [polo shirt, short sleeves]", 
        "系带衬衫: [tied shirt, collared shirt, open shirt, short sleeves]",
        "格子系带衬衫: [tied shirt, plaid shirt, collared shirt, open shirt, short sleeves]",
        "高龄阿兰毛衣: [aran sweater, long sleeves, turtleneck]", 
        "高龄罗纹毛衣: [ribbed sweater, long sleeves, turtleneck]", 
        "露肩阿兰毛衣: [aran sweater, off-shoulder sweater, bare shoulders, long sleeves]", 
        "露肩罗纹毛衣: [ribbed sweater, off-shoulder sweater, bare shoulders, long sleeves]", 
        "抹胸: [bandeau, low neckline, midriff]", 
        "吊带背心: [camisole, halter top, shoulder strap], {midriff, crop top}", 
        "居家背心: [tank top], {midriff, crop top}", 
        "运动背心: [sports bra]" 
    ],  
    "bottomwear": [ 
        "(不指定)", 
        "格子百褶长裙: [checkered skirt, pleated skirt, long skirt], {double-breasted}",  
        "格子蕾丝百褶超短裙: [checkered skirt, pleated skirt, layered skirt, lace-trimmed skirt, miniskirt], {double-breasted}",
        "蕾丝百褶超短裙: [pleated skirt, layered skirt, lace-trimmed skirt, miniskirt], {double-breasted}",  
        "格子蕾丝褶边超短裙: [checkered skirt, frilled skirt, layered skirt, lace-trimmed skirt, miniskirt], {double-breasted}",
        "蕾丝褶边超短裙: [frilled skirt, layered skirt, lace-trimmed skirt, miniskirt], {double-breasted}",  
        "包臀竖条长裙: [pencil skirt, vertical-striped skirt, long skirt, side slit, tight skirt], {double-breasted}", 
        "包臀裙: [pencil skirt, miniskirt, tight skirt], {double-breasted}", 
        "吊带长裙: [suspender skirt, long skirt, underbust], {double-breasted}", 
        "吊带竖条长裙: [suspender skirt, vertical-striped skirt, long skirt, underbust], {double-breasted}", 
        "吊带超短裙: [suspender skirt, pleated skirt, miniskirt, underbust], {double-breasted}",
        "吊带格子超短裙: [suspender skirt, checkered skirt, pleated skirt, miniskirt, underbust], {double-breasted}", 
        "吊带竖条超短裙: [suspender skirt, vertical-striped skirt, pleated skirt, miniskirt, underbust], {double-breasted}", 
        "吊带蕾丝褶边超短裙: [suspender skirt, layered skirt, lace-trimmed skirt, miniskirt, underbust], {double-breasted}",
        "吊带格子蕾丝褶边超短裙: [suspender skirt, checkered skirt, layered skirt, lace-trimmed skirt, miniskirt, underbust], {double-breasted}", 
        "吊带竖条蕾丝褶边超短裙: [suspender skirt, vertical-striped skirt, layered skirt, lace-trimmed skirt, miniskirt, underbust], {double-breasted}", 
        "牛仔热裤: [short shorts, denim shorts], {double-breasted}", 
        "吊带热裤: [short shorts, suspender shorts], {double-breasted}", 
        "牛仔长裤: [jeans, pants], {double-breasted}" 
        "瑜伽裤: [yoga pants], {double-breasted}" 
    ], 
    "outcover": [ 
        "(不指定)", 
        "披巾: [shawl]", 
        "开衫毛衣: [cardigan]", 
        "西装背心: [vest]", 
        "毛衣背心: [sweater vest]", 
        "西装露胸背心: [waistcoat]", 
        "西装外套: [blazer]", 
        "风衣: [overcoat, trench coat]", 
        "皮草: [winter coat, fur-trimmed coat]", 
        "迷彩夹克: [camouflage jacket]", 
        "皮夹克: [leather jacket, cropped jacket]", 
        "莱特曼夹克: [letterman jacket]", 
        "飞行员夹克: [bomber jacket]", 
        "牛仔夹克: [denim jacket, cropped jacket]", 
        "毛皮边饰夹克: [fur-trimmed jacket]", 
        "冲锋衣: [windbreaker]", 
        "羽绒服: [puffer jacket]", 
        "腰间衣服: [clothes around waist]", 
        "腰围夹克: [jacket around waist]", 
        "围腰毛衣: [sweater around waist]" 
    ],  
    "bra": [ 
        "(不指定)", 
        "蕾丝胸罩: [bra, lace bra]", 
        "无带蕾丝胸罩: [bra, lace bra, strapless bra]", 
        "无杯蕾丝胸罩: [bra, lace bra, cupless bra]" 
    ], 
    "panties": [ 
        "(不指定)", 
        "蕾丝高腰内裤: [panties, lace panties, highleg panties]", 
        "蕾丝低腰内裤: [panties, lace panties, lowleg panties]", 
        "蕾丝高腰无裆内裤: [panties, lace panties, crotchless panties, highleg panties]" 
        "蕾丝低腰无裆内裤: [panties, lace panties, crotchless panties, lowleg panties]" 
    ], 
    "holding": [ "(不指定)", "拿奶茶: [holding_bubble_tea]", "拿马克杯: [holding_mug]", "拿着书: [holding_book]", "拿着书包: [holding_school_bag]", "拿着猫: [holding_cat]", "拿着球: [holding_ball]", "提着篮子: [holding_basket]", "拿水瓶: [holding_bottle]", "拿扫帚: [holding_broom]", "拿相机: [holding_camera]", "拿易拉罐: [holding_can]", "拿棒棒糖: [holding_lollipop]", "拿卡牌: [holding_card]", "拿筷子: [holding_chopsticks]", "拿香烟: [holding_cigarette]", "拿旗子: [holding_flag]", "拿着花: [holding_flower]", "拿披萨: [holding_pizza]", "拿汉堡: [holding_burger]", "拿礼物: [holding_gift]", "拿帽子: [holding_hat]", "拿电吉他: [holding_electric_guitar]", "拿吉他盒: [holding_guitar_case]", "拿着笔: [holding_pen]", "拿着纸: [holding_paper]", "拿手机: [holding_phone]", "端碟子: [holding_plate]", "托盘子: [holding_tray]", "拿鞋子: [holding shoes]", "拿扇子: [holding_fan]", "抱着毛绒玩具: [holding_stuffed_animal]", "拿着毛巾: [holding_towel]", "撑伞: [holding_umbrella]", "握着鞭子: [holding_whip]", "拿着花束: [holding_bouquet]", "拿行李箱: [holding_suitcase]", "拿麦克风: [holding_microphone]", "握着平板电脑: [holding_tablet_pc]", "握着剪贴板: [holding_clipboard]", "拿魔杖: [holding_wand]", "拿巨剑: [holding_greatsword, huge_weapon]", "拿弓箭: [holding_bow_weapon, holding_arrow]", "拿弓箭和符纸: [holding_bow_weapon, holding_ofuda]", "拿枕头挂听诊器: [holding_syringe, stethoscope]", "拿步枪: [holding_rifle]", "拿突击步枪: [holding_assault_rifle]", "拿手枪: [holding_handgun, thigh_holster]", "拿左轮手枪: [holding_revolver]", "忠诚链锯剑爆弹手枪: [holding_chainsaw, holding_handgun]", "拿薙刀: [holding_naginata,holding_polearm]", "拿薙刀和符纸: [holding_naginata,holding_polearm, holding_ofuda]", "拿太刀: [holding_katana]", "拿手里剑苦无: [holding_shuriken, holding_kunai]", "拿剑: [holding_sword]", "拿剑盾: [holding_sword, holding_shield]", "拿能量剑: [holding_energy_sword]", "拿能量枪: [holding_energy_gun]", "拿能量剑盾: [holding_energy_sword, holding_shield]", "拿骑枪: [holding_lance, huge_weapon]", "拿长枪: [holding_spear, holding_polearm, huge_weapon]", "拿战斧: [holding_axe, huge_weapon]", "拿战戟: [holding_halberd, holding_polearm, huge_weapon]", "拿战锤: [holding_hammer, holding_polearm, huge_weapon]", "拿镰刀: [holding_scythe, holding_polearm, huge_weapon]", "拿法杖: [holding_staff]", "握着鞭子: [holding_whip, riding_crop]", "拿网球拍: [holding_tennis_racket]", "拿法杖和书: [holding_staff, holding_book]", "拿未拆避孕套: [holding_condom, condom_wrapper]", "拿未拆避孕套条: [holding_condom, condom_packet_strip]", "拿用过的避孕套: [holding_condom, used_condom]" ], 
}

SUIT_MAPPING = {
    "网球服": ["拿网球拍: [holding_tennis_racket]"], "皮革女王": ["握着鞭子: [holding_whip, riding_crop]"], "偶像打歌服": ["拿麦克风: [holding_microphone]"], "艾达王cos": ["拿手枪: [holding_handgun, thigh_holster]"], "骑士姬": ["拿巨剑: [holding_greatsword, huge_weapon]", "拿剑盾: [holding_sword, holding_shield]", "拿骑枪: [holding_lance, huge_weapon]", "拿长枪: [holding_spear, holding_polearm, huge_weapon]", "拿战斧: [holding_axe, huge_weapon]", "拿战戟: [holding_halberd, holding_polearm, huge_weapon]", "拿战锤: [holding_hammer, holding_polearm, huge_weapon]"], "比基尼盔甲": ["拿巨剑: [holding_greatsword, huge_weapon]", "拿剑盾: [holding_sword, holding_shield]", "拿骑枪: [holding_lance, huge_weapon]", "拿长枪: [holding_spear, holding_polearm, huge_weapon]", "拿战斧: [holding_axe, huge_weapon]", "拿战戟: [holding_halberd, holding_polearm, huge_weapon]", "拿战锤: [holding_hammer, holding_polearm, huge_weapon]"], "机娘": ["拿巨剑: [holding_greatsword, huge_weapon]", "拿能量剑: [holding_energy_sword]", "拿能量枪: [holding_energy_gun]", "拿能量剑盾: [holding_energy_sword, holding_shield]", "拿骑枪: [holding_lance, huge_weapon]", "拿长枪: [holding_spear, holding_polearm, huge_weapon]", "拿战斧: [holding_axe, huge_weapon]", "拿战戟: [holding_halberd, holding_polearm, huge_weapon]", "拿战锤: [holding_hammer, holding_polearm, huge_weapon]"], "魔法少女": ["拿魔杖: [holding_wand]", "拿巨剑: [holding_greatsword, huge_weapon]", "拿弓箭: [holding_bow_weapon, holding_arrow]"], "巫女": ["拿弓箭: [holding_bow_weapon, holding_arrow]", "拿弓箭和符纸: [holding_bow_weapon, holding_ofuda]", "拿薙刀: [holding_naginata,holding_polearm]", "拿薙刀和符纸: [holding_naginata,holding_polearm, holding_ofuda]"], "阴阳师": ["拿弓箭: [holding_bow_weapon, holding_arrow]", "拿弓箭和符纸: [holding_bow_weapon, holding_ofuda]", "拿薙刀: [holding_naginata,holding_polearm]", "拿薙刀和符纸: [holding_naginata,holding_polearm, holding_ofuda]"], "护士": ["握着平板电脑: [holding_tablet_pc]", "握着剪贴板: [holding_clipboard]", "拿枕头挂听诊器: [holding_syringe, stethoscope]"], "女警": ["拿步枪: [holding_rifle]", "拿突击步枪: [holding_assault_rifle]", "拿手枪: [holding_handgun, thigh_holster]", "拿左轮手枪: [holding_revolver]"], "军装": ["拿步枪: [holding_rifle]", "拿突击步枪: [holding_assault_rifle]", "拿手枪: [holding_handgun, thigh_holster]", "拿左轮手枪: [holding_revolver]"], "nazi": ["拿步枪: [holding_rifle]", "拿突击步枪: [holding_assault_rifle]", "拿手枪: [holding_handgun, thigh_holster]", "拿左轮手枪: [holding_revolver]"], "女忍": ["拿太刀: [holding_katana]", "拿手里剑苦无: [holding_shuriken, holding_kunai]"], "对魔忍": ["拿太刀: [holding_katana]", "拿手里剑苦无: [holding_shuriken, holding_kunai]"], "战斗修女": ["忠诚链锯剑爆弹手枪: [holding_chainsaw, holding_handgun]"], "女巫": ["拿镰刀: [holding_scythe, holding_polearm, huge_weapon]", "拿法杖: [holding_staff]", "拿法杖和书: [holding_staff, holding_book]"], "白无垢": ["拿着花束: [holding_bouquet]"], "新娘": ["拿着花束: [holding_bouquet]"]
}

COLOR_DATA = {
    "shoe_col": [
        "(不指定)", 
        "🔴红色: [red]", "🔴深红色: [darkred]", "🟤🔴栗色: [maroon]", 
        "🟠橙色: [orange]", "🟡金色: [gold]", "🟡黄色: [yellow]", 
        "🟢淡绿色: [lightgreen]", "🟢绿色: [green]", "🟢墨绿色: [darkgreen]", "🟢🔵青色: [aqua]", 
        "🔵淡蓝色: [lightblue]", "🔵蓝色: [blue]", "🔵深蓝色: [darkblue]", 
        "🟣淡紫色: [lightpurple]", "🟣紫色: [purple]", "🟣深紫色: [darkpurple]", 
        "🩷淡粉色: [lightpink]", "🩷粉色: [pink]", "🩷深粉色: [dark pink]", 
        "🟤⚪浅棕色: [light brown]", "🟤深棕色: [brown]", "🟤⚪⚪米色: [beige]", 
        "⚪白色: [white]", "⚪🩶银色: [silver]", "🩶灰色: [grey]", "⚫黑色: [black]", 
    ],
    "leg_col": [
        "(不指定)", 
        "🔴红色: [red]", 
        "🟣淡紫色: [lightpurple]", 
        "🩷淡粉色: [lightpink]", 
        "🟤深棕色: [brown]", 
        "🟤⚪⚪米色: [beige]", 
        "⚪白色: [white]", 
        "⚫黑色: [black]", 
    ],
    "und_col": [
        "(不指定)", 
        "🔴红色: [red]", "🔴深红色: [darkred]", 
        "🟡金色: [gold]", "🟢🔵青色: [aqua]", 
        "🔵蓝色: [blue]", "🟣紫色: [purple]",
        "🩷淡粉色: [lightpink]", "🩷深粉色: [dark pink]", 
        "⚪白色: [white]", "⚫黑色: [black]", 
    ],
    "cloth_col": [
        "(不指定)", 
        "🔴红色: [red]", "🔴深红色: [darkred]", "🔴绯红色: [crimson]", "🟤🔴栗色: [maroon]", 
        "🟠橙色: [orange]", "🟡淡黄色: [lightyellow]", "🟡黄色: [yellow]", 
        "🟢淡绿色: [lightgreen]", "🟢墨绿色: [darkgreen]", "🟢🔵青色: [aqua]", 
        "🔵淡蓝色: [lightblue]", "🔵深蓝色: [darkblue]", "🔵🟣靛蓝色: [indigo]",
        "🟣淡紫色: [lightpurple]", "🟣深紫色: [darkpurple]", 
        "🩷淡粉色: [lightpink]", "🩷深粉色: [dark pink]", 
        "🟤深棕色: [brown]", "🟤⚪浅棕色: [light brown]", "🟤⚪⚪米色: [beige]", "🟤⚪⚪卡其色: [khaki]", 
        "⚪白色: [white]", "🩶灰色: [grey]", "⚫黑色: [black]", 
    ]
}

CONSOLIDATED_DATA = {
    "FEMALE_CHARACTER_DATA": FEMALE_CHARACTER_DATA,
    "shoe_col": COLOR_DATA["shoe_col"],
    "leg_col": COLOR_DATA["leg_col"],
    "und_col": COLOR_DATA["und_col"],
    "cloth_col": COLOR_DATA["cloth_col"]
}

# ==============================================================================
# 附属配置 (只保留鞋子、丝袜、手持)
# ==============================================================================
SUB_CONFIG = [
    ("legwear", "丝袜", "leg_col", "丝袜颜色", "leg_col"),
    ("shoes", "鞋子", "shoe_col", "鞋子颜色", "shoe_col"), 
    ("holding", "手持物品", None, None, None),
]

# ==============================================================================
# 服装模式配置
# ==============================================================================
CLOTHING_MODES_CONFIG = {
    "G1_Nude": { "items": [] },
    "G2_Outfit": {
        "items": [ ("outfits", "G2:套装", None, None, None) ]
    },
    "G3_Cosplay": {
        "items": [ ("cosplay", "G3:Cosplay", None, None, None) ]
    },
    "G4_Dress": {
        "items": [ ("dress", "G4:连衣裙", "cloth_col", "连衣裙颜色", "cloth_col") ]
    },
    "G5_MixMatch": {
        "items": [
            ("topwear", "G5:上衣", "cloth_col", "上衣颜色", "cloth_col"),
            ("bottomwear", "G5:下装", "cloth_col", "下装颜色", "cloth_col"),
            ("outcover", "G5:外套", "cloth_col", "外套颜色", "cloth_col"), 
        ]
    },
    "G6_Lingerie": {
        "items": [
            ("bra", "G6:胸罩", "und_col", "内衣颜色", "und_col"),
            ("panties", "G6:内裤", "und_col", "内衣颜色", "und_col"),
        ]
    }
}

# ==============================================================================
# 通用辅助函数
# ==============================================================================
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

# ==============================================================================
# 节点类: 服装定制器 (Costume Customizer)
# ==============================================================================
class SlaaneshCostumeCustomizer:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        required_inputs = {
            "总开关": ("BOOLEAN", {"default": True, "label_on": "节点开启", "label_off": "节点关闭", "display": "toggle"}), 
            "模式选择": (["🔒 手动指定", "🎲 部分随机(手动优先)", "🔓 完全随机"], {"default": "🎲 部分随机(手动优先)"}),
            "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF, "step": 1}),
            "出图模式": (["头像 (Portrait)", "上半身 (Upper Body)", "胸像 (Breast Focus)", "中景 (Cowboy Shot)", "下半身 (Lower Body)", "全身 (Full Body)"], {"default": "全身 (Full Body)"}),
            "服装模式": (["G1: 全裸 (Nude)", "G2: 套装 (Uniform)", "G3: Cosplay (角色扮演)", "G4: 连衣裙 (Dress)", "G5: 上下混搭 (Mix & Match)", "G6: 内衣 (Lingerie)"], {"default": "G1: 全裸 (Nude)"}),
        }

        # 加载 CLOTHING_MODES (主服装) - 不带开关，默认随机
        for mode_key, mode_data in CLOTHING_MODES_CONFIG.items():
            for item_en_key, item_cn_key, color_en_key, color_cn_key, color_data_source in mode_data["items"]:
                
                # 仅为 "outcover" 添加入口开关
                if item_en_key == "outcover":
                    required_inputs[f"启用_{item_cn_key}"] = ("BOOLEAN", {"default": False, "label_on": "开启", "label_off": "关闭"})

                raw_list = FEMALE_CHARACTER_DATA.get(item_en_key, ["(不指定)"])
                clean_list = [x for x in raw_list if x != "(不指定)"]
                ui_list = ["🎲 随机"] + [register_opt(x) for x in clean_list if x]
                required_inputs[item_cn_key] = (ui_list,)
                
                if color_cn_key:
                    # [UI排版优化] 如果是G6内衣模式且当前是胸罩(bra)，跳过颜色注册
                    # 目的是让颜色选项等到内裤(panties)时再注册，从而显示在最下方
                    if mode_key == "G6_Lingerie" and item_en_key == "bra":
                        continue

                    if color_cn_key not in required_inputs:
                        raw_color_list = CONSOLIDATED_DATA.get(color_data_source, ["(不指定)"])
                        clean_color_list = [x for x in raw_color_list if x != "(不指定)"]
                        ui_color_list = ["🎲 随机"] + [register_opt(x) for x in clean_color_list if x]
                        required_inputs[color_cn_key] = (ui_color_list,)

        # 加载 SUB_CONFIG (鞋袜手持) - 带开关
        for item_en_key, item_cn_key, color_en_key, color_cn_key, color_data_source in SUB_CONFIG:
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

    # [修改] 移除了第4个输出类型
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    # [修改] 移除了第4个输出名称
    RETURN_NAMES = ("正面提示词", "负面提示词", "手部提示词")
    FUNCTION = "process_costume"
    CATEGORY = "slaaneshcontroller/character"

    @classmethod
    def IS_CHANGED(s, **kwargs):
        if kwargs.get("总开关") and kwargs.get("模式选择") != "🔒 手动指定":
            return int(kwargs.get("seed", 0))
        return False

    def process_costume(self, **kwargs):
        
        def parse_layered_string(text, mode_str):
            if not text or "(不指定)" in text or "🎲" in text: return ""
            if "__HEAD__" not in text and "__UPPER__" not in text: return text
            parts = re.split(r'__(?:HEAD|UPPER|LEG)__', text)
            while len(parts) < 4: parts.append("")
            
            kept_parts = []
            if "头像" in mode_str: kept_parts = [parts[0]]
            elif "上半身" in mode_str: kept_parts = [parts[0], parts[1]]
            elif "胸像" in mode_str: kept_parts = [parts[1], parts[2]]
            elif "中景" in mode_str: kept_parts = [parts[0], parts[1], parts[2]]
            elif "下半身" in mode_str: kept_parts = [parts[1], parts[2], parts[3]]
            else: kept_parts = parts

            return ", ".join(list(filter(None, map(str.strip, kept_parts))))

        if not kwargs.get("总开关", False): return ("", "", "")

        pos_parts = []
        neg_parts = []
        mode = kwargs.get("模式选择", "🔒 手动指定")
        seed = int(kwargs.get("seed", 0))
        rng = random.Random(seed)
        
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

        clothing_mode_select = kwargs.get("服装模式", "(不指定)")

        blocked_slots = []
        if "头像" in shot_mode:
            blocked_slots = ["bottomwear", "legwear", "shoes", "panties", "holding"]
        elif "上半身" in shot_mode:
            blocked_slots = ["legwear", "shoes"]
        elif "胸像" in shot_mode:
            blocked_slots = ["shoes"]
        elif "中景" in shot_mode:
            blocked_slots = ["shoes"]

        # 1. 确定服装组 (保持原有逻辑)
        active_group_key = None
        if clothing_mode_select != "(不指定)":
            prefix = clothing_mode_select.split(":")[0]
            for key in CLOTHING_MODES_CONFIG.keys():
                if key.startswith(prefix):
                    active_group_key = key
                    break
        elif mode != "🔒 手动指定":
            random_keys = [k for k in CLOTHING_MODES_CONFIG.keys() if k != "G1_Nude"]
            active_group_key = rng.choice(random_keys)

        is_nude = (active_group_key == "G1_Nude")
        if is_nude: pos_parts.append("completely nude")

        # 2. 处理服装项
        current_suit_name = ""
        if active_group_key and not is_nude:
            group_data = CLOTHING_MODES_CONFIG[active_group_key]
            for item_en_key, item_cn_key, color_en_key, color_cn_key, color_data_source in group_data["items"]:
                
                if active_group_key == "G5_MixMatch" and item_en_key in blocked_slots: continue

                # 外套开关逻辑检查
                if item_en_key == "outcover":
                    if not kwargs.get(f"启用_{item_cn_key}", False):
                        continue

                item_val = kwargs.get(item_cn_key, "🎲 随机")
                item_manual = GLOBAL_OPTS_MAP.get(item_val, item_val)
                
                raw_text = ""
                if item_manual == "🎲 随机":
                    item_pool = FEMALE_CHARACTER_DATA.get(item_en_key, ["(不指定)"])
                    valid_items = [x for x in item_pool if x != "(不指定)"]
                    if valid_items:
                        raw_text = rng.choice(valid_items)
                else:
                    raw_text = item_manual

                if active_group_key in ["G2_Outfit", "G3_Cosplay"] and raw_text:
                    current_suit_name = raw_text

                pc_pos = extract_tag(raw_text, "pos")
                if active_group_key in ["G2_Outfit", "G3_Cosplay", "G4_Dress"]:
                    pc_pos = parse_layered_string(pc_pos, shot_mode)

                raw_color = ""
                if color_en_key:
                    color_val = kwargs.get(color_cn_key, "🎲 随机")
                    color_manual = GLOBAL_OPTS_MAP.get(color_val, color_val)
                    
                    if color_manual == "🎲 随机":
                        if raw_text:
                            color_pool = CONSOLIDATED_DATA.get(color_data_source, ["(不指定)"])
                            valid_colors = [x for x in color_pool if x != "(不指定)"]
                            if valid_colors:
                                raw_color = rng.choice(valid_colors)
                    else:
                        raw_color = color_manual

                pcc_pos = extract_tag(raw_color, "pos")
                
                # 颜色提示词拼接优化 (后缀模式)
                combined = ""
                if pcc_pos and pc_pos:
                    if item_en_key == "dress":
                        # 连衣裙: [tag], [color] dress
                        combined = f"{pc_pos}, {pcc_pos} dress"
                    elif item_en_key == "topwear":
                        # 上衣: [tag], [color] top
                        combined = f"{pc_pos}, {pcc_pos} top"
                    elif item_en_key == "bottomwear":
                        # 下装: [tag], [color] bottom
                        combined = f"{pc_pos}, {pcc_pos} bottom"
                    else:
                        # 外套、内衣等保持默认: [color] [tag]
                        combined = f"{pcc_pos} {pc_pos}"
                else:
                    combined = pcc_pos or pc_pos

                if combined: pos_parts.append(enforce_str(combined))

                pc_neg = extract_tag(raw_text, "neg")
                pcc_neg = extract_tag(raw_color, "neg")
                if pc_neg: neg_parts.append(pc_neg)
                if pcc_neg: neg_parts.append(pcc_neg)

        # 3. 处理鞋袜手持
        for item_en_key, item_cn_key, color_en_key, color_cn_key, color_data_source in SUB_CONFIG:
            
            is_enabled = kwargs.get(f"启用_{item_cn_key}", False)
            if not is_enabled: continue

            if item_en_key in blocked_slots: continue
            
            common_blocked = ["shoes", "legwear"]
            if is_nude and item_en_key in common_blocked: continue
            if active_group_key in ["G2_Outfit", "G3_Cosplay"] and item_en_key in common_blocked: continue

            item_val = kwargs.get(item_cn_key, "🎲 随机")
            item_manual = GLOBAL_OPTS_MAP.get(item_val, item_val)
            
            raw_text = ""
            
            if item_en_key == "holding":
                if is_nude: continue
                matched_pool = next((pool for s_key, pool in SUIT_MAPPING.items() if s_key in current_suit_name), None)
                
                force_random = (mode == "🔓 完全随机")
                if not force_random and item_manual != "🎲 随机":
                    raw_text = item_manual
                else:
                    if matched_pool: 
                        raw_text = rng.choice(matched_pool)
                    else:
                        item_pool = FEMALE_CHARACTER_DATA.get("holding", ["(不指定)"])
                        valid_items = [x for x in item_pool if x != "(不指定)"]
                        if valid_items: 
                            raw_text = rng.choice(valid_items)
                
                p = extract_tag(raw_text, "pos")
                n = extract_tag(raw_text, "neg")
                if p: pos_parts.append(p)
                if n: neg_parts.append(n)
                continue

            force_random = (mode == "🔓 完全随机")
            if not force_random and item_manual != "🎲 随机":
                raw_text = item_manual
            else:
                item_pool = FEMALE_CHARACTER_DATA.get(item_en_key, ["(不指定)"])
                valid_items = [x for x in item_pool if x != "(不指定)"]
                if valid_items:
                    raw_text = rng.choice(valid_items)

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
                        raw_color = rng.choice(valid_colors)

            p_item = extract_tag(raw_text, "pos")
            p_color = extract_tag(raw_color, "pos")
            
            # 附属物品的颜色拼接优化
            combined = ""
            if p_color and p_item:
                if item_en_key == "shoes":
                    # 鞋子: [tag], [color] shoes
                    combined = f"{p_item}, {p_color} shoes"
                else:
                    # 丝袜等: [color] [tag]
                    combined = f"{p_color} {p_item}"
            else:
                combined = p_color or p_item

            if combined: pos_parts.append(enforce_str(combined))

            n_item = extract_tag(raw_text, "neg")
            n_color = extract_tag(raw_color, "neg")
            if n_item: neg_parts.append(n_item)
            if n_color: neg_parts.append(n_color)

        final_pos = ", ".join(filter(None, pos_parts))
        final_neg = ", ".join(filter(None, neg_parts))
        if final_pos: final_pos += ", "
        if final_neg: final_neg += ", "

        # ==============================================================================
        # 新增: 手部与脚部提示词提取逻辑
        # ==============================================================================
        
        # 定义关键词库
        glove_keywords = ["gloves", "gauntlets", "bracer", "arm warmers"]
        # [修改] 删除了 foot_keywords 列表

        # 分割最终的正向提示词 (保持原始Tag格式，不转小写，仅匹配时转小写)
        raw_tags = [t.strip() for t in final_pos.split(',') if t.strip()]
        
        extracted_gloves = []
        # [修改] 删除了 extracted_feet 列表

        for tag in raw_tags:
            tag_lower = tag.lower()
            
            # 过滤掉 "holding" (手持物品)，防止 "holding shoes" 被识别为脚部
            if "holding" in tag_lower:
                continue

            # 检测手套
            if any(k in tag_lower for k in glove_keywords):
                extracted_gloves.append(tag)
                
            # [修改] 删除了检测鞋袜的循环逻辑

        # 构建手部提示词
        hand_output_list = ["perfect detailed hands"]
        if extracted_gloves:
            hand_output_list.extend(extracted_gloves)
        else:
            hand_output_list.append("fingernails")
            
        final_hand = ", ".join(hand_output_list)
        if final_hand: final_hand += ", "

        # [修改] 删除了 final_foot 的构建
        # [修改] 返回值中移除了 final_foot
        return (final_pos, final_neg, final_hand)

NODE_CLASS_MAPPINGS = { 
    "SlaaneshCostumeCustomizer": SlaaneshCostumeCustomizer
}
NODE_DISPLAY_NAME_MAPPINGS = { 
    "SlaaneshCostumeCustomizer": "色孽の女角色服装定制器"
}
