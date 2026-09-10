<template>
  <div class="portal" :class="{ 'no-webgl': !webglOk }">
    <!-- 呼吸色场：全屏 WebGL 片元着色器（降级=静态曙光渐变） -->
    <canvas ref="glCanvas" class="portal__field" aria-hidden="true"></canvas>

    <!-- 角标：细字身份条 -->
    <header class="portal__corners">
      <span class="brand">
        HELLOAGENTS<i class="brand__dot"></i>
        <span class="brand__cn">智能旅行助手</span>
      </span>
      <span class="corner-note">LOCAL DEMO · :8000</span>
    </header>

    <!-- 主区：超大单字 + 细字规格 + 悬浮表单 -->
    <main class="portal__stage">
      <section class="portal__copy">
        <h1 class="portal__title">出发<span class="portal__period">。</span></h1>
        <p class="portal__sub">告诉我你想去哪。四个 AI 专员，二十八秒，一份完整行程。</p>
        <ul class="portal__spec" aria-label="系统规格">
          <li>04 AGENTS · 串行流水线</li>
          <li>16 MAP TOOLS · 高德 MCP</li>
          <li>~28S · 完整行程生成</li>
        </ul>
      </section>

      <form class="sheet" novalidate @submit.prevent="handleSubmit">
        <div class="sheet__head">
          <span class="sheet__no">FORM · 8 FIELDS</span>
          <span class="sheet__title">旅行申请表</span>
        </div>

        <div class="grid">
          <label class="field field--wide-name">
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

          <fieldset class="field field--seg">
            <legend class="field__label">交通方式</legend>
            <div class="seg">
              <button
                v-for="t in TRANSPORT_OPTIONS" :key="t" type="button"
                class="seg__item" :class="{ 'is-on': formData.transportation === t }"
                @click="formData.transportation = t"
              >{{ t }}</button>
            </div>
          </fieldset>

          <fieldset class="field field--seg">
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

        <button type="submit" class="go" :class="{ 'is-busy': loading }" :disabled="loading">
          <span v-if="!loading">开始规划</span>
          <span v-else>规划中 · 四专员出动</span>
        </button>
        <p v-if="errors.form" class="sheet__form-err">{{ errors.form }}</p>
      </form>
    </main>

    <footer class="portal__foot">
      <span>FastAPI × Vue3 × MCP</span>
      <span>四 Agent 流水线 · 数据来自高德地图真实接口</span>
    </footer>
  </div>
</template>

<script setup lang="ts">
// ══════════ Home · 着色器门户 ══════════
// 世界：全屏呼吸色场（WebGL 片元着色器）上浮细字表单；光标搅动色场；
// 提交后呼吸加速——为阶段二 SSE 真进度预留「色场渐亮=四Agent进度」的接口。
// 业务逻辑与原版一致：8 字段 → generateTripPlan → sessionStorage → /result。

import { onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { generateTripPlan } from '@/services/api'
import type { TripFormData } from '@/types'
import '@fontsource-variable/spline-sans-mono'
import '@fontsource/noto-sans-sc/900.css'

const TRANSPORT_OPTIONS = ['公共交通', '自驾', '步行', '混合'] as const
const STAY_OPTIONS = ['经济型酒店', '舒适型酒店', '豪华酒店', '民宿'] as const
const PREFERENCE_OPTIONS = ['历史文化', '自然风光', '美食', '购物', '艺术', '休闲'] as const

const router = useRouter()
const loading = ref(false)
const webglOk = ref(true)
const glCanvas = ref<HTMLCanvasElement | null>(null)

const today = new Date().toISOString().slice(0, 10)

// 表单状态：日期用原生 date 控件（字符串 YYYY-MM-DD），省掉 Dayjs 转换层
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

function togglePreference(p: string) {
  const i = formData.preferences.indexOf(p)
  if (i >= 0) formData.preferences.splice(i, 1)
  else formData.preferences.push(p)
}

// 日期联动：自动算天数；越界给出指明问题与恢复方式的人话提示
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
  shaderSpeedTarget = 2.4 // 呼吸加速：色场开始「天亮」
  try {
    const response = await generateTripPlan({ ...formData })
    if (response.success && response.data) {
      sessionStorage.setItem('tripPlan', JSON.stringify(response.data))
      router.push('/result')
    } else {
      errors.form = response.message || '生成失败，请重试'
    }
  } catch (err: any) {
    errors.form = err?.message || '网络出了问题：请确认后端已启动后重试'
  } finally {
    loading.value = false
    shaderSpeedTarget = 1
  }
}

