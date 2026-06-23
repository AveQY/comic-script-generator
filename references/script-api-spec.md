# 在线脚本生成接口规范

`comic-script-generator` 提供在线接口，允许外部系统远程调用生成漫画分镜脚本。

## 接口设计原则

1. **单一职责**：一个请求 = 一次完整脚本生成（完整一集或按集生成）
2. **幂等性**：相同参数重复调用返回相同结果
3. **版本化**：通过 `version` 字段兼容不同版本的请求/响应格式
4. **状态追踪**：通过 `job_id` 查询长时间运行的生成任务
5. **错误标准化**：所有错误返回统一的 `error` 结构

## 端点定义

### 1. 生成脚本

```
POST /v1/generate
```

**请求体：**
```json
{
  "version": "1.0",
  "project_id": "optional-existing-project-id",
  "mode": "B",
  "episodes_planned": 6,
  "current_episode": 1,
  "topic": "校园恋爱故事",
  "outline": "主角在觉醒日发现自己的特殊能力...",
  "characters": [
    {
      "name": "阿明",
      "age": 17,
      "appearance": "短发，校服",
      "personality": "内向",
      "background": "普通高中生"
    }
  ],
  "existing_summary": "前情提要（续写时提供）",
  "foreshadowing": ["神秘项链", "奇怪的梦"],
  "callback_webhook": "https://example.com/webhook"
}
```

**必填字段：** `mode`, `topic` 或 `outline` 至少一个

**响应体（成功）：**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued|processing|completed|failed",
  "progress": 0-100,
  "result": {
    "project_id": "xxx",
    "episode_number": 1,
    "title": "第1集：觉醒之日",
    "scenes_count": 50,
    "script_path": "projects/xxx/episodes/ep001_xxx.md",
    "content_markdown": "# 第1集..."
  },
  "error": null
}
```

**响应体（失败）：**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "failed",
  "progress": 0,
  "result": null,
  "error": {
    "code": "INVALID_OUTLINE",
    "message": "大纲不能为空",
    "details": "topic 和 outline 至少提供一个"
  }
}
```

### 2. 查询任务状态

```
GET /v1/jobs/{job_id}
```

**响应体：**
```json
{
  "job_id": "xxx",
  "status": "completed",
  "progress": 100,
  "created_at": "2026-06-23T10:00:00Z",
  "completed_at": "2026-06-23T10:05:00Z",
  "result": { ... },
  "error": null
}
```

### 3. 列出项目

```
GET /v1/projects
```

**响应体：**
```json
{
  "projects": [
    {
      "project_id": "xxx",
      "name": "校园恋爱故事",
      "mode": "B",
      "total_episodes": 6,
      "completed_episodes": 2,
      "created_at": "2026-06-23T10:00:00Z",
      "updated_at": "2026-06-23T12:00:00Z"
    }
  ]
}
```

### 4. 获取项目详情

```
GET /v1/projects/{project_id}
```

**响应体：**
```json
{
  "project_id": "xxx",
  "name": "校园恋爱故事",
  "mode": "B",
  "config": { ... },
  "episodes": [
    {
      "episode_number": 1,
      "title": "觉醒之日",
      "scenes_count": 50,
      "created_at": "..."
    }
  ]
}
```

### 5. 续写脚本

```
POST /v1/continue
```

**请求体：**
```json
{
  "version": "1.0",
  "project_id": "existing-project-id",
  "mode": "B",
  "current_episode": 2,
  "outline": "第二集大纲..."
}
```

**必填字段：** `project_id`, `current_episode`

## 错误码

| code | HTTP 状态 | 说明 |
|------|----------|------|
| `INVALID_REQUEST` | 400 | 请求参数错误 |
| `MISSING_REQUIRED_FIELD` | 400 | 缺少必填字段 |
| `INVALID_MODE` | 400 | mode 不是 A/B/C |
| `PROJECT_NOT_FOUND` | 404 | project_id 不存在 |
| `JOB_NOT_FOUND` | 404 | job_id 不存在 |
| `RATE_LIMIT_EXCEEDED` | 429 | 请求频率超限 |
| `INTERNAL_ERROR` | 500 | 服务器内部错误 |
| `MODEL_ERROR` | 502 | 模型生成失败 |

## 安全要求

1. **API Key 认证**：所有接口必须在 Header 中携带 `Authorization: Bearer *** **HTTPS 强制**：生产环境必须使用 HTTPS
3. **Rate Limit**：每个 API Key 限流（如 10 请求/分钟）
4. **敏感信息过滤**：响应中不得泄露系统配置、API Key、内部路径
5. **Webhook 验证**：`callback_webhook` 必须支持签名验证

## 客户端集成示例

```bash
# 1. 提交生成请求
curl -X POST https://api.example.com/v1/generate \
  -H "Authorization: Bearer *** \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "B",
    "topic": "校园恋爱故事",
    "outline": "主角在觉醒日..."
  }'

# 2. 轮询任务状态
curl https://api.example.com/v1/jobs/{job_id} \
  -H "Authorization: Bearer *** # 3. 获取结果
curl https://api.example.com/v1/projects/{project_id} \
  -H "Authorization: Bearer <api_key>"
```

## 与 Story Renderer 接口的区别

| 维度 | Comic Script Generator | Story Renderer |
|------|----------------------|----------------|
| 输入 | 大纲/话题/角色设定 | 完整故事脚本 |
| 输出 | 分镜脚本 markdown | 图片/视频 |
| 接口目的 | 内容创作 | 内容渲染 |
| 接口复杂度 | 中等（5 个端点） | 较高（含项目管理） |
| 状态跟踪 | 按 job 追踪生成任务 | 按 project 追踪渲染进度 |
