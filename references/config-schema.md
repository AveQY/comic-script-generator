# 项目配置文件 schema

每个漫画项目根目录下的 `config.json`，用于记录项目设置和生成进度。

## 完整 schema

```json
{
  "project_name": "string, required",
  "created_at": "ISO 8601 timestamp",
  "updated_at": "ISO 8601 timestamp",
  "density_mode": "A | B | C",
  "art_style": "string, 艺术风格描述",
  "language": "zh-CN | en-US | ja-JP",
  "total_episodes": "number, 计划总集数",
  "current_episode": "number, 当前写到第几集",
  "episodes_planned": "number, 与 total_episodes 相同",
  "status": "planning | writing | reviewing | completed",
  "source": "outline | hotspot",
  "hotspot_date": "YYYY-MM-DD, 热点抓取日期",
  "characters": ["角色名列表"],
  "foreshadowing_active": ["未回收伏笔描述"],
  "notes": "string, 项目备注"
}
```

## 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `project_name` | string | ✅ | 项目名称，与目录名一致 |
| `created_at` | string | ✅ | 项目创建时间 |
| `updated_at` | string | ✅ | 最后更新时间（每次生成新集后更新） |
| `density_mode` | string | ✅ | 分镜密度模式：A/B/C |
| `art_style` | string | ❌ | 艺术风格描述，用于 AI 绘图提示词 |
| `language` | string | ❌ | 剧本语言，默认 zh-CN |
| `total_episodes` | number | ✅ | 计划总集数 |
| `current_episode` | number | ✅ | 当前已完成的集数 |
| `episodes_planned` | number | ✅ | 与 total_episodes 相同，保持向后兼容 |
| `status` | string | ✅ | 项目状态 |
| `source` | string | ✅ | 内容来源 |
| `hotspot_date` | string | ❌ | 热点抓取日期（source=hotspot 时填写） |
| `characters` | array | ❌ | 已创建的角色名列表 |
| `foreshadowing_active` | array | ❌ | 当前未回收的伏笔描述 |
| `notes` | string | ❌ | 项目备注，可记录特殊设定 |

## 示例

```json
{
  "project_name": "天台相遇",
  "created_at": "2026-06-23T10:00:00+08:00",
  "updated_at": "2026-06-23T12:30:00+08:00",
  "density_mode": "B",
  "art_style": "manga style, soft pastel colors, cinematic lighting",
  "language": "zh-CN",
  "total_episodes": 6,
  "current_episode": 2,
  "episodes_planned": 6,
  "status": "writing",
  "source": "outline",
  "characters": ["阿明", "小雨", "阿明母亲"],
  "foreshadowing_active": [
    "阿明父亲的遗物（第2集埋下）",
    "天台栏杆上的涂鸦（第1集埋下）"
  ],
  "notes": "用户偏好对话自然，减少文艺腔"
}
```

## 初始化脚本使用

初始化脚本 `init_project.py` 会自动生成此配置文件，默认值：

```python
DEFAULT_CONFIG = {
    "density_mode": "B",
    "art_style": "",
    "language": "zh-CN",
    "total_episodes": 6,
    "current_episode": 0,
    "status": "planning",
    "source": "outline",
    "characters": [],
    "foreshadowing_active": [],
    "notes": ""
}
```

用户可以在初始化时通过命令行参数覆盖这些默认值。
