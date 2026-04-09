---
name: image-enhancement
description: 当需要增强图片质量、修复模糊图片、提升图片分辨率、优化图片效果时调用此技能。触发词：图片增强、图像增强、图片修复、提升画质、图片放大、超分辨率、图片优化。
---

# 图片增强

## 核心能力

**图片质量增强、分辨率提升、图像修复优化。**

---

## 适用场景

- 图片质量提升
- 低分辨率图片放大
- 模糊图片修复
- 图片效果优化

---

## 常用工具

### AI增强工具

```markdown
在线工具：
- waifu2x.udp.jp - 动漫图片放大
- bigjpg.com - AI图片放大
- letsenhance.io - 图片增强
- upscayl.org - 开源AI放大（桌面应用）

桌面软件：
- Topaz Gigapixel AI - 专业放大
- Adobe Photoshop - 智能放大
- Upscayl - 免费开源
- waifu2x - 动漫专用

命令行工具：
- Real-ESRGAN - 通用超分辨率
- waifu2x-ncnn-vulkan - 动漫图片
- ESRGAN - 通用增强
```

### Python库

```bash
# 安装依赖
pip install opencv-python pillow numpy
pip install basicsr  # 超分辨率
pip install realesrgan  # Real-ESRGAN
```

---

## 图片放大

### OpenCV放大

```python
import cv2
import numpy as np

def upscale_image(image_path, scale=2, method='lanczos'):
    """
    图片放大

    参数：
        image_path: 图片路径
        scale: 放大倍数
        method: 插值方法

    返回：
        numpy.ndarray: 放大后的图片
    """
    img = cv2.imread(image_path)

    methods = {
        'nearest': cv2.INTER_NEAREST,
        'bilinear': cv2.INTER_LINEAR,
        'bicubic': cv2.INTER_CUBIC,
        'lanczos': cv2.INTER_LANCZOS4
    }

    interpolation = methods.get(method, cv2.INTER_LANCZOS4)

    height, width = img.shape[:2]
    new_size = (width * scale, height * scale)

    upscaled = cv2.resize(img, new_size, interpolation=interpolation)

    return upscaled

# 使用
result = upscale_image('input.jpg', scale=2, method='lanczos')
cv2.imwrite('output.jpg', result)
```

### Real-ESRGAN增强

```python
import cv2
from realesrgan import RealESRGANer
from basicsr.archs.rrdbnet import RRDBNet

def ai_upscale(image_path, output_path, scale=4):
    """
    使用Real-ESRGAN进行AI放大

    参数：
        image_path: 输入图片路径
        output_path: 输出图片路径
        scale: 放大倍数 (2, 4, 8)
    """
    # 初始化模型
    model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64,
                    num_block=23, num_grow_ch=32, scale=scale)

    upsampler = RealESRGANer(
        scale=scale,
        model_path=f'resources/RealESRGAN_x{scale}plus.pth',
        model=model,
        tile=0,
        tile_pad=10,
        pre_pad=0,
        half=False
    )

    # 读取并处理图片
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    output, _ = upsampler.enhance(img, outscale=scale)

    cv2.imwrite(output_path, output)

# 使用
ai_upscale('low_res.jpg', 'high_res.jpg', scale=4)
```

---

## 图片修复

### 去噪处理

```python
import cv2
import numpy as np

def denoise_image(image_path, strength=10):
    """
    图片去噪

    参数：
        image_path: 图片路径
        strength: 去噪强度 (1-20)

    返回：
        numpy.ndarray: 去噪后的图片
    """
    img = cv2.imread(image_path)

    # 非局部均值去噪
    denoised = cv2.fastNlMeansDenoisingColored(
        img, None, strength, strength, 7, 21
    )

    return denoised

def denoise_preserve_edges(image_path, h=10):
    """
    保边去噪

    参数：
        image_path: 图片路径
        h: 滤波强度
    """
    img = cv2.imread(image_path)

    # 双边滤波（保边去噪）
    denoised = cv2.bilateralFilter(img, 9, 75, 75)

    return denoised
```

### 锐化处理

```python
def sharpen_image(image_path, amount=1.0):
    """
    图片锐化

    参数：
        image_path: 图片路径
        amount: 锐化强度

    返回：
        numpy.ndarray: 锐化后的图片
    """
    img = cv2.imread(image_path)

    # 高斯模糊
    blurred = cv2.GaussianBlur(img, (0, 0), 3)

    # USM锐化
    sharpened = cv2.addWeighted(img, 1.0 + amount, blurred, -amount, 0)

    return sharpened

def unsharp_mask(image_path, sigma=1.0, strength=1.5):
    """
    USM锐化（Unsharp Mask）

    参数：
        image_path: 图片路径
        sigma: 高斯模糊参数
        strength: 锐化强度
    """
    import PIL.Image as Image
    from PIL import ImageFilter

    img = Image.open(image_path)

    # 创建模糊版本
    blurred = img.filter(ImageFilter.GaussianBlur(radius=sigma))

    # 锐化 = 原图 + 强度 × (原图 - 模糊)
    sharpened = Image.blend(img, blurred, 1.0 - strength)

    return sharpened
```

