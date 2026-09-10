<template>
  <div class="dossier">
    <!-- 顶栏：返回 + 标题 + 操作 -->
    <header class="dossier__bar">
      <button class="bar-btn" @click="goBack">
        <ArrowLeft :size="15" /><span>返回首页</span>
      </button>
      <span class="dossier__mark" v-if="tripPlan">{{ tripPlan.city }} · 旅行档案</span>
      <div class="bar-actions">
        <template v-if="!editMode">
          <button class="bar-btn" @click="toggleEditMode"><Pencil :size="14" /><span>编辑行程</span></button>
          <button class="bar-btn" @click="exportAsImage"><ImageIcon :size="14" /><span>导出图片</span></button>
          <button class="bar-btn" @click="exportAsPDF"><FileText :size="14" /><span>导出PDF</span></button>
        </template>
        <template v-else>
          <button class="bar-btn bar-btn--accent" @click="saveChanges"><Save :size="14" /><span>保存修改</span></button>
          <button class="bar-btn" @click="cancelEdit"><X :size="14" /><span>取消编辑</span></button>
        </template>
      </div>
    </header>

    <div v-if="tripPlan" class="dossier__body">
      <!-- 左：悬浮卡片侧边栏 -->
      <nav class="dossier__nav" aria-label="页面导航">
        <button
          v-for="item in navItems" :key="item.key"
          class="nav__item" :class="{ 'is-active': activeSection === item.key }"
          @click="scrollToSection(item.key)"
        >{{ item.label }}</button>
        <template v-for="(day, index) in tripPlan.days" :key="`d${index}`">
          <button
            class="nav__item nav__item--sub"
            :class="{ 'is-active': activeSection === `day-${index}` }"
            @click="scrollToSection(`day-${index}`)"
          >D{{ index + 1 }} · {{ (day.date || '').slice(5) }}</button>
        </template>
      </nav>



      <!-- 主内容 -->
      <main class="dossier__main">
        <!-- 行程概览 -->
        <section id="overview" class="panel">
          <h2 class="panel__title">{{ tripPlan.city }}旅行计划</h2>
          <div class="meta">
            <span class="meta__k">日期</span>
            <span class="meta__v meta__v--mono">{{ tripPlan.start_date }} → {{ tripPlan.end_date }}</span>
          </div>
          <div class="meta meta--top">
            <span class="meta__k">建议</span>
            <div class="sug">
              <div v-for="b in suggestionBlocks" :key="b.title" class="sug__block">
                <span class="sug__title">{{ b.title }}</span>
                <ul class="sug__list">
                  <li v-for="(it, i) in b.items" :key="i">{{ it }}</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        <!-- 预算明细 -->
        <section id="budget" class="panel" v-if="tripPlan.budget">
          <h2 class="panel__title">预算明细</h2>
          <div class="budget">
            <div class="budget__cell" v-for="cell in budgetCells" :key="cell.label">
              <span class="budget__label">{{ cell.label }}</span>
              <span class="budget__num">¥{{ cell.value }}</span>
            </div>
          </div>
          <div class="budget__total">
            <span class="budget__total-k">预估总费用</span>
            <span class="budget__total-v">¥{{ tripPlan.budget.total }}</span>
          </div>
        </section>

        <!-- 景点地图 -->
        <section id="map" class="panel panel--map">
          <h2 class="panel__title">景点地图</h2>
          <div id="amap-container" class="amap-box"></div>
        </section>

        <!-- 每日行程：手写手风琴 -->
        <section id="days" class="panel">
          <h2 class="panel__title">每日行程</h2>
          <article
            v-for="(day, index) in tripPlan.days" :key="index"
            :id="`day-${index}`"
            class="day" :class="{ 'is-open': openDay === index }"
          >
            <button class="day__head" @click="toggleDay(index)">
              <span class="day__no">D{{ day.day_index + 1 }}</span>
              <span class="day__date">{{ day.date }}</span>
              <span class="day__desc">{{ day.description }}</span>
              <ChevronDown :size="16" class="day__chev" />
            </button>

            <div class="day__fold">
              <div class="day__inner">
                <div class="meta-row">
                  <span class="meta-row__k">行程</span><span class="meta-row__v">{{ day.description }}</span>
                  <span class="meta-row__k">交通</span><span class="meta-row__v">{{ day.transportation }}</span>
                  <span class="meta-row__k">住宿</span><span class="meta-row__v">{{ day.accommodation }}</span>
                </div>

                <h3 class="day__sub">景点安排</h3>
                <div class="spots">
                  <div v-for="(item, i) in day.attractions" :key="i" class="spot">
                    <div class="spot__ops" v-if="editMode">
                      <button class="op" :disabled="i === 0" @click="moveAttraction(day.day_index, i, 'up')" aria-label="上移"><ArrowUp :size="13" /></button>
                      <button class="op" :disabled="i === day.attractions.length - 1" @click="moveAttraction(day.day_index, i, 'down')" aria-label="下移"><ArrowDown :size="13" /></button>
                      <button class="op op--danger" @click="deleteAttraction(day.day_index, i)" aria-label="删除"><Trash2 :size="13" /></button>
                    </div>
                    <div class="spot__pic">
                      <img :src="getAttractionImage(item.name, i)" :alt="item.name" @error="handleImageError" />
                      <span class="spot__no">{{ i + 1 }}</span>
                      <span v-if="item.ticket_price" class="spot__price">¥{{ item.ticket_price }}</span>
                    </div>
                    <div class="spot__body">
                      <h4 class="spot__name">{{ item.name }}</h4>
                      <template v-if="editMode">
                        <label class="spot__field">地址<input v-model="item.address" class="spot__input" /></label>
                        <label class="spot__field">游览时长(分钟)<input v-model.number="item.visit_duration" type="number" min="10" max="480" class="spot__input" /></label>
                        <label class="spot__field">描述<textarea v-model="item.description" rows="2" class="spot__input"></textarea></label>
                      </template>
                      <template v-else>
                        <p class="spot__line"><span>地址</span>{{ item.address }}</p>
                        <p class="spot__line"><span>时长</span>{{ item.visit_duration }} 分钟</p>
                        <p class="spot__line spot__line--desc"><span>描述</span>{{ item.description }}</p>
                        <p v-if="item.rating" class="spot__line"><span>评分</span>{{ item.rating }}</p>
                      </template>
                    </div>
                  </div>
                </div>

                <template v-if="day.hotel">
                  <h3 class="day__sub">住宿推荐</h3>
                  <div class="hotel">
                    <span class="hotel__name">{{ day.hotel.name }}</span>
                    <div class="hotel__facts">
                      <span>{{ day.hotel.type }}</span><span>{{ day.hotel.price_range }}</span>
                      <span>评分 {{ day.hotel.rating }}</span><span>{{ day.hotel.distance }}</span>
                    </div>
                    <p class="hotel__addr">{{ day.hotel.address }}</p>
                  </div>
                </template>

                <h3 class="day__sub">餐饮安排</h3>
                <div class="meals">
                  <div v-for="meal in day.meals" :key="meal.type" class="meal">
                    <span class="meal__type">{{ getMealLabel(meal.type) }}</span>
                    <span class="meal__name">{{ meal.name }}</span>
                    <span v-if="meal.description" class="meal__desc">{{ meal.description }}</span>
                  </div>
                </div>
              </div>
            </div>
          </article>
        </section>

        <!-- 天气 -->
        <section id="weather" class="panel" v-if="tripPlan.weather_info && tripPlan.weather_info.length > 0">
          <h2 class="panel__title">天气信息</h2>
          <div class="weather">
            <div v-for="w in tripPlan.weather_info" :key="w.date" class="wcard">
              <div class="wcard__top">
                <span class="wcard__date">{{ w.date.slice(5) }}</span>
                <Sun :size="20" :stroke-width="1.8" class="wcard__sun" />
              </div>
              <div class="wcard__temp">{{ w.day_temp }}<i>°</i></div>
              <div class="wcard__cond">{{ w.day_weather }}</div>
              <div class="wcard__divider"></div>
              <div class="wcard__row"><Moon :size="14" class="wcard__ic" /><span>夜间 {{ w.night_weather }} {{ w.night_temp }}°</span></div>
              <div class="wcard__row"><Wind :size="14" class="wcard__ic" /><span>{{ w.wind_direction }} {{ w.wind_power }}</span></div>
            </div>
          </div>
        </section>
      </main>

      <!-- 右：AI 规划助手（模拟界面，功能即将上线） -->
      <aside class="copilot">
        <div class="copilot__head">
          <span class="copilot__dot"></span>
          <span class="copilot__name">规划助手</span>
          <span class="copilot__badge">AI</span>
        </div>
        <div class="copilot__chat">
          <div class="bubble bubble--ai">
            你好，我是你的规划助手。这份{{ tripPlan.city }}行程已生成，
            可以试试问我：「第二天下雨怎么办？」
          </div>
          <div class="bubble bubble--me">带老人出行，节奏能慢一点吗？</div>
          <div class="bubble bubble--ai bubble--pending">
            <span class="typing"><i></i><i></i><i></i></span>
            该功能即将上线
          </div>
        </div>
        <div class="copilot__input">
          <input type="text" placeholder="问问你的行程…" disabled />
          <button disabled>发送</button>
        </div>
        <p class="copilot__note">智能对话 · 即将上线</p>
      </aside>
    </div>

    <!-- 空态 -->
    <div v-else class="dossier__empty">
      <MapPin :size="44" />
      <p>暂无旅行计划数据</p>
      <button class="bar-btn bar-btn--accent" @click="goBack"><ArrowLeft :size="14" /><span>返回首页创建行程</span></button>
    </div>

    <!-- 回到顶部 -->
    <button v-show="showTop" class="to-top" @click="toTop" aria-label="回到顶部"><ChevronUp :size="18" /></button>
  </div>
