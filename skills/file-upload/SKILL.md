# 文件上传处理

## 描述
文件上传全链路方案，涵盖分片上传、OSS 直传、本地存储、图片压缩/裁剪等。

## 触发条件
当用户提到：文件上传、分片上传、断点续传、OSS、S3、MinIO、Multer、图片处理、缩略图、文件校验、大文件上传、multipart 时使用此技能。

## 方案选型

| 场景 | 推荐方案 | 适用范围 |
|------|----------|----------|
| 小文件（<10MB） | Multer / python-multipart | 表单直传 |
| 大文件（>100MB） | 分片上传 + 断点续传 | 视频/大型文件 |
| 云存储 | AWS S3 / 阿里云 OSS 预签名 URL | 生产环境标配 |
| 本地开发 | 本地磁盘 + 静态服务 | 开发/小项目 |
| 图片处理 | Sharp / Pillow | 压缩、裁剪、水印 |

## 核心代码示例

### TypeScript - Multer + Sharp 图片上传
```typescript
import multer from 'multer';
import sharp from 'sharp';
import path from 'path';
import crypto from 'crypto';

const storage = multer.memoryStorage();

const upload = multer({
  storage,
  limits: { fileSize: 10 * 1024 * 1024 },
  fileFilter: (_req, file, cb) => {
    const allowed = /^image\/(jpeg|png|webp|gif)$/;
    cb(null, allowed.test(file.mimetype));
  },
});

/**
 * @描述 图片上传处理：压缩 + 生成缩略图
 * @参数 buffer - 原始文件 Buffer
 * @返回 { original, thumbnail } 存储路径
 */
async function processImage(buffer: Buffer, destDir: string) {
  const hash = crypto.randomBytes(8).toString('hex');
  const filename = `${Date.now()}-${hash}.webp`;

  const originalPath = path.join(destDir, filename);
  await sharp(buffer).webp({ quality: 80 }).toFile(originalPath);

  const thumbPath = path.join(destDir, `thumb-${filename}`);
  await sharp(buffer).resize(200, 200, { fit: 'cover' }).webp({ quality: 60 }).toFile(thumbPath);

  return { original: originalPath, thumbnail: thumbPath };
}

// Express 路由
app.post('/upload/image', upload.single('file'), async (req, res) => {
  if (!req.file) return res.status(400).json({ code: 1, msg: '缺少文件' });
  const result = await processImage(req.file.buffer, './uploads');
  res.json({ code: 0, msg: 'ok', data: result });
});
```

### TypeScript - S3 预签名 URL 直传
```typescript
import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';

const s3 = new S3Client({ region: process.env.AWS_REGION });

async function getUploadUrl(filename: string, contentType: string) {
  const key = `uploads/${Date.now()}/${filename}`;
  const command = new PutObjectCommand({
    Bucket: process.env.S3_BUCKET,
    Key: key,
    ContentType: contentType,
  });
  const url = await getSignedUrl(s3, command, { expiresIn: 600 });
  return { uploadUrl: url, fileKey: key };
}
```

### Python - FastAPI 分片上传
```python
import os, hashlib, aiofiles
from fastapi import UploadFile, APIRouter

router = APIRouter()
UPLOAD_DIR = "./uploads/chunks"

@router.post("/upload/chunk")
async def upload_chunk(
    file: UploadFile,
    chunk_index: int,
    total_chunks: int,
    file_hash: str,
):
    """
    描述：分片上传接口，支持断点续传
    参数：
        chunk_index: 当前分片索引
        total_chunks: 总分片数
        file_hash: 文件 MD5 用于合并校验
    """
    chunk_dir = os.path.join(UPLOAD_DIR, file_hash)
    os.makedirs(chunk_dir, exist_ok=True)

    chunk_path = os.path.join(chunk_dir, f"{chunk_index:04d}")
    async with aiofiles.open(chunk_path, "wb") as f:
        await f.write(await file.read())

    uploaded = len(os.listdir(chunk_dir))
    if uploaded == total_chunks:
        final_path = os.path.join("./uploads", f"{file_hash}_{file.filename}")
        async with aiofiles.open(final_path, "wb") as out:
            for i in range(total_chunks):
                async with aiofiles.open(os.path.join(chunk_dir, f"{i:04d}"), "rb") as chunk:
                    await out.write(await chunk.read())
        return {"code": 0, "msg": "合并完成", "data": {"path": final_path}}

    return {"code": 0, "msg": f"已上传 {uploaded}/{total_chunks}"}
```

## 最佳实践

1. **安全校验** → 服务端校验 MIME type + 文件头魔数，不信任前端扩展名
2. **文件名** → 随机哈希命名，禁止使用原始文件名（防路径穿越）
3. **大小限制** → Nginx/网关层 + 应用层双重限制
4. **分片策略** → 单片 2-5MB，并发 3-6 片，支持重试
5. **清理机制** → 定期清理未合并的分片和临时文件
6. **CDN 加速** → 上传完成后回源 CDN，返回 CDN URL
7. **病毒扫描** → 生产环境对上传文件做安全扫描
