"""Unsplash图片服务 —— 全项目唯一的"真·HTTP直调"外部服务

【使命】给景点找配图。教材13.4.4 特意说明：图片搜索不需要AI决策，
所以它没做成工具/MCP，就是普通的 requests.get——"按需选通道"的正面教材。
"""

import requests
from typing import List, Optional
from ..config import get_settings

class UnsplashService:
    """Unsplash图片服务类 —— 景点配图采购员

    【干什么用】拿关键词(如"故宫 北京")去 Unsplash 图库搜图，把图片URL填进行程。
    【类比】公司里负责配图的运营：接需求→去免费图库搜→贴链接。
    你的 .env 没配 Unsplash Key，所以这位采购员目前每次都空手而归——景点无图，但功能照常。
    """
    
    def __init__(self):
        """初始化服务"""
        settings = get_settings()
        self.access_key = settings.unsplash_access_key
        self.base_url = "https://api.unsplash.com"
    
    def search_photos(self, query: str, per_page: int = 5) -> List[dict]:
        """搜索图片 —— 去图库按关键词搜，整理成统一格式的字典列表

        【干什么用】组装带 client_id(你的AccessKey) 的请求 → 把结果抽成
        {url, thumb, description, photographer}；任何异常都返回[]，绝不抛出。
        【类比】搜索引擎搜图后只登记"图链+说明+作者"进表格——
        失败(断网/没Key)就交一张空表，不让配图这种小事拖垮行程主流程。

        Args:
        
        Args:
            query: 搜索关键词
            per_page: 每页数量
            
        Returns:
            图片列表
        """
        try:
            url = f"{self.base_url}/search/photos"
            params = {
                "query": query,
                "per_page": per_page,
                "client_id": self.access_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            # 提取图片URL
            photos = []
            for photo in results:
                photos.append({
                    "id": photo.get("id"),
                    "url": photo.get("urls", {}).get("regular"),
                    "thumb": photo.get("urls", {}).get("thumb"),
                    "description": photo.get("description") or photo.get("alt_description"),
                    "photographer": photo.get("user", {}).get("name")
                })
            
            return photos
            
        except Exception as e:
            print(f"❌ Unsplash搜索失败: {str(e)}")
            return []
    
    def get_photo_url(self, query: str) -> Optional[str]:
        """获取单张图片URL —— search_photos 的"只要一张"简化版，行程API实际调用的就是它

        Args:

        Args:
            query: 搜索关键词

        Returns:
            图片URL
        """
        photos = self.search_photos(query, per_page=1)
        if photos:
            return photos[0].get("url")
        return None


# 全局服务实例
_unsplash_service = None


def get_unsplash_service() -> UnsplashService:
    """获取Unsplash服务实例(单例模式) —— 第6个手写单例闸门，同一个套路刷满全场"""
    global _unsplash_service
    
    if _unsplash_service is None:
        _unsplash_service = UnsplashService()
    
    return _unsplash_service