</template>

<script setup lang="ts">
// ══════════ Result · 着色器门户 · 旅行档案 ══════════
// 世界迁移：紫→深色 hairline + 细字 mono + #ff7a45 accent；高德地图换 dark 底。
// 业务逻辑与原版一致：编辑(移动/删除/改字段)、导出(html2canvas/jsPDF)、地图标点+路线。

import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  ArrowLeft, ArrowUp, ArrowDown, ChevronDown, ChevronUp, Pencil, Save, X,
  Image as ImageIcon, FileText, Trash2, Sun, Moon, Wind, MapPin
} from 'lucide-vue-next'
import AMapLoader from '@amap/amap-jsapi-loader'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'
import type { TripPlan } from '@/types'

const router = useRouter()
const tripPlan = ref<TripPlan | null>(null)
const editMode = ref(false)
const originalPlan = ref<TripPlan | null>(null)
const attractionPhotos = ref<Record<string, string>>({})
const activeSection = ref('overview')
const openDay = ref<number | null>(0) // 手风琴：默认展开第一天
let map: any = null

const navItems = [
  { key: 'overview', label: '概览' },
  { key: 'budget', label: '预算' },
  { key: 'map', label: '地图' },
  { key: 'days', label: '每日' },
  { key: 'weather', label: '天气' }
]

