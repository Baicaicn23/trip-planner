// ══════════ API服务封装 —— 店面对后厨的"专线电话" ══════════
// 【本文件是什么】前端调后端的唯一出口：整个前端只有这一个文件知道后端地址。
// 【类比】苍穹外卖管理端的 request.js：axios实例+拦截器+API函数，三件套一模一样。
// 【好处】后端地址变了只改这里一处；哪个页面要调接口都来这领函数，不在页面里散落写网址。

import axios from 'axios'
import type { TripFormData, TripPlanResponse } from '@/types'

// 后端地址从 .env 读（VITE_API_BASE_URL=http://localhost:8000），读不到就兜底
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 创建专线电话机：2分钟超时——四Agent串行干活可能要几十秒，太短会中途挂断
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2分钟超时
  headers: {
    'Content-Type': 'application/json'
  }
})

// ── 拦截器：每通电话都过的"安检门"（现在只打日志，以后加登录token也在这） ──
// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    console.log('发送请求:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    console.log('收到响应:', response.status, response.config.url)
    return response
  },
  (error) => {
    console.error('响应错误:', error.response?.status, error.message)
    return Promise.reject(error)
  }
)

/**
 * 生成旅行计划 —— 全店最重要的一个电话（Home.vue的"开始规划"拨的就是它）
 *
 * 【干什么用】把表单(TripFormData)POST到 /api/trip/plan，拆开信封返回。
 * 【类比】@PostMapping 对应的前端 half：后端 trip.py 接单，这里发单——合同两端。
 */
export async function generateTripPlan(formData: TripFormData): Promise<TripPlanResponse> {
  try {
    const response = await apiClient.post<TripPlanResponse>('/api/trip/plan', formData)
    return response.data
  } catch (error: any) {
    console.error('生成旅行计划失败:', error)
    // 把后端报错(比如422的detail)翻成人话抛给页面弹窗
    throw new Error(error.response?.data?.detail || error.message || '生成旅行计划失败')
  }
}

/**
 * 健康检查 —— 打后端 /health 探个活，确认专线通不通
 */
export async function healthCheck(): Promise<any> {
  try {
    const response = await apiClient.get('/health')
    return response.data
  } catch (error: any) {
    console.error('健康检查失败:', error)
    throw new Error(error.message || '健康检查失败')
  }
}

export default apiClient

