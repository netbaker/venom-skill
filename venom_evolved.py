#!/usr/bin/env python3
"""
毒液 v5 - 周报自动分发 + 连续猎食 streak 版
适者生存，更有深度的猎食体验
v4 基础上新增：连续猎食 Streak + 周报 Markdown 导出 + 成就系统
"""

import os
import re
import random
import json
from pathlib import Path
from datetime import datetime, timedelta
import hashlib


class VenomGene:
    """毒液基因 - 控制猎食策略"""
    
    def __init__(self):
        # 触手权重（基因）
        self.tentacle_weights = {
            "脚本": 1.0,
            "笔记": 1.0,
            "兴趣": 1.0,
            "知识": 1.0,
            "MOC": 1.0
        }
        
        # 猎物选择偏好
        self.prefer_recent = 0.5
        self.code_preview_lines = 20
        self.note_preview_lines = 15
        
        # 适应度记录
        self.fitness_history = []
        
    def mutate(self, rate=0.1):
        """基因变异"""
        for key in self.tentacle_weights:
            if random.random() < rate:
                delta = random.uniform(-0.3, 0.3)
                self.tentacle_weights[key] = max(0.1, min(2.0, self.tentacle_weights[key] + delta))
        
        if random.random() < rate:
            self.prefer_recent = max(0.1, min(0.9, self.prefer_recent + random.uniform(-0.2, 0.2)))
    
    def select_tentacle(self):
        """自然选择 - 基于权重随机选择触手"""
        tentacles = list(self.tentacle_weights.keys())
        weights = [self.tentacle_weights[t] for t in tentacles]
        return random.choices(tentacles, weights=weights, k=1)[0]
    
    def select_multiple_tentacles(self, n=2):
        """自然选择 - 基于权重随机选择n条触手（不重复）"""
        tentacles = list(self.tentacle_weights.keys())
        weights = [self.tentacle_weights[t] for t in tentacles]
        chosen = []
        remaining_tentacles = tentacles[:]
        remaining_weights = weights[:]
        for _ in range(min(n, len(remaining_tentacles))):
            idx = random.choices(range(len(remaining_weights)), weights=remaining_weights, k=1)[0]
            chosen.append(remaining_tentacles[idx])
            remaining_tentacles.pop(idx)
            remaining_weights.pop(idx)
        return chosen
    
    def update_fitness(self, tentacle, score):
        """更新适应度"""
        self.fitness_history.append({
            "tentacle": tentacle,
            "score": score,
            "timestamp": datetime.now().isoformat()
        })
        self._evolve_weights()
    
    def _evolve_weights(self):
        """进化 - 根据适应度调整权重"""
        if len(self.fitness_history) < 5:
            return
        
        recent_history = self.fitness_history[-20:]
        tentacle_scores = {}
        
        for record in recent_history:
            t = record["tentacle"]
            s = record["score"]
            if t not in tentacle_scores:
                tentacle_scores[t] = []
            tentacle_scores[t].append(s)
        
        avg_scores = {}
        for t, scores in tentacle_scores.items():
            avg_scores[t] = sum(scores) / len(scores)
        
        for t in self.tentacle_weights:
            if t in avg_scores:
                delta = (avg_scores[t] - 0.5) * 0.2
                self.tentacle_weights[t] = max(0.1, min(2.0, self.tentacle_weights[t] + delta))
    
    def get_status(self):
        """获取基因状态"""
        return {
            "weights": self.tentacle_weights.copy(),
            "prefer_recent": self.prefer_recent,
            "total_hunts": len(self.fitness_history),
            "avg_fitness": sum(r["score"] for r in self.fitness_history) / max(len(self.fitness_history), 1)
        }


