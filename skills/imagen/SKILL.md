---
name: imagen
description: 使用 Google Imagen 或其他 AI 图像生成模型创建、编辑、处理图像。触发词：AI画图、图像生成、Imagen、AI绘画、图片生成、AI作图、AI绘图、图像合成、图片编辑。
---

# AI 图像生成

## 核心能力

**图像生成、编辑、风格迁移、智能处理。**

## 适用场景

- 根据文本描述生成图像
- 图像风格转换
- 图像编辑与修复
- 批量图像处理

## Imagen API 使用

### 基础图像生成

```python
import requests
import base64
from PIL import Image
from io import BytesIO

# Google Vertex AI Imagen
PROJECT_ID = "your-project-id"
LOCATION = "us-central1"

def generate_image(prompt, model="imagen-3.0-generate-001"):
    """使用 Imagen 生成图像"""

    url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{model}:predict"

    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "1:1",
            "safetyFilterLevel": "block_some",
            "personGeneration": "allow_adult"
        }
    }

    response = requests.post(url, json=payload, headers={
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json"
    })

    result = response.json()
    image_data = base64.b64decode(result["predictions"][0]["bytesBase64Encoded"])
    image = Image.open(BytesIO(image_data))
    return image

# 使用示例
image = generate_image("一只穿西装的猫在办公室里使用电脑，写实风格")
image.save("business_cat.png")
```

### 图像编辑

```python
def edit_image(image_path, edit_prompt, mask_path=None):
    """编辑现有图像"""
    with open(image_path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode()

    mask_base64 = None
    if mask_path:
        with open(mask_path, "rb") as f:
            mask_base64 = base64.b64encode(f.read()).decode()

    payload = {
        "instances": [{
            "prompt": edit_prompt,
            "image": {"bytesBase64Encoded": image_base64},
        }],
        "parameters": {
            "sampleCount": 1,
            "editMode": "inpainting"
        }
    }

    if mask_base64:
        payload["instances"][0]["mask"] = {"bytesBase64Encoded": mask_base64}

    return call_imagen_api(payload)
```

## 提示词工程

### 结构化提示词

```
[主体] + [动作/场景] + [风格] + [光线] + [构图]

示例：
"一只橘猫穿着宇航服在月球表面行走，写实风格高细节，自然光照，低角度拍摄构图"
```

### 最佳实践

- 使用具体描述（"一只金色的金毛犬"而非"一只狗"）
- 指定艺术风格（"数字艺术、油画、3D渲染"）
- 包含光线信息（"柔和的自然光、黄金时刻"）

## 注意事项

- 遵守使用条款和版权规定
- 添加水印或标注 AI 生成
- 检查安全过滤结果
- 合理控制请求频率
