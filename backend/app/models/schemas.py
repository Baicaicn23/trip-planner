"""数据模型定义 —— 全项目的"普通话"字典

【使命】前端(TypeScript)、后端(Python)、LLM、高德API四方各说各的"方言"，
本文件用 Pydantic 定义统一数据格式：进来的数据自动验证+转换，出去的数据保证结构正确，
FastAPI 还能据此自动生成 /docs 接口文档。

【逻辑块地图】（自底向上：先小积木，后大积木）
  ① 请求模型  TripRequest / POISearchRequest / RouteRequest —— 前端→后端的"点单"
  ② 基础积木  Location / Attraction / Meal / Hotel          —— 最小数据件
  ③ 组合积木  DayPlan → TripPlan                            —— 拼成一份完整行程
  ④ 特殊处理  WeatherInfo（温度清洗验证器，全文件唯一的"程序逻辑"）
  ⑤ 统一信封  *Response / ErrorResponse                     —— 所有API响应的外壳
"""

from typing import List, Optional, Union
from pydantic import BaseModel, Field, field_validator
from datetime import date


# ════════════════ 块① 请求模型：前端→后端方向的"点单" ════════════════
# Field(..., ...) 里的 ... 是"必填"记号（Ellipsis）；default= 是可选。
# ge/le/gt 是范围验证；example 只影响 /docs 文档展示，不参与验证。

class TripRequest(BaseModel):
    """旅行规划请求

    【干什么用】你在首页点「开始规划」的瞬间，表单里的8项内容打包成这个类发给后端——它是整个系统的入口数据。
    【类比】像外卖App的下单页：城市=送哪儿、日期=什么时候送、偏好=口味备注；
    也像你在 Claude Code 对话框里输入的第一句需求——写得越明确，AI 规划得越靠谱。
    """
    city: str = Field(..., description="目的地城市", example="北京")
    start_date: str = Field(..., description="开始日期 YYYY-MM-DD", example="2025-06-01")
    end_date: str = Field(..., description="结束日期 YYYY-MM-DD", example="2025-06-03")
    travel_days: int = Field(..., description="旅行天数", ge=1, le=30, example=3)  # 天数必须1~30，填0直接被拒
    transportation: str = Field(..., description="交通方式", example="公共交通")
    accommodation: str = Field(..., description="住宿偏好", example="经济型酒店")
    preferences: List[str] = Field(default=[], description="旅行偏好标签", example=["历史文化", "美食"])  # 标签列表，可多个
    free_text_input: Optional[str] = Field(default="", description="额外要求", example="希望多安排一些博物馆")  # 用户自由补充，全可选
    
    class Config:
        json_schema_extra = {
            "example": {
                "city": "北京",
                "start_date": "2025-06-01",
                "end_date": "2025-06-03",
                "travel_days": 3,
                "transportation": "公共交通",
                "accommodation": "经济型酒店",
                "preferences": ["历史文化", "美食"],
                "free_text_input": "希望多安排一些博物馆"
            }
        }


class POISearchRequest(BaseModel):
    """POI搜索请求（POI = 地图上一个可搜索的"兴趣点"：一家店、一个景点都算）

    【干什么用】给前端搜索小功能用的：告诉高德"在哪个城市、找什么关键词"。
    【类比】相当于打开高德地图App在搜索框输入"故宫"——keywords是你敲的字，city是当前所在城市。
    """
    keywords: str = Field(..., description="搜索关键词", example="故宫")
    city: str = Field(..., description="城市", example="北京")
    citylimit: bool = Field(default=True, description="是否限制在城市范围内")


class RouteRequest(BaseModel):
    """路线规划请求

    【干什么用】让高德算"从A地到B地怎么走、多远、多久"。
    【类比】就是高德地图App里的导航：填起点终点，选步行/驾车/公交（route_type），点"开始导航"。
    """
    origin_address: str = Field(..., description="起点地址", example="北京市朝阳区阜通东大街6号")
    destination_address: str = Field(..., description="终点地址", example="北京市海淀区上地十街10号")
    origin_city: Optional[str] = Field(default=None, description="起点城市")
    destination_city: Optional[str] = Field(default=None, description="终点城市")
    route_type: str = Field(default="walking", description="路线类型: walking/driving/transit")


