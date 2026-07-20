# comic-script-generator 线上阅读器部署记录

用于未来维护 `https://<your-reader-domain>/reader` 时快速定位代码和部署关系。

## 所属 skill

- Hermes skill：`creative/comic-script-generator`
- 本机 Hermes 使用副本：`C:\Users\YOUR_USERNAME\AppData\Local\hermes\skills\creative\comic-script-generator\`
- 本机开发副本：`C:\Users\YOUR_USERNAME\Desktop\my-skills\comic-script-generator\`

## 服务器部署

服务器 IP：`<your-server-ip>`

线上站点不是直接从 skill 目录运行，而是独立 Python API 项目：

- 项目目录：`/path/to/comic-script-generator-api`
- Reader 页面：`/path/to/comic-script-generator-api/reader.html`
- 主程序：`/path/to/comic-script-generator-api/app.py`
- 运行命令：`python3 app.py`（前台）或后台运行
- 监听端口：`127.0.0.1:8081`

Nginx：

- 配置文件：`/etc/nginx/sites-available/<your-reader-domain>`
- enabled：`/etc/nginx/sites-enabled/<your-reader-domain>`
- 域名：`<your-reader-domain>`
- 反代：`location / { proxy_pass http://127.0.0.1:8081; }`
- 已移除 default site，避免端口冲突
- HTTPS：使用 certbot 申请证书，自动配置 443 跳转

访问链路：

```text
https://<your-reader-domain>/reader
→ Nginx :80/:443
→ http://127.0.0.1:8081/reader
→ /path/to/comic-script-generator-api/reader.html
```

## DNS 配置要求

- 在域名服务商处将 `<your-reader-domain>` 的 A 记录指向 `<your-server-ip>`
- 如果使用 Cloudflare，需要关闭代理/CDN，改为 "DNS only" 模式，否则流量不会到达本机 Nginx
- DNS 生效后访问 `http://<your-reader-domain>/reader` 验证

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
- 修改服务器 API/reader 时，注意它是独立项目 `/path/to/comic-script-generator-api`，不是直接修改 Hermes skill 目录。
- 如果要把脚本生成结果继续转成图或视频，优先加载 `story-renderer`，不要把图像渲染逻辑塞回 `comic-script-generator`。
