---
name: slack-gif-creator
description: 创建Slack动画GIF，制作Slack表情动画
triggers: [Slack GIF, GIF动画, Slack表情, 动画表情, GIF制作]
---

# Slack GIF 制作

A toolkit providing utilities and knowledge for creating animated GIFs optimized for Slack.

## Slack Requirements

**Dimensions:**

- Emoji GIFs: 128x128 (recommended)
- Message GIFs: 480x480

**Parameters:**

- FPS: 10-30 (lower is smaller file size)
- Colors: 48-128 (fewer = smaller file size)
- Duration: Keep under 3 seconds for emoji GIFs

## Core Workflow

```python
from core.gif_builder import GIFBuilder
from PIL import Image, ImageDraw

# 1. Create builder
builder = GIFBuilder(width=128, height=128, fps=10)

# 2. Generate frames
for i in range(12):
    frame = Image.new('RGB', (128, 128), (240, 248, 255))
    draw = ImageDraw.Draw(frame)
    # Draw your animation using PIL primitives
    builder.add_frame(frame)

# 3. Save with optimization
builder.save('output.gif', num_colors=48, optimize_for_emoji=True)
```

## Animation Concepts

### Shake/Vibrate

- Use `math.sin()` or `math.cos()` with frame index
- Add small random variations for natural feel

### Pulse/Heartbeat

- Use `math.sin(t * frequency * 2 * math.pi)` for smooth pulse
- Scale between 0.8 and 1.2 of base size

### Bounce

- Use easing with `bounce_out` for landing
- Apply gravity by increasing y velocity each frame

### Spin/Rotate

- PIL: `image.rotate(angle, resample=Image.BICUBIC)`

### Fade In/Out

- Create RGBA image, adjust alpha channel
- Or use `Image.blend(image1, image2, alpha)`

### Slide

- Use easing with `ease_out` for smooth stop

## Available Utilities

### GIFBuilder (`core.gif_builder`)

Assembles frames and optimizes for Slack

### Validators (`core.validators`)

Check if GIF meets Slack requirements

### Easing Functions (`core.easing`)

Smooth motion instead of linear

### Frame Helpers (`core.frame_composer`)

Convenience functions for common needs

## Dependencies

```bash
pip install pillow imageio numpy
```