# ════════════════ 块② 基础积木：Location/Attraction/Meal/Hotel ════════════════
# 注意嵌套写法：Attraction 里塞了一个 Location 对象而不是裸的经纬度——
# 这就是"自底向上"：先把最小的积木造标准，大积木直接引用它。

class Location(BaseModel):
    """地理位置（经纬度坐标）

    【干什么用】给地图上的一个点定"门牌号"：经度longitude(东西方向)、纬度latitude(南北方向)。景点/酒店/餐厅全靠它才能画上地图。
    【类比】像微信发定位时长按地图出现的那个红点——没有坐标，结果页的地图就没法插旗子。
    """
    longitude: float = Field(..., description="经度")
    latitude: float = Field(..., description="纬度")


class Attraction(BaseModel):
    """景点信息 —— 行程的核心单元，字段最全

    【干什么用】描述行程里的一站，比如"故宫"：叫什么、在哪、建议玩多久(visit_duration)、门票多少、评分几星。
    【类比】像大众点评里的一张店铺卡片——PlannerAgent 产出的每个景点都是一张卡片，前端拿它渲染文字+地图插旗。
    """
    name: str = Field(..., description="景点名称")
    address: str = Field(..., description="地址")
    location: Location = Field(..., description="经纬度坐标")  # 嵌套模型：传入dict会自动转成Location对象
    visit_duration: int = Field(..., description="建议游览时间(分钟)")
    description: str = Field(..., description="景点描述")
    category: Optional[str] = Field(default="景点", description="景点类别")
    rating: Optional[float] = Field(default=None, description="评分")
    photos: Optional[List[str]] = Field(default_factory=list, description="景点图片URL列表")  # default_factory：每次实例化现造一个新列表，最稳妥的默认值写法
    poi_id: Optional[str] = Field(default="", description="POI ID")  # 高德地图对每个地点的编号
    image_url: Optional[str] = Field(default=None, description="图片URL")
    ticket_price: int = Field(default=0, description="门票价格(元)")


class Meal(BaseModel):
    """餐饮信息

    【干什么用】行程中的一顿饭：早/午/晚餐还是零食(type)、在哪儿吃(name)、大概花多少(estimated_cost)。
    【类比】像你手机里的外卖订单记录：商家名+品类+实付金额，只不过这单是AI提前一天帮你"预订"好的。
    """
    type: str = Field(..., description="餐饮类型: breakfast/lunch/dinner/snack")
    name: str = Field(..., description="餐饮名称")
    address: Optional[str] = Field(default=None, description="地址")
    location: Optional[Location] = Field(default=None, description="经纬度坐标")
    description: Optional[str] = Field(default=None, description="描述")
    estimated_cost: int = Field(default=0, description="预估费用(元)")


class Hotel(BaseModel):
    """酒店信息

    【干什么用】每晚住哪儿：酒店名、离景点多远(distance)、一晚大概多少钱(estimated_cost)。
    【类比】像携程/美团上的酒店列表卡片：价格区间、评分、距离一目了然。
    """
    name: str = Field(..., description="酒店名称")
    address: str = Field(default="", description="酒店地址")
    location: Optional[Location] = Field(default=None, description="酒店位置")
    price_range: str = Field(default="", description="价格范围")
    rating: str = Field(default="", description="评分")
    distance: str = Field(default="", description="距离景点距离")
    type: str = Field(default="", description="酒店类型")
    estimated_cost: int = Field(default=0, description="预估费用(元/晚)")


# ════════════════ 块③ 组合积木：DayPlan → TripPlan ════════════════
# 一天 = 景点列表 + 餐饮列表 + 可选酒店；整个行程 = 天数列表 + 天气 + 预算。
# LLM(PlannerAgent) 的产出最终要能通过 TripPlan 的验证，才算合格。