const budgetCells = ref<{ label: string; value: number }[]>([])
function buildBudgetCells(plan: TripPlan) {
  if (!plan.budget) return
  budgetCells.value = [
    { label: '景点门票', value: plan.budget.total_attractions },
    { label: '酒店住宿', value: plan.budget.total_hotels },
    { label: '餐饮费用', value: plan.budget.total_meals },
    { label: '交通费用', value: plan.budget.total_transportation }
  ]
}

/* 建议 → 结构化小节：LLM 常用【标题】内容组织文本，解析成块渲染；
   块内再按 "1." 编号拆条目，排版就分点了 */
const suggestionBlocks = ref<{ title: string; items: string[] }[]>([])
function buildSuggestions(text: string) {
  const blocks: { title: string; items: string[] }[] = []
  const re = /【([^】]+)】([^【]*)/g
  let m: RegExpExecArray | null
  while ((m = re.exec(text))) {
    const title = m[1].trim()
    const body = m[2].trim()
    const items = body
      .split(/(?=(?:[1-9]|1[0-2])\.)/)
      .map(t => t.replace(/^\s*[0-9]+\.\s*/, '').trim())
      .filter(Boolean)
    blocks.push({ title, items: items.length ? items : [body] })
  }
  suggestionBlocks.value = blocks.length
    ? blocks
    : [{ title: '总体建议', items: [text] }]
}

onMounted(async () => {
  const data = sessionStorage.getItem('tripPlan')
  if (data) {
    tripPlan.value = JSON.parse(data)
    buildBudgetCells(tripPlan.value)
    buildSuggestions(tripPlan.value.overall_suggestions || '')
    await nextTick()
    initMap()                 // 地图先行，不等图片
    loadAttractionPhotos()    // 图片并行补
  }
  window.addEventListener('scroll', onScroll, { passive: true })
})

const showTop = ref(false)
const onScroll = () => { showTop.value = window.scrollY > 300 }
const toTop = () => window.scrollTo({ top: 0, behavior: 'smooth' })
onBeforeUnmount(() => window.removeEventListener('scroll', onScroll))

const goBack = () => router.push('/')

// 滚动到指定区域；每日行程需先展开再定位
function scrollToSection(key: string) {
  activeSection.value = key
  const m = key.match(/^day-(\d+)$/)
  if (m) openDay.value = Number(m[1])
  nextTick(() => {
    document.getElementById(key)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  })
}

function toggleDay(index: number) {
  openDay.value = openDay.value === index ? null : index
}

const toggleEditMode = () => {
  editMode.value = true
  originalPlan.value = JSON.parse(JSON.stringify(tripPlan.value))
  message.info('进入编辑模式')
}

const saveChanges = () => {
  editMode.value = false
  if (tripPlan.value) {
    sessionStorage.setItem('tripPlan', JSON.stringify(tripPlan.value))
  }
  message.success('修改已保存')
  if (map) map.destroy()
  nextTick(() => initMap())
}

const cancelEdit = () => {
  if (originalPlan.value) {
    tripPlan.value = JSON.parse(JSON.stringify(originalPlan.value))
  }
  editMode.value = false
  message.info('已取消编辑')
}

const deleteAttraction = (dayIndex: number, attrIndex: number) => {
  if (!tripPlan.value) return
  const day = tripPlan.value.days[dayIndex]
  if (day.attractions.length <= 1) {
    message.warning('每天至少需要保留一个景点')
    return
  }
  day.attractions.splice(attrIndex, 1)
  message.success('景点已删除')
}

const moveAttraction = (dayIndex: number, attrIndex: number, direction: 'up' | 'down') => {
  if (!tripPlan.value) return
  const attractions = tripPlan.value.days[dayIndex].attractions
  if (direction === 'up' && attrIndex > 0) {
    [attractions[attrIndex], attractions[attrIndex - 1]] = [attractions[attrIndex - 1], attractions[attrIndex]]
  } else if (direction === 'down' && attrIndex < attractions.length - 1) {
    [attractions[attrIndex], attractions[attrIndex + 1]] = [attractions[attrIndex + 1], attractions[attrIndex]]
  }
}

const getMealLabel = (type: string): string => {
  const labels: Record<string, string> = { breakfast: '早餐', lunch: '午餐', dinner: '晚餐', snack: '小吃' }
  return labels[type] || type
}

