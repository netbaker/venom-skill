#!/usr/bin/env python3
"""
毒液测试脚本
测试所有触手的功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from venom import Venom

def test_all_tentacles():
    """测试所有触手"""
    workspace = r"D:\整理_个人\workspace\practice"
    venom = Venom(workspace)
    
    print("🦑 毒液测试开始...\n")
    
    # 测试每个触手
    tentacles = ["脚本", "笔记", "兴趣", "知识", "MOC"]
    
    for tentacle in tentacles:
        print(f"\n{'='*50}")
        print(f"测试触手：{tentacle}")
        print('='*50)
        
        # 模拟猎食
        if tentacle == "脚本":
            scripts = venom.scan_scripts()
            print(f"找到 {len(scripts)} 个脚本文件")
            if scripts:
                print(f"示例：{scripts[0].name}")
        
        elif tentacle == "笔记":
            notes = venom.scan_notes()
            print(f"找到 {len(notes)} 个笔记文件")
            if notes:
                print(f"示例：{notes[0].name}")
        
        elif tentacle == "兴趣":
            interest, related_files = venom.get_interest_content()
            print(f"随机兴趣：{interest}")
            print(f"相关文件：{len(related_files)} 个")
        
        elif tentacle == "知识":
            knowledge = venom.get_random_knowledge()
            print(f"随机知识：{knowledge[:50]}...")
        
        elif tentacle == "MOC":
            moc_files, directories = venom.scan_moc()
            print(f"MOC文件：{len(moc_files)} 个")
            print(f"目录：{len(directories)} 个")
    
    print(f"\n{'='*50}")
    print("测试完成！")
    print('='*50)

def test_single_hunt():
    """测试单次猎食"""
    workspace = r"D:\整理_个人\workspace\practice"
    venom = Venom(workspace)
    
    print("\n🦑 单次猎食测试...\n")
    result = venom.hunt()
    print(venom.format_result(result))

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "all":
        test_all_tentacles()
    else:
        test_single_hunt()