class DayPlan(BaseModel):
    """单日行程 —— 行程册里的一页

    【干什么用】把某一天打包：这天(date)去哪些景点、吃哪几顿饭、住哪家酒店、当日建议(description)。
    【类比】像纸质行程本上的一页，也像日历App里展开的一天：上午故宫、中午四季民福、晚上回酒店。
    """
    date: str = Field(..., description="日期 YYYY-MM-DD")
    day_index: int = Field(..., description="第几天(从0开始)")
    description: str = Field(..., description="当日行程描述")
    transportation: str = Field(..., description="交通方式")
    accommodation: str = Field(..., description="住宿")
    hotel: Optional[Hotel] = Field(default=None, description="推荐酒店")
    attractions: List[Attraction] = Field(default=[], description="景点列表")
    meals: List[Meal] = Field(default=[], description="餐饮列表")


# ════════════════ 块④ 特殊处理：天气温度清洗 ════════════════
# 高德API返回的温度是 "16°C" 这种字符串，没法直接算平均温/做比较。
# field_validator(mode='before') = 在Pydantic做类型检查【之前】先跑这个清洗函数：
# 字符串→去掉单位→转int；转不成(比如返回了"暂无")就兜底为0，绝不让整个请求崩掉。

class WeatherInfo(BaseModel):
    """天气信息

    【干什么用】某天的天气预报：白天/夜间天气和温度、风向风力——用来提醒你"6月2日有雨，记得带伞"。
    【类比】就是手机自带天气App里的一天视图。注意温度是"16°C"这种脏字符串进来的，全靠下面的"翻译官"清洗成数字。
    """
    date: str = Field(..., description="日期 YYYY-MM-DD")
    day_weather: str = Field(default="", description="白天天气")
    night_weather: str = Field(default="", description="夜间天气")
    day_temp: Union[int, str] = Field(default=0, description="白天温度")  # 放行str：先让它进门，验证器再清洗成int
    night_temp: Union[int, str] = Field(default=0, description="夜间温度")
    wind_direction: str = Field(default="", description="风向")
    wind_power: str = Field(default="", description="风力")

    @field_validator('day_temp', 'night_temp', mode='before')
    @classmethod
    def parse_temperature(cls, v):
        """解析温度,移除°C等单位 —— 温度翻译官

        【干什么用】高德返回"16°C"，但行程册里的温度要参与计算比较，这里把单位剥掉转成数字16；
        碰上"暂无"翻译不动就记0，绝不让一条坏数据掀翻整个请求。
        【类比】像跨国会议的同声传译：外方(高德)说什么方言都行，进会议室(计算逻辑)前必须译成标准普通话。
        """
        if isinstance(v, str):
            # 移除°C, ℃等单位符号
            v = v.replace('°C', '').replace('℃', '').replace('°', '').strip()
            try:
                return int(v)
            except ValueError:
                return 0  # 容错：清洗失败宁可记0，也不让一次坏数据掀翻整个行程
        return v


class Budget(BaseModel):
    """预算信息

    【干什么用】这次旅行要花多少钱：门票/住宿/餐饮/交通四项分账 + 总计total。
    【类比】像记账App的月度分类汇总——四张小卡片各管一项，前端用红色大字号重点展示total。
    """
    total_attractions: int = Field(default=0, description="景点门票总费用")
    total_hotels: int = Field(default=0, description="酒店总费用")
    total_meals: int = Field(default=0, description="餐饮总费用")
    total_transportation: int = Field(default=0, description="交通总费用")
    total: int = Field(default=0, description="总费用")


class TripPlan(BaseModel):
    """旅行计划 —— 整个系统的最终产物

    【干什么用】AI 规划出的完整成果：N天的days + 每天天气 + 总体建议 + 预算。PlannerAgent 的输出必须能通过它的验证，前端才有东西可渲染。
    【类比】像旅行社最后递到你手里的那本装订好的行程册；也像让 Claude Code 做完一轮研究后交付的那份完整报告。
    """
    city: str = Field(..., description="目的地城市")
    start_date: str = Field(..., description="开始日期")
    end_date: str = Field(..., description="结束日期")
    days: List[DayPlan] = Field(..., description="每日行程")
    weather_info: List[WeatherInfo] = Field(default=[], description="天气信息")
    overall_suggestions: str = Field(..., description="总体建议")
    budget: Optional[Budget] = Field(default=None, description="预算信息")