/* ─────────── 呼吸色场（WebGL 片元着色器） ─────────── */
let raf = 0
let gl: WebGLRenderingContext | null = null
let uTime: WebGLUniformLocation | null = null
let uMouse: WebGLUniformLocation | null = null
let uSpeed: WebGLUniformLocation | null = null
let uRes: WebGLUniformLocation | null = null
let shaderSpeed = 1
let shaderSpeedTarget = 1
let mx = 0.5, my = 0.5, tmx = 0.5, tmy = 0.5

const VERT = 'attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}'
const FRAG = `
precision highp float;
uniform vec2 uRes;uniform float uTime;uniform vec2 uMouse;uniform float uSpeed;
float hash(vec2 v){return fract(sin(dot(v,vec2(127.1,311.7)))*43758.5453);}
float noise(vec2 v){vec2 i=floor(v),f=fract(v);f=f*f*(3.-2.*f);
  return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);}
float fbm(vec2 v){float s=0.,a=.5;for(int i=0;i<5;i++){s+=a*noise(v);v*=2.03;a*=.5;}return s;}
void main(){
  vec2 p=(gl_FragCoord.xy-.5*uRes)/uRes.y;
  vec2 m=(uMouse-.5)*vec2(uRes.x/uRes.y,1.);
  float md=length(p-m);
  p+=(p-m)*.10*exp(-md*3.2);
  float t=uTime*.028*uSpeed;
  float n1=fbm(p*1.7+vec2(t,-t*.6));
  float n2=fbm(p*3.4-vec2(t*.7,t*.35)+n1);
  float dawn=smoothstep(.32,.88,n1*n2*2.0);
  vec3 base=vec3(.031,.047,.090);
  vec3 cool=vec3(.13,.24,.38);
  vec3 warm=vec3(1.0,.42,.23);
  vec3 col=base+cool*n2*.30+warm*dawn*.38*uSpeed*.62;
  col+=(hash(gl_FragCoord.xy+uTime)-.5)*.030;
  gl_FragColor=vec4(col,1.);
}`

function initShader() {
  const canvas = glCanvas.value
  if (!canvas) return
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches
  gl = canvas.getContext('webgl', { antialias: false, alpha: false })
  if (!gl) { webglOk.value = false; return }

  const prog = gl.createProgram()!
  for (const [type, src] of [
    [gl.VERTEX_SHADER, VERT],
    [gl.FRAGMENT_SHADER, FRAG]
  ] as const) {
    const s = gl.createShader(type)!
    gl.shaderSource(s, src)
    gl.compileShader(s)
    gl.attachShader(prog, s)
  }
  gl.linkProgram(prog)
  gl.useProgram(prog)

  const buf = gl.createBuffer()
  gl.bindBuffer(gl.ARRAY_BUFFER, buf)
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW)
  const loc = gl.getAttribLocation(prog, 'p')
  gl.enableVertexAttribArray(loc)
  gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0)

  uTime = gl.getUniformLocation(prog, 'uTime')
  uMouse = gl.getUniformLocation(prog, 'uMouse')
  uSpeed = gl.getUniformLocation(prog, 'uSpeed')
  uRes = gl.getUniformLocation(prog, 'uRes')

  function resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, window.innerWidth < 768 ? 1 : 1.5)
    canvas!.width = Math.floor(window.innerWidth * dpr)
    canvas!.height = Math.floor(window.innerHeight * dpr)
    gl!.viewport(0, 0, canvas!.width, canvas!.height)
  }
  resize()
  addEventListener('resize', resize)
  const onMove = (e: PointerEvent) => {
    tmx = e.clientX / window.innerWidth
    tmy = 1 - e.clientY / window.innerHeight
  }
  addEventListener('pointermove', onMove)

  if (reduced) {
    // 减少动效：只渲染一帧静态色场
    gl.uniform2f(uRes!, canvas.width, canvas.height)
    gl.uniform1f(uTime!, 40)
    gl.uniform2f(uMouse!, 0.5, 0.5)
    gl.uniform1f(uSpeed!, 1)
    gl.drawArrays(gl.TRIANGLES, 0, 3)
    return
  }
  const t0 = performance.now()
  function frame(now: number) {
    shaderSpeed += (shaderSpeedTarget - shaderSpeed) * 0.02
    mx += (tmx - mx) * 0.05
    my += (tmy - my) * 0.05
    gl!.uniform1f(uTime!, (now - t0) / 1000)
    gl!.uniform2f(uMouse!, mx, my)
    gl!.uniform1f(uSpeed!, shaderSpeed)
    gl!.uniform2f(uRes!, canvas!.width, canvas!.height)
    gl!.drawArrays(gl.TRIANGLES, 0, 3)
    raf = requestAnimationFrame(frame)
  }
  raf = requestAnimationFrame(frame)
}