const loadAttractionPhotos = async () => {
  if (!tripPlan.value) return
  const promises: Promise<void>[] = []
  tripPlan.value.days.forEach(day => {
    day.attractions.forEach(attraction => {
      const promise = fetch(`http://localhost:8000/api/poi/photo?name=${encodeURIComponent(attraction.name)}`)
        .then(res => res.json())
        .then(data => {
          if (data.success && data.data.photo_url) {
            attractionPhotos.value[attraction.name] = data.data.photo_url
          }
        })
        .catch(err => console.error(`获取${attraction.name}图片失败:`, err))
      promises.push(promise)
    })
  })
  await Promise.all(promises)
}

// 占位图：旧紫渐变换成世界内色（曙光/夜蓝/青灰系暗渐变）
const getAttractionImage = (name: string, index: number): string => {
  if (attractionPhotos.value[name]) return attractionPhotos.value[name]
  const pairs = [
    ['#dce9ff', '#c3daff'], ['#ffeeda', '#ffdfc0'], ['#dcf2e4', '#bfe8cf'],
    ['#efe6ff', '#dfceff'], ['#ffe3e3', '#ffcaca']
  ]
  const [start, end] = pairs[index % pairs.length]
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300">
    <defs><linearGradient id="g${index}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="${start}"/><stop offset="100%" stop-color="${end}"/>
    </linearGradient></defs>
    <rect width="400" height="300" fill="url(#g${index})"/>
    <text x="50%" y="52%" dominant-baseline="middle" text-anchor="middle"
      font-family="'Maple Mono NF CN',monospace" font-size="24" font-weight="700" fill="rgba(29,29,31,.72)">${name}</text>
  </svg>`
  return `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svg)))}`
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect width="400" height="300" fill="%23141a28"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="sans-serif" font-size="16" fill="rgba(232,236,244,.5)"%3E图片加载失败%3C/text%3E%3C/svg%3E'
}

/* ── 导出：克隆主内容 → 注入地图快照 → html2canvas/jsPDF ──
   世界迁移后不再需要 ant-card 后处理（新卡片自带完整样式），导出即所见（深色档案）。 */
async function buildExportContainer(): Promise<HTMLElement> {
  const element = document.querySelector('.dossier__main') as HTMLElement
  if (!element) throw new Error('未找到内容元素')
  const box = document.createElement('div')
  box.style.width = element.offsetWidth + 'px'
  box.style.backgroundColor = '#f5f5f7'
  box.style.padding = '24px'
  box.innerHTML = element.innerHTML

  const mapContainer = document.getElementById('amap-container')
  if (mapContainer && map) {
    const mapCanvas = mapContainer.querySelector('canvas')
    if (mapCanvas) {
      const snap = mapCanvas.toDataURL('image/png')
      const target = box.querySelector('#amap-container')
      if (target) target.innerHTML = `<img src="${snap}" style="width:100%;height:100%;object-fit:cover;" />`
    }
  }
  box.style.position = 'absolute'
  box.style.left = '-9999px'
  document.body.appendChild(box)
  return box
}

const exportAsImage = async () => {
  try {
    message.loading({ content: '正在生成图片...', key: 'export', duration: 0 })
    const box = await buildExportContainer()
    const canvas = await html2canvas(box, {
      backgroundColor: '#f5f5f7', scale: 2, logging: false, useCORS: true, allowTaint: true
    })
    document.body.removeChild(box)
    const link = document.createElement('a')
    link.download = `旅行计划_${tripPlan.value?.city}_${Date.now()}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
    message.success({ content: '图片导出成功!', key: 'export' })
  } catch (error: any) {
    console.error('导出图片失败:', error)
    message.error({ content: `导出图片失败: ${error.message}`, key: 'export' })
  }
}

const exportAsPDF = async () => {
  try {
    message.loading({ content: '正在生成PDF...', key: 'export', duration: 0 })
    const box = await buildExportContainer()
    const canvas = await html2canvas(box, {
      backgroundColor: '#f5f5f7', scale: 2, logging: false, useCORS: true, allowTaint: true
    })
    document.body.removeChild(box)
    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })
    const imgWidth = 210
    const imgHeight = (canvas.height * imgWidth) / canvas.width
    let heightLeft = imgHeight
    let position = 0
    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
    heightLeft -= 297
    while (heightLeft > 0) {
      position = heightLeft - imgHeight
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
      heightLeft -= 297
    }
    pdf.save(`旅行计划_${tripPlan.value?.city}_${Date.now()}.pdf`)
    message.success({ content: 'PDF导出成功!', key: 'export' })
  } catch (error: any) {
    console.error('导出PDF失败:', error)
    message.error({ content: `导出PDF失败: ${error.message}`, key: 'export' })
  }
}

