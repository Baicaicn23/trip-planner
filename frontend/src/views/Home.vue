<template>
  <div class="home">
    <!-- 毛玻璃导航栏 -->
    <header class="nav">
      <div class="nav__inner">
        <span class="nav__brand">智能旅行助手</span>
        <a
          class="nav__link"
          href="https://github.com/Baicaicn23/trip-planner"
          target="_blank" rel="noopener"
        >GitHub</a>
      </div>
    </header>

    <!-- Hero -->
    <section class="hero">
      <h1 class="hero__title">把旅行规划，<br />交给 AI。</h1>
      <p class="hero__sub">
        四个 AI 专员分工协作：搜景点、查天气、荐酒店、排行程。<br />
        三十秒，一份可直接出行的完整计划。
      </p>
      <div class="hero__cta">
        <button class="btn btn--primary" @click="scrollToForm">开始规划</button>
        <button class="btn btn--secondary" @click="scrollToHow">了解工作原理</button>
      </div>
    </section>

    <!-- 申请表 -->
    <section id="form" ref="formSection" class="form-section">
      <form class="sheet" novalidate @submit.prevent="handleSubmit">
        <div class="sheet__head">
          <h2 class="sheet__title">旅行申请表</h2>
          <span class="sheet__meta">8 项 · 约 1 分钟填完</span>
        </div>

        <div class="grid">
          <label class="field field--full">
            <span class="field__label">目的地城市</span>
            <input
              v-model.trim="formData.city"
              type="text"
              class="field__input"
              placeholder="北京、郑州、成都…"
              autocomplete="off"
            />
            <span v-if="errors.city" class="field__err">{{ errors.city }}</span>
          </label>

          <div class="field field--days">
            <span class="field__label">天数 · 自动</span>
            <span class="field__days">{{ formData.travel_days }}<i>天</i></span>
          </div>

          <label class="field">
            <span class="field__label">出发日期</span>
            <input v-model="formData.start_date" type="date" class="field__input" :min="today" />
            <span v-if="errors.start_date" class="field__err">{{ errors.start_date }}</span>
          </label>

          <label class="field">
            <span class="field__label">返回日期</span>
            <input v-model="formData.end_date" type="date" class="field__input" :min="formData.start_date || today" />
            <span v-if="errors.end_date" class="field__err">{{ errors.end_date }}</span>
          </label>

          <fieldset class="field field--full">
            <legend class="field__label">交通方式</legend>
            <div class="seg">
              <button
                v-for="t in TRANSPORT_OPTIONS" :key="t" type="button"
                class="seg__item" :class="{ 'is-on': formData.transportation === t }"
                @click="formData.transportation = t"
              >{{ t }}</button>
            </div>
          </fieldset>

          <fieldset class="field field--full">
            <legend class="field__label">住宿偏好</legend>
            <div class="seg">
              <button
                v-for="a in STAY_OPTIONS" :key="a" type="button"
                class="seg__item" :class="{ 'is-on': formData.accommodation === a }"
                @click="formData.accommodation = a"
              >{{ a }}</button>
            </div>
          </fieldset>

          <fieldset class="field field--full">
            <legend class="field__label">旅行偏好 · 可多选</legend>
            <div class="chips">
              <button
                v-for="p in PREFERENCE_OPTIONS" :key="p" type="button"
                class="chip" :class="{ 'is-on': formData.preferences.includes(p) }"
                :aria-pressed="formData.preferences.includes(p)"
                @click="togglePreference(p)"
              >{{ p }}</button>
            </div>
          </fieldset>

          <label class="field field--full">
            <span class="field__label">额外要求 · 可留空</span>
            <input
              v-model.trim="formData.free_text_input"
              type="text"
              class="field__input"
              placeholder="例如：想看升旗，不吃辣，带老人出行…"
            />
          </label>
        </div>

        <button type="submit" class="go" :disabled="loading">
          <span v-if="!loading">开始规划</span>
          <span v-else>规划中 · 四专员出动…</span>
        </button>
        <p v-if="errors.form" class="sheet__form-err">{{ errors.form }}</p>

        <!-- 规划进度：四专员步进卡 -->
        <div v-if="loading" class="steps" aria-live="polite">
          <div v-for="(s, i) in STEPS" :key="s.label" class="step" :class="stepClass(i)">
            <span class="step__icon">
              <Check v-if="i < progressStep" :size="14" class="step__check" />
              <span v-else-if="i === progressStep" class="step__spin"></span>
            </span>
            <span class="step__label">{{ s.label }}</span>
            <span class="step__state">{{ stateText(i) }}</span>
          </div>
          <div class="steps__bar"><div class="steps__fill" :style="{ width: progressPct + '%' }"></div></div>
        </div>
      </form>
    </section>

    <!-- 工作原理 -->
    <section id="how" ref="howSection" class="how">
      <h2 class="how__title">四位专员，各司其职。</h2>
      <p class="how__sub">不是一个聊天机器人包揽全部，而是一条多智能体流水线——每一步都查真实数据。</p>
      <div class="how__row">
        <div class="how__item">
          <MapPin :size="30" :stroke-width="1.6" class="how__ic" />
          <h3>景点搜索</h3>
          <p>按你的偏好调用高德地图，只推荐真实存在的地点。</p>
        </div>
        <div class="how__item">
          <CloudSun :size="30" :stroke-width="1.6" class="how__ic" />
          <h3>天气查询</h3>
          <p>拉取未来几天的实时预报，行程跟着天气走。</p>
        </div>
        <div class="how__item">
          <BedDouble :size="30" :stroke-width="1.6" class="how__ic" />
          <h3>酒店推荐</h3>
          <p>按预算与住宿偏好筛选，标出距离与价格。</p>
        </div>
        <div class="how__item">
          <CalendarCheck :size="30" :stroke-width="1.6" class="how__ic" />
          <h3>行程规划</h3>
          <p>整合全部信息，生成含预算、三餐与建议的完整计划。</p>
        </div>
      </div>
      <p class="how__foot">
        底层：FastAPI × Vue3 × MCP 协议 × DeepSeek · 代码开源于
        <a href="https://github.com/Baicaicn23/trip-planner" target="_blank" rel="noopener">GitHub</a>
      </p>
    </section>

    <footer class="foot">
      <span>HelloAgents 智能旅行助手 · 本地演示</span>
      <span>数据来自高德地图真实接口</span>
    </footer>
  </div>
