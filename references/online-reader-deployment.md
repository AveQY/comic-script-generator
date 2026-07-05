# comic-script-generator 线上阅读器部署记录

用于未来维护 `https://comic-script-generator.YOUR_DOMAIN/reader` 时快速定位代码和部署关系。

## 所属 skill

- Hermes skill：`creative/comic-script-generator`
- 本机 Hermes 使用副本：`C:\Users\YOUR_USERNAME\AppData\Local\hermes\skills\creative\comic-script-generator\`
- 本机开发副本：`C:\Users\YOUR_USERNAME\Desktop\my-skills\comic-script-generator\`

## 服务器部署

服务器：服务器-叶 / AWS Lightsail `YOUR_SERVER_IP`

线上站点不是直接从 skill 目录运行，而是独立 Python API 项目：

- 项目目录：`<user-home>/comic-script-generator-api`
- Reader 页面：`<user-home>/comic-script-generator-api/reader.html`
- 主程序：`<user-home>/comic-script-generator-api/app.py`
- systemd 服务：`comic-api.service`
- 运行命令：`<user-home>/comic-script-generator-api/venv/bin/python app.py`
- 监听端口：`127.0.0.1:8081` / `0.0.0.0:8081`（以现场 `ss` 为准）

Nginx：

- 配置文件：`/etc/nginx/sites-available/comic-script-generator`
- enabled：`/etc/nginx/sites-enabled/comic-script-generator`
- 域名：`comic-script-generator.YOUR_DOMAIN`
- 反代：`location / { proxy_pass http://127.0.0.1:8081; }`

访问链路：

```text
https://comic-script-generator.YOUR_DOMAIN/reader
→ Nginx
→ http://127.0.0.1:8081/reader
→ <user-home>/comic-script-generator-api/reader.html
```

## 相关 skill 组合

最适合和本 skill 一起使用的是：

- `creative/story-renderer`：把分镜脚本转换为图片或视频；这是最直接的下游配套 skill。
- `creative/comfyui`：需要接本地 ComfyUI 工作流、批量生图、角色一致性时使用。
- `software-development/python-service-deployment`：维护 `comic-api.service`、systemd、Nginx 反代、Flask/FastAPI 部署时使用。
- `dogfood`：测试 `/reader` 页面可用性、按钮、接口、移动端显示时使用。
- `creative/claude-design` 或 `creative/popular-web-designs`：改造 reader 页面 UI/视觉风格时使用。

## 快速排查命令

```bash
systemctl status comic-api.service --no-pager -l
systemctl cat comic-api.service --no-pager
sudo sed -n '1,220p' /etc/nginx/sites-available/comic-script-generator
ss -tulpen | grep -E '(:80|:443|:8081)'
ps -eo pid,user,cmd | grep -Ei 'comic|reader|nginx' | grep -v grep
```

## 维护提醒

- 修改 skill 内容时，需要同步本机 Hermes 使用副本和 Desktop 开发副本。
- 修改服务器 API/reader 时，注意它是独立项目 `<user-home>/comic-script-generator-api`，不是直接修改 Hermes skill 目录。
- 如果要把脚本生成结果继续转成图或视频，优先加载 `story-renderer`，不要把图像渲染逻辑塞回 `comic-script-generator`。
