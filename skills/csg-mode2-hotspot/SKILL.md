---
name: csg-mode2-hotspot
description: >-
  从百度热搜等平台抓取热点话题，生成创意大纲和漫画分镜脚本。支持 TOP10 展示、用户选择后生成。
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, terminal
---

### 模式二：热点话题生成

1. **题材选择流程**
   - 询问用户：
     ```
     请选择创作方向：
     1. 提供具体题材（如：校园恋爱、科幻冒险、职场励志）
     2. 让我抓取热点话题 TOP10 供你选择
     ```

2. **抓取热点**
   - **平台访问限制（重要）**：
     - ✅ **百度热搜**（top.baidu.com/board?tab=realtime）：无需登录，可直接抓取，推荐优先使用
     - ❌ 微博热搜（s.weibo.com/top/summary）：需要登录，会重定向到访客系统
     - ❌ 知乎热榜（zhihu.com/hot）：需要登录，返回空页面
     - ⚠️ B站、抖音、豆瓣：访问受限或需特殊处理
   - **抓取策略**：
     1. 优先使用 `browser_navigate` 访问百度热搜；**浏览器超时/不可用时改用 JSON API**：`curl "https://top.baidu.com/api/board?platform=pc&tab=realtime"`（`platform=pc` 有数据，`wise` 返回近空；标题字段 `word`/`query`、热度 `hotScore`/`heatScore` 双兜底，完整解析脚本见 `references/hotspot-scraping.md`）
     2. 提取热点标题、排名信息
     3. 根据话题内容分类（社会、科技、娱乐、体育等）
     4. 筛选出适合创作的话题（排除纯时政、过于严肃的内容）
   - 时效性：15天内
   - 类型：全类型
   - 保存热点记录到 `hotspots/YYYY-MM-DD.md`

3. **展示 TOP10**
   - 从抓取结果中筛选适合创作的话题（排除纯时政、灾难等不适合漫画的内容）
   - 按热度排序，展示：
     ```
     1. 【类型/风格】<话题标题>
        创作方向：<简要说明改编思路>
     2. ...
     ```
   - 用户选择后，生成创意大纲

4. **生成流程**
   - 基于热点生成故事大纲
   - 确认后进入"模式一"的生成流程