onMounted(initShader)
onBeforeUnmount(() => { cancelAnimationFrame(raf) })
</script>

<style scoped>
/* 世界：着色器门户。深单色场 + 细字白 + 炽热橙 hover。桌面优先。 */
.portal{position:relative;min-height:100vh;display:flex;flex-direction:column;
  background:#0a0e1a;color:#e8ecf4;overflow:hidden;}
.portal__field{position:fixed;inset:0;width:100%;height:100%;display:block;}
.portal.no-webgl .portal__field{display:none;}
.portal.no-webgl{background:
  radial-gradient(120% 90% at 70% 10%,#2a1c10 0%,transparent 55%),
  radial-gradient(90% 80% at 20% 90%,#12243c 0%,transparent 60%),#0a0e1a;}

/* 细字标签：等宽 tracked（世界的语法） */
.brand,.corner-note,.portal__spec li,.portal__foot,.sheet__no{
  font-family:'Spline Sans Mono Variable',ui-monospace,Menlo,monospace;
  font-size:11px;letter-spacing:.32em;text-transform:uppercase;color:rgba(232,236,244,.72);}
.brand__cn{font-family:'PingFang SC','Microsoft YaHei',sans-serif;letter-spacing:.5em;
  font-size:12px;color:rgba(232,236,244,.6);margin-left:.4em;}
.brand__dot{display:inline-block;width:6px;height:6px;border-radius:50%;
  background:#ff7a45;margin:0 .9em .1em .9em;vertical-align:middle;}

.portal__corners{position:relative;z-index:2;display:flex;justify-content:space-between;
  align-items:center;flex-wrap:wrap;gap:8px;padding:26px 40px;}

.portal__stage{position:relative;z-index:1;flex:1;display:grid;
  grid-template-columns:minmax(0,1.05fr) minmax(360px,480px);gap:48px;
  align-items:center;width:min(1240px,100% - 80px);margin:0 auto;padding:24px 0 48px;}

/* 超大单字（世界语法：oversized display） */
.portal__title{font-family:'Noto Sans SC','PingFang SC',sans-serif;font-weight:900;
  font-size:min(11vw,150px);line-height:1.02;letter-spacing:-.02em;
  color:#f2f5fa;margin:0 0 22px;
  animation:dawn 1.6s cubic-bezier(.16,1,.3,1) both;}
.portal__period{color:#ff7a45;}
.portal__sub{font-size:17px;line-height:1.9;color:rgba(232,236,244,.82);
  max-width:34em;margin:0 0 30px;animation:dawn 1.6s .15s cubic-bezier(.16,1,.3,1) both;}
.portal__spec{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:10px;
  animation:dawn 1.6s .3s cubic-bezier(.16,1,.3,1) both;}
.portal__spec li::before{content:'';display:inline-block;width:18px;height:1px;
  background:#ff7a45;vertical-align:middle;margin-right:14px;}

/* 悬浮表单：backdrop-blur 是功能性的——保证色场亮区扫过时文字可读 */
.sheet{position:relative;border:1px solid rgba(232,236,244,.14);border-radius:4px;
  background:rgba(10,14,26,.55);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);
  box-shadow:0 24px 60px rgba(0,0,0,.45);padding:26px 28px 24px;
  animation:rise 1.1s .35s cubic-bezier(.16,1,.3,1) both;}
.sheet__head{display:flex;justify-content:space-between;align-items:baseline;
  border-bottom:1px solid rgba(232,236,244,.14);padding-bottom:12px;margin-bottom:20px;}
.sheet__title{font-family:'PingFang SC',sans-serif;font-size:17px;font-weight:700;color:#f2f5fa;}

.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px 20px;}
.field{display:flex;flex-direction:column;gap:8px;border:0;padding:0;margin:0;min-width:0;}
.field--wide-name{grid-column:span 2;}
.field--full{grid-column:span 2;}
.field__label{font-family:'PingFang SC',sans-serif;font-size:12px;
  color:rgba(232,236,244,.72);letter-spacing:.08em;}
.field__input{background:transparent;border:0;border-bottom:1px solid rgba(232,236,244,.28);
  color:#eef2f8;font-size:15px;padding:7px 2px;caret-color:#ff7a45;border-radius:0;
  font-family:inherit;transition:border-color .2s;}
.field__input::placeholder{color:rgba(232,236,244,.62);}
.field__input:hover{border-bottom-color:rgba(232,236,244,.5);}
.field__input:focus{outline:none;border-bottom-color:#ff7a45;
  box-shadow:0 1px 0 0 #ff7a45;}
input[type="date"].field__input{font-family:'Spline Sans Mono Variable',Menlo,monospace;
  font-size:14px;letter-spacing:.02em;}
input[type="date"].field__input::-webkit-calendar-picker-indicator{
  filter:invert(.85) sepia(.3);cursor:pointer;}
.field__err{font-family:'PingFang SC',sans-serif;font-size:12px;color:#ffb08f;}
.field__days{font-family:'Spline Sans Mono Variable',Menlo,monospace;font-size:26px;
  color:#f2f5fa;line-height:1.15;}
.field__days i{font-family:'PingFang SC',sans-serif;font-style:normal;font-size:12px;
  color:rgba(232,236,244,.6);margin-left:6px;letter-spacing:.2em;}

.seg{display:flex;gap:6px;flex-wrap:wrap;}
.seg__item{flex:1;min-width:64px;background:transparent;border:1px solid rgba(232,236,244,.2);
  color:rgba(232,236,244,.75);font-family:'PingFang SC',sans-serif;font-size:13px;
  padding:8px 4px;cursor:pointer;border-radius:2px;transition:all .18s;}
.seg__item:hover{border-color:rgba(232,236,244,.5);color:#eef2f8;}
.seg__item.is-on{border-color:#ff7a45;color:#ff9d6b;background:rgba(255,122,69,.08);}
.seg__item:focus-visible{outline:2px solid #ff7a45;outline-offset:2px;}

.chips{display:flex;gap:8px;flex-wrap:wrap;}
.chip{display:inline-flex;align-items:center;gap:8px;background:transparent;
  border:1px solid rgba(232,236,244,.2);color:rgba(232,236,244,.75);
  font-family:'PingFang SC',sans-serif;font-size:13px;padding:8px 14px;
  cursor:pointer;border-radius:999px;transition:all .18s;}
.chip::before{content:'';width:6px;height:6px;border-radius:50%;
  border:1px solid rgba(232,236,244,.5);transition:all .18s;}
.chip:hover{border-color:rgba(232,236,244,.5);color:#eef2f8;}
.chip.is-on{border-color:#ff7a45;color:#ff9d6b;}
.chip.is-on::before{background:#ff7a45;border-color:#ff7a45;}
.chip:focus-visible{outline:2px solid #ff7a45;outline-offset:2px;}

.go{margin-top:22px;width:100%;height:52px;background:transparent;
  border:1px solid rgba(232,236,244,.4);border-radius:3px;color:#f2f5fa;
  font-family:'Noto Sans SC','PingFang SC',sans-serif;font-size:16px;font-weight:700;letter-spacing:.35em;
  cursor:pointer;transition:all .25s;}
.go:hover:not(:disabled){background:#ff7a45;border-color:#ff7a45;color:#0a0e1a;}
.go:focus-visible{outline:2px solid #ff7a45;outline-offset:3px;}
.go:disabled{opacity:.6;cursor:progress;animation:breath 1.6s ease-in-out infinite;}
.sheet__form-err{font-family:'PingFang SC',sans-serif;font-size:13px;
  color:#ffb08f;margin:12px 0 0;text-align:center;}

.portal__foot{position:relative;z-index:1;display:flex;justify-content:space-between;
  gap:16px;flex-wrap:wrap;padding:20px 40px;border-top:1px solid rgba(232,236,244,.1);
  color:rgba(232,236,244,.66);}

/* 唯一的运动时刻：黎明渐显 + 上浮 */
@keyframes dawn{from{opacity:0;transform:translateY(14px);filter:blur(6px);}
  to{opacity:1;transform:none;filter:none;}}
@keyframes rise{from{opacity:0;transform:translateY(24px);}
  to{opacity:1;transform:none;}}
@keyframes breath{0%,100%{opacity:.45;}50%{opacity:.85;}}

@media (prefers-reduced-motion: reduce){
  .portal__title,.portal__sub,.portal__spec,.sheet{animation:none;}
  .go:disabled{animation:none;}
}
@media (max-width: 960px){
  .portal__stage{grid-template-columns:1fr;gap:30px;width:calc(100% - 40px);padding-top:8px;}
  .portal__title{font-size:64px;}
  .portal__corners{padding:20px 20px;}
  .portal__foot{padding:16px 20px;}
}
@media (max-width: 560px){
  .grid{grid-template-columns:1fr;}
  .field--wide-name,.field--full{grid-column:auto;}
  .portal__title{font-size:52px;}
  .corner-note{display:none;}
  .brand__cn{letter-spacing:.2em;}
}
</style>
