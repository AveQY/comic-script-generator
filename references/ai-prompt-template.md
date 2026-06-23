# AI 绘图提示词模板

每个分镜场景生成后，自动附带 AI 绘图提示词，适配主流图像生成工具。

## 提示词结构

每个场景的提示词分为两部分：

1. **正向提示词（Positive Prompt）**：画面描述 + 风格标签
2. **反向提示词（Negative Prompt）**：需要避免的内容

## 格式规范

### Stable Diffusion / ComfyUI 格式

```markdown
**AI 提示词**：

正向：
```
masterpiece, best quality, cinematic lighting, [画面描述], [镜头角度], [角色细节], [环境氛围], [艺术风格]
```

反向：
```
worst quality, low quality, blurry, deformed, bad anatomy, extra limbs, watermark, text, signature
```
```

### Midjourney 格式

```markdown
**AI 提示词**（Midjourney）：

```
[画面描述], [镜头角度], [艺术风格], cinematic lighting, masterpiece --ar 16:9 --stylize 250 --v 6
```
```

### DALL-E / GPT-Image 格式

```markdown
**AI 提示词**：

```
[画面描述]，[镜头角度]，[艺术风格]，电影级光影，高质量细节
```
```

## 各分镜密度模式的提示词策略

### 模式 A：对话多，镜头少

**特点**：每个镜头承载大量对话信息，提示词侧重**角色表情+对话氛围**。

**提示词模板**：
```markdown
**AI 提示词**：

正向：
```
masterpiece, best quality, [角色名] [表情/动作], [环境], cinematic lighting, manga style, detailed face, [对话氛围关键词]
```

反向：
```
worst quality, low quality, blurry, deformed, bad anatomy, extra limbs
```
```

**示例**：
```
**AI 提示词**：

正向：
```
masterpiece, best quality, 阿明 低头沉思, 教室窗外樱花飘落, cinematic lighting, manga style, detailed face, melancholic atmosphere
```

反向：
```
worst quality, low quality, blurry, deformed, bad anatomy, extra limbs
```
```

### 模式 B：一个对话对应一个镜头

**特点**：每个镜头独立，提示词侧重**单镜头叙事**。

**提示词模板**：
```markdown
**AI 提示词**：

正向：
```
masterpiece, best quality, [镜头类型], [画面描述], cinematic lighting, [艺术风格]
```

反向：
```
worst quality, low quality, blurry, deformed, bad anatomy, extra limbs
```
```

**示例**：
```
**AI 提示词**：

正向：
```
masterpiece, best quality, medium shot, 阿明转身看着小雨, 夕阳光晕笼罩, cinematic lighting, manga style
```

反向：
```
worst quality, low quality, blurry, deformed, bad anatomy, extra limbs
```
```

### 模式 C：一段对话多个镜头

**特点**：镜头数量多，提示词侧重**连续动作/表情分解**。

**提示词模板**：
```markdown
**AI 提示词**：

正向：
```
masterpiece, best quality, [镜头类型], [单动作/表情], cinematic lighting, manga style, [连续镜头序号]
```

反向：
```
worst quality, low quality, blurry, deformed, bad anatomy, extra limbs
```
```

**示例**：
```
**AI 提示词**：

正向：
```
masterpiece, best quality, close-up, 阿明眼神闪烁, cinematic lighting, manga style, shot 1 of 8
```

正向：
```
masterpiece, best quality, medium shot, 阿明转身, cinematic lighting, manga style, shot 2 of 8
```

正向：
```
masterpiece, best quality, close-up (小雨), 小雨脸颊微红, cinematic lighting, manga style, shot 3 of 8
```
```

## 艺术风格预设

根据故事类型自动推荐风格标签：

| 故事类型 | 推荐艺术风格 |
|----------|-------------|
| 校园恋爱 | manga style, shoujo manga, soft pastel colors |
| 科幻冒险 | sci-fi concept art, futuristic, neon lights |
| 悬疑推理 | dark noir, high contrast, dramatic shadows |
| 动作格斗 | dynamic angle, motion blur, action pose |
| 奇幻冒险 | fantasy illustration, epic scale, magical lighting |
| 日常治愈 | watercolor style, warm tones, cozy atmosphere |

## 角色一致性建议

在生成连续场景时，建议：

1. **固定角色描述词**：每个角色创建固定的描述词模板，在所有场景中复用
   ```
   阿明：black short hair, slim build, school uniform, sharp but gentle eyes
   小雨：shoulder-length ponytail, big eyes, dimples, white shirt + plaid skirt
   ```

2. **使用 LoRA/Embedding**：在 Stable Diffusion 中训练角色 LoRA，保持一致性

3. **参考图固定**：每次生成时使用相同的角色参考图

## 批量生成建议

对于模式 C（150-250场景），建议：

1. **按场次分组生成**：每 5-10 个场景为一组，保持上下文一致
2. **先关键帧后补间**：先生成转折点/情感高潮的关键镜头，再生成过渡镜头
3. **保持场景编号**：提示词中包含场景编号，方便后期排序
