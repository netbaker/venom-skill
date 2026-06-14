#!/usr/bin/env python3
"""
毒液 - 知识猎食者
打破信息茧房，发现意想不到的知识关联
"""

import os
import random
import json
from pathlib import Path
from datetime import datetime
import hashlib

class Venom:
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path)
        self.skills_path = self.workspace_path / ".workbuddy" / "skills" / "venom"
        self.config_file = self.skills_path / "interests.json"
        self.history_file = self.skills_path / "history.json"
        self.config = self.load_config()
        self.history = self.load_history()
        
    def load_config(self):
        """加载配置文件"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "interests": ["AI", "编程", "投资", "健康", "心理学", "设计", "哲学", "科学"],
            "custom_sources": []
        }
    
    def load_history(self):
        """加载猎食历史"""
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_history(self):
        """保存猎食历史"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def scan_scripts(self):
        """扫描工作区脚本"""
        script_extensions = ['.py', '.js', '.sh', '.bat', '.html', '.css', '.json']
        scripts = []
        
        for ext in script_extensions:
            scripts.extend(self.workspace_path.rglob(f"*{ext}"))
        
        # 排除一些目录
        exclude_dirs = {'.git', 'node_modules', '__pycache__', '.workbuddy'}
        scripts = [s for s in scripts if not any(excluded in s.parts for excluded in exclude_dirs)]
        
        return scripts
    
    def scan_notes(self):
        """扫描最近笔记"""
        notes = list(self.workspace_path.rglob("*.md"))
        
        # 排除一些目录
        exclude_dirs = {'.git', 'node_modules', '__pycache__', '.workbuddy'}
        notes = [n for n in notes if not any(excluded in n.parts for excluded in exclude_dirs)]
        
        # 按修改时间排序
        notes.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        return notes
    
    def get_interest_content(self):
        """获取个人兴趣相关内容"""
        interest = random.choice(self.config["interests"])
        
        # 在工作区中搜索相关内容
        related_files = []
        for file in self.workspace_path.rglob("*"):
            if file.is_file() and interest.lower() in file.name.lower():
                related_files.append(file)
        
        return interest, related_files
    
    def get_random_knowledge(self):
        """获取随机知识"""
        # 这里可以集成外部API，目前返回本地知识
        knowledge_sources = [
            "你知道吗？Python的GIL（全局解释器锁）在多线程场景下会限制CPU密集型任务的性能。",
            "JavaScript的闭包可以捕获外部变量，这是函数式编程的重要特性。",
            "投资中的复利效应：年化10%，7年翻倍。",
            "人类大脑每天产生约70,000个想法。",
            "设计中的黄金比例：1:1.618，广泛应用于艺术和建筑。",
            "心理学中的锚定效应：人们倾向于依赖第一个接收到的信息。",
            "量子计算的叠加态：一个量子比特可以同时处于0和1的状态。",
            "健康小知识：每天步行10,000步可以显著改善心血管健康。"
        ]
        return random.choice(knowledge_sources)
    
    def scan_moc(self):
        """扫描Dashboard MOC"""
        moc_files = []
        
        # 扫描索引文件
        index_patterns = ["*index*", "*toc*", "*dashboard*", "*moc*", "*目录*"]
        for pattern in index_patterns:
            moc_files.extend(self.workspace_path.rglob(f"{pattern}.md"))
        
        # 扫描目录结构
        directories = [d for d in self.workspace_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
        
        return moc_files, directories
    
    def extract_preview(self, file_path, max_lines=10):
        """提取文件内容预览"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:max_lines]
                return ''.join(lines)
        except:
            return f"[无法读取文件内容]"
    
    def generate_insight(self, file_path, content):
        """生成知识关联提示"""
        insights = [
            "这个文件展示了代码的优雅结构。",
            "看看这个实现，也许能启发你解决其他问题。",
            "代码中的模式往往反映了更深层的设计思想。",
            "每次阅读代码都是一次学习机会。",
            "优秀的代码就像诗歌，值得细细品味。"
        ]
        return random.choice(insights)
    
    def hunt(self):
        """开始猎食"""
        # 随机选择触手
        tentacles = ["脚本", "笔记", "兴趣", "知识", "MOC"]
        tentacle = random.choice(tentacles)
        
        result = {
            "tentacle": tentacle,
            "timestamp": datetime.now().isoformat(),
            "content": None
        }
        
        if tentacle == "脚本":
            scripts = self.scan_scripts()
            if scripts:
                script = random.choice(scripts)
                preview = self.extract_preview(script)
                result["content"] = {
                    "type": "script",
                    "path": str(script),
                    "preview": preview,
                    "insight": self.generate_insight(script, preview)
                }
            else:
                result["content"] = {"type": "empty", "message": "没有找到脚本文件"}
        
        elif tentacle == "笔记":
            notes = self.scan_notes()
            if notes:
                note = random.choice(notes)
                preview = self.extract_preview(note)
                result["content"] = {
                    "type": "note",
                    "path": str(note),
                    "preview": preview,
                    "insight": self.generate_insight(note, preview)
                }
            else:
                result["content"] = {"type": "empty", "message": "没有找到笔记文件"}
        
        elif tentacle == "兴趣":
            interest, related_files = self.get_interest_content()
            if related_files:
                file = random.choice(related_files)
                preview = self.extract_preview(file)
                result["content"] = {
                    "type": "interest",
                    "interest": interest,
                    "path": str(file),
                    "preview": preview,
                    "insight": f"你对「{interest}」感兴趣，这个文件可能相关。"
                }
            else:
                result["content"] = {
                    "type": "interest",
                    "interest": interest,
                    "message": f"没有找到与「{interest}」直接相关的文件"
                }
        
        elif tentacle == "知识":
            knowledge = self.get_random_knowledge()
            result["content"] = {
                "type": "knowledge",
                "content": knowledge,
                "insight": "随机知识，打破思维定式。"
            }
        
        elif tentacle == "MOC":
            moc_files, directories = self.scan_moc()
            if moc_files:
                moc = random.choice(moc_files)
                preview = self.extract_preview(moc)
                result["content"] = {
                    "type": "moc",
                    "path": str(moc),
                    "preview": preview,
                    "insight": "知识地图，连接不同领域的思想。"
                }
            elif directories:
                directory = random.choice(directories)
                files = list(directory.iterdir())[:5]
                result["content"] = {
                    "type": "moc",
                    "path": str(directory),
                    "files": [str(f) for f in files],
                    "insight": f"探索「{directory.name}」目录，发现隐藏的宝藏。"
                }
            else:
                result["content"] = {"type": "empty", "message": "没有找到MOC文件"}
        
        # 保存历史
        self.history.append(result)
        self.save_history()
        
        return result
    
    def format_result(self, result):
        """格式化猎食结果"""
        tentacle = result["tentacle"]
        content = result["content"]
        
        output = f"🦑 毒液猎食结果\n\n"
        output += f"触手来源：{tentacle}\n"
        
        if content["type"] == "empty":
            output += f"状态：{content['message']}\n"
            return output
        
        if "path" in content:
            output += f"猎物位置：{content['path']}\n"
        
        if "preview" in content:
            output += f"\n猎物预览：\n```\n{content['preview']}\n```\n"
        
        if "content" in content and content["type"] == "knowledge":
            output += f"\n随机知识：\n{content['content']}\n"
        
        if "interest" in content:
            output += f"兴趣领域：{content['interest']}\n"
        
        if "files" in content:
            output += f"\n目录内容：\n"
            for file in content["files"]:
                output += f"  - {file}\n"
        
        if "insight" in content:
            output += f"\n💡 发现提示：{content['insight']}\n"
        
        return output

def main():
    """主函数"""
    workspace = r"D:\整理_个人\workspace\practice"
    venom = Venom(workspace)
    
    print("🦑 毒液启动...\n")
    result = venom.hunt()
    print(venom.format_result(result))

if __name__ == "__main__":
    main()
