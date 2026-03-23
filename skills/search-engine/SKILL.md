# 搜索实现

## 描述
全文搜索与搜索引擎集成方案，涵盖 Elasticsearch、MeiliSearch、数据库全文搜索等。

## 触发条件
当用户提到：搜索、全文搜索、Elasticsearch、MeiliSearch、Algolia、搜索引擎、模糊搜索、分词、搜索建议、搜索高亮、倒排索引、LIKE 查询优化 时使用此技能。

## 方案选型

| 场景 | 推荐方案 | 适用范围 |
|------|----------|----------|
| 轻量搜索（<10 万条） | PostgreSQL 全文搜索 | 小数据量、不加新依赖 |
| 中等规模即开即用 | MeiliSearch | 10 万-千万级，部署简单 |
| 大规模/复杂查询 | Elasticsearch | 千万级+，聚合分析 |
| 前端即时搜索 | Fuse.js / FlexSearch | 纯前端、数据量小 |
| 托管服务 | Algolia / Typesense Cloud | 免运维 |

## 核心代码示例

### TypeScript - MeiliSearch 集成
```typescript
import { MeiliSearch } from 'meilisearch';

const client = new MeiliSearch({
  host: process.env.MEILI_HOST || 'http://localhost:7700',
  apiKey: process.env.MEILI_API_KEY,
});

/**
 * @描述 初始化搜索索引，配置可搜索/过滤/排序字段
 */
async function setupIndex() {
  const index = client.index('products');
  await index.updateSettings({
    searchableAttributes: ['name', 'description', 'tags'],
    filterableAttributes: ['category', 'price', 'inStock'],
    sortableAttributes: ['price', 'createdAt'],
    rankingRules: ['words', 'typo', 'proximity', 'attribute', 'sort', 'exactness'],
  });
}

// 搜索接口
async function searchProducts(query: string, options?: {
  category?: string;
  minPrice?: number;
  maxPrice?: number;
  page?: number;
  limit?: number;
}) {
  const { category, minPrice, maxPrice, page = 1, limit = 20 } = options || {};
  const filters: string[] = [];
  if (category) filters.push(`category = "${category}"`);
  if (minPrice !== undefined) filters.push(`price >= ${minPrice}`);
  if (maxPrice !== undefined) filters.push(`price <= ${maxPrice}`);

  return client.index('products').search(query, {
    filter: filters.length > 0 ? filters.join(' AND ') : undefined,
    limit,
    offset: (page - 1) * limit,
    attributesToHighlight: ['name', 'description'],
    highlightPreTag: '<mark>',
    highlightPostTag: '</mark>',
  });
}

// 数据同步
async function syncToIndex(products: Product[]) {
  await client.index('products').addDocuments(products, { primaryKey: 'id' });
}
```

### Python - Elasticsearch 集成
```python
from elasticsearch import AsyncElasticsearch

es = AsyncElasticsearch(hosts=[{"host": "localhost", "port": 9200}])

async def create_index():
    """描述：创建搜索索引，配置中文分词"""
    await es.indices.create(index="articles", body={
        "settings": {"analysis": {"analyzer": {"default": {"type": "ik_max_word"}}}},
        "mappings": {
            "properties": {
                "title": {"type": "text", "analyzer": "ik_max_word"},
                "content": {"type": "text", "analyzer": "ik_smart"},
                "author": {"type": "keyword"},
                "created_at": {"type": "date"},
                "tags": {"type": "keyword"},
            }
        }
    })

async def search_articles(query: str, page: int = 1, size: int = 20) -> dict:
    """
    描述：多字段搜索 + 高亮 + 分页
    参数：
        query: 搜索关键词
        page: 页码
        size: 每页条数
    返回：搜索结果列表
    """
    body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["title^3", "content", "tags^2"],
                "type": "best_fields",
                "fuzziness": "AUTO",
            }
        },
        "highlight": {
            "fields": {"title": {}, "content": {"fragment_size": 150}},
            "pre_tags": ["<mark>"],
            "post_tags": ["</mark>"],
        },
        "from": (page - 1) * size,
        "size": size,
    }
    result = await es.search(index="articles", body=body)
    return {
        "total": result["hits"]["total"]["value"],
        "items": [
            {**hit["_source"], "highlight": hit.get("highlight", {})}
            for hit in result["hits"]["hits"]
        ],
    }
```

### PostgreSQL 全文搜索（轻量方案）
```sql
-- 添加全文搜索向量列
ALTER TABLE articles ADD COLUMN search_vector tsvector;
UPDATE articles SET search_vector = to_tsvector('chinese', coalesce(title,'') || ' ' || coalesce(content,''));
CREATE INDEX idx_articles_search ON articles USING GIN(search_vector);

-- 搜索查询
SELECT id, title, ts_headline('chinese', content, query) AS snippet,
       ts_rank(search_vector, query) AS rank
FROM articles, to_tsquery('chinese', '关键词') query
WHERE search_vector @@ query
ORDER BY rank DESC LIMIT 20;
```

## 最佳实践

1. **渐进选型** → 先用 DB 全文搜索，数据量增长后迁移到专用搜索引擎
2. **数据同步** → 写入 DB 后异步同步搜索引擎（消息队列/CDC）
3. **分词** → 中文搜索必须配置中文分词器（IK / jieba）
4. **权重** → 标题权重 > 标签权重 > 正文权重
5. **防抖** → 前端搜索框输入防抖 300ms，减少无效请求
6. **搜索建议** → 搜索词补全 + 拼音纠错提升体验
7. **监控** → 记录搜索词和点击率，优化排序和同义词
