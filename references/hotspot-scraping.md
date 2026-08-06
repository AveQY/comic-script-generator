# 热点抓取实战指南

## 平台可访问性测试结果（2026-06-21）

### ✅ 可用平台

#### 百度热搜
- **URL**: `https://top.baidu.com/board?tab=realtime`
- **访问方式**: `browser_navigate`
- **登录要求**: 无
- **数据获取**: 直接从页面元素提取
- **更新频率**: 实时
- **推荐指数**: ⭐⭐⭐⭐⭐

### ❌ 受限平台

#### 微博热搜
- **URL**: `https://s.weibo.com/top/summary`
- **问题**: 自动重定向到访客系统（passport.weibo.com/visitor/visitor）
- **解决方案**: 暂无可靠方案，不推荐使用

#### 知乎热榜
- **URL**: `https://www.zhihu.com/hot`
- **问题**: 返回空页面，需要登录
- **解决方案**: 暂无可靠方案，不推荐使用

#### B站、抖音、豆瓣
- **状态**: 未完整测试
- **预期**: 可能需要登录或有反爬限制

## 抓取流程

### 1. 访问百度热搜

```python
browser_navigate(url="https://top.baidu.com/board?tab=realtime")
```

### 2. 提取数据

从 `browser_snapshot` 中提取链接文本：
- 热点标题通常在链接元素中
- 排名从页面结构推断（1-50）
- 标签（"新"、"热"）表示热度

### 3. 数据结构化

```python
hotspots = [
    {
        "rank": 1,
        "title": "话题标题",
        "source": "百度热搜",
        "type": "类型分类"  # 社会/科技/娱乐/体育/文化等
    },
    # ...
]
```

### 4. 筛选创作适合度

**适合创作的话题特征**：
- 有故事性（人物、情节、冲突）
- 情感共鸣（亲情、友情、爱情、励志）
- 轻松幽默（生活趣事、反转、吐槽）
- 科普教育（传统文化、科学知识）
- 社会热点但不过于沉重

**不适合创作的话题**：
- 纯时政新闻
- 重大灾难事件
- 敏感政治话题
- 过于沉重的悲剧

### 5. 保存格式

文件：`hotspots/YYYY-MM-DD.md`

```markdown
# 热点记录 - 2026-06-21

## 数据来源
- 百度热搜实时榜
- 抓取时间：2026-06-21 14:30

## TOP15 热点话题

1. **话题标题1** - 类型
2. **话题标题2** - 类型
...
```

## 展示给用户的格式

```
📊 TOP10 适合创作的热点话题

1. 【励志/传记】蔡磊发布《倒计时》演讲
   创作方向：渐冻症患者的抗争故事

2. 【搞笑/社会】男子一夜连叫3次代驾仍因醉驾被查
   创作方向：反常识的搞笑故事

...
```

## 浏览器失效时的 curl 降级方案（2026-07-20 实测新增）

`browser_navigate` 访问 `top.baidu.com/board?tab=realtime` 可能因浏览器守护进程未启动/Chromium 缺库而超时（120s）。此时**不要反复重试浏览器**，改用百度热搜 JSON API 直接 curl：

```bash
curl -s --max-time 15 "https://top.baidu.com/api/board?platform=pc&tab=realtime" | python3 -c "
import json, sys
data = json.loads(sys.stdin.read())
for card in data.get('data', {}).get('cards', []):
    for i, item in enumerate(card.get('content', [])[:30], 1):
        title = item.get('word', '') or item.get('query', '')
        hot = item.get('hotScore', '') or item.get('heatScore', '')
        if title:
            print(f'{i:2d}. [{hot}] {title}')
    break
"
```

要点：
- `platform=pc` 返回完整榜单（2026-07-20 实测抓到 30 条）；`platform=wise` 同 URL 返回近空数据，勿用。
- 标题字段优先 `word`，热度字段优先 `hotScore`；部分条目字段名不同，需双 fallback。
- 解析容错：curl 失败或 JSON 空时回退 `fallback_hot_topics()`（LLM 生成候选），与 SKILL.md 模式四「话题来源兜底」一致。

## 常见问题

### Q: 如果百度热搜也无法访问怎么办？
A: 先用上面的 curl API 降级；再不行回退到 `web_search("最近热点话题")` 或 `fallback_hot_topics()`，从搜索结果中提取。

### Q: 抓取频率建议？
A: 每天抓取1次即可，热点变化不会太快。

### Q: 如何判断话题是否过时？
A: 检查热点记录文件的日期，超过15天的不再使用。

## 更新日志

- 2026-06-21: 初始版本，测试百度/微博/知乎可访问性