class IntelligentAnalyzer:
    """智能解读器 - 分析内容并生成解读"""
    
    @staticmethod
    def analyze_script(file_path, content):
        """分析脚本文件并生成解读"""
        lines = content.strip().split('\n')
        analysis = {
            "type": "unknown",
            "features": [],
            "insight": ""
        }
        
        filename = Path(file_path).name.lower()
        
        # JS/TS 文件分析
        if filename.endswith(('.js', '.ts', '.jsx', '.tsx')):
            if 'var app' in content or 'const app' in content or 'getApp()' in content:
                analysis["type"] = "小程序应用入口"
                analysis["insight"] = "这是小程序的应用初始化文件，负责全局状态和存储管理。"
            elif 'module.exports' in content or 'exports.' in content:
                analysis["type"] = "模块化导出"
                analysis["insight"] = "使用 CommonJS 模块系统，把功能封装成可复用的模块。"
            elif 'function' in content and '(' in content:
                analysis["type"] = "JavaScript 函数"
                analysis["insight"] = "JavaScript 函数是实现行为的积木，每个函数都在解决一个小问题。"
            elif 'class' in content:
                analysis["type"] = "JavaScript 类"
                analysis["insight"] = "用面向对象的方式组织代码，让业务逻辑更清晰可维护。"
            else:
                analysis["type"] = "JavaScript 脚本"
                analysis["insight"] = "JavaScript 是前端世界的主要语言，负责让页面动起来。"
            analysis["features"].append("JS/TS 脚本")
        
        # JSON 文件分析
        elif filename.endswith('.json') and content.strip().startswith('{'):
            try:
                parsed = json.loads(content)
                keys = list(parsed.keys()) if isinstance(parsed, dict) else []
                analysis["type"] = "配置文件"
                analysis["insight"] = f"JSON 配置文件，定义了 {', '.join(keys[:3])}" if keys else "JSON 配置文件"
                analysis["features"].append(f"{len(keys)}个顶层字段")
            except json.JSONDecodeError:
                analysis["type"] = "JSON 数据"
                analysis["insight"] = "JSON 格式的静态数据，虽然简单但结构清晰。"
        
        # Python 文件分析
        elif filename.endswith('.py'):
            if 'def ' in content or 'class ' in content:
                funcs = re.findall(r'def\s+(\w+)', content)
                classes = re.findall(r'class\s+(\w+)', content)
                analysis["features"].extend([f"{len(funcs)}个函数", f"{len(classes)}个类"])
                analysis["features"].extend(funcs[:3])  # 前3个函数名
                
                if 'hash' in content or 'md5' in content or 'sha' in content:
                    analysis["type"] = "文件校验"
                    analysis["insight"] = "这个工具用哈希算法来识别或校验文件，就像给每个文件做了一个数字指纹。"
                elif 'os.path' in content or 'Path' in content or 'rglob' in content:
                    analysis["type"] = "文件操作"
                    analysis["insight"] = "这个脚本在文件系统中巡游，寻找特定的文件或整理目录结构。"
                elif 'def main' in content or '__main__' in content:
                    analysis["type"] = "独立程序"
                    analysis["insight"] = "这是一个可以独立运行的程序，从 main 入口出发，完成特定任务。"
                elif 'request' in content or 'http' in content or 'api' in content:
                    analysis["type"] = "网络请求"
                    analysis["insight"] = "这个脚本在与外部世界对话，通过 API 获取或发送数据。"
                elif 'class ' in content and 'def __init__' in content:
                    analysis["type"] = "面向对象设计"
                    analysis["insight"] = "这是一个面向对象的实现，用类来封装数据和行为，体现了一种结构化思维。"
                elif 'lambda' in content or 'map(' in content or 'filter(' in content or 'list(' in content:
                    analysis["type"] = "函数式编程"
                    analysis["insight"] = "使用了函数式编程范式，用更高阶的抽象来处理数据流，代码简洁而优雅。"
                else:
                    analysis["type"] = "通用工具"
                    analysis["insight"] = "这是一个实用的小工具，虽然功能简单，但正是这些小小脚本在日常工作中发挥大作用。"
            else:
                analysis["type"] = "纯 Python 脚本"
                analysis["insight"] = "没有函数或类的简单 Python 脚本，可能是配置或一次性任务。"
        
        # Shell/Bat 文件
        elif filename.endswith(('.sh', '.bat', '.cmd', '.ps1')):
            analysis["type"] = "脚本文件"
            analysis["features"].append("shell/batch 脚本")
            analysis["insight"] = "系统脚本，通过命令行直接操作系统，适合自动化日常任务。"
        
        # CSS 文件
        elif filename.endswith('.css'):
            analysis["type"] = "样式表"
            analysis["features"].append("CSS 样式")
            analysis["insight"] = "CSS 控制着页面的外观，同样的结构不同的样式就是两种气质。"
        
        # 其他情况
        else:
            analysis["type"] = "通用脚本"
            analysis["insight"] = "这是一个脚本文件，可能藏着你需要的灵感。"
        
        # 检测特殊模式（对所有文件类型生效）
        if 'try:' in content and 'except' in content:
            analysis["features"].append("含异常处理")
        if 'asyncio' in content or 'async ' in content or 'await ' in content:
            analysis["type"] = "异步编程"
            analysis["insight"] = "使用异步编程模型，可以并发处理多个任务，在等待 I/O 的同时不阻塞其他操作。"
        if 'logging' in content:
            analysis["features"].append("有日志记录")
        if 'TODO' in content or 'FIXME' in content:
            analysis["features"].append("包含开发标记")
        
        # 计算复杂度指标
        analysis["line_count"] = len(lines)
        analysis["features"] = list(set(analysis["features"]))  # 去重
        
        if not analysis["insight"]:
            analysis["insight"] = f"这个脚本有 {len(analysis['features'])} 个特征：{', '.join(analysis['features'][:4])}。"
        
        return analysis
    
    @staticmethod
    def analyze_note(file_path, content, modified=None):
        """分析笔记文件并生成摘要"""
        lines = content.strip().split('\n')
        analysis = {
            "title": "",
            "structure": "",
            "word_count": 0,
            "key_topics": [],
            "insight": ""
        }
        
        # 提取标题
        for line in lines:
            if line.startswith('# '):
                analysis["title"] = line[2:].strip()
                break
            elif line.startswith('## ') and not analysis["title"]:
                analysis["title"] = line[3:].strip()
        
        if not analysis["title"]:
            analysis["title"] = Path(file_path).stem
        
        # 分析结构
        headings = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)
        analysis["structure"] = f"{len(headings)}个章节" if headings else "单段落"
        analysis["key_topics"] = [h for h in headings[:5]]  # 前5个头衔作为关键词
        
        # 估算字数
        analysis["word_count"] = len(content.replace('\n', ' ').replace('#', '').strip())
        
        # 生成解读
        content_lower = content.lower()
        if 'todo' in content_lower or '待办' in content_lower or '计划' in content_lower:
            analysis["type"] = "待办清单"
            analysis["insight"] = f"这是一份行动计划，记录了 {len(headings)} 个任务项。完成比完美更重要。"
        elif 'project' in content_lower or '项目' in content_lower:
            analysis["type"] = "项目文档"
            analysis["insight"] = "这个项目文档记录了某个工作的进展和决策，是知识沉淀的好方法。"
        elif 'skill' in content_lower or '技能' in content_lower:
            analysis["type"] = "技能笔记"
            analysis["insight"] = "技能总结文档，把学到的知识系统化，这是深度学习的好方式。"
        elif 'memory' in content_lower or '记忆' in content_lower:
            analysis["type"] = "记忆笔记"
            analysis["insight"] = "这是一段记忆的数字化保存，未来的自己回看时会很有味道。"
        elif '代码' in content or 'code' in content or 'python' in content:
            analysis["type"] = "技术笔记"
            analysis["insight"] = "技术学习笔记，把代码和问题记录下来，方便以后查阅和复盘。"
        elif '投资' in content or 'stock' in content or 'finance' in content:
            analysis["type"] = "投资笔记"
            analysis["insight"] = "投资记录和分析，理性的思考加上纪律性的执行，是长期盈利的基础。"
        else:
            analysis["type"] = "通用笔记"
            analysis["insight"] = f"这篇 {analysis['word_count']} 字的笔记记录了某个时刻的思考，可能藏着未来的灵感火花。"
        
        return analysis
    
    @staticmethod
    def expand_knowledge(topic, content):
        """基于内容扩展知识点"""
        expansions = {
            "量子计算": [
                "量子纠缠意味着两个粒子无论相距多远都能瞬间影响对方，爱因斯坦称之为'鬼魅般的超距离作用'。",
                "目前的量子计算机还处于早期阶段，但理论证明它们在某些问题上能超越任何经典计算机。",
            ],
            "投资": [
                "巴菲特说'别人贪婪我恐惧，别人恐惧我贪婪'，但真正难的是知行合一。",
                "复利的第七定律：时间是你最好的朋友，耐心是最强的杠杆。",
            ],
            "编程": [
                "干净的代码不是写得漂亮，而是读起来像散文一样流畅。",
                "技术债就像金融债——少量可以帮助快速推进，太多就会拖垮整个团队。",
            ],
            "心理学": [
                "达克效应：能力越低的人越容易高估自己，因为他们根本不知道自己不知道。",
                "人们不是不喜欢改变，而是不喜欢被强迫的改变。",
            ],
            "科学": [
                "科学的精神不在于'我知道答案'，而在于'我还在追问'。",
                "每一个重大发现，最初都来自一个'这不可能'的假设。",
            ],
            "设计": [
                "好的设计让你感觉不到设计的存在，它应该像空气一样自然地融入体验。",
                "极简不是什么都加，而是去掉所有不必要的。",
            ],
            "哲学": [
                "苏格拉底说'未经审视的人生不值得过'，反思本身就是意义的一部分。",
                "存在主义的核心：存在先于本质——我们先来到世界，然后定义自己是谁。",
            ],
            "AI": [
                "AI不是要取代人类，而是要放大人类的创造力和判断力。",
                "深度学习让人工智能从'规则驱动'走向'数据驱动'，但真正的智能还需要常识。",
            ],
            "生物学": [
                "人体细胞每7年几乎全部更新一遍，所以从物质层面看，7年前的你和现在的你不是同一个人。",
                "线粒体DNA只通过母系遗传，这意味着我们可以通过它追溯到'线粒体夏娃'。",
            ],
            "天文学": [
                "你看到的星光可能已经旅行了数百万年——每一次仰望星空都是在回顾宇宙的历史。",
                "宇宙中恒星的数量比地球上所有沙滩上的沙子颗粒还要多。",
            ],
            "数学": [
                "零的发明是人类思想的巅峰之一——它代表'没有'，却又是一个'数'。",
                "斐波那契数列在自然界随处可见：花瓣的排列、贝壳的螺旋、树枝的分叉。",
            ],
            "语言": [
                "语言塑造思维：爱斯基摩人有几十个词形容雪，因为这对他们的生活方式至关重要。",
                "学习一门新语言，就是获得了一种新的思维方式。",
            ],
            "历史": [
                "历史不是循环的，但它押韵——每隔一段时间，人类会犯类似的模式性错误。",
                "文明的进步往往始于一个'如果...会怎样'的问题。",
            ],
            "健康": [
                "最好的药物往往是免费的：睡眠、运动和好心情。",
                "预防胜于治疗——你的生活习惯决定了你未来的健康状况。",
            ],
        }
        
        # 根据 topic 返回扩展知识
        if topic in expansions:
            return random.choice(expansions[topic])
        
        # 如果找不到特定 topic，返回通用知识点
        general_knowledge = [
            "知识就像大海，你学得越多，越发现自己不知道得更多——这正是求知的乐趣所在。",
            "好奇心是学习的原动力，保持对未知的好奇，你会发现世界每天都在给你惊喜。",
            "跨学科思考是最强大的思维工具之一——乔布斯把书法课上学到的美学理念用在了苹果电脑的字体设计上。",
        ]
        return random.choice(general_knowledge)
    
    @staticmethod
    def get_interest_hook(interest):
        """根据兴趣生成个性化钩子"""
        hooks = {
            "AI": "人工智能正在重塑每一个行业，理解它的原理和局限，你就能站在趋势的前沿。",
            "编程": "编程不仅仅是写代码，更是一种解决问题的思维方式。",
            "投资": "投资的核心不是预测市场，而是理解自己。",
            "健康": "身体是最好的资本，投资健康永远回报率最高。",
            "心理学": "理解人心，首先是理解自己。",
            "设计": "好的设计是无声的——它让用户体验自然流畅，毫不费力。",
            "哲学": "哲学不是给出答案，而是学会问更好的问题。",
            "科学": "科学精神的核心：质疑一切，但只相信证据。",
            "机器学习": "机器学习是现代AI的心脏，它让机器从数据中学习，而不是被编程。",
            "创业": "创业是一场马拉松，不是短跑——坚持比速度更重要。",
            "阅读": "阅读是最低成本的成长方式，一本书就是一个陌生人给你的建议。",
            "音乐": "音乐是人类最直接的情感语言，跨越文化和语言的障碍。",
        }
        return hooks.get(interest, f"兴趣 '{interest}' 可能隐藏着独特的发现路径。")


