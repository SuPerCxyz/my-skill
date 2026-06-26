# TMDB 接口

Use this file when querying TMDB, scoring candidates, or building image URLs. Keep API key handling aligned with [configuration.md](configuration.md) and safety output rules.

## API Key

- 优先读取环境变量 `TMDB_API_KEY`
- 其次读取 Skill 配置中的 `tmdb_api_key`
- 如果没有 API Key，则禁止直接调用 TMDB API
- API Key 不得写入日志、预览、NFO、映射文件或回滚脚本

## API URL(使用 append_to_response 减少请求次数)

```python
# 优先使用 TMDB 官方 API
# 详情接口使用 append_to_response 合并请求:

# movie:
#   /movie/{id}?language=zh-CN&append_to_response=credits,keywords,release_dates,images,external_ids

# tv:
#   /tv/{id}?language=zh-CN&append_to_response=credits,keywords,content_ratings,images,external_ids

# season:
#   /tv/{id}/season/{season_number}?language=zh-CN&append_to_response=credits,images,external_ids

# 搜索接口:
#   搜索剧集: https://api.themoviedb.org/3/search/tv?query={name}&language=zh-CN
#   搜索电影: https://api.themoviedb.org/3/search/movie?query={name}&language=zh-CN
#   图片配置: https://api.themoviedb.org/3/configuration
```

## 网页抓取(fallback)

网页抓取仅作为 fallback(API 缺失字段、图片页面特殊字段、用户明确要求时):

```
#   剧集: https://www.themoviedb.org/tv/{tmdb_id}?language=zh-CN
#   季:   https://www.themoviedb.org/tv/{tmdb_id}/season/{n}?language=zh-CN
#   电影: https://www.themoviedb.org/movie/{tmdb_id}?language=zh-CN
#   演员: https://www.themoviedb.org/tv/{tmdb_id}/cast?language=zh-CN
```

## 匹配置信度评分

```
- 标题完全匹配:+50
- 原标题完全匹配:+30
- 年份一致:+20
- 类型一致 movie/tv:+20
- 中文标题相似:+20
- 英文标题相似:+20
- 年份相差 1 年以内:+10
- 年份相差超过 2 年:-30
- 类型不一致:-40

最终分数:
- >=80:允许自动选择
- 60-79:必须让用户确认
- <60:视为未匹配
```

## 图片 URL 拼接

```python
# 不要硬编码完整 URL
# 使用 TMDB configuration 获取 base_url
# 格式: {base_url}{size}{file_path}
# base_url: https://image.tmdb.org/t/p/
# sizes:
#   poster: w342, w500, w780, original
#   backdrop: w300, w780, w1280, original
#   still: w185, w300, w500, original
#   logo: w92, w154, w185, w300, w500, original

TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/"

def get_image_url(file_path, size="original"):
    """拼接 TMDB 图片 URL"""
    return f"{TMDB_IMAGE_BASE}{size}{file_path}"

# 使用示例:
# poster_url = get_image_url("/yT4C02yo5MsPLB3damor8YncRvW.jpg", "original")
# still_url = get_image_url("/aAR0a7vvrMmYVmm5HneKHdS4tIB.jpg", "w500")
```