/* ── 高德地图：dark 底 + 橙色标记，融入世界 ── */
const initMap = async () => {
  const box = document.getElementById('amap-container')
  const withTimeout = <T,>(p: Promise<T>, ms: number) =>
    Promise.race([p, new Promise<T>((_, rej) => setTimeout(() => rej(new Error('地图加载超时（需要外网）')), ms))])
  try {
    const AMap = await withTimeout(AMapLoader.load({
      key: import.meta.env.VITE_AMAP_WEB_JS_KEY,
      version: '2.0',
      plugins: ['AMap.Marker', 'AMap.Polyline', 'AMap.InfoWindow']
    }), 15000)
    map = new AMap.Map('amap-container', {
      zoom: 12,
      center: [113.625368, 34.746573], // 默认中心点（郑州）
      viewMode: '2D',
      mapStyle: 'amap://styles/whitesmoke'   // 浅色底图，融入 Apple 风
    })
    addAttractionMarkers(AMap)
    message.success('地图加载成功')
  } catch (error: any) {
    console.error('地图加载失败:', error)
    if (box) box.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#86868b;font-size:14px;">地图加载失败：请检查网络（高德服务需要外网）后刷新重试</div>'
    message.error('地图加载失败')
  }
}

const addAttractionMarkers = (AMap: any) => {
  if (!tripPlan.value) return
  const markers: any[] = []
  const allAttractions: any[] = []
  tripPlan.value.days.forEach((day, dayIndex) => {
    day.attractions.forEach((attraction, attrIndex) => {
      if (attraction.location && attraction.location.longitude && attraction.location.latitude) {
        allAttractions.push({ ...attraction, dayIndex, attrIndex })
      }
    })
  })

  allAttractions.forEach((attraction, index) => {
    const marker = new AMap.Marker({
      position: [attraction.location.longitude, attraction.location.latitude],
      title: attraction.name,
      anchor: 'center',
      content: `<div style="width:28px;height:28px;border-radius:50%;background:#fff;
        border:2.5px solid #007AFF;color:#007AFF;display:flex;align-items:center;justify-content:center;
        font-size:13px;font-weight:700;font-family:'Maple Mono NF CN',monospace;
        box-shadow:0 2px 8px rgba(0,122,255,.35);">${index + 1}</div>`
    })
    const infoWindow = new AMap.InfoWindow({
      content: `
        <div style="padding:10px;background:#fff;color:#1d1d1f;min-width:220px;border-radius:12px;box-shadow:0 8px 32px rgba(0,0,0,.10);font-family:'PingFang SC',sans-serif;">
          <h4 style="margin:0 0 8px 0;color:#1d1d1f;">${attraction.name}</h4>
          <p style="margin:4px 0;"><span style="color:#86868b;">地址</span> ${attraction.address}</p>
          <p style="margin:4px 0;"><span style="color:#86868b;">时长</span> ${attraction.visit_duration}分钟</p>
          <p style="margin:4px 0;"><span style="color:#86868b;">描述</span> ${attraction.description}</p>
          <p style="margin:4px 0;color:#007AFF;">第${attraction.dayIndex + 1}天 · 景点${attraction.attrIndex + 1}</p>
        </div>`,
      offset: new AMap.Pixel(0, -30)
    })
    marker.on('click', () => infoWindow.open(map, marker.getPosition()))
    markers.push(marker)
  })

  map.add(markers)
  if (allAttractions.length > 0) map.setFitView(markers)
  drawRoutes(AMap, allAttractions)
}

const drawRoutes = (AMap: any, attractions: any[]) => {
  if (attractions.length < 2) return
  const dayGroups: any = {}
  attractions.forEach(attr => {
    if (!dayGroups[attr.dayIndex]) dayGroups[attr.dayIndex] = []
    dayGroups[attr.dayIndex].push(attr)
  })
  // 弧形细虚线：相邻点间用二次贝塞尔曲线采样，向右侧拱起，柔和不遮挡
  const arcPoints = (a: any, b: any): [number, number][] => {
    const [x1, y1] = [a.location.longitude, a.location.latitude]
    const [x2, y2] = [b.location.longitude, b.location.latitude]
    const mx = (x1 + x2) / 2, my = (y1 + y2) / 2
    const dx = x2 - x1, dy = y2 - y1
    const len = Math.hypot(dx, dy) || 1
    const k = len * 0.16                    // 拱高与距离成正比
    const cx = mx + (dy / len) * k, cy = my - (dx / len) * k
    const pts: [number, number][] = []
    for (let t = 0; t <= 1.0001; t += 0.05) {
      const u = 1 - t
      pts.push([
        u * u * x1 + 2 * u * t * cx + t * t * x2,
        u * u * y1 + 2 * u * t * cy + t * t * y2
      ])
    }
    return pts
  }
  Object.keys(dayGroups).forEach(dayIdx => {
    const list = dayGroups[dayIdx].sort((a: any, b: any) => a.attrIndex - b.attrIndex)
    for (let i = 0; i < list.length - 1; i++) {
      const polyline = new AMap.Polyline({
        path: arcPoints(list[i], list[i + 1]),
        strokeColor: '#007AFF',
        strokeWeight: 2,
        strokeOpacity: 0.75,
        strokeStyle: 'dashed'
      })
      map.add(polyline)
    }
  })
}
</script>

