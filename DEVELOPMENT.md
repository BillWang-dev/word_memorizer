# 英语听写与词汇记忆系统 - 开发文档

## 📋 项目概述

基于Python开发的英语单词学习系统，集成听写练习、智能复习调度和学习统计功能。

## 🎯 核心功能

1. **单词听写练习**: 基于TTS的语音听写，支持手动输入答案
2. **智能复习调度**: 基于SM-2算法的间隔重复学习
3. **学习统计分析**: 可视化学习进度和成绩趋势
4. **音频缓存管理**: 本地缓存TTS音频，提升响应速度

## 🚀 技术架构

### 核心模块

| 模块 | 功能描述 | 负责人 | 代码量 | 文件路径 |
|------|----------|--------|--------|----------|
| Core (核心逻辑) | 词汇管理、复习调度算法 | 成员 A | ≈ 400 | logic/core.py |
| Audio (音频引擎) | TTS合成、音频播放、缓存 | 成员 B | ≈ 350 | audio/listen.py |
| GUI (用户界面) | Tkinter界面、交互逻辑 | 成员 C | ≈ 400 | ui/main.py |

### 数据流程

```
用户操作 → GUI界面 → 核心逻辑 → 音频引擎 → 学习数据存储
    ↓
统计面板 ← 数据可视化 ← 学习记录
```

## 📅 开发计划

| 阶段 | 时间 | 主要任务 | 完成状态 |
|------|------|----------|----------|
| D1-D3 | 需求分析 | 功能设计、技术选型 | ✅ 完成 |
| D4-D6 | 核心开发 | 词汇管理、复习算法 | ✅ 完成 |
| D7-D9 | 音频模块 | TTS集成、音频缓存 | ✅ 完成 |
| D10-D12 | GUI开发 | 界面设计、交互逻辑 | ✅ 完成 |
| D13-D15 | 测试优化 | 单元测试、性能优化 | ✅ 完成 |

## 🛠️ 技术栈

### 核心依赖
- **GUI**: Tkinter + sv-ttk (现代主题)
- **音频**: edge-tts, pygame, pydub
- **数据处理**: pandas, numpy
- **可视化**: matplotlib
- **构建**: PyInstaller

### 算法实现
- **SM-2间隔重复**: 智能复习调度
- **文本相似度**: 听写答案评分
- **音频缓存**: LRU缓存策略

## 📊 数据结构

### WordItem类
```python
class WordItem:
    word: str              # 单词
    meaning: str           # 中文释义
    pronunciation: str     # 音标
    difficulty: int        # 难度等级(1-5)
    review_count: int      # 复习次数
    correct_count: int     # 正确次数
    next_review: datetime  # 下次复习时间
    interval: int          # 复习间隔(天)
    ease_factor: float     # 易度因子
```

### 学习记录
```python
class LearningRecord:
    word_id: str           # 单词ID
    timestamp: datetime    # 学习时间
    is_correct: bool       # 是否正确
    answer: str           # 用户答案
    similarity: float     # 相似度分数
```

## 🔧 核心算法

### SM-2间隔重复算法

```python
def calculate_next_review(self, word_item, quality):
    """计算下次复习时间"""
    if quality >= 3:  # 答对
        if word_item.interval == 0:
            word_item.interval = 1
        elif word_item.interval == 1:
            word_item.interval = 6
        else:
            word_item.interval = int(word_item.interval * word_item.ease_factor)
        
        word_item.ease_factor = max(1.3, 
            word_item.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
    else:  # 答错
        word_item.interval = 0
        word_item.ease_factor = max(1.3, word_item.ease_factor - 0.2)
    
    return word_item.interval
```

### 文本相似度计算

```python
def calculate_similarity(self, correct, user_answer):
    """计算文本相似度"""
    # 预处理
    correct = correct.lower().strip()
    user_answer = user_answer.lower().strip()
    
    # 完全匹配
    if correct == user_answer:
        return 1.0
    
    # 编辑距离计算
    distance = self.levenshtein_distance(correct, user_answer)
    max_len = max(len(correct), len(user_answer))
    
    return 1.0 - (distance / max_len)
```

## 🎨 用户界面

### 主要界面组件

1. **听写界面**
   - 音频播放控制
   - 答案输入区域
   - 结果反馈显示

2. **统计面板**
   - 学习进度概览
   - 准确率趋势图
   - 每日学习数据

3. **设置面板**
   - 音频参数配置
   - 复习策略设置

## 📈 性能优化

### 音频缓存策略
- **LRU缓存**: 最近使用的音频优先保留
- **预加载**: 智能预加载常用单词音频
- **压缩存储**: 音频文件压缩存储

### 内存管理
- **智能清理**: 定期清理过期缓存
- **延迟加载**: 按需加载matplotlib等重库
- **异步处理**: 音频生成和播放异步化

## 🧪 测试策略

### 单元测试
- 核心算法测试
- 数据类验证
- 音频模块测试

### 集成测试
- GUI交互测试
- 端到端功能测试
- 性能压力测试

## 📦 部署方案

### 可执行文件构建
```bash
# Windows
pyinstaller --onefile --windowed ui/main.py

# macOS
pyinstaller --onefile --windowed ui/main.py

# Linux
pyinstaller --onefile ui/main.py
```

### 依赖管理
- 使用requirements.txt管理依赖
- 虚拟环境隔离
- 版本锁定确保兼容性

## 🔍 故障排除

### 常见问题
1. **音频播放失败**: 检查pygame安装和系统音频
2. **GUI启动异常**: 验证Tkinter和sv-ttk安装
3. **依赖冲突**: 使用虚拟环境隔离

### 调试工具
- 日志系统记录运行状态
- 异常捕获和错误报告
- 性能监控和优化建议

## 📚 文档维护

### 代码注释
- 函数级文档字符串
- 复杂算法注释说明
- 配置参数说明

### 用户文档
- 安装指南
- 使用说明
- 故障排除

---

**项目状态**: ✅ 开发完成，已发布v1.1.0版本
**最后更新**: 2024年12月