### 模糊修复

```python
def deblur_image(image_path, iterations=10):
    """
    简单去模糊（Richardson-Lucy算法）

    参数：
        image_path: 图片路径
        iterations: 迭代次数
    """
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # 估计模糊核（这里使用简单的高斯模糊核）
    psf = np.ones((5, 5)) / 25

    # 傅里叶变换
    img_fft = np.fft.fft2(img)
    psf_fft = np.fft.fft2(psf, s=img.shape)

    # Richardson-Lucy迭代
    result = img.copy().astype(float)
    for _ in range(iterations):
        conv = np.real(np.fft.ifft2(psf_fft * np.fft.fft2(result)))
        relative_blur = img / (conv + 1e-10)
        result = result * np.real(np.fft.ifft2(np.conj(psf_fft) * np.fft.fft2(relative_blur)))

    return result.astype(np.uint8)
```

---

## 图片增强

### 对比度增强

```python
import cv2
import numpy as np

def enhance_contrast(image_path, method='clahe'):
    """
    对比度增强

    参数：
        image_path: 图片路径
        method: 增强方法 (clahe, histogram, adaptive)

    返回：
        numpy.ndarray: 增强后的图片
    """
    img = cv2.imread(image_path)

    if method == 'clahe':
        # CLAHE（限制对比度自适应直方图均衡化）
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

    elif method == 'histogram':
        # 直方图均衡化
        img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
        img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
        enhanced = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)

    elif method == 'adaptive':
        # 自适应直方图均衡化
        enhanced = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        enhanced = cv2.equalizeHist(enhanced)
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)

    return enhanced
```

### 色彩增强

```python
def enhance_colors(image_path, saturation=1.2, brightness=1.1):
    """
    色彩增强

    参数：
        image_path: 图片路径
        saturation: 饱和度倍数
        brightness: 亮度倍数
    """
    import PIL.Image as Image
    from PIL import ImageEnhance

    img = Image.open(image_path)

    # 饱和度增强
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(saturation)

    # 亮度增强
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(brightness)

    return img
```

### 综合增强

```python
def auto_enhance(image_path, output_path):
    """
    自动图片增强

    包含：去噪、锐化、对比度增强、色彩增强
    """
    import cv2

    # 读取图片
    img = cv2.imread(image_path)

    # 1. 去噪
    denoised = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)

    # 2. 锐化
    kernel = np.array([[-1, -1, -1],
                       [-1,  9, -1],
                       [-1, -1, -1]])
    sharpened = cv2.filter2D(denoised, -1, kernel)

    # 3. CLAHE对比度增强
    lab = cv2.cvtColor(sharpened, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    enhanced = cv2.merge([l, a, b])
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

    # 保存结果
    cv2.imwrite(output_path, enhanced)

    return enhanced
```

---

## 批量处理

```python
import os
from pathlib import Path

def batch_enhance(input_dir, output_dir, scale=2):
    """
    批量增强图片

    参数：
        input_dir: 输入目录
        output_dir: 输出目录
        scale: 放大倍数
    """
    os.makedirs(output_dir, exist_ok=True)

    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}

    for file_path in Path(input_dir).iterdir():
        if file_path.suffix.lower() not in image_extensions:
            continue

        output_path = Path(output_dir) / file_path.name

        try:
            # 使用AI放大
            ai_upscale(str(file_path), str(output_path), scale)
            print(f"✓ {file_path.name}")
        except Exception as e:
            print(f"✗ {file_path.name}: {e}")
```

---

## 命令行工具

### ImageMagick

```bash
# 放大图片
magick input.jpg -resize 200% output.jpg

# 锐化
magick input.jpg -sharpen 0x1 output.jpg

# 对比度增强
magick input.jpg -contrast-stretch 0%x0% output.jpg

# 自动增强
magick input.jpg -auto-level -auto-gamma output.jpg

# 降噪
magick input.jpg -noise 5 output.jpg
```

### FFmpeg（视频帧）

```bash
# 从视频提取帧并增强
ffmpeg -i input.mp4 -vf "hqdn3d=4:3:6:4.5" -qscale:v 2 output_%04d.jpg

# 视频放大
ffmpeg -i input.mp4 -vf "scale=iw*2:ih*2:flags=lanczos" output.mp4
```

---

## 注意事项

```
建议：
- 保留原始图片备份
- 根据图片类型选择方法
- 适度增强避免过度处理
- 批量处理前先测试单张

避免：
- 多次重复放大
- 过度锐化产生伪影
- 忽略原始图片质量限制
- 放大低质量截图期望过高
```

---

## 相关技能

- `video-processing` - 视频处理
- `canvas-design` - 设计创作
- `file-organization` - 文件整理