</template>

<script setup lang="ts">
// ══════════ Home · Apple 风浅色版（apple-web-design skill 首个应用） ══════════
// 设计：白底大留白 + #f5f5f7 交替节段 + 系统蓝交互色 + 胶囊按钮 + 弹簧动效。
// 业务逻辑不变：8 字段 → generateTripPlan → sessionStorage → /result。

import { computed, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { MapPin, CloudSun, BedDouble, CalendarCheck, Check } from 'lucide-vue-next'
import { generateTripPlan } from '@/services/api'
import type { TripFormData } from '@/types'

const TRANSPORT_OPTIONS = ['公共交通', '自驾', '步行', '混合'] as const
const STAY_OPTIONS = ['经济型酒店', '舒适型酒店', '豪华酒店', '民宿'] as const
const PREFERENCE_OPTIONS = ['历史文化', '自然风光', '美食', '购物', '艺术', '休闲'] as const

const router = useRouter()
const loading = ref(false)
const formSection = ref<HTMLElement | null>(null)
const howSection = ref<HTMLElement | null>(null)

const today = new Date().toISOString().slice(0, 10)

const formData = reactive<TripFormData>({
  city: '',
  start_date: '',
  end_date: '',
  travel_days: 1,
  transportation: '公共交通',
  accommodation: '经济型酒店',
  preferences: [],
  free_text_input: ''
})

const errors = reactive<Record<string, string>>({})

/* 规划进度模拟：节奏对齐后端四步串行流水线（约 7s/步）。
   阶段二接 SSE 真进度时，只需把 progressStep 改为由后端事件驱动。 */
const STEPS = [
  { icon: MapPin, label: '搜索景点' },
  { icon: CloudSun, label: '查询天气' },
  { icon: BedDouble, label: '推荐酒店' },
  { icon: CalendarCheck, label: '生成行程计划' }
]
const progressStep = ref(0) // 0~3=当前进行步，4=全部完成
let progressTimer: number | undefined
const progressPct = computed(() => Math.min((progressStep.value / 4) * 100, 100))

function startProgress() {
  progressStep.value = 0
  progressTimer = window.setInterval(() => {
    if (progressStep.value < 4) progressStep.value += 1
  }, 7000)
}
function finishProgress() {
  if (progressTimer) window.clearInterval(progressTimer)
  progressTimer = undefined
  progressStep.value = 4
}
function stepClass(i: number) {
  return {
    'is-done': i < progressStep.value,
    'is-doing': i === progressStep.value,
    'is-wait': i > progressStep.value
  }
}
function stateText(i: number) {
  if (i < progressStep.value) return '已完成'
  if (i === progressStep.value) return '进行中…'
  return '排队中'
}

function togglePreference(p: string) {
  const i = formData.preferences.indexOf(p)
  if (i >= 0) formData.preferences.splice(i, 1)
  else formData.preferences.push(p)
}

function scrollToForm() {
  formSection.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
function scrollToHow() {
  howSection.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

watch([() => formData.start_date, () => formData.end_date], ([s, e]) => {
  if (!s || !e) return
  const days = Math.round((+new Date(e) - +new Date(s)) / 86400000) + 1
  if (days > 30) {
    message.warning('最多规划 30 天：请把返回日期提前')
    formData.end_date = ''
  } else if (days <= 0) {
    message.warning('返回日期不能早于出发日期：请重新选择')
    formData.end_date = ''
  } else {
    formData.travel_days = days
  }
})

function validate(): boolean {
  errors.city = errors.start_date = errors.end_date = errors.form = ''
  if (!formData.city) errors.city = '填上目的地，我们才知道往哪查'
  if (!formData.start_date) errors.start_date = '选一下出发日期'
  if (!formData.end_date) errors.end_date = '选一下返回日期'
  return !errors.city && !errors.start_date && !errors.end_date
}

async function handleSubmit() {
  if (!validate()) return
  loading.value = true
  startProgress()
  try {
    const response = await generateTripPlan({ ...formData })
    finishProgress()
    if (response.success && response.data) {
      sessionStorage.setItem('tripPlan', JSON.stringify(response.data))
      router.push('/result')
    } else {
      errors.form = response.message || '生成失败，请重试'
    }
  } catch (err: any) {
    errors.form = err?.message || '网络出了问题：请确认后端已启动后重试'
  } finally {
    if (progressTimer) window.clearInterval(progressTimer)
    loading.value = false
  }
}
</script>

<style scoped>
/* ═══ Apple 风浅色 · token 见 ~/.zcode/skills/apple-web-design/references ═══ */
.home{background:#fff;color:#1d1d1f;min-height:100vh;
  font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Helvetica Neue",
  "PingFang SC","Microsoft YaHei",sans-serif;}
.home :deep(*),
.home{--ease-apple:cubic-bezier(.25,.1,.25,1);}

/* 毛玻璃导航栏 */
.nav{position:sticky;top:0;z-index:100;
  backdrop-filter:saturate(180%) blur(20px);-webkit-backdrop-filter:saturate(180%) blur(20px);
  background:rgba(255,255,255,.72);}
.nav__inner{display:flex;justify-content:space-between;align-items:center;
  height:52px;width:min(1200px,100% - 48px);margin:0 auto;}
.nav__brand{font-size:15px;font-weight:600;color:#1d1d1f;}
.nav__link{font-size:13px;color:#6e6e73;text-decoration:none;transition:color .25s var(--ease-apple);}
.nav__link:hover{color:#007AFF;}

/* Hero */
.hero{text-align:center;padding:110px 24px 96px;}
.hero__title{font-size:clamp(44px,6.5vw,72px);font-weight:700;line-height:1.08;
  letter-spacing:-.03em;color:#1d1d1f;margin:0 0 26px;}
.hero__sub{font-size:19px;line-height:1.65;color:#6e6e73;margin:0 auto 40px;max-width:36em;}
.hero__cta{display:flex;gap:14px;justify-content:center;flex-wrap:wrap;}

/* 胶囊按钮 */
.btn{border-radius:980px;border:0;cursor:pointer;font-family:inherit;
  font-size:16px;padding:13px 30px;
  transition:filter .25s var(--ease-apple),transform .25s var(--ease-apple);}
.btn:focus-visible{outline:2px solid #007AFF;outline-offset:3px;}
.btn--primary{background:#007AFF;color:#fff;}
.btn--primary:hover{filter:brightness(1.08);transform:translateY(-1px);}
.btn--secondary{background:#e8e8ed;color:#1d1d1f;}
.btn--secondary:hover{filter:brightness(.97);transform:translateY(-1px);}

/* 表单节段：#f5f5f7 交替底 + 白卡 */
.form-section{background:#f5f5f7;padding:88px 24px;}
.sheet{max-width:720px;margin:0 auto;background:#fff;border-radius:18px;
  box-shadow:0 4px 24px rgba(0,0,0,.06);padding:36px 40px 32px;
  animation:rise .7s var(--ease-ios,cubic-bezier(.32,.72,0,1)) both;}
.sheet__head{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:26px;}
.sheet__title{font-size:24px;font-weight:700;letter-spacing:-.02em;color:#1d1d1f;margin:0;}
.sheet__meta{font-size:13px;color:#86868b;}

.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px 24px;}
.field{display:flex;flex-direction:column;gap:8px;border:0;padding:0;margin:0;min-width:0;}
.field--full{grid-column:span 2;}
.field__label{font-size:13px;font-weight:500;color:#6e6e73;}
.field__input{background:rgba(120,120,128,.12);border:0;border-radius:12px;
  padding:12px 14px;font-size:15px;color:#1d1d1f;font-family:inherit;
  transition:box-shadow .25s var(--ease-apple);}
.field__input::placeholder{color:#86868b;}
.field__input:focus{outline:none;box-shadow:0 0 0 3.5px rgba(0,122,255,.28);background:#fff;}
input[type="date"].field__input{font-variant-numeric:tabular-nums;}
.field__err{font-size:12px;color:#FF3B30;}
.field__days{font-size:26px;font-weight:600;color:#1d1d1f;
  font-variant-numeric:tabular-nums;padding:6px 0;}
.field__days i{font-style:normal;font-size:13px;font-weight:400;color:#86868b;margin-left:6px;}

.seg{display:flex;gap:8px;flex-wrap:wrap;}
.seg__item{flex:1;min-width:64px;background:rgba(120,120,128,.12);border:0;
  border-radius:10px;color:#6e6e73;font-family:inherit;font-size:14px;
  padding:10px 4px;cursor:pointer;transition:all .25s var(--ease-apple);}
.seg__item:hover{background:rgba(120,120,128,.2);}
.seg__item.is-on{background:#007AFF;color:#fff;}
.seg__item:focus-visible{outline:2px solid #007AFF;outline-offset:2px;}

.chips{display:flex;gap:8px;flex-wrap:wrap;}
.chip{background:rgba(120,120,128,.12);border:0;border-radius:980px;
  color:#6e6e73;font-family:inherit;font-size:14px;padding:9px 18px;
  cursor:pointer;transition:all .25s var(--ease-apple);}
.chip:hover{background:rgba(120,120,128,.2);}
.chip.is-on{background:rgba(0,122,255,.14);color:#007AFF;font-weight:600;}
.chip:focus-visible{outline:2px solid #007AFF;outline-offset:2px;}

.go{margin-top:28px;width:100%;height:52px;border:0;border-radius:980px;
  background:#007AFF;color:#fff;font-family:inherit;font-size:17px;font-weight:600;
  cursor:pointer;transition:filter .25s var(--ease-apple),transform .25s var(--ease-apple);}
.go:hover:not(:disabled){filter:brightness(1.08);transform:translateY(-1px);}
.go:disabled{opacity:.6;cursor:progress;}
.go:focus-visible{outline:2px solid #007AFF;outline-offset:3px;}
.sheet__form-err{font-size:13px;color:#FF3B30;margin:12px 0 0;text-align:center;}

/* 规划进度卡 */
.steps{margin-top:20px;background:#f5f5f7;border-radius:14px;padding:6px 18px;
  animation:rise .5s var(--ease-apple) both;}
.step{display:flex;align-items:center;gap:12px;padding:12px 2px;
  border-bottom:1px solid rgba(60,60,67,.08);}
.step:nth-last-child(2){border-bottom:0;}
.step__icon{width:26px;height:26px;border-radius:50%;flex-shrink:0;
  display:flex;align-items:center;justify-content:center;
  background:rgba(120,120,128,.12);color:#86868b;transition:background .3s var(--ease-apple);}
.step.is-wait .step__label{color:#86868b;}
.step.is-doing .step__icon{background:rgba(0,122,255,.14);color:#007AFF;}
.step__spin{width:14px;height:14px;border-radius:50%;
  border:2px solid rgba(0,122,255,.25);border-top-color:#007AFF;
  animation:spin .8s linear infinite;}
.step.is-done .step__icon{background:#34C759;color:#fff;}
.step__check{animation:pop .4s var(--ease-apple) both;}
.step__label{flex:1;font-size:14px;color:#1d1d1f;transition:color .3s var(--ease-apple);}
.step__state{font-size:12px;color:#86868b;transition:color .3s var(--ease-apple);}
.step.is-doing .step__state{color:#007AFF;}
.step.is-done .step__state{color:#34C759;}
.steps__bar{height:4px;border-radius:980px;background:rgba(120,120,128,.16);
  margin:12px 2px 14px;overflow:hidden;}
.steps__fill{height:100%;background:#007AFF;border-radius:980px;
  transition:width .6s var(--ease-apple);}
@keyframes spin{to{transform:rotate(360deg);}}
@keyframes pop{0%{transform:scale(.3);opacity:0;}70%{transform:scale(1.18);}100%{transform:scale(1);opacity:1;}}

/* 工作原理 */
.how{padding:104px 24px;text-align:center;}
.how__title{font-size:clamp(30px,4vw,44px);font-weight:700;letter-spacing:-.02em;
  color:#1d1d1f;margin:0 0 16px;}
.how__sub{font-size:17px;line-height:1.65;color:#6e6e73;max-width:38em;margin:0 auto 64px;}
.how__row{display:grid;grid-template-columns:repeat(4,1fr);gap:32px;max-width:1120px;margin:0 auto;}
.how__item h3{font-size:17px;font-weight:600;color:#1d1d1f;margin:14px 0 8px;}
.how__item p{font-size:14px;line-height:1.7;color:#6e6e73;margin:0;}
.how__ic{color:#007AFF;}
.how__foot{margin-top:72px;font-size:13px;color:#86868b;}
.how__foot a{color:#007AFF;text-decoration:none;}
.how__foot a:hover{text-decoration:underline;}

.foot{background:#f5f5f7;padding:28px 24px;display:flex;justify-content:space-between;
  gap:12px;flex-wrap:wrap;font-size:12px;color:#86868b;
  width:min(1200px,100% - 48px);margin:0 auto;}

@keyframes rise{from{opacity:0;transform:translateY(20px);}to{opacity:1;transform:none;}}

@media (prefers-reduced-motion:reduce){
  .sheet{animation:none;}
  .btn,.go,.seg__item,.chip{transition:none;}
}
@media (max-width:900px){
  .hero{padding:72px 20px 64px;}
  .how__row{grid-template-columns:repeat(2,1fr);}
  .sheet{padding:28px 22px;}
}
@media (max-width:560px){
  .grid{grid-template-columns:1fr;}
  .field--full{grid-column:auto;}
  .how__row{grid-template-columns:1fr;}
}
</style>
