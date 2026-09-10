// 多方案数据层：旅行计划持久化到 localStorage，支持多方案切换/删除
import type { TripPlan } from '@/types'

export interface StoredPlan {
  id: string
  plan: TripPlan
  savedAt: number
}

const KEY = 'tripPlans'
const CUR = 'tripPlans.current'

export function listPlans(): StoredPlan[] {
  try {
    const arr = JSON.parse(localStorage.getItem(KEY) || '[]') as StoredPlan[]
    return arr.sort((a, b) => b.savedAt - a.savedAt)
  } catch {
    return []
  }
}

export function savePlan(plan: TripPlan): string {
  const arr = JSON.parse(localStorage.getItem(KEY) || '[]') as StoredPlan[]
  // 相同城市+日期范围视为同一次规划，覆盖更新
  const exist = arr.find(
    p => p.plan.city === plan.city && p.plan.start_date === plan.start_date && p.plan.end_date === plan.end_date
  )
  const id = exist?.id ?? `plan_${Date.now()}`
  const next = arr.filter(p => p.id !== id)
  next.push({ id, plan, savedAt: Date.now() })
  localStorage.setItem(KEY, JSON.stringify(next))
  localStorage.setItem(CUR, id)
  return id
}

export function getPlan(id: string): StoredPlan | null {
  return listPlans().find(p => p.id === id) ?? null
}

export function deletePlan(id: string) {
  const arr = JSON.parse(localStorage.getItem(KEY) || '[]') as StoredPlan[]
  localStorage.setItem(KEY, JSON.stringify(arr.filter(p => p.id !== id)))
  if (localStorage.getItem(CUR) === id) localStorage.removeItem(CUR)
}

export function getCurrentId(): string | null {
  return localStorage.getItem(CUR)
}

export function setCurrentId(id: string) {
  localStorage.setItem(CUR, id)
}