<style scoped>
/* ═══ Apple 风浅色 v2 · 大圆角统一 · 三栏布局 ═══ */
.dossier{min-height:100vh;background:#fff;color:#1d1d1f;--ease-apple:cubic-bezier(.25,.1,.25,1);
  --r-lg:24px;--r-md:16px;
  font-family:'Maple Mono NF CN',-apple-system,BlinkMacSystemFont,"PingFang SC",
  "Microsoft YaHei",sans-serif;}

/* 顶栏 */
.dossier__bar{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:16px;
  padding:12px 28px;background:rgba(255,255,255,.72);
  backdrop-filter:saturate(180%) blur(20px);-webkit-backdrop-filter:saturate(180%) blur(20px);
  border-bottom:1px solid rgba(60,60,67,.12);}
.dossier__mark{font-size:13px;font-weight:600;color:#1d1d1f;}
.bar-actions{margin-left:auto;display:flex;gap:8px;}
.bar-btn{display:inline-flex;align-items:center;gap:7px;background:rgba(120,120,128,.12);
  border:0;border-radius:980px;color:#1d1d1f;font-family:inherit;font-size:13px;
  padding:8px 15px;cursor:pointer;transition:filter .25s var(--ease-apple),transform .25s var(--ease-apple);}
.bar-btn:hover{filter:brightness(.96);transform:translateY(-1px);}
.bar-btn:focus-visible{outline:2px solid #007AFF;outline-offset:2px;}
.bar-btn--accent{background:#007AFF;color:#fff;}
.bar-btn--accent:hover{filter:brightness(1.08);}

/* 三栏：悬浮左栏 / 主列 / AI 右栏 */
.dossier__body{display:grid;grid-template-columns:190px minmax(0,1fr) 300px;
  gap:24px;width:min(1400px,100% - 56px);margin:24px auto;align-items:start;}

/* 左：悬浮卡片侧边栏 */
.dossier__nav{position:sticky;top:76px;display:flex;flex-direction:column;gap:2px;
  background:#fff;border-radius:var(--r-lg);box-shadow:0 4px 24px rgba(0,0,0,.07);
  padding:14px 12px;}
.nav__item{background:transparent;border:0;text-align:left;cursor:pointer;
  font-family:inherit;font-size:13px;color:#6e6e73;padding:9px 14px;
  border-radius:12px;transition:all .25s var(--ease-apple);}
.nav__item:hover{background:rgba(120,120,128,.12);color:#1d1d1f;}
.nav__item.is-active{background:rgba(0,122,255,.13);color:#007AFF;font-weight:600;}
.nav__item--sub{padding-left:26px;color:#86868b;}

/* 右：AI 规划助手（模拟） */
.copilot{position:sticky;top:76px;display:flex;flex-direction:column;
  background:#fff;border-radius:var(--r-lg);box-shadow:0 4px 24px rgba(0,0,0,.07);
  padding:18px 16px 14px;max-height:calc(100vh - 110px);}
.copilot__head{display:flex;align-items:center;gap:8px;padding-bottom:12px;
  border-bottom:1px solid rgba(60,60,67,.1);margin-bottom:12px;}
.copilot__dot{width:8px;height:8px;border-radius:50%;background:#34C759;}
.copilot__name{font-size:14px;font-weight:700;color:#1d1d1f;}
.copilot__badge{margin-left:auto;font-size:10px;font-weight:700;letter-spacing:.1em;
  background:linear-gradient(135deg,#007AFF,#5ac8fa);color:#fff;
  border-radius:6px;padding:2px 7px;}
.copilot__chat{display:flex;flex-direction:column;gap:10px;overflow-y:auto;
  flex:1;min-height:120px;padding-right:2px;}
.bubble{max-width:88%;padding:10px 13px;font-size:12.5px;line-height:1.75;
  border-radius:16px;}
.bubble--ai{background:#f5f5f7;color:#1d1d1f;border-top-left-radius:5px;align-self:flex-start;}
.bubble--me{background:#007AFF;color:#fff;border-top-right-radius:5px;align-self:flex-end;}
.bubble--pending{color:#86868b;}
.typing{display:inline-flex;gap:4px;margin-right:8px;vertical-align:middle;}
.typing i{width:5px;height:5px;border-radius:50%;background:#86868b;
  animation:blink 1.2s infinite;}
.typing i:nth-child(2){animation-delay:.2s;}
.typing i:nth-child(3){animation-delay:.4s;}
@keyframes blink{0%,80%,100%{opacity:.3;}40%{opacity:1;}}
.copilot__input{display:flex;gap:8px;margin-top:12px;}
.copilot__input input{flex:1;background:rgba(120,120,128,.12);border:0;
  border-radius:12px;padding:10px 12px;font-size:12.5px;font-family:inherit;color:#1d1d1f;}
.copilot__input input::placeholder{color:#86868b;}
.copilot__input button{background:rgba(120,120,128,.2);border:0;border-radius:12px;
  color:#86868b;font-family:inherit;font-size:12px;padding:0 14px;cursor:not-allowed;}
.copilot__note{font-size:10.5px;color:#86868b;text-align:center;margin:10px 0 0;
  letter-spacing:.15em;}

/* 主列 */
.dossier__main{display:flex;flex-direction:column;gap:24px;min-width:0;}
.panel{background:#fff;border-radius:var(--r-lg);box-shadow:0 4px 24px rgba(0,0,0,.06);
  padding:26px 30px;animation:rise .7s var(--ease-ios,cubic-bezier(.32,.72,0,1)) both;}
.panel:nth-child(2){animation-delay:.08s;}
.panel:nth-child(3){animation-delay:.16s;}
.panel:nth-child(4){animation-delay:.24s;}
.panel__title{font-size:21px;font-weight:700;letter-spacing:-.02em;color:#1d1d1f;
  margin:0 0 18px;}

.meta{display:flex;gap:16px;margin-bottom:12px;}
.meta--top{align-items:flex-start;}
.meta__k{flex:0 0 44px;font-size:13px;color:#86868b;padding-top:2px;}
.meta__v{font-size:15px;line-height:1.8;color:#1d1d1f;}
.meta__v--mono{font-variant-numeric:tabular-nums;letter-spacing:.04em;}

/* 建议分点 */
.sug{display:flex;flex-direction:column;gap:14px;flex:1;}
.sug__block{background:#f5f5f7;border-radius:var(--r-md);padding:14px 18px;}
.sug__title{display:inline-block;font-size:13px;font-weight:700;color:#007AFF;
  margin-bottom:8px;}
.sug__list{margin:0;padding:0;list-style:none;}
.sug__list li{position:relative;font-size:13.5px;line-height:1.85;color:#1d1d1f;
  padding-left:16px;margin-bottom:4px;}
.sug__list li::before{content:'';position:absolute;left:2px;top:.75em;
  width:5px;height:5px;border-radius:50%;background:rgba(0,122,255,.5);}

/* 预算 */
.budget{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:18px;}
.budget__cell{background:#f5f5f7;border-radius:var(--r-md);padding:16px 18px;}
.budget__label{display:block;font-size:13px;color:#6e6e73;margin-bottom:8px;}
.budget__num{font-size:24px;font-weight:600;color:#1d1d1f;font-variant-numeric:tabular-nums;}
.budget__total{display:flex;justify-content:space-between;align-items:baseline;
  border-top:1px solid rgba(60,60,67,.12);padding-top:18px;}
.budget__total-k{font-size:14px;color:#6e6e73;}
.budget__total-v{font-size:36px;font-weight:700;color:#007AFF;font-variant-numeric:tabular-nums;}

/* 地图 */
.panel--map .amap-box{width:100%;height:440px;border-radius:var(--r-md);overflow:hidden;}

/* 每日行程 */
.day{background:#f5f5f7;border-radius:var(--r-lg);margin-bottom:14px;overflow:hidden;
  transition:box-shadow .3s var(--ease-apple),background .3s var(--ease-apple);}
.day.is-open{background:#fff;box-shadow:0 4px 24px rgba(0,0,0,.06);}
.day__head{display:flex;align-items:center;gap:16px;width:100%;
  background:transparent;border:0;padding:18px 22px;cursor:pointer;
  color:inherit;text-align:left;font-family:inherit;}
.day__head:focus-visible{outline:2px solid #007AFF;outline-offset:-2px;}
.day__no{font-size:15px;font-weight:700;color:#007AFF;font-variant-numeric:tabular-nums;}
.day__date{font-size:13px;color:#86868b;font-variant-numeric:tabular-nums;}
.day__desc{flex:1;font-size:13px;color:#6e6e73;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.day__chev{flex-shrink:0;color:#86868b;transition:transform .35s var(--ease-apple);}
.day.is-open .day__chev{transform:rotate(180deg);color:#007AFF;}
.day__fold{display:grid;grid-template-rows:0fr;transition:grid-template-rows .35s var(--ease-apple);}
.day.is-open .day__fold{grid-template-rows:1fr;}
.day__inner{overflow:hidden;padding:0 22px;}
.day.is-open .day__inner{padding:4px 22px 24px;}

.meta-row{display:grid;grid-template-columns:auto 1fr;gap:6px 18px;
  border-bottom:1px solid rgba(60,60,67,.1);padding-bottom:14px;margin-bottom:16px;}
.meta-row__k{font-size:13px;color:#86868b;}
.meta-row__v{font-size:14px;line-height:1.7;color:#1d1d1f;}
.day__sub{font-size:13px;font-weight:600;color:#6e6e73;margin:20px 0 14px;
  display:flex;align-items:center;gap:12px;}
.day__sub::after{content:'';flex:1;height:1px;background:rgba(60,60,67,.1);}

/* 景点卡：浅色图片 + 大圆角 */
.spots{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:14px;}
.spot{position:relative;display:grid;grid-template-columns:132px 1fr;gap:14px;
  background:#fff;border:1px solid rgba(60,60,67,.08);border-radius:var(--r-md);padding:12px;
  transition:box-shadow .3s var(--ease-apple),transform .3s var(--ease-apple);}
.spot:hover{box-shadow:0 8px 32px rgba(0,0,0,.10);transform:translateY(-2px);}
.spot__ops{position:absolute;top:8px;right:8px;display:flex;gap:6px;z-index:2;}
.op{display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;
  background:#fff;border:1px solid rgba(60,60,67,.18);border-radius:980px;
  color:#6e6e73;cursor:pointer;transition:all .2s var(--ease-apple);}
.op:hover:not(:disabled){border-color:#007AFF;color:#007AFF;}
.op:disabled{opacity:.3;cursor:not-allowed;}
.op--danger:hover:not(:disabled){border-color:#FF3B30;color:#FF3B30;}
.spot__pic{position:relative;border-radius:12px;overflow:hidden;}
.spot__pic img{display:block;width:100%;height:132px;object-fit:cover;}
.spot__no{position:absolute;left:8px;top:8px;width:22px;height:22px;
  display:flex;align-items:center;justify-content:center;
  background:#007AFF;color:#fff;font-size:12px;font-weight:700;border-radius:980px;
  font-variant-numeric:tabular-nums;}
.spot__price{position:absolute;right:0;bottom:0;background:rgba(255,255,255,.92);
  color:#1d1d1f;font-size:12px;font-weight:600;padding:3px 9px;
  font-variant-numeric:tabular-nums;}
.spot__name{font-size:15px;font-weight:600;color:#1d1d1f;margin:2px 0 8px;}
.spot__line{font-size:13px;line-height:1.7;color:#1d1d1f;margin:0 0 4px;}
.spot__line span{color:#86868b;margin-right:10px;font-size:12px;}
.spot__line--desc{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}
.spot__field{display:flex;flex-direction:column;gap:4px;font-size:12px;color:#6e6e73;margin-bottom:8px;}
.spot__input{background:rgba(120,120,128,.12);border:0;border-radius:10px;
  color:#1d1d1f;font-family:inherit;font-size:13px;padding:7px 10px;}
.spot__input:focus{outline:none;box-shadow:0 0 0 3px rgba(0,122,255,.25);}

/* 酒店 / 餐饮 */
.hotel{background:#f5f5f7;border-radius:var(--r-md);padding:16px 20px;}
.hotel__name{font-size:15px;font-weight:600;color:#1d1d1f;}
.hotel__facts{display:flex;gap:18px;flex-wrap:wrap;margin:8px 0 6px;
  font-size:12px;color:#6e6e73;font-variant-numeric:tabular-nums;}
.hotel__addr{font-size:13px;color:#6e6e73;margin:0;}
.meals{display:flex;flex-direction:column;}
.meal{display:flex;gap:16px;align-items:baseline;padding:10px 0;
  border-bottom:1px dashed rgba(60,60,67,.12);}
.meal:last-child{border-bottom:0;}
.meal__type{flex:0 0 44px;font-size:12px;color:#007AFF;font-weight:600;}
.meal__name{font-size:14px;color:#1d1d1f;font-weight:600;}
.meal__desc{font-size:13px;color:#6e6e73;}

/* 天气：iOS 天气 App 风（蓝底白字大温度） */
.weather{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:14px;}
.wcard{border-radius:20px;padding:18px 18px 14px;color:#fff;
  background:linear-gradient(180deg,#59a7f2 0%,#8ec9f7 100%);
  box-shadow:0 8px 24px rgba(89,167,242,.35);}
.wcard__top{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;}
.wcard__date{font-size:13px;color:rgba(255,255,255,.9);}
.wcard__sun{color:rgba(255,255,255,.95);}
.wcard__temp{font-size:46px;font-weight:600;line-height:1.05;
  font-variant-numeric:tabular-nums;}
.wcard__temp i{font-style:normal;font-size:26px;vertical-align:.42em;}
.wcard__cond{font-size:13px;color:rgba(255,255,255,.92);margin:2px 0 12px;}
.wcard__divider{height:1px;background:rgba(255,255,255,.3);margin-bottom:10px;}
.wcard__row{display:flex;gap:9px;align-items:center;font-size:12.5px;
  color:rgba(255,255,255,.95);margin-bottom:7px;}
.wcard__ic{color:rgba(255,255,255,.85);flex-shrink:0;}

/* 空态 / 回顶部 */
.dossier__empty{min-height:70vh;display:flex;flex-direction:column;gap:18px;
  align-items:center;justify-content:center;color:#6e6e73;}
.to-top{position:fixed;right:36px;bottom:36px;z-index:30;width:44px;height:44px;
  display:flex;align-items:center;justify-content:center;
  background:rgba(255,255,255,.72);border:1px solid rgba(60,60,67,.15);border-radius:980px;
  color:#1d1d1f;cursor:pointer;
  backdrop-filter:saturate(180%) blur(20px);-webkit-backdrop-filter:saturate(180%) blur(20px);
  box-shadow:0 4px 24px rgba(0,0,0,.08);transition:all .25s var(--ease-apple);}
.to-top:hover{transform:translateY(-2px);box-shadow:0 8px 32px rgba(0,0,0,.12);}

@keyframes rise{from{opacity:0;transform:translateY(16px);}to{opacity:1;transform:none;}}

@media (prefers-reduced-motion:reduce){
  .panel{animation:none;}
  .bar-btn,.spot,.to-top{transition:none;}
}
@media (max-width:1280px){
  .dossier__body{grid-template-columns:180px minmax(0,1fr);}
  .copilot{display:none;}
}
@media (max-width:1024px){
  .dossier__body{grid-template-columns:1fr;}
  .dossier__nav{display:none;}
}
</style>
