#!/usr/bin/env python3
"""
毒液 v2 - 达尔文进化版
适者生存，优胜劣汰
"""

import os
import random
import json
from pathlib import Path
from datetime import datetime
import hashlib

class VenomGene:
    """毒液基因 - 控制猎食策略"""
    
    def __init__(self):
        # 触手权重（基因）- 初始值相等
        self.tentacle_weights = {
            "脚本": 1.0,
            "笔记": 1.0,
            "兴趣": 1.0,
            "知识": 1.0,
            "MOC": 1.0
        }
        
        # 猎物选择偏好（基因）
        self.prefer_recent = 0.5  # 偏好最近文件的程度
        self.code_preview_lines = 15  # 代码预览行数
        self.note_preview_lines = 8  # 笔记预览行数
        
        # 适应度记录
        self.fitness_history = []
        
    def mutate(self, rate=0.1):
        """基因变异 - 随机调整权重"""
        for key in self.tentacle_weights:
            if random.random() < rate:
                # 变异：随机增减权重
                delta = random.uniform(-0.3, 0.3)
                self.tentacle_weights[key] = max(0.1, min(2.0, self.tentacle_weights[key] + delta))
        
        # 变异偏好
        if random.random() < rate:
            self.prefer_recent = max(0.1, min(0.9, self.prefer_recent + random.uniform(-0.2, 0.2)))
    
    def select_tentacle(self):
        """自然选择 - 基于权重随机选择触手"""
        tentacles = list(self.tentacle_weights.keys())
        weights = [self.tentacle_weights[t] for t in tentacles]
        return random.choices(tentacles, weights=weights, k=1)[0]
    
    def update_fitness(self, tentacle, score):
        """更新适应度 - 记录哪些触手更成功"""
        self.fitness_history.append({
            "tentacle": tentacle,
            "score": score,
            "timestamp": datetime.now().isoformat()
        })
        
        # 基于历史调整权重
        self._evolve_weights()
    
    def _evolve_weights(self):
        """进化 - 根据适应度调整权重"""
        if len(self.fitness_history) < 5:
            return  # 数据太少，不进化
        
        # 计算每个触手的平均得分
        recent_history = self.fitness_history[-20:]  # 只看最近20次
        tentacle_scores = {}
        
        for record in recent_history:
            t = record["tentacle"]
            s = record["score"]
            if t not in tentacle_scores:
                tentacle_scores[t] = []
            tentacle_scores[t].append(s)
        
        # 计算平均分
        avg_scores = {}
        for t, scores in tentacle_scores.items():
            avg_scores[t] = sum(scores) / len(scores)
        
        # 根据得分调整权重（适者生存）
        for t in self.tentacle_weights:
            if t in avg_scores:
                # 得分高的触手权重增加，得分低的权重减少
                delta = (avg_scores[t] - 0.5) * 0.2  # 0.5是基准线
                self.tentacle_weights[t] = max(0.1, min(2.0, self.tentacle_weights[t] + delta))
    
    def get_status(self):
        """获取基因状态"""
        return {
            "weights": self.tentacle_weights.copy(),
            "prefer_recent": self.prefer_recent,
            "total_hunts": len(self.fitness_history),
            "avg_fitness": sum(r["score"] for r in self.fitness_history) / max(len(self.fitness_history), 1)
        }


