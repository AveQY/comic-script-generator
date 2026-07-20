# Reader 前端：模态框 → 独立视图模式（2026-07-19）

记录本次「接口文档」从模态框（modal dialog）改为独立视图（main-region swap）的实战经验与动机。**适用于 Reader 单文件 SPA 内任何"新功能入口"的呈现方式选择**。

## 用户明确偏好（2026-07-19）

> 用户原话："点击接口文档应该是一个新界面展示"

**规则**：在 Reader 单文件 SPA（`templates/reader.html`）里新增"功能入口"（API 文档、统计页、设置页、关于页等），默认应该用**独立视图**（切换 `#main` 内容 + `setNav()` 高亮），**不是模态框**（`position:fixed` 弹层 + mask）。

只有以下情况才考虑模态框：
- 短小确认/输入（如"是否删除？"）
- 中断式提示（如登录过期）
- 全局性一次性引导

**独立视图的好处**：
- 与 showHome / showRank / showRecent / showComic 一致，符合 SPA 心智模型
- 移动端 tab 自然衔接（底部 tab 加按钮即可，无需处理模态框在小屏上的适配）
- 不锁 `body` 滚动，主页面滚动条保持一致
- 返回路径清晰（点其它导航即切换，不需要 Esc / 点遮罩）
- 侧边栏保持可见，可快速跳转分类

## 实现模板

### 1. 顶部导航 + 移动端 tab

```html
<button id="navXxx" onclick="showXxx()">🎯 名字</button>
<!-- 移动端： -->
<button id="mXxx" onclick="showXxx()">🎯<br>名字</button>
```

### 2. setNav 注册

```js
function setNav(n){
  ['Home','Cats','Shelf','Rank','Recent','Xxx','Comic'].forEach(x=>{
    let e=document.getElementById('nav'+x);
    if(e) e.classList.toggle('active',x===n);
  });
  ['Home','Cats','Shelf','Rank','Recent','Xxx','Comic'].forEach(x=>{
    let e=document.getElementById('m'+x);
    if(e) e.classList.toggle('active',x===n);
  });
}
```

注意两个数组要同步加 `'Xxx'`，漏一个会导致移动端/桌面端有一边不高亮。

### 3. showXxx() 函数骨架

```js
function showXxx(){
  setNav('Xxx');
  document.getElementById('main').innerHTML = `<section class="section">
    <div class="section-head"><h2>🎯 标题</h2><small>副标题</small></div>
    ... 内容 ...
  </section>`;
  window.scrollTo(0,0);   // ← 必须，切换视图后滚回顶部
}
```

**`window.scrollTo(0,0)` 是必须的**——否则用户从长列表（如"最新"100 条）切到短内容（如文档）时，浏览器会保留滚动位置，看起来像"页面空白"。

### 4. 从模态框迁移时的清理清单

把已有的模态框改为独立视图时，**必须完整清理**这些残留，否则 CSS/JS 越改越乱：

| 类型 | 待清理选择器/标识符 |
|---|---|
| HTML | `<div class="Xxx-modal">` 整段（含 mask、dialog、head、close 按钮） |
| CSS | `.Xxx-modal`、`.Xxx-modal.open`、`.Xxx-mask`、`.Xxx-dialog`、`.Xxx-head`、`.Xxx-close`、`.Xxx-btn`（独立触发按钮样式） |
| JS | `openXxx()`、`closeXxx()`、`document.addEventListener('keydown', Esc→close)` |
| 移动端 `@media` | 模态框专属的 `.Xxx-dialog max-height`、`border-radius` 调整 |

**验证命令**（清理后跑一遍，全为 0 即干净）：

```bash
f=/path/to/reader.html
grep -c "Xxx-modal\|Xxx-mask\|Xxx-dialog\|openXxx\|closeXxx\|id=\"XxxModal\"" $f
# 期望: 0
```

### 5. 内容样式适配

模态框里的内容样式（如 `.api-endpoint`、`.api-route`）在独立视图下需要：
- 去掉 `max-height` / `overflow-y:auto` 限制（不再需要在弹层内滚动）
- 加宽 padding（模态框内空间紧张用 14px，独立视图可以用 18-20px）
- 去掉 `box-shadow` 弹层阴影，改用更轻的 `0 1px 3px rgba(15,23,42,.04)` 卡片阴影
- `font-size` 微调（独立视图下文字可以稍大，13→14px）

## 本次实战记录

**Before**：API 文档是 `.api-modal` + mask 弹层，由顶栏右侧独立按钮 `openApiDoc()` 触发。

**After**：API 文档是 `showApiDoc()` 函数渲染到 `#main`，通过顶栏 `navApi` + 移动端 `mApi` 触发，`setNav('Api')` 高亮。

**踩到的坑**：
1. 删除模态框 HTML 时用 `sed -i '518,689d'` 按行号删除——**前提是要先用 `grep -n` 确认起止行**，不能凭印象。
2. patch CSS 时凭记忆构造 `old_string`，结果两次都不匹配（我以为的样式 vs 文件里实际样式不同）。**教训：长文件 patch 前必须 `read_file` 对齐真实内容，不能凭记忆写 old_string**——这跟 `references/patch-intext-pitfall-2026-07-08.md` 对中文正文的教训是同一类，但对 CSS/代码段同样适用。
3. 改造时容易漏掉移动端的 `mXxx` 按钮——`setNav` 数组和 HTML 都要同步加。

## 同步更新

本次改造同步更新了：
- 线上文件 `<reader-deploy-dir>/reader.html`
- skill 模板 `/root/.hermes/skills/comic-script-generator/templates/reader.html`

两者 md5 一致后才能算完成。**改 Reader 前端文件时永远要同步这两个位置**——线上跑的是 `<user-home>/.../reader.html`，但 skill 模板也要更新，否则下次部署会从旧模板重新生成。