class VenomEvolved:
    """毒液 v5 - 周报自动分发 + 连续猎食 streak 版"""
    
    def __init__(self, workspace_path):
        self.workspace_path = Path(workspace_path)
        self.skills_path = self.workspace_path / ".workbuddy" / "skills" / "venom"
        self.gene_file = self.skills_path / "gene.json"
        self.config_file = self.skills_path / "interests.json"
        self.favorites_file = self.skills_path / "favorites.json"
        self.gene = self.load_gene()
        self.config = self.load_config()
        self.favorites = self.load_favorites_data()
        
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
    
    def load_config(self):
        """加载兴趣配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"interests": ["AI", "编程", "投资", "健康", "心理学", "设计", "哲学", "科学"]}
    
    def save_config(self):
        """保存兴趣配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
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
        interests = self.config.get("interests", [
            "AI", "编程", "投资", "健康", "心理学", "设计", "哲学", "科学"
        ])
        interest = random.choice(interests)
        
        related_files = []
        for file in self.workspace_path.rglob("*"):
            if file.is_file() and interest.lower() in file.name.lower():
                related_files.append(file)
        
        return interest, related_files
    
    def get_random_knowledge(self):
        """获取随机知识 - 升级版本"""
        # 扩展知识库，按主题分类
        knowledge_pool = [
            ("量子计算", "一个量子比特可以同时处于0和1的叠加态，这让量子计算机能并行处理指数级的计算任务。"),
            ("设计原理", "黄金比例 1:1.618 在自然界和艺术中无处不在，从向日葵的种子排列到帕特农神庙的建筑比例。"),
            ("心理学", "锚定效应：人们做决策时会过度依赖第一个接收到的信息，即使这个信息与决策无关。"),
            ("投资", "复利的魔力：年化10%的收益，7年翻倍，20年翻7倍，50年翻117倍。"),
            ("编程", "递归的美：一个函数调用自身，就像两面镜子之间的无限反射，但必须有一个退出条件。"),
            ("生物学", "人类大脑有860亿个神经元，每个神经元平均有7000个突触连接，总连接数比银河系的星星还多。"),
            ("物理学", "熵增定律：宇宙的总熵永远在增加，这就是为什么时间只能向前流逝。"),
            ("哲学", "忒修斯之船：如果一艘船的所有零件都被替换，它还是原来那艘船吗？"),
            ("数学", "欧拉恒等式 e^(iπ) + 1 = 0 被誉为最美的数学公式，它将五个最重要的数学常数联系在一起。"),
            ("神经科学", "大脑的可塑性：即使成年后，大脑仍然可以通过学习和练习重塑神经连接。"),
            ("化学", "水的密度在4°C时最大，这就是为什么冰会浮在水面上——这个反常现象拯救了地球上的生命。"),
            ("天文学", "宇宙的年龄是138亿年，但我们可观测的宇宙直径是930亿光年——因为宇宙本身在膨胀。"),
            ("计算机科学", "图灵机是所有现代计算机的理论基础，它证明了有些问题是无法被任何算法解决的。"),
            ("经济学", "机会成本：做任何选择的真正成本，是你放弃的那个选项的价值。"),
            ("语言学", "萨丕尔-沃尔夫假说：语言决定思维。说不同语言的人，对世界的认知也不同。"),
            ("艺术", "蒙娜丽莎的微笑之所以神秘，是因为达芬奇用了'晕涂法'，让嘴角的轮廓模糊不清。"),
            ("历史", "印刷术的发明让知识民主化，互联网的发明让信息民主化，AI的发明正在让智能民主化。"),
            ("医学", "安慰剂效应：即使药片是假的，只要病人相信它有效，身体就会产生真实的生理反应。"),
            ("社会学", "邓巴数：人类能维持的稳定社交关系上限是150人——这就是为什么微信好友超过150个就开始混乱。"),
            ("进化论", "人类和香蕉共享60%的DNA，和黑猩猩共享98.7%的DNA——生命的统一性令人惊叹。"),
            ("人工智能", "AI 不是魔法，而是统计学和算力的结合——让机器从数据中找规律，而不是硬编码规则。"),
            ("设计模式", "DRY原则：不要重复自己。如果一段逻辑出现了两次，就该考虑把它提取成一个函数。"),
            ("系统思维", "系统思维关注整体而非局部——有时候最优的子组件加起来会产生最差的整体表现。"),
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
        except Exception:
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    lines = f.readlines()[:max_lines]
                    return ''.join(lines)
            except Exception:
                return "[无法读取文件内容]"
    
    def get_full_content(self, file_path, max_chars=2000):
        """获取文件全文（用于分析）"""
        try:
            # 对于 Python/JS 文件，先读取前 8000 字符来做分析
            # 因为关键代码通常在前面
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(8000)
                if len(content) < 8000:
                    full = content
                else:
                    full = content + "\n...（已截断，共" + str(Path(file_path).stat().st_size // 1024) + "KB）"
                return full
        except Exception:
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    content = f.read(8000)
                    if len(content) < 8000:
                        full = content
                    else:
                        full = content + "\n...（已截断，共" + str(Path(file_path).stat().st_size // 1024) + "KB）"
                    return full
            except Exception:
                return ""
    
    def hunt(self):
        """开始猎食 - 智能解读版"""
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
                script = random.choice(scripts)
                full_content = self.get_full_content(script)
                
                if full_content:
                    analysis = IntelligentAnalyzer.analyze_script(script, full_content)
                    preview = self.extract_preview(script, self.gene.code_preview_lines)
                    
                    result["content"] = {
                        "type": "script",
                        "path": str(script),
                        "name": script.name,
                        "extension": script.suffix,
                        "preview": preview,
                        "analysis": analysis,
                        "full_content_length": len(full_content)
                    }
        
        elif tentacle == "笔记":
            notes = self.scan_notes()
            if notes:
                note = random.choice(notes)
                full_content = self.get_full_content(note)
                modified = datetime.fromtimestamp(note.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                
                if full_content:
                    analysis = IntelligentAnalyzer.analyze_note(note, full_content, modified)
                    preview = self.extract_preview(note, self.gene.note_preview_lines)
                    
                    result["content"] = {
                        "type": "note",
                        "path": str(note),
                        "name": note.name,
                        "modified": modified,
                        "preview": preview,
                        "analysis": analysis,
                        "full_content_length": len(full_content)
                    }
        
        elif tentacle == "兴趣":
            interest, related_files = self.get_interest_content()
            hook = IntelligentAnalyzer.get_interest_hook(interest)
            
            result["content"] = {
                "type": "interest",
                "interest": interest,
                "hook": hook,
                "related_count": len(related_files),
                "files": [str(f) for f in related_files[:3]]
            }
        
        elif tentacle == "知识":
            topic, content = self.get_random_knowledge()
            expansion = IntelligentAnalyzer.expand_knowledge(topic, content)
            
            result["content"] = {
                "type": "knowledge",
                "topic": topic,
                "content": content,
                "expansion": expansion
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
                    "files": [(f.name, f.stat().st_size if f.is_file() else 0) for f in files],
                    "total_items": len(list(directory.iterdir()))
                }
        
        return result
    
    def format_result(self, result):
        """格式化猎食结果 - 新版精美输出"""
        tentacle = result["tentacle"]
        content = result["content"]
        
        output = f"\n🦑 毒液 v5 · 智能解读\n"
        output += f"{'─'*60}\n"
        output += f"🎣 触手来源：{tentacle}（权重: {self.gene.tentacle_weights[tentacle]:.2f}）\n"
        output += f"📅 猎食时间：{datetime.fromisoformat(result['timestamp']).strftime('%Y-%m-%d %H:%M')}\n"
        output += f"{'─'*60}\n\n"
        
        if content is None:
            output += "这次猎物溜走了，换个方向试试？\n"
            return output
        
        if content["type"] == "script":
            analysis = content["analysis"]
            output += f"🐍 工作区脚本\n"
            output += f"📄 猎物：{content['name']}\n"
            output += f"🔧 类型：{analysis['type']}\n"
            output += f"📊 特征：{', '.join(analysis['features']) if analysis['features'] else '无特别标注'}\n"
            if analysis["line_count"] > 0:
                output += f"📏 代码量：{analysis['line_count']} 行\n"
            output += f"\n💡 解读：{analysis['insight']}\n"
            
            if content["full_content_length"] < 2000:  # 如果不大，显示全部预览
                output += f"\n📝 代码预览：\n"
                output += f"```python\n{content['preview']}\n```\n"
            else:
                output += f"\n📝 代码预览（共 {content['full_content_length']} 字符）：\n"
                output += f"```python\n{content['preview']}\n```\n"
            
            output += f"\n📂 位置：{content['path']}\n"
        
        elif content["type"] == "note":
            analysis = content["analysis"]
            output += f"📝 最近笔记\n"
            output += f"📖 标题：{analysis['title']}\n"
            output += f"🏷️ 类型：{analysis['type']}\n"
            output += f"📐 结构：{analysis['structure']}\n"
            if analysis["key_topics"]:
                output += f"🔑 主题：{', '.join(analysis['key_topics'])}\n"
            output += f"📏 字数：{analysis['word_count']} 字\n"
            output += f"🕒 修改：{content['modified']}\n"
            output += f"\n💡 解读：{analysis['insight']}\n"
            
            output += f"\n📝 内容预览（共 {content['full_content_length']} 字符）：\n"
            output += f"```\n{content['preview']}\n```\n"
            output += f"\n📂 位置：{content['path']}\n"
        
        elif content["type"] == "interest":
            output += f"🎯 个人兴趣\n"
            output += f"💭 随机兴趣：{content['interest']}\n"
            output += f"📎 相关文件：{content['related_count']} 个\n"
            if content.get('hook'):
                output += f"\n💡 兴趣导读：{content['hook']}\n"
            
            if content.get('files'):
                output += f"\n📁 相关项目：\n"
                for f in content['files'][:3]:
                    output += f"   • {Path(f).name}\n"
        
        elif content["type"] == "knowledge":
            output += f"📚 随机知识\n"
            output += f"🏷️ 领域：{content['topic']}\n"
            output += f"\n{content['content']}\n"
            
            if content.get('expansion'):
                output += f"\n💡 延伸思考：{content['expansion']}\n"
        
        elif content["type"] == "moc":
            output += f"🗂️ 目录探索\n"
            output += f"📂 目录：{content['name']}/\n"
            output += f"📊 文件数：{content['total_items']} 个\n"
            output += f"\n📋 内容预览：\n"
            
            for name, size in content['files']:
                if size > 0:
                    size_str = f"{size:,} bytes" if size > 1024 else f"{size} bytes"
                    output += f"   📄 {name} ({size_str})\n"
                else:
                    output += f"   📁 {name}/\n"
            
            output += f"\n💡 解读：目录是知识的地图，探索结构可以发现隐藏的宝藏。\n"
            output += f"🗂️ 目录探索\n"
            output += f"📂 目录：{content['name']}/\n"
            output += f"📊 文件数：{content['total_items']} 个\n"
            output += f"\n📋 内容预览：\n"
            
            for name, size in content['files']:
                if size > 0:
                    size_str = f"{size:,} bytes" if size > 1024 else f"{size} bytes"
                    output += f"   📄 {name} ({size_str})\n"
                else:
                    output += f"   📁 {name}/\n"
            
            output += f"\n💡 解读：目录是知识的地图，探索结构可以发现隐藏的宝藏。\n"
        
        # 显示进化状态（精简版）
        status = self.gene.get_status()
        output += f"\n{'─'*60}\n"
        output += f"🧬 进化状态 | 总猎食：{status['total_hunts']} 次 | 平均适应度：{status['avg_fitness']:.2f}\n"
        output += f"{'='*60}\n"
        
        return output
    
    def give_feedback(self, score):
        """用户反馈 - 驱动进化"""
        last_hunt = self.gene.fitness_history[-1] if self.gene.fitness_history else None
        if last_hunt:
            self.gene.update_fitness(last_hunt["tentacle"], score)
            self.save_gene()
            return f"收到反馈！适应度 {score:.2f}，毒液正在进化..."
        return "没有找到最近的猎食记录。"
    
    # ========== 杂交猎食 ==========
    
    def hunt_from_tentacle(self, tentacle):
        """从指定触手猎食（私有方法，供 hunt_hybrid 复用 hunt 逻辑）"""
        tentacle = tentacle.strip()
        result = {
            "tentacle": tentacle,
            "timestamp": datetime.now().isoformat(),
            "content": None
        }
        
        if tentacle == "脚本":
            scripts = self.scan_scripts()
            if scripts:
                script = random.choice(scripts)
                full_content = self.get_full_content(script)
                if full_content:
                    analysis = IntelligentAnalyzer.analyze_script(script, full_content)
                    preview = self.extract_preview(script, self.gene.code_preview_lines)
                    result["content"] = {
                        "type": "script",
                        "path": str(script),
                        "name": script.name,
                        "extension": script.suffix,
                        "preview": preview,
                        "analysis": analysis,
                        "full_content_length": len(full_content)
                    }
        
        elif tentacle == "笔记":
            notes = self.scan_notes()
            if notes:
                note = random.choice(notes)
                full_content = self.get_full_content(note)
                modified = datetime.fromtimestamp(note.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                if full_content:
                    analysis = IntelligentAnalyzer.analyze_note(note, full_content, modified)
                    preview = self.extract_preview(note, self.gene.note_preview_lines)
                    result["content"] = {
                        "type": "note",
                        "path": str(note),
                        "name": note.name,
                        "modified": modified,
                        "preview": preview,
                        "analysis": analysis,
                        "full_content_length": len(full_content)
                    }
        
        elif tentacle == "兴趣":
            interest, related_files = self.get_interest_content()
            hook = IntelligentAnalyzer.get_interest_hook(interest)
            result["content"] = {
                "type": "interest",
                "interest": interest,
                "hook": hook,
                "related_count": len(related_files),
                "files": [str(f) for f in related_files[:3]]
            }
        
        elif tentacle == "知识":
            topic, content = self.get_random_knowledge()
            expansion = IntelligentAnalyzer.expand_knowledge(topic, content)
            result["content"] = {
                "type": "knowledge",
                "topic": topic,
                "content": content,
                "expansion": expansion
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
                    "files": [(f.name, f.stat().st_size if f.is_file() else 0) for f in files],
                    "total_items": len(list(directory.iterdir()))
                }
        
        return result
    
    def hunt_hybrid(self, hybrid_count=2):
        """杂交猎食 - 从多条触手同时猎食并产生跨域连接洞察"""
        tentacles = self.gene.select_multiple_tentacles(n=hybrid_count)
        
        output_parts = []
        for t in tentacles:
            prey = self.hunt_from_tentacle(t)
            output_parts.append(prey)
        
        # 生成跨域连接洞察
        connection = self._generate_cross_domain_connection(output_parts)
        
        result = {
            "mode": "hybrid",
            "tentacles": tentacles,
            "preys": output_parts,
            "connection": connection,
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    def _generate_cross_domain_connection(self, preys):
        """生成跨域连接洞察"""
        types = [p.get("tentacle", "") for p in preys]
        contents = [p.get("content", {}) for p in preys]
        type_set = tuple(sorted(set(types)))
        
        # 模板1: 脚本+知识
        if "脚本" in type_set and "知识" in type_set:
            script_idx = types.index("脚本")
            knowledge_idx = types.index("知识")
            script_name = contents[script_idx].get("name", "脚本")
            analysis = contents[script_idx].get("analysis", {})
            script_func = analysis.get("insight", "")[:50] or "工具函数"
            knowledge_topic = contents[knowledge_idx].get("topic", "")
            connection = (
                f"这份代码的「{script_name}」功能和「{knowledge_topic}」有着相似的底层逻辑：\n"
                f"  代码用结构化方式处理问题，而 {knowledge_topic} 揭示的是自然界/宇宙的结构规律。\n"
                f"  二者都是试图在混沌中寻找秩序。"
            )
            return connection
        
        # 模板2: 知识+兴趣
        if "知识" in type_set and "兴趣" in type_set:
            knowledge_idx = types.index("知识")
            interest_idx = types.index("兴趣")
            knowledge_topic = contents[knowledge_idx].get("topic", "")
            interest = contents[interest_idx].get("interest", "")
            expansion = IntelligentAnalyzer.expand_knowledge(knowledge_topic, "")
            connection = (
                f"{knowledge_topic} 的知识与你的兴趣「{interest}」产生了奇妙的化学反应。\n"
                f"  {expansion}"
            )
            return connection
        
        # 模板3: 脚本+笔记
        if "脚本" in type_set and "笔记" in type_set:
            script_idx = types.index("脚本")
            note_idx = types.index("笔记")
            script_name = contents[script_idx].get("name", "脚本")
            analysis = contents[script_idx].get("analysis", {})
            script_type = analysis.get("type", "脚本")
            note_analysis = contents[note_idx].get("analysis", {})
            note_title = note_analysis.get("title", "笔记")
            note_topic = ", ".join(note_analysis.get("key_topics", ["内容"]))[:40] or "内容"
            connection = (
                f"你在代码里用了 {script_type} 这样的设计模式，而这篇笔记《{note_title}》提到了类似的 {note_topic}——\n"
                f"  代码不仅是实现，也是思维方式的外化。你的代码风格反映了你记录知识的方式。"
            )
            return connection
        
        # 模板4: 笔记+兴趣
        if "笔记" in type_set and "兴趣" in type_set:
            note_idx = types.index("笔记")
            interest_idx = types.index("兴趣")
            note_analysis = contents[note_idx].get("analysis", {})
            note_title = note_analysis.get("title", "笔记")
            note_type = note_analysis.get("type", "笔记")
            interest = contents[interest_idx].get("interest", "")
            connection = (
                f"你的《{note_title}》（{note_type}）和当前兴趣「{interest}」形成呼应。\n"
                f"  知识笔记是对过去的沉淀，兴趣是对未来的探索——二者交汇点就是你的成长轨迹。"
            )
            return connection
        
        # 模板5: 脚本+兴趣
        if "脚本" in type_set and "兴趣" in type_set:
            script_idx = types.index("脚本")
            interest_idx = types.index("兴趣")
            script_name = contents[script_idx].get("name", "脚本")
            analysis = contents[script_idx].get("analysis", {})
            script_insight = analysis.get("insight", "")[:60]
            interest = contents[interest_idx].get("interest", "")
            connection = (
                f"「{script_name}」这件工具和你关注的「{interest}」看似无关，\n"
                f"  但实际上它体现了你解决问题的一种方式：{script_insight}"
            )
            return connection
        
        # 模板6: 脚本+MOC
        if "脚本" in type_set and "MOC" in type_set:
            script_idx = types.index("脚本")
            moc_idx = types.index("MOC")
            script_name = contents[script_idx].get("name", "脚本")
            moc_name = contents[moc_idx].get("name", "目录")
            connection = (
                f"「{script_name}」放在「{moc_name}」目录下是个有趣的选择——\n"
                f"  代码是知识的执行层，目录是知识的索引层，它们在同一个空间交汇。"
            )
            return connection
        
        # 模板7: 笔记+MOC
        if "笔记" in type_set and "MOC" in type_set:
            note_idx = types.index("笔记")
            moc_idx = types.index("MOC")
            note_analysis = contents[note_idx].get("analysis", {})
            note_title = note_analysis.get("title", "笔记")
            moc_name = contents[moc_idx].get("name", "目录")
            connection = (
                f"《{note_title}》这篇笔记与「{moc_name}」目录形成了内容与结构的互补——\n"
                f"  目录帮你组织知识的位置，笔记帮你记录知识的深度。"
            )
            return connection
        
        # 模板8: 兴趣+MOC
        if "兴趣" in type_set and "MOC" in type_set:
            interest_idx = types.index("兴趣")
            moc_idx = types.index("MOC")
            interest = contents[interest_idx].get("interest", "")
            moc_name = contents[moc_idx].get("name", "目录")
            connection = (
                f"你对「{interest}」的兴趣，和「{moc_name}」目录的结构——\n"
                f"  一个是内容的主题，一个是知识的地形。找到它们的交集，就是你的专属知识地图。"
            )
            return connection
        
        # 模板9: 知识+MOC
        if "知识" in type_set and "MOC" in type_set:
            knowledge_idx = types.index("知识")
            moc_idx = types.index("MOC")
            knowledge_topic = contents[knowledge_idx].get("topic", "")
            moc_name = contents[moc_idx].get("name", "目录")
            connection = (
                f"「{knowledge_topic}」这样的跨学科知识与「{moc_name}」目录的组织方式异曲同工——\n"
                f"  两者都在建立关联：知识跨越学科边界，目录跨越文件边界。"
            )
            return connection
        
        # 模板10: 三触手联动
        if len(tentacles) >= 3:
            connected = ", ".join(types)
            preview_words = []
            for c in contents:
                ct = c.get("type", "")
                if ct == "knowledge" and c.get("topic"):
                    preview_words.append(c["topic"])
                elif ct == "script" and c.get("name"):
                    preview_words.append(c["name"])
                elif ct == "note" and c.get("analysis", {}).get("title"):
                    preview_words.append(c["analysis"]["title"])
                elif ct == "interest" and c.get("interest"):
                    preview_words.append(c["interest"])
                elif ct == "moc" and c.get("name"):
                    preview_words.append(c["name"])
            
            words_str = " ↔ ".join(preview_words[:3]) if preview_words else connected
            connection = (
                f"三条触手 {connected} 同时激活，产生了罕见的好奇共振！\n"
                f"  捕到的信息片段：{words_str}\n"
                f"  当多个维度的知识同时浮现时，它们之间会产生隐形的连线。"
            )
            return connection
        
        # 默认模板：两触手通用
        if len(types) >= 2:
            t1, t2 = types[0], types[1]
            p1 = contents[0].get("name", contents[0].get("topic", "")) or contents[0].get("interest", "") or "知识点"
            p2 = contents[1].get("name", contents[1].get("topic", "")) or contents[1].get("interest", "") or "知识点"
            connection = (
                f"{t1} 和 {t2} 同时出击，捕获了「{p1}」和「{p2}」。\n"
                f"  看似独立的两个发现，可能藏着跨域连接的种子。"
            )
            return connection
        
        return "触手联动完成，但未检测到明显的关联。"
    
    def format_hybrid_result(self, result):
        """格式化杂交猎食结果"""
        output = f"\n🦑 毒液 v5 · 杂交猎食\n"
        output += f"{'─'*60}\n"
        output += f"🔗 联动触手：{' + '.join(result['tentacles'])}\n"
        output += f"📅 杂交时间：{datetime.fromisoformat(result['timestamp']).strftime('%Y-%m-%d %H:%M')}\n"
        output += f"{'─'*60}\n\n"
        
        for i, prey in enumerate(result["preys"], 1):
            tentacle = prey["tentacle"]
            content = prey["content"]
            output += f"── 触手{len(result['tentacles'])}中的第{i}条 ──\n"
            
            if content is None:
                output += f"[{tentacle}] 猎物溜走了\n\n"
                continue
            
            if content["type"] == "script":
                analysis = content["analysis"]
                output += f"   🐍 {tentacle} | {content['name']} [{analysis.get('type','')}]  "
                if analysis.get("insight"):
                    output += f"- {analysis['insight'][:60]}...\n"
                else:
                    output += "\n"
            
            elif content["type"] == "note":
                analysis = content["analysis"]
                output += f"   📝 {tentacle} | 《{analysis.get('title','未命名')}》 [{analysis.get('type','')}]  "
                if analysis.get("insight"):
                    output += f"- {analysis['insight'][:60]}...\n"
                else:
                    output += "\n"
            
            elif content["type"] == "interest":
                output += f"   🎯 {tentacle} | 兴趣: {content['interest']} | 相关 {content['related_count']} 文件\n"
                if content.get("hook"):
                    output += f"      💬 {content['hook'][:80]}\n"
            
            elif content["type"] == "knowledge":
                output += f"   📚 {tentacle} | {content['topic']}\n"
                output += f"      {content['content'][:100]}\n"
            
            elif content["type"] == "moc":
                output += f"   🗂️ {tentacle} | 目录: {content['name']} ({content['total_items']} 项)\n"
            
            output += "\n"
        
        # 跨域连接洞察
        output += f"{'═'*60}\n"
        output += f"🧠 跨域连接洞察\n"
        output += f"{'═'*60}\n"
        output += f"  {result['connection']}\n"
        output += f"{'═'*60}\n"
        
        return output
    
    # ========== 周回顾 ==========
    
    def weekly_review(self, days=7):
        """本周回顾 - 统计猎食数据并生成洞察"""
        now = datetime.now()
        cutoff = now.timestamp() - days * 86400
        
        history = self.gene.fitness_history
        
        # 筛选近 N 天的记录
        recent = []
        for rec in history:
            try:
                ts = datetime.fromisoformat(rec["timestamp"]).timestamp()
                if ts >= cutoff:
                    recent.append(rec)
            except (ValueError, KeyError):
                continue
        
        # 统计各触手次数和平均满意度
        tentacle_counts = {}
        tentacle_scores = {}
        for rec in recent:
            t = rec["tentacle"]
            s = rec["score"]
            tentacle_counts[t] = tentacle_counts.get(t, 0) + 1
            if t not in tentacle_scores:
                tentacle_scores[t] = []
            tentacle_scores[t].append(s)
        
        avg_scores = {t: sum(scores)/len(scores) for t, scores in tentacle_scores.items()}
        
        # 生成报告
        output = f"\n🦑 毒液 v5 · 每周回顾（过去 {days} 天）\n"
        output += f"{'═'*60}\n"
        output += f"📊 总猎食次数：{len(recent)} 次\n"
        
        if tentacle_counts:
            output += f"\n🎯 触手活跃统计\n"
            for t, count in sorted(tentacle_counts.items(), key=lambda x: -x[1]):
                avg = avg_scores.get(t, 0)
                weight = self.gene.tentacle_weights.get(t, 1.0)
                output += f"   {t}: {count} 次 (均分 {avg:.2f}, 权重 {weight:.2f})\n"
            
            # 最活跃触手
            top_tentacle = max(tentacle_counts, key=tentacle_counts.get)
            output += f"\n🏆 本周主力：{top_tentacle}（{tentacle_counts[top_tentacle]} 次猎食）\n"
        
        # 收藏夹热门
        favs = self.favorites.get("favorites", [])
        if favs:
            output += f"\n⭐ 收藏热点\n"
            for i, f in enumerate(favs[-5:], 1):
                output += f"   {i}. [{f['tentacle']}] {f['name']}"
                if f.get("tag"):
                    output += f" ({f['tag']})"
                output += "\n"
        else:
            output += f"\n⭐ 收藏夹暂无内容，多猎食几次就能攒起来了。\n"
        
        # 知识聚类
        output += self._generate_knowledge_cluster(favs)
        
        # 进化建议
        total_hunts = len(self.gene.fitness_history)
        if total_hunts > 0 and total_hunts % 20 == 0:
            output += f"\n🔄 基因即将变异！（累计 {total_hunts} 次，靠近 20 的倍数）\n"
        elif total_hunts > 0:
            next_mutate = ((total_hunts // 20) + 1) * 20
            output += f"\n🧬 累计猎食 {total_hunts} 次，距下次基因变异还需 {next_mutate - total_hunts} 次。\n"
        
        output += f"\n{'═'*60}\n"
        return output
    
    def _generate_knowledge_cluster(self, favs):
        """基于收藏夹生成知识聚类洞察"""
        if not favs:
            return ""
        
        # 按类型分组
        by_type = {}
        for f in favs:
            ft = f.get("type", "other")
            if ft not in by_type:
                by_type[ft] = []
            by_type[ft].append(f)
        
        type_labels = {
            "script": "脚本工具",
            "note": "笔记文档",
            "interest": "兴趣内容",
            "knowledge": "知识片段",
            "moc": "目录结构"
        }
        
        if len(by_type) <= 1:
            dominant = list(by_type.keys())[0]
            label = type_labels.get(dominant, dominant)
            return f"\n🧩 知识聚类：你的收藏集中在「{label}」领域，说明你对这类内容有很强的偏好吗？\n"
        
        # 多种类型 -> 跨域学习者
        top_types = sorted(by_type.items(), key=lambda x: -len(x[1]))[:3]
        type_names = [type_labels.get(t, t) for t, _ in top_types]
        
        connection = ""
        if "脚本工具" in type_names and "笔记文档" in type_names:
            connection = "你用代码解决具体问题，用笔记沉淀抽象思考——这正是知行合一的模式。"
        elif "知识片段" in type_names and "兴趣内容" in type_names:
            connection = "广泛的知识摄入加上兴趣驱动的探索，构成了你的学习飞轮。"
        elif "脚本工具" in type_names and "目录结构" in type_names:
            connection = "你重视工具链和知识结构的配合，这是系统性思维的体现。"
        else:
            connection = f"你的知识结构分布在{', '.join(type_names)}等多个维度，呈现出典型的T型人才特征。"
        
        return f"\n🧩 知识聚类\n" \
               f"   收藏覆盖 {len(by_type)} 类内容：{', '.join(type_names)}\n" \
               f"   💡 {connection}\n"
    
    def save_gene(self):
        """保存基因"""
        data = {
            "weights": self.gene.tentacle_weights,
            "prefer_recent": self.gene.prefer_recent,
            "fitness_history": self.gene.fitness_history[-50:]
        }
        with open(self.gene_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # ========== Streak 系统 (v5) ==========
    
    def load_streak_data(self):
        """加载 Streak 数据"""
        streak_file = self.skills_path / "streak.json"
        if streak_file.exists():
            try:
                with open(streak_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"last_hunt_date": "", "streak_days": 0, "best_streak": 0, "total_hunt_days": 0}
    
    def save_streak_data(self, data):
        """保存 Streak 数据"""
        streak_file = self.skills_path / "streak.json"
        with open(streak_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def update_streak(self):
        """更新连续猎食 Streak - 每次猎食时调用"""
        streak_data = self.load_streak_data()
        today = datetime.now().strftime("%Y-%m-%d")
        last_date = streak_data.get("last_hunt_date", "")
        
        # 今天是第一次
        if not last_date:
            streak_data["streak_days"] = 1
            streak_data["last_hunt_date"] = today
            streak_data["total_hunt_days"] = 1
        # 昨天（连续+1）
        elif last_date == (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"):
            streak_data["streak_days"] += 1
            streak_data["last_hunt_date"] = today
        # 更早（断了重置为1，但在同一天不算）
        elif last_date != today:
            streak_data["streak_days"] = 1
            streak_data["last_hunt_date"] = today
        
        # 更新最佳连续记录
        if streak_data["streak_days"] > streak_data.get("best_streak", 0):
            streak_data["best_streak"] = streak_data["streak_days"]
        
        self.save_streak_data(streak_data)
        
        # 返回 streak 信息
        streak = streak_data["streak_days"]
        best = streak_data["best_streak"]
        msg = f"\n🔥 连续猎食 Streak: {streak} 天！（历史最佳：{best} 天）\n"
        
        if streak >= 7:
            msg += "   🏅 你是一个持之以恒的猎人！连续 7 天，毒液已经深深融入了你的生活节奏。"
        elif streak >= 3:
            msg += "   ⛺ 连续 3 天了，看来你已经养成了知识探索的习惯。"
        elif streak >= 2:
            msg += "   🌱 开始了连续猎食之旅，继续保持！"
        else:
            msg += "   🌟 今天开始了新的猎食之旅，明天见？"
        
        return msg
    
    # ========== 周报 Markdown 导出 (v5) ==========
    
    def generate_weekly_markdown(self, days=7):
        """生成周报 Markdown 内容，可直接导出为文件"""
        review_text = self.weekly_review(days=days)
        
        # 提取数据
        now = datetime.now()
        week_start = (now - timedelta(days=days)).strftime("%Y-%m-%d")
        week_end = now.strftime("%Y-%m-%d")
        
        favs = self.favorites.get("favorites", [])
        favs_recent = [f for f in favs if f.get("timestamp", "").startswith(week_start)]
        
        md = f"""# 🦑 毒液周报 - 第 {now.isocalendar()[1]} 周 ({week_start} ~ {week_end})

## 📊 猎食概况

- **总猎食次数**：{len(self.gene.fitness_history)} 次（累计）
- **本周猎食**：根据 fitness_history 统计
- **收藏夹**：{len(favs)} 条
- **连续 Streak**：{self.load_streak_data().get('streak_days', 0)} 天

## ⭐ 本周收藏精华
"""
        if favs_recent:
            for i, f in enumerate(favs_recent, 1):
                tag = f" ({f['tag']})" if f.get("tag") else ""
                md += f"- {i}. [{f['tentacle']}] {f['name']}{tag} → {f.get('preview_first_line', '')[:50]}\n"
        else:
            md += "- 本周暂无新收藏\n"
        
        md += f"""
## 🧬 进化状态

```
{review_text}
```

---

*报告由 🦑 毒液 v5 自动生成于 {now.strftime('%Y-%m-%d %H:%M')}*"
        """
        return md
    
    def save_weekly_report(self, days=7):
        """生成周报并保存到文件"""
        md = self.generate_weekly_markdown(days=days)
        now = datetime.now()
        report_path = self.skills_path / f"weekly_report_{now.strftime('%Y%m%d')}.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(md)
        
        return str(report_path), md
    
    # ========== 成就系统 (v5) ==========
    
    def check_achievements(self):
        """检查解锁成就"""
        streak_data = self.load_streak_data()
        total = len(self.gene.fitness_history)
        favs = self.favorites.get("favorites", [])
        
        achievements_unlocked = []
        achievements_locked = []
        
        # 成就定义
        all_achievements = [
            ("初次狩猎", "完成第一次猎食", total >= 1, "🌱", total, 1),
            ("十次猎食", "累计猎食 10 次", total >= 10, "🦑", total, 10),
            ("五十次猎食", "累计猎食 50 次", total >= 50, "🐉", total, 50),
            ("百次猎食", "累计猎食 100 次", total >= 100, "👑", total, 100),
            ("三日 streak", "连续猎食 3 天", streak_data.get("streak_days", 0) >= 3, "🔥", streak_data.get("streak_days", 0), 3),
            ("七日 streak", "连续猎食 7 天", streak_data.get("streak_days", 0) >= 7, "💎", streak_data.get("streak_days", 0), 7),
            ("三十日 streak", "连续猎食 30 天", streak_data.get("streak_days", 0) >= 30, "🏆", streak_data.get("streak_days", 0), 30),
            ("收藏家", "收藏 1 条猎物", len(favs) >= 1, "⭐", len(favs), 1),
            ("收藏夹", "收藏 5 条猎物", len(favs) >= 5, "📚", len(favs), 5),
            ("博览群书", "收藏 10 条猎物", len(favs) >= 10, "📖", len(favs), 10),
            ("进化先驱", "基因变异 1 次（累计猎食 20 次）", total >= 20, "🧬", total, 20),
        ]
        
        for name, desc, unlocked, emoji, current_progress, threshold in all_achievements:
            if unlocked:
                achievements_unlocked.append({"name": name, "desc": desc, "emoji": emoji})
            else:
                achievements_locked.append({"name": name, "desc": desc, "emoji": emoji, "progress": min(current_progress, threshold), "threshold": threshold})
        
        result = f"\n🦑 毒液 v5 · 成就系统\n{'═'*50}\n"
        
        if achievements_unlocked:
            result += f"\n✅ 已解锁 ({len(achievements_unlocked)} 个)\n"
            for a in achievements_unlocked:
                result += f"   {a['emoji']} {a['name']}: {a['desc']}\n"
        
        # 显示最近的未解锁成就
        locked_shown = achievements_locked[:5]
        if locked_shown:
            result += f"\n🔒 即将解锁\n"
            for a in locked_shown:
                bar_len = min(a['progress'] // max(a['threshold'] // 10, 1), 10)
                bar = '█' * bar_len + '░' * (10 - bar_len)
                result += f"   {a['emoji']} {a['name']}: [{bar}] {a['progress']}/{a['threshold']}\n"
        
        return result


    # ========== 收藏系统 ==========
    
    def load_favorites_data(self):
        """加载收藏数据"""
        if self.favorites_file.exists():
            with open(self.favorites_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"favorites": []}
    
    def save_favorites(self):
        """保存收藏数据"""
        with open(self.favorites_file, 'w', encoding='utf-8') as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=2)
    
    def favorite(self, prey_data, tag=""):
        """添加收藏"""
        content = prey_data.get("content")
        if content is None:
            return False
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "tentacle": prey_data.get("tentacle", "未知"),
            "path": content.get("path", ""),
            "name": content.get("name", content.get("topic", content.get("interest", "未知"))),
            "type": content.get("type", "unknown"),
            "preview_first_line": "",
            "tag": tag or ""
        }
        
        # 提取预览首行
        preview = content.get("preview", "")
        if preview:
            first_line = preview.split('\n')[0].strip()
            if first_line.startswith('# '):
                first_line = first_line[2:]
            entry["preview_first_line"] = first_line[:80]
        else:
            # 根据不同类型取关键信息
            ct = content.get("type")
            if ct == "knowledge" and content.get("content"):
                entry["preview_first_line"] = content["content"][:80]
            elif ct == "interest" and content.get("interest"):
                entry["preview_first_line"] = content["interest"]
            elif ct == "moc" and content.get("name"):
                entry["preview_first_line"] = content["name"]
            else:
                entry["preview_first_line"] = str(entry["name"])[:80]
        
        self.favorites["favorites"].append(entry)
        self.save_favorites()
        return True
    
    def list_favorites(self):
        """列出所有收藏，按日期分组"""
        favs = self.favorites.get("favorites", [])
        if not favs:
            return "收藏夹空空如也，快去收藏你喜欢的猎物吧！"
        
        # 按日期分组
        groups = {}
        for f in reversed(favs):
            ts = f.get("timestamp", "")
            date_key = ts[:10] if ts else "未知日期"
            if date_key not in groups:
                groups[date_key] = []
            groups[date_key].append(f)
        
        output = f"\n🦑 毒液 v5 · 收藏夹（共 {len(favs)} 条）\n"
        output += f"{'═'*60}\n"
        
        for date_key, items in groups.items():
            output += f"\n📅 {date_key}\n"
            for i, f in enumerate(items, 1):
                icon = {"script": "🐍", "note": "📝", "interest": "🎯", "knowledge": "📚", "moc": "🗂️"}.get(f["type"], "📌")
                tag_str = f" [{f['tag']}]" if f.get("tag") else ""
                preview = f.get("preview_first_line", "")
                if preview and len(preview) > 40:
                    preview = preview[:40] + "…"
                output += f"   {icon} {i}. {f['name']}{tag_str}\n"
                if preview:
                    output += f"      💬 {preview}\n"
                output += f"      🏷️ 触手: {f['tentacle']}\n"
        
        output += f"\n{'═'*60}\n"
        return output
    
    def remove_favorite(self, path):
        """移除收藏"""
        originals = self.favorites.get("favorites", [])
        new_favs = [f for f in originals if f.get("path") != path]
        if len(new_favs) == len(originals):
            return False, "未找到匹配的收藏"
        self.favorites["favorites"] = new_favs
        self.save_favorites()
        return True, "已移除收藏"


def main():
    """主函数 - 交互式菜单"""
    workspace = r"D:\整理_个人\workspace\practice"
    venom = VenomEvolved(workspace)
    
    print("\n=== 猎食菜单 ===\n")
    try:
        choice = input("请选择模式：\n"
                       "  1. 单次猎食（默认）\n"
                       "  2. 杂交猎食（2-3条触手联动）\n"
                       "  3. 查看收藏夹\n"
                       "  4. 添加收藏\n"
                       "  5. 本周回顾\n"
                       "  6. 成就一览\n"
                       "  7. 导出周报 Markdown\n"
                       "  8. 退出\n"
                       "输入选项编号（1-7），直接回车默认模式1: ").strip()
    except (EOFError, KeyboardInterrupt):
        choice = "1"
    
    if not choice:
        choice = "1"
    
    if choice == "1":
        result = venom.hunt()
        print(venom.format_result(result))
        print(venom.update_streak())
        print(venom.check_achievements())
        venom.save_gene()
    
    elif choice == "2":
        hybrid_count = 2
        result = venom.hunt_hybrid(hybrid_count=hybrid_count)
        print(venom.format_hybrid_result(result))
        print(venom.update_streak())
        venom.save_gene()
    
    elif choice == "3":
        print(venom.list_favorites())
    
    elif choice == "4":
        print("最近3次猎食记录：\n")
        history = venom.gene.fitness_history[-3:]
        if not history:
            print("  没有猎食记录可收藏！先进行一次猎食吧。")
        else:
            for i, rec in enumerate(reversed(history), 1):
                ts = rec.get("timestamp", "")[:10]
                score = rec.get("score", 0)
                print(f"  {i}. [{rec['tentacle']}] {ts} (评分: {score:.2f})")
            try:
                idx_input = input("\n选择编号收藏（输入序号，或取消输入0）: ").strip()
                idx = int(idx_input) if idx_input else 0
                if 1 <= idx <= len(history):
                    # 执行一次对应触手的猎食来收集详情
                    tentacle = history[-idx]["tentacle"]
                    prey = venom.hunt_from_tentacle(tentacle)
                    try:
                        tag = input("可选标签（直接回车跳过）: ").strip()
                    except:
                        tag = ""
                    if venom.favorite(prey, tag=tag):
                        print(f"  ✅ 已收藏：{prey['content'].get('name', prey['content'].get('topic', '未知'))}")
                    else:
                        print("  ❌ 收藏失败")
            except ValueError:
                print("  无效输入")
            except EOFError:
                print("  取消收藏")
    
    elif choice == "5":
        try:
            days_input = input("回顾天数（默认7，输入正整数）: ").strip()
            days = int(days_input) if days_input else 7
            days = max(1, min(90, days))
        except ValueError:
            days = 7
        print(venom.weekly_review(days=days))
    
    elif choice == "6":
        print(venom.check_achievements())
    
    elif choice == "7":
        try:
            days_input = input("周报天数（默认7）: ").strip()
            days = int(days_input) if days_input else 7
        except ValueError:
            days = 7
        report_path, md = venom.save_weekly_report(days=days)
        print(f"\n📄 周报已导出到: {report_path}\n")
        print(md[:1500] + ("\n...\n" if len(md) > 1500 else ""))
    
    elif choice == "8":
        print("再见！🦑")
    
    else:
        print("再见！🦑")
    
    print()


if __name__ == "__main__":
    main()
