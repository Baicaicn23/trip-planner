// ══════════ 类型定义 —— 后端 schemas.py 的"前端影子" ══════════
// 【本文件是什么】后端 Pydantic 模型的 TypeScript 镜像（教材13.5.2）：
//   后端改了字段名而这里没同步，前端一编译就标红——用类型当"边境哨兵"。
// 【读法】`?` = 可选字段（对应后端 Optional）；interface 只描述数据形状，不装任何逻辑。
// 【命名】后端叫 TripRequest，前端习惯叫 TripFormData——名字不同，字段一模一样。

/**
 * 经纬度坐标 —— 镜像自后端 Location
 * 【类比】微信发定位时长按地图出现的那个红点：地图插旗全靠它
 */
export interface Location {
  longitude: number
  latitude: number
}

/**
 * 景点 —— 镜像自后端 Attraction
 * 【类比】大众点评里的店铺卡片：名称/地址/坐标/建议游玩时长/门票
 */
export interface Attraction {
  name: string
  address: string
  location: Location
  visit_duration: number
  description: string
  category?: string
  rating?: number
  image_url?: string
  ticket_price?: number
}

/**
 * 一顿饭 —— 镜像自后端 Meal
 * 【类比】外卖订单记录：品类(type)/商家名/预估花费
 */
export interface Meal {
  type: 'breakfast' | 'lunch' | 'dinner' | 'snack'
  name: string
  address?: string
  location?: Location
  description?: string
  estimated_cost?: number
}

/**
 * 酒店 —— 镜像自后端 Hotel
 * 【类比】携程的酒店卡片：价格区间/评分/离景点距离
 */
export interface Hotel {
  name: string
  address: string
  location?: Location
  price_range: string
  rating: string
  distance: string
  type: string
  estimated_cost?: number
}

/**
 * 预算 —— 镜像自后端 Budget
 * 【类比】记账App的分类汇总：门票/住宿/餐饮/交通四张小卡+红色总计
 */
export interface Budget {
  total_attractions: number
  total_hotels: number
  total_meals: number
  total_transportation: number
  total: number
}

/**
 * 单日行程 —— 镜像自后端 DayPlan
 * 【类比】行程本里的一页：今天去哪、吃什么、住哪里
 */
export interface DayPlan {
  date: string
  day_index: number
  description: string
  transportation: string
  accommodation: string
  hotel?: Hotel
  attractions: Attraction[]
  meals: Meal[]
}

/**
 * 天气 —— 镜像自后端 WeatherInfo
 * 【类比】天气App的一天视图（后端已把"16°C"清洗成纯数字，这边放心用 number）
 */
export interface WeatherInfo {
  date: string
  day_weather: string
  night_weather: string
  day_temp: number
  night_temp: number
  wind_direction: string
  wind_power: string
}

/**
 * 完整旅行计划 —— 镜像自后端 TripPlan（后端AI的最终产物）
 * 【类比】旅行社递给你的那本装订好的行程册
 */
export interface TripPlan {
  city: string
  start_date: string
  end_date: string
  days: DayPlan[]
  weather_info: WeatherInfo[]
  overall_suggestions: string
  budget?: Budget
}

/**
 * 规划请求 —— 镜像自后端 TripRequest（你填的表单就长这样）
 * ⚠️ 注意字段名是 travel_days 不是 days——上次422的教训就在这
 */
export interface TripFormData {
  city: string
  start_date: string
  end_date: string
  travel_days: number
  transportation: string
  accommodation: string
  preferences: string[]
  free_text_input: string
}

/**
 * 统一响应信封 —— 镜像自后端 TripPlanResponse
 * 【类比】快递面单：先看success签收状态，再拆data里的货
 */
export interface TripPlanResponse {
  success: boolean
  message: string
  data?: TripPlan
}
