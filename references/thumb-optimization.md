# Reader 缩略图优化：内容协商 + disk_cache + Service Worker

2026-07-06 记录。目标：降低漫画阅读器图片加载带宽与 CPU，支持离线访问。

## 后端实现要点

- `/thumb` 路由现在按 `Accept` 头协商返回 `image/avif` → `image/webp` → `image/jpeg`
- 新增 `cache_key(project, rel, w, h, fit, fmt)` 生成稳定缓存文件名：`sha256(project\0rel\0w\0h\0fit\0fmt).ext`
- 新增 `disk_cache/` 命中层：先读 `/path/to/comic-projects/disk_cache/`，命中直接返回，不进入 Pillow
- 未命中才实时压缩，结果写回 `disk_cache/`

### 内容协商优先级

1. `image/avif` → AVIF，质量 50，speed 8
2. `image/webp` → WEBP，质量 78，method 6
3. 无以上两者 → JPEG，质量 78，progressive=True

## 预生成脚本

文件：`scripts/pregen_thumbs.py`

```bash
python3 scripts/pregen_thumbs.py
```

输出：
- 目录：`/path/to/comic-projects/disk_cache/`
- 格式：WebP only
- 尺寸：`600x600 cover` + `800x1100 inside`
- 并发：8 线程
- 索引：`disk_cache/index.json`

实测：341 张 PNG → 682 个 WebP，耗时约 70 秒，总计 94.0 MB。

## 前端接入备忘

- Service Worker 文件：`/path/to/comic-script-generator-api/sw.js`
- 前端注册：`navigator.serviceWorker.register('/sw.js')`
- 图片建议改为 `<picture>` 结构，按格式优先级请求：
  - `/thumb?...&format=avif`
  - `/thumb?...&format=webp`
  - `/thumb?...&format=jpeg`

## 维护注意

- `app.py` 必须 `import hashlib`，否则缓存层会触发 `NameError`
- `Image.crop((left, top, left + w, top + h))` 必须传一个 4-tuple，不能拆成两个参数
- 预生成后如果原图更新，需重新运行 `pregen_thumbs.py` 或手动清理对应缓存文件
- 重启 `python3 app.py` 后 `/thumb` 新逻辑才会生效
