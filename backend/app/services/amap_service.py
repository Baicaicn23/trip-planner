"""高德地图MCP服务封装 —— 双通道供应商接线板

【使命】全项目所有"查高德"的需求都从这条线走，但有两种按法：
  Agent通道——LLM自己生成[TOOL_CALL]（车间主任那边的用法，经过AI决策）；
  程序通道——路由代码直接指定工具名点菜（本文件AmapService的用法，不经过AI）。
两者共享同一个MCP服务器进程（单例），省资源好限流。
【易错点】本文件并不是"绕过MCP直调高德HTTP"，而是"绕过LLM直调MCP"——
高德的HTTP请求永远由 amap-mcp-server 代发，我们只是不让LLM参与决策。
"""

from typing import List, Dict, Any, Optional
from hello_agents.tools import MCPTool
from ..config import get_settings
from ..models.schemas import Location, POIInfo, WeatherInfo

# 全局MCP工具实例
_amap_mcp_tool = None


def get_amap_mcp_tool() -> MCPTool:
    """获取高德地图MCP工具实例(单例模式) —— 全项目唯一的一部"电话总机"

    【干什么用】首次调用时启动 uvx amap-mcp-server 子进程、把高德Key以环境变量
    AMAP_MAPS_API_KEY 转交给它，auto_expand=True 自动问服务器要全部工具清单(16个)。
    之后全项目任何"查高德"都复用这条连接，谁也不许另办电话。
    【类比】公司只办一条供应商专线：开通时登记账号(你的Key)、拿到服务目录(16个工具)，
    各部门(Agent和路由)共用——这就是教材13.4.3"共享MCP实例"的落地。

    Returns:
    
    Returns:
        MCPTool实例
    """
    global _amap_mcp_tool
    
    if _amap_mcp_tool is None:
        settings = get_settings()
        
        if not settings.amap_api_key:
            raise ValueError("高德地图API Key未配置,请在.env文件中设置AMAP_API_KEY")
        
        # 创建MCP工具
        _amap_mcp_tool = MCPTool(
            name="amap",
            description="高德地图服务,支持POI搜索、路线规划、天气查询等功能",
            server_command=["uvx", "amap-mcp-server"],
            env={"AMAP_MAPS_API_KEY": settings.amap_api_key},
            auto_expand=True  # 自动展开为独立工具
        )
        
        print(f"✅ 高德地图MCP工具初始化成功")
        print(f"   工具数量: {len(_amap_mcp_tool._available_tools)}")
        
        # 打印可用工具列表
        if _amap_mcp_tool._available_tools:
            print("   可用工具:")
            for tool in _amap_mcp_tool._available_tools[:5]:  # 只打印前5个
                print(f"     - {tool.get('name', 'unknown')}")
            if len(_amap_mcp_tool._available_tools) > 5:
                print(f"     ... 还有 {len(_amap_mcp_tool._available_tools) - 5} 个工具")
    
    return _amap_mcp_tool


