# 🦑 毒液 - 知识猎食者

[![Version](https://img.shields.io/badge/version-2.1-blue.svg)](https://github.com/workbuddy/venom)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

**一句话**：「我也不知道想看什么，给我找点有意思的。」

## 这是什么？

毒液是一个打破信息茧房的知识探索工具。它像毒液的5条触手一样，从多个知识源随机抽取内容，帮助你发现意想不到的知识关联。

## ✨ 特性

- 🦑 **5条触手**：从脚本、笔记、兴趣、知识、MOC 五个维度猎食
- 🧬 **达尔文进化**：基于用户反馈自动优化猎食策略
- 🎯 **22个知识领域**：覆盖量子计算、设计原理、心理学、投资、编程等
- 📊 **猎食统计**：记录猎食历史，分析知识分布
- 🔄 **智能反馈**：根据用户喜好调整猎食方向
- 🎲 **随机发现**：用随机性打破信息茧房

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/workbuddy/venom.git

# 进入目录
cd venom

# 运行毒液
python venom.py
```

### 使用

```bash
# 命令行运行
python venom.py

# 或者双击启动（Windows）
start_venom.bat
```

### 在 WorkBuddy 中使用

直接说触发词：
- "毒液"
- "给我找点有意思的"
- "我不知道想看什么"
- "随机知识"
- "打破信息茧房"
- "知识探险"
- "venom"

## 📖 工作原理

毒液从5个知识源中随机猎食：

| 触手 | 知识源 | 扫描目标 |
|------|--------|----------|
| 🦑 触手1 | 工作区脚本 | `.py`, `.js`, `.sh`, `.bat`, `.html` 文件 |
| 🦑 触手2 | 最近笔记 | `.md` 文件（按修改时间排序） |
| 🦑 触手3 | 个人兴趣 | 用户配置的兴趣关键词 |
| 🦑 触手4 | 随机知识 | 内置知识库（22个领域） |
| 🦑 触手5 | Dashboard MOC | 索引文件、目录结构、配置文件 |

## 🧬 达尔文进化机制

毒液 v2 引入了达尔文进化论：

1. **基因系统**：每个触手有权重基因
2. **自然选择**：基于用户反馈调整权重
3. **基因变异**：10%概率随机调整权重
4. **适者生存**：高权重触手更容易被选中

```
进化前（初始权重）：
脚本   | 1.00 | ██████████
笔记   | 1.00 | ██████████
兴趣   | 1.00 | ██████████
知识   | 1.00 | ██████████
MOC    | 1.00 | ██████████

进化后（10次猎食后）：
脚本   | 1.36 | █████████████
笔记   | 1.24 | ████████████
知识   | 1.06 | ██████████
MOC    | 0.96 | █████████
兴趣   | 0.88 | ████████
```

## 📁 文件结构

```
venom/
├── SKILL.md              # 技能定义文件
├── README.md             # 使用说明
├── RELEASE.md            # 发布说明
├── venom.py              # 原版毒液脚本
├── venom_evolved.py      # 达尔文进化版脚本 ⭐
├── interests.json        # 兴趣配置文件
├── test-prompts.json     # 测试用例
├── start_venom.bat       # Windows启动脚本
├── test_venom.py         # 测试脚本
└── .gitignore            # Git忽略文件
```

## ⚙️ 配置

### 兴趣配置

编辑 `interests.json` 自定义你的兴趣领域：

```json
{
  "interests": [
    "AI",
    "编程",
    "投资",
    "健康",
    "心理学",
    "设计",
    "哲学",
    "科学"
  ]
}
```

## 🧪 测试

```bash
# 运行测试
python test_venom.py

# 运行所有测试
python test_venom.py all
```

## 📊 评分

毒液技能经过达尔文优化，获得 90/100 分：

| 维度 | 评分 |
|------|------|
| Frontmatter质量 | 9/10 |
| 工作流清晰度 | 9/10 |
| 边界条件覆盖 | 9/10 |
| 检查点设计 | 9/10 |
| 指令具体性 | 9/10 |
| 资源整合度 | 9/10 |
| 整体架构 | 9/10 |
| 实测表现 | 9/10 |

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- 感谢 [obsidian-serendrip](https://github.com/ystkw/obsidian-serendrip) 的灵感
- 感谢 WorkBuddy 团队的支持

## 📧 联系方式

- 作者：WorkBuddy
- 仓库：https://github.com/workbuddy/venom
- 主页：https://workbuddy.cn/skills/venom

---

**毒液**：打破信息茧房，发现意想不到的知识关联。🦑