# ════════════════ 块⑤ 统一信封：所有API响应的外壳 ════════════════
# success / message / data 三件套——前端拿到任何响应都先看 success，
# 再决定渲染 data 还是弹出 message。前端不用为每种接口猜不同的返回结构。
# （POIInfo/RouteInfo 是信封里 data 字段的"内容物"）

class TripPlanResponse(BaseModel):
    """旅行计划响应 —— 成功时后端递出的信封

    【干什么用】所有成功响应的统一外壳：success=办成没、message=一句话说明、data=真正的行程册。
    【类比】像快递面单：先看签收状态(success)，再拆里面的货(data)。前端永远按同一套路拆包裹，不用为每种接口猜格式。
    """
    success: bool = Field(..., description="是否成功")
    message: str = Field(default="", description="消息")
    data: Optional[TripPlan] = Field(default=None, description="旅行计划数据")


class POIInfo(BaseModel):
    """POI信息 —— 地图上"一个地点"的标准卡

    【干什么用】高德搜出来的一个地点：名称、类型、地址、坐标、电话。
    【类比】高德地图App搜索结果列表里的每一条：店名+类型+地址+电话，点开能看详情。
    """
    id: str = Field(..., description="POI ID")
    name: str = Field(..., description="名称")
    type: str = Field(..., description="类型")
    address: str = Field(..., description="地址")
    location: Location = Field(..., description="经纬度坐标")
    tel: Optional[str] = Field(default=None, description="电话")


class POISearchResponse(BaseModel):
    """POI搜索响应 —— POI搜索结果的信封

    【干什么用】success/message/data 三件套，data里装一沓POIInfo卡片。
    【类比】搜索框敲完字回车，地图App弹出的那份结果列表——这个类就是装那张列表的快递盒。
    """
    success: bool = Field(..., description="是否成功")
    message: str = Field(default="", description="消息")
    data: List[POIInfo] = Field(default=[], description="POI列表")


class RouteInfo(BaseModel):
    """路线信息 —— 导航算出来的结果

    【干什么用】一段路线的硬指标：多远(distance米)、多久(duration秒)、什么方式(route_type)、文字描述。
    【类比】高德导航出发前给的那句"全程2.5公里，步行约35分钟"。
    """
    distance: float = Field(..., description="距离(米)")
    duration: int = Field(..., description="时间(秒)")
    route_type: str = Field(..., description="路线类型")
    description: str = Field(..., description="路线描述")


class RouteResponse(BaseModel):
    """路线规划响应 —— 导航结果的信封

    【干什么用】success/message/data(RouteInfo) 三件套外壳。
    【类比】导航页顶部那张信息卡外面的包装盒。
    """
    success: bool = Field(..., description="是否成功")
    message: str = Field(default="", description="消息")
    data: Optional[RouteInfo] = Field(default=None, description="路线信息")


class WeatherResponse(BaseModel):
    """天气查询响应 —— 天气结果的信封

    【干什么用】data里装一串WeatherInfo(每天一条)的统一外壳。
    【类比】天气App"未来N天"列表页的整包数据。
    """
    success: bool = Field(..., description="是否成功")
    message: str = Field(default="", description="消息")
    data: List[WeatherInfo] = Field(default=[], description="天气信息")


# ════════════════ 错误响应 ════════════════

class ErrorResponse(BaseModel):
    """错误响应 —— 出错时后端的统一"道歉模板"

    【干什么用】任何接口失败都长这样：success=False、message=出了什么事、error_code=事故编号(可选)。
    【类比】像银行App转账失败弹出的那条红字提示——保证失败时前端也有标准格式可解析，而不是拿到一坨天书报错。
    """
    success: bool = Field(default=False, description="是否成功")
    message: str = Field(..., description="错误消息")
    error_code: Optional[str] = Field(default=None, description="错误代码")