class AmapService:
    """高德地图服务封装类 —— 给"程序"用的自助点菜窗口

    【干什么用】把MCPTool的原始调用包装成 search_poi()/get_weather() 这样的人话方法，
    给 poi.py/map.py 路由用——代码直接指定工具名，不劳烦LLM决策。
    【类比】供应商官网的"自助下单页"：不用打电话(Agent)问客服推荐，
    照服务目录按单号下单——快、稳、100%确定，适合不需要动脑的固定查询。
    """
    
    def __init__(self):
        """初始化服务"""
        self.mcp_tool = get_amap_mcp_tool()
    
    def search_poi(self, keywords: str, city: str, citylimit: bool = True) -> List[POIInfo]:
        """搜索POI —— 程序版地图搜索（⚠️半成品）

        【干什么用】直接指定 maps_text_search 工具查高德——和景点专员用的是同一个工具，
        区别只是参数由代码写死，没有LLM参与。
        【类比】同一家供应商：Agent通道是打电话让客服推荐，这里是照菜单报菜名。
        ⚠️诚实提示：下面的 TODO 说明本方法只打印不解析、实际返回[]——
        教材配套代码也有未完成的部分，第⑥站联调会验证到。

        Args:
        
        Args:
            keywords: 搜索关键词
            city: 城市
            citylimit: 是否限制在城市范围内
            
        Returns:
            POI信息列表
        """
        try:
            # 调用MCP工具
            result = self.mcp_tool.run({
                "action": "call_tool",
                "tool_name": "maps_text_search",
                "arguments": {
                    "keywords": keywords,
                    "city": city,
                    "citylimit": str(citylimit).lower()
                }
            })
            
            # 解析结果
            # 注意: MCP工具返回的是字符串,需要解析
            # 这里简化处理,实际应该解析JSON
            print(f"POI搜索结果: {result[:200]}...")  # 打印前200字符
            
            # TODO: 解析实际的POI数据
            return []
            
        except Exception as e:
            print(f"❌ POI搜索失败: {str(e)}")
            return []
    
    def get_weather(self, city: str) -> List[WeatherInfo]:
        """查询天气 —— 程序版天气查询（⚠️半成品：TODO未解析，返回[]）

        Args:
        
        Args:
            city: 城市名称
            
        Returns:
            天气信息列表
        """
        try:
            # 调用MCP工具
            result = self.mcp_tool.run({
                "action": "call_tool",
                "tool_name": "maps_weather",
                "arguments": {
                    "city": city
                }
            })
            
            print(f"天气查询结果: {result[:200]}...")
            
            # TODO: 解析实际的天气数据
            return []
            
        except Exception as e:
            print(f"❌ 天气查询失败: {str(e)}")
            return []
    
    def plan_route(
        self,
        origin_address: str,
        destination_address: str,
        origin_city: Optional[str] = None,
        destination_city: Optional[str] = None,
        route_type: str = "walking"
    ) -> Dict[str, Any]:
        """规划路线 —— 按出行方式映射工具：walking/driving/transit三选一（⚠️半成品返回{}）

        Args:
        
        Args:
            origin_address: 起点地址
            destination_address: 终点地址
            origin_city: 起点城市
            destination_city: 终点城市
            route_type: 路线类型 (walking/driving/transit)
            
        Returns:
            路线信息
        """
        try:
            # 根据路线类型选择工具
            tool_map = {
                "walking": "maps_direction_walking_by_address",
                "driving": "maps_direction_driving_by_address",
                "transit": "maps_direction_transit_integrated_by_address"
            }
            
            tool_name = tool_map.get(route_type, "maps_direction_walking_by_address")
            
            # 构建参数
            arguments = {
                "origin_address": origin_address,
                "destination_address": destination_address
            }
            
            # 公共交通需要城市参数
            if route_type == "transit":
                if origin_city:
                    arguments["origin_city"] = origin_city
                if destination_city:
                    arguments["destination_city"] = destination_city
            else:
                # 其他路线类型也可以提供城市参数提高准确性
                if origin_city:
                    arguments["origin_city"] = origin_city
                if destination_city:
                    arguments["destination_city"] = destination_city
            
            # 调用MCP工具
            result = self.mcp_tool.run({
                "action": "call_tool",
                "tool_name": tool_name,
                "arguments": arguments
            })
            
            print(f"路线规划结果: {result[:200]}...")
            
            # TODO: 解析实际的路线数据
            return {}
            
        except Exception as e:
            print(f"❌ 路线规划失败: {str(e)}")
            return {}
    
    def geocode(self, address: str, city: Optional[str] = None) -> Optional[Location]:
        """地理编码(地址转坐标) —— 把"景山前街4号"这种地址变成经纬度坐标（⚠️半成品返回None）

        【干什么用】地址→坐标的翻译器：地图插旗、算距离都得先有经纬度。
        【类比】像快递员把"xx路xx号"翻译成GPS定位点——没有坐标，导航没法开始。

        Args:
            address: 地址
            city: 城市

        Returns:
            经纬度坐标
        """
        try:
            arguments = {"address": address}
            if city:
                arguments["city"] = city

            result = self.mcp_tool.run({
                "action": "call_tool",
                "tool_name": "maps_geo",
                "arguments": arguments
            })

            print(f"地理编码结果: {result[:200]}...")

            # TODO: 解析实际的坐标数据
            return None

        except Exception as e:
            print(f"❌ 地理编码失败: {str(e)}")
            return None

    def get_poi_detail(self, poi_id: str) -> Dict[str, Any]:
        """获取POI详情 —— 五个方法里唯一真正解析了结果的：正则抠出JSON返回

        【干什么用】凭高德给地点发的编号(poi_id)查详情：营业时间/图片/评分等。
        【类比】像凭取件码开快递柜——编号对得上才给你打开柜门。

        Args:

        Args:
            poi_id: POI ID

        Returns:
            POI详情信息
        """
        try:
            result = self.mcp_tool.run({
                "action": "call_tool",
                "tool_name": "maps_search_detail",
                "arguments": {
                    "id": poi_id
                }
            })

            print(f"POI详情结果: {result[:200]}...")

            # 解析结果并提取图片
            import json
            import re

            # 尝试从结果中提取JSON
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data

            return {"raw": result}

        except Exception as e:
            print(f"❌ 获取POI详情失败: {str(e)}")
            return {}


# 创建全局服务实例
_amap_service = None


def get_amap_service() -> AmapService:
    """获取高德地图服务实例(单例模式) —— 全项目第5个手写单例闸门，套路同 get_llm"""
    global _amap_service
    
    if _amap_service is None:
        _amap_service = AmapService()
    
    return _amap_service

