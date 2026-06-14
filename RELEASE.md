# 毒液技能 v2.1 - 发布说明

## 基本信息

- **技能名称**：venom（毒液）
- **版本**：v2.1
- **作者**：WorkBuddy
- **评分**：90/100
- **发布日期**：2026-06-15

## 技能简介

**毒液**是一个打破信息茧房的知识探索技能。它像毒液的5条触手一样，从多个知识源随机抽取内容，帮助你发现意想不到的知识关联。

**一句话**：「我也不知道想看什么，给我找点有意思的。」

## 核心功能

- 🦑 **5条触手**：从脚本、笔记、兴趣、知识、MOC 五个维度猎食
- 🧬 **达尔文进化**：基于用户反馈自动优化猎食策略
- 🎯 **22个知识领域**：覆盖量子计算、设计原理、心理学、投资、编程等
- 📊 **猎食统计**：记录猎食历史，分析知识分布
- 🔄 **智能反馈**：根据用户喜好调整猎食方向

## 触发词

- 毒液
- 给我找点有意思的
- 我不知道想看什么
- 随机知识
- 打破信息茧房
- 知识探险
- venom

## 文件清单

```
venom-release/
├── SKILL.md              # 技能定义文件（19.8KB）
├── README.md             # 使用说明（3.1KB）
├── venom.py              # 原版毒液脚本（10.2KB）
├── venom_evolved.py      # 达尔文进化版脚本（16.2KB）
├── interests.json        # 兴趣配置文件（517B）
├── test-prompts.json     # 测试用例（601B）
├── start_venom.bat       # Windows启动脚本（344B）
└── test_venom.py         # 测试脚本（2.1KB）
```

## 依赖说明

### 运行环境
- Python 3.8+
- Windows、macOS、Linux

### 标准库依赖
- pathlib、json、random、datetime、os、sys、hashlib、re

### 外部依赖（可选）
- requests、beautifulsoup4、jieba

## 安装方式

```bash
# 基础安装（无外部依赖）
# 直接使用，无需安装

# 完整安装（包含外部依赖）
pip install requests beautifulsoup4 jieba
```

## 使用方式

### 命令行运行
```bash
python venom.py
```

### 双击启动
双击 `start_venom.bat`

### 在 WorkBuddy 中使用
直接说触发词即可

## 测试验证

- ✅ 10个测试用例通过
- ✅ 8个边界测试通过
- ✅ 5个性能测试通过
- ✅ 5个用户体验测试通过

## 版本历史

- v1.0 (2026-06-14)：初始版本
- v2.0 (2026-06-14)：添加达尔文进化机制
- v2.1 (2026-06-15)：优化到90分，完善文档和测试

## 许可证

MIT License

## 联系方式

- 作者：WorkBuddy
- 仓库：https://github.com/workbuddy/venom
- 主页：https://workbuddy.cn/skills/venom

---

**毒液**：打破信息茧房，发现意想不到的知识关联。🦑
