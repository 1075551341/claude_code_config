---
name: image-generation
description: 使用 AI 生成图像。触发词：AI画图、图像生成、DALL-E、Stable Diffusion、AI绘画、图片生成、AI作图、AI绘图、Midjourney。
---

# AI 图像生成

## 支持的服务

### 1. DALL-E (OpenAI)

```python
from openai import OpenAI

client = OpenAI()

response = client.images.generate(
    model="dall-e-3",
    prompt="一只穿西装的猫在办公室工作，数字艺术风格",
    size="1024x1024",
    quality="standard",
    n=1,
)

image_url = response.data[0].url
```

### 2. Stable Diffusion

```python
import requests

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

def generate_image(prompt: str) -> bytes:
    response = requests.post(API_URL, headers=headers, json={
        "inputs": prompt,
    })
    return response.content

# 保存图像
image_data = generate_image("a beautiful sunset over mountains")
with open("output.png", "wb") as f:
    f.write(image_data)
```

### 3. Midjourney（通过 Discord API）

```python
# 需要第三方库
# pip install midjourney-api

from midjourney_api import Midjourney

mj = Midjourney(user_token="YOUR_TOKEN")
result = mj.imagine("futuristic city, cyberpunk style, highly detailed")
print(result.image_url)
```

### 4. Google Imagen (Gemini)

```python
import google.generativeai as genai

genai.configure(api_key="YOUR_API_KEY")

model = genai.GenerativeModel('imagen-3.0-generate-001')
response = model.generate_image(
    prompt="A serene Japanese garden with cherry blossoms",
    number_of_images=1,
)
```

## 提示词优化

### 结构化提示词

```
[主体] + [动作/场景] + [风格] + [技术参数]

示例：
主体：一只橙色的猫
场景：坐在窗台上看着外面的雨
风格：水彩画风格，温暖色调
技术：高度细节，柔和光线
```

### 风格关键词

```
# 艺术风格
油画风格：oil painting, thick brushstrokes, impasto
水彩风格：watercolor, soft edges, flowing colors
动漫风格：anime style, cel shading, vibrant colors
赛博朋克：cyberpunk, neon lights, futuristic
像素艺术：pixel art, 8-bit, retro game style

# 视角
特写：close-up, macro shot
远景：wide shot, landscape
俯视：aerial view, bird's eye view
平视：eye level, straight on

# 光线
自然光：natural lighting, soft daylight
电影光：cinematic lighting, dramatic shadows
逆光：backlight, rim lighting
黄金时段：golden hour, warm tones
```

### 质量关键词

```
高质量：high quality, highly detailed, 4k, 8k
专业：professional photography, award winning
清晰：sharp focus, crystal clear
细节：intricate details, fine details
```

### 负面提示词（排除不想要的）

```
# Stable Diffusion 负面提示词示例
negative_prompt = """
low quality, blurry, pixelated,
watermark, signature, text, logo,
deformed, ugly, bad anatomy,
extra limbs, missing limbs,
"""
```

## 尺寸规格

### DALL-E 3

```
1024x1024  - 正方形
1792x1024  - 横向
1024x1792  - 纵向
```

### Stable Diffusion XL

```
1024x1024  - 默认
512x512    - 快速生成
2048x2048  - 高分辨率（需更多显存）
```

## 完整示例

```python
from openai import OpenAI
import httpx
import os

def generate_and_save(
    prompt: str,
    output_path: str = "generated_image.png",
    style: str = "vivid",
    size: str = "1024x1024"
) -> str:
    """
    生成图像并保存到本地

    参数:
        prompt: 图像描述
        output_path: 保存路径
        style: "vivid" 或 "natural"
        size: 图像尺寸

    返回:
        保存的文件路径
    """
    client = OpenAI()

    # 生成图像
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        quality="standard",
        style=style,
        n=1,
    )

    image_url = response.data[0].url
    revised_prompt = response.data[0].revised_prompt  # 优化后的提示词

    print(f"原始提示词: {prompt}")
    print(f"优化提示词: {revised_prompt}")

    # 下载图像
    image_data = httpx.get(image_url).content

    # 保存
    with open(output_path, "wb") as f:
        f.write(image_data)

    return output_path

# 使用
generate_and_save(
    prompt="A modern minimalist logo for a tech startup, blue and white colors",
    output_path="logo.png"
)
```

## 图像编辑

### Inpainting（局部重绘）

```python
# Stable Diffusion Inpainting
response = client.image.edit(
    image=open("original.png", "rb"),
    mask=open("mask.png", "rb"),  # 白色区域会被重绘
    prompt="A cat instead of dog",
    size="1024x1024"
)
```

### 图像变体

```python
# 基于现有图像生成变体
response = client.images.create_variation(
    image=open("original.png", "rb"),
    n=3,  # 生成3个变体
    size="1024x1024"
)
```

## 注意事项

1. **内容政策**：遵守各平台的 AI 生成内容政策
2. **版权**：AI 生成图像的版权归属因地区而异
3. **水印**：部分服务会添加隐形水印
4. **费用**：注意 API 调用费用
5. **存储**：图像 URL 通常有时效限制，需及时下载
