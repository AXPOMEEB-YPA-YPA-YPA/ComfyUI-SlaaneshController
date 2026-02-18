import os
import shutil
import py_compile

# 这里列出你需要加密的文件名
source_files = [
    "AccessoryCustomizer.py",
    "BodyCustomizer.py",
    "CostumeCustomizer.py",
    "GroupSexControl.py",
    "MaleCharacterCustomizer.py",
    "PoseControl.py",
    "SceneControl.py",
    "SoloSexControl.py"
]

# 创建输出目录
output_dir = "dist"
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)
os.makedirs(output_dir)

print(f"🚀 开始编译到 {output_dir} 文件夹...")

# 1. 复制 __init__.py (入口文件保留源码，不要编译，否则容易报错)
if os.path.exists("__init__.py"):
    shutil.copy("__init__.py", os.path.join(output_dir, "__init__.py"))
    print("✅ 已复制 __init__.py")

# 2. 编译其他文件为 .pyc
for filename in source_files:
    if os.path.exists(filename):
        # 目标文件名：例如 PoseControl.pyc
        target_name = filename + "c" 
        target_path = os.path.join(output_dir, target_name)
        
        try:
            # 编译文件
            py_compile.compile(filename, cfile=target_path, doraise=True)
            print(f"🔒 已编译: {filename} -> {target_name}")
        except Exception as e:
            print(f"❌ 编译失败 {filename}: {e}")
    else:
        print(f"⚠️ 文件不存在: {filename}")

print("\n🎉 打包完成！请将 'dist' 文件夹内的内容发布给用户。")