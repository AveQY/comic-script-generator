# 轻小说阅读器前端集成

## 概述

Reader 前端支持「漫画」和「轻小说」两种阅读模式切换。轻小说模式将 `export_light_novel.py` 生成的 `light_novel/ln*.md` 文件渲染为番茄小说风格的正文页面，`<!-- ILLUST_N -->` 标记自动匹配已有渲染图作为插图。

## 后端 API

### `/light-novels?project=<项目名>`

列出项目下的轻小说文件。

**响应格式**：
```json
{
  "project": "DemoProjectA",
  "count": 6,
  "novels": [
    {
      "file": "light_novel/ln001_入住第一天.md",
      "title": "第1集：入住第一天",
      "chars": 15049,
      "url": "/file?project=DemoProjectA&path=light_novel/ln001_入住第一天.md"
    }
  ]
}
```

### 文件访问

轻小说文件通过既有 `/file?project=&path=` 端点访问，无需新增路由。目录结构自动基于 `light_novel/` 子目录。

## 前端修改要点

`reader.html` 是单文件 SPA，修改集中在三处：

### 1. CSS 新增（在 `</style>` 前插入）

- `.mode-toggle` / `.mode-btn` — Header 模式切换按钮样式
- `.novel-reader` — 正文阅读区（米黄背景、宋体/楷体、大行距）
- `.novel-dialogue` / `.novel-narration` — 对话气泡/旁白样式
- `.novel-illust` — 插图容器（居中、圆角、1px 边框）
- `.novel-chapter-nav` — 上下章导航按钮
- `.novel-font-size` — 字号调节控件
- `.novel-progress` — 阅读进度条
- `.novel-list` / `.novel-item` — 章节列表

### 2. HTML 新增（Header 区域）

```html
<div class="mode-toggle" id="modeToggle">
  <button class="mode-btn active" onclick="switchMode('comic')" id="modeComic">🖼 漫画</button>
  <button class="mode-btn" onclick="switchMode('novel')" id="modeNovel">📖 小说</button>
</div>
```

### 3. JS 新增函数

| 函数 | 职责 |
|------|------|
| `switchMode(mode)` | 切换漫画/小说模式，更新按钮状态 |
| `showNovelView()` | 显示轻小说章节列表 |
| `showComicView()` | 切回漫画主视图 |
| `loadLightNovels(project)` | 从 `/light-novels` API 加载章节列表 |
| `renderNovelList()` | 渲染章节列表卡片 |
| `loadLightNovel(index)` | 加载并渲染指定章节正文 |
| `renderNovel(md, index)` | 将 Markdown 转为番茄小说风格 HTML |
| `changeFontSize(delta)` | 字号调节（14-28px） |
| `updateNovelProgress()` | 滚动监听 + 阅读进度条 |

关键函数 `renderNovel` 的 Markdown 解析规则：
- `<!-- ILLUST_N -->` → 尝试匹配已有的渲染图（通过 `currentDetail.images` 按序号查找），找到则嵌入 `<img>`，找不到显示 `· · ·`
- `> xxx` → `<div class="novel-narration">`（旁白，斜体+缩进）
- `「xxx」——角色` → `<div class="novel-dialogue">`
- 其他文本 → `<p>`（段落，首行缩进）
- `# ` → 跳过（标题单独渲染）
- `---` → 跳过

### 数据流

```text
loadProject()
  → loadLightNovelsInBg()  // 预取轻小说列表到 currentNovels
  → switchMode() → showNovelView() / renderComicDetail()

loadLightNovel(index)
  → fetch(novel.url)       // 从 /file 端点获取 light_novel/ln*.md
  → renderNovel(md, index) // 解析 Markdown + 嵌入插图
```

插图匹配逻辑：
- `currentNovelIndex * 7 + (ILLUST_N - 1)` 算出该插图在 `currentDetail.images` 中的近似索引
- 用 `Math.min(sceneIdx, images.length - 1)` 防越界
- 插图 URL 直接复用渲染图的已有路径

## 文件名约定

```
light_novel/
├── ln001_入住第一天.md     # 轻小说正文
├── ln002_深夜厨房战争.md
├── ln003_大扫除战争.md
└── ...

render_input/
├── key_scenes001_入住第一天.json   # 关键场景渲染清单
└── ...
```

## 调试技巧

1. **轻小说列表为空**：检查 `light_novel/` 目录是否存在，运行 `export_light_novel.py`
2. **插图不显示**：轻小说模式使用已有渲染图（`rendered/ep*/scene_*.png`），如果渲染图不存在则显示 `· · ·` 分隔符
3. **阅读进度条不动**：确认 `#main` 元素有可滚动内容且 `updateNovelProgress()` 绑定了 scroll 事件
4. **URL 编码问题**：中文项目名和文件名必须 `encodeURIComponent`，前端已处理；如果新加端点请保持一致