class VenomEvolved:
    """毒液 v2 - 达尔文进化版"""
    
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path)
        self.skills_path = self.workspace_path / ".workbuddy" / "skills" / "venom"
        self.gene_file = self.skills_path / "gene.json"
        self.gene = self.load_gene()
        
    def load_gene(self):
        """加载基因"""
        if self.gene_file.exists():
            with open(self.gene_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                gene = VenomGene()
                gene.tentacle_weights = data.get("weights", gene.tentacle_weights)
                gene.prefer_recent = data.get("prefer_recent", gene.prefer_recent)
                gene.fitness_history = data.get("fitness_history", [])
                return gene
        return VenomGene()
    
    def save_gene(self):
        """保存基因"""
        data = {
            "weights": self.gene.tentacle_weights,
            "prefer_recent": self.gene.prefer_recent,
            "fitness_history": self.gene.fitness_history[-50:]  # 只保留最近50条
        }
        with open(self.gene_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def scan_scripts(self):
        """扫描工作区脚本"""
        script_extensions = ['.py', '.js', '.sh', '.bat', '.html', '.css', '.json']
        scripts = []
        
        for ext in script_extensions:
            scripts.extend(self.workspace_path.rglob(f"*{ext}"))
        
        exclude_dirs = {'.git', 'node_modules', '__pycache__', '.workbuddy'}
        scripts = [s for s in scripts if not any(excluded in s.parts for excluded in exclude_dirs)]
        
        return scripts
    
    def scan_notes(self):
        """扫描最近笔记"""
        notes = list(self.workspace_path.rglob("*.md"))
        
        exclude_dirs = {'.git', 'node_modules', '__pycache__', '.workbuddy'}
        notes = [n for n in notes if not any(excluded in n.parts for excluded in exclude_dirs)]
        
        notes.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        return notes
    
    def get_interest_content(self):
        """获取个人兴趣相关内容"""
        interests = ['AI', '编程', '投资', '健康', '心理学', '设计', '哲学', '科学', '机器学习', '创业']
        interest = random.choice(interests)
        
        related_files = []
        for file in self.workspace_path.rglob("*"):
            if file.is_file() and interest.lower() in file.name.lower():
                related_files.append(file)
        
        return interest, related_files
    
    def get_random_knowledge(self):
        """获取随机知识"""
        knowledge_pool = [
            ('量子计算', '一个量子比特可以同时处于0和1的叠加态，这让量子计算机能并行处理指数级的计算任务。'),
            ('设计原理', '黄金比例 1:1.618 在自然界和艺术中无处不在，从向日葵的种子排列到帕特农神庙的建筑比例。'),
            ('心理学', '锚定效应：人们做决策时会过度依赖第一个接收到的信息，即使这个信息与决策无关。'),
            ('投资', '复利的魔力：年化10%的收益，7年翻倍，20年翻7倍，50年翻117倍。'),
            ('编程', '递归的美：一个函数调用自身，就像两面镜子之间的无限反射，但必须有一个退出条件。'),
            ('生物学', '人类大脑有860亿个神经元，每个神经元平均有7000个突触连接，总连接数比银河系的星星还多。'),
            ('物理学', '熵增定律：宇宙的总熵永远在增加，这就是为什么时间只能向前流逝。'),
            ('哲学', '忒修斯之船：如果一艘船的所有零件都被替换，它还是原来那艘船吗？'),
            ('数学', '欧拉恒等式 e^(iπ) + 1 = 0 被誉为最美的数学公式，它将五个最重要的数学常数联系在一起。'),
            ('神经科学', '大脑的可塑性：即使成年后，大脑仍然可以通过学习和练习重塑神经连接。'),
            ('化学', '水的密度在4°C时最大，这就是为什么冰会浮在水面上——这个反常现象拯救了地球上的生命。'),
            ('天文学', '宇宙的年龄是138亿年，但我们可观测的宇宙直径是930亿光年——因为宇宙本身在膨胀。'),
            ('计算机科学', '图灵机是所有现代计算机的理论基础，它证明了有些问题是无法被任何算法解决的。'),
            ('经济学', '机会成本：做任何选择的真正成本，是你放弃的那个选项的价值。'),
            ('语言学', '萨丕尔-沃尔夫假说：语言决定思维。说不同语言的人，对世界的认知也不同。'),
            ('艺术', '蒙娜丽莎的微笑之所以神秘，是因为达芬奇用了"晕涂法"，让嘴角的轮廓模糊不清。'),
            ('历史', '印刷术的发明让知识民主化，互联网的发明让信息民主化，AI的发明正在让智能民主化。'),
            ('医学', '安慰剂效应：即使药片是假的，只要病人相信它有效，身体就会产生真实的生理反应。'),
            ('社会学', '邓巴数：人类能维持的稳定社交关系上限是150人——这就是为什么微信好友超过150个就开始混乱。'),
            ('进化论', '人类和香蕉共享60%的DNA，和黑猩猩共享98.7%的DNA——生命的统一性令人惊叹。'),
        ]
        return random.choice(knowledge_pool)
    
    def scan_moc(self):
        """扫描Dashboard MOC"""
        directories = [d for d in self.workspace_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
        return directories
    
    def extract_preview(self, file_path, max_lines=15):
        """提取文件内容预览"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:max_lines]
                return ''.join(lines)
        except:
            return "[无法读取文件内容]"
    
    def hunt(self):
        """开始猎食 - 达尔文选择"""
        # 自然选择触手
        tentacle = self.gene.select_tentacle()
        
        result = {
            "tentacle": tentacle,
            "timestamp": datetime.now().isoformat(),
            "content": None
        }
        
        if tentacle == "脚本":
            scripts = self.scan_scripts()
            if scripts:
                # 基因决定偏好：最近 vs 随机
                if random.random() < self.gene.prefer_recent:
                    script = scripts[0] if scripts else None
                else:
                    script = random.choice(scripts)
                
                if script:
                    preview = self.extract_preview(script, self.gene.code_preview_lines)
                    result["content"] = {
                        "type": "script",
                        "path": str(script),
                        "name": script.name,
                        "preview": preview
                    }
        
        elif tentacle == "笔记":
            notes = self.scan_notes()
            if notes:
                # 基因决定偏好：最近 vs 随机
                if random.random() < self.gene.prefer_recent:
                    note = notes[0]
                else:
                    note = random.choice(notes[:10])
                
                preview = self.extract_preview(note, self.gene.note_preview_lines)
                result["content"] = {
                    "type": "note",
                    "path": str(note),
                    "name": note.name,
                    "preview": preview,
                    "modified": datetime.fromtimestamp(note.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                }
        
        elif tentacle == "兴趣":
            interest, related_files = self.get_interest_content()
            result["content"] = {
                "type": "interest",
                "interest": interest,
                "related_count": len(related_files),
                "files": [str(f) for f in related_files[:3]]
            }
        
        elif tentacle == "知识":
            topic, content = self.get_random_knowledge()
            result["content"] = {
                "type": "knowledge",
                "topic": topic,
                "content": content
            }
        
        elif tentacle == "MOC":
            directories = self.scan_moc()
            if directories:
                directory = random.choice(directories)
                files = list(directory.iterdir())[:5]
                result["content"] = {
                    "type": "moc",
                    "path": str(directory),
                    "name": directory.name,
                    "files": [(f.name, f.stat().st_size if f.is_file() else 0) for f in files]
                }
        
        return result
    
    def format_result(self, result):
        """格式化猎食结果"""
        tentacle = result["tentacle"]
        content = result["content"]
        
        output = f"🦑 毒液 v2 · 达尔文进化版\n"
        output += f"{'='*60}\n"
        output += f"触手来源：{tentacle} (权重: {self.gene.tentacle_weights[tentacle]:.2f})\n\n"
        
        if content is None:
            output += "本次猎食无果。\n"
            return output
        
        if content["type"] == "script":
            output += f"📁 工作区脚本\n"
            output += f"猎物：{content['name']}\n"
            output += f"位置：{content['path']}\n\n"
            output += f"预览：\n```\n{content['preview']}\n```\n"
            output += f"\n💡 代码是思想的结晶，每一行都承载着解决问题的智慧。\n"
        
        elif content["type"] == "note":
            output += f"📝 最近笔记\n"
            output += f"猎物：{content['name']}\n"
            output += f"修改时间：{content['modified']}\n\n"
            output += f"预览：\n```\n{content['preview']}\n```\n"
            output += f"\n💡 笔记是思维的快照，记录了某个时刻的灵感。\n"
        
        elif content["type"] == "interest":
            output += f"🎯 个人兴趣\n"
            output += f"随机兴趣：{content['interest']}\n"
            output += f"相关文件：{content['related_count']} 个\n"
            if content['files']:
                output += f"文件列表：\n"
                for f in content['files']:
                    output += f"  - {f}\n"
            output += f"\n💡 兴趣是最好的老师，跟随好奇心走。\n"
        
        elif content["type"] == "knowledge":
            output += f"📚 随机知识\n"
            output += f"领域：{content['topic']}\n\n"
            output += f"{content['content']}\n"
            output += f"\n💡 知识的价值在于连接，今天的随机可能成为明天的灵感。\n"
        
        elif content["type"] == "moc":
            output += f"🗂️ Dashboard MOC\n"
            output += f"探索目录：{content['name']}/\n\n"
            output += f"内容预览：\n"
            for name, size in content['files']:
                if size > 0:
                    output += f"  - {name} ({size} bytes)\n"
                else:
                    output += f"  - {name}/ [目录]\n"
            output += f"\n💡 目录是知识的地图，探索结构发现隐藏的宝藏。\n"
        
        # 显示进化状态
        status = self.gene.get_status()
        output += f"\n{'='*60}\n"
        output += f"🧬 进化状态\n"
        output += f"总猎食次数：{status['total_hunts']}\n"
        output += f"平均适应度：{status['avg_fitness']:.2f}\n"
        output += f"基因变异率：10%\n"
        
        return output
    
    def give_feedback(self, score):
        """用户反馈 - 驱动进化"""
        # score: 0-1，越高表示越有趣
        last_hunt = self.gene.fitness_history[-1] if self.gene.fitness_history else None
        if last_hunt:
            self.gene.update_fitness(last_hunt["tentacle"], score)
            self.save_gene()
            return f"收到反馈！适应度 {score:.2f}，毒液正在进化..."
        return "没有找到最近的猎食记录。"


def main():
    """主函数"""
    workspace = r"D:\整理_个人\workspace\practice"
    venom = VenomEvolved(workspace)
    
    print("🦑 毒液 v2 · 达尔文进化版 启动...\n")
    result = venom.hunt()
    print(venom.format_result(result))
    
    # 保存基因
    venom.save_gene()


if __name__ == "__main__":
    main()
