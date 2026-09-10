---
name: HelloAgents 智能旅行助手
description: 着色器门户——会呼吸的黎明色场上浮细字表单，四 Agent 流水线的入口世界
colors:
  ink: "#0a0e1a"
  mist: "#e8ecf4"
  bright: "#f2f5fa"
  input-white: "#eef2f8"
  ember: "#ff7a45"
  ember-text: "#ff9d6b"
  ember-error: "#ffb08f"
  hairline: "rgba(232, 236, 244, 0.14)"
typography:
  display:
    fontFamily: "'Noto Sans SC', 'PingFang SC', sans-serif"
    fontSize: "min(11vw, 150px)"
    fontWeight: 900
    lineHeight: 1.02
    letterSpacing: "-0.02em"
  body:
    fontFamily: "'PingFang SC', 'Microsoft YaHei', sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.9
  mono:
    fontFamily: "'Spline Sans Mono Variable', ui-monospace, Menlo, monospace"
    fontSize: "11px"
    fontWeight: 400
    letterSpacing: "0.32em"
  numeral:
    fontFamily: "'Spline Sans Mono Variable', ui-monospace, Menlo, monospace"
    fontSize: "26px"
    lineHeight: 1.15
rounded:
  hair: "2px"
  tight: "3px"
  card: "4px"
  pill: "999px"
spacing:
  hair: "8px"
  xs: "10px"
  sm: "18px"
  md: "20px"
  lg: "26px"
  xl: "40px"
  xxl: "48px"
components:
  button-primary:
    backgroundColor: "transparent"
    textColor: "{colors.bright}"
    typography: "700 16px/1 'Noto Sans SC', 'PingFang SC', sans-serif"
    rounded: "{rounded.tight}"
    height: "52px"
    width: "100%"
  button-primary-hover:
    backgroundColor: "{colors.ember}"
    textColor: "{colors.ink}"
  input-underline:
    backgroundColor: "transparent"
    textColor: "{colors.input-white}"
    rounded: "0"
    padding: "7px 2px"
  chip:
    backgroundColor: "transparent"
    textColor: "rgba(232, 236, 244, 0.75)"
    rounded: "{rounded.pill}"
    padding: "8px 14px"
  chip-selected:
    backgroundColor: "transparent"
    textColor: "{colors.ember-text}"
  segment-selected:
    backgroundColor: "rgba(255, 122, 69, 0.08)"
    textColor: "{colors.ember-text}"
    rounded: "{rounded.hair}"
    padding: "8px 4px"
  card-sheet:
    backgroundColor: "rgba(10, 14, 26, 0.55)"
    textColor: "{colors.mist}"
    rounded: "{rounded.card}"
    padding: "26px 28px 24px"
---

# Design System: HelloAgents 智能旅行助手

## Overview

**Creative North Star: "着色器门户（The Breathing Shader Portal）"**

整个世界立在一片**会呼吸的黎明色场**上：全屏 WebGL 片元着色器渲染深海军夜色，fbm 噪声缓慢起伏，光标搅动色场，提交表单后呼吸加速——色场逐渐"天亮"。所有 UI 都是这个活色场上的**细字浮层**：细体等宽元数据、细下划线输入、细边控件，克制的炽热橙只出现在"状态"上。真实感压倒装饰感：表单是唯一的主体，色场是唯一的氛围。

这不是安静的静态页面——背景永远在活着。因此所有可读性决策都服务于同一件事：**在色场亮区扫过时，文字仍必须清晰**。这解释了浮层卡的 backdrop-blur（功能性，非装饰）、三种白的最亮一档用于标题、以及 accent 以"状态点染"而非大面积平涂的方式使用。

**适用范围（当前边界）**：本系统目前只覆盖 **Home 首屏**（`/`，世界的第一个已验证表面，disposition: ship）。`App.vue` 中 `route.name === 'Home'` 直接渲染 router-view（不套壳）；**Result 页仍为旧世界**（Ant Design 旧壳 `#001529`），属阶段一第二步的迁移对象——这是已声明的适用范围，不是本文件的遗漏。为新表面生成设计时遵循本文件；不要从 Result 页提取任何值。

**Key Characteristics:**
- 全屏活色场（WebGL shader）打底，UI 以细字浮层悬于其上
- 单一 accent：炽热橙 #ff7a45，只做状态（焦点/选中/hover/caret/选区）
- 细字等宽元数据语法：11px / .32em / 大写，承载真实信息
- 细线形体：1px 低alpha白线 + 2–4px 近直角圆角，唯一 pill 是偏好 chips
- 唯一授权的大动效时刻：黎明 stagger 渐显；其余全部 ≤0.25s 状态过渡
- 浏览器原生部件（选区/滚动条/焦点环/caret）一并主题化进这个世界

## Colors

深海军夜色底上一组冷白，加唯一一把火：炽热橙。暖色不在 CSS 调色板里——黎明暖区由着色器程序化生成。

### Primary
- **炽热橙 Ember** (#ff7a45)：全系统唯一 accent。用途全部是"状态与引导"：表单句号、品牌圆点、规格刻度线、输入焦点下划线、caret、::selection 底色、seg/chip 选中描边、主按钮 hover 填充、focus-visible 焦点环。它标记"可交互与正在发生"，从不作为静态装饰平涂。

### Neutral
- **夜幕 Ink** (#0a0e1a)：世界基底。页面底色、::selection 上的文字色、主按钮 hover 上的文字色、滚动条轨道色。
- **细字白 Mist** (#e8ecf4)：正文与标签基色；其 alpha 序列（0.10–0.75）是全部边线、分隔线、占位符、次级标签的实际材料。
- **高亮白 Bright** (#f2f5fa)：标题、表单卡标题、天数读数、主按钮文字——需要从色场亮区里跳出来的字。
- **输入白 Input White** (#eef2f8)：输入框文字与控件 hover 态文字。
- **暖橙文 Ember Text** (#ff9d6b)：选中 seg/chip 的文字色——accent 在深底上做正文级小字时的提亮变体。
- **错误暖橙 Ember Error** (#ffb08f)：表单校验与提交错误文案。错误不引入红色系，仍是这把火的柔和档。

### Named Rules
**The Single Ember Rule.** 全世界只有一把火（#ff7a45 及其两个文字变体）。任何新颜色进入前先回答：它是不是一种"状态"？不是，就没有颜色。

**The Dawn is Procedural Rule.** 黎明暖区只属于着色器程序（shader 常量 warm ≈ vec3(1.0, .42, .23)），不是固定 UI 色值。禁止把 shader 色抄成 CSS 颜色当第二 accent 用；CSS 里的暖橙只有上表三枚。

## Typography

**Display Font:** Noto Sans SC 900（自托管 @fontsource/noto-sans-sc/900.css 分片；回退 PingFang SC）
**Body Font:** PingFang SC 系统栈（中文正文，不自托管）
**Label/Mono Font:** Spline Sans Mono Variable（自托管 @fontsource-variable/spline-sans-mono；拉丁/数字专用）

**Character:** 900 重黑中文单字与 11px 疏排等宽小字构成极大/极小的两极——投屏 30 秒内，超大单字给冲击力，tracked mono 给"工程仪器"的可信感。中间地带全部交给系统 PingFang，克制而不抢戏。

### Hierarchy
- **Display**（Noto Sans SC 900，min(11vw, 150px)，行高 1.02，字距 -0.02em）：首屏唯一超大单字"出发。"，句号用 ember。一个表面至多一个。
- **Body**（PingFang SC 400，17px，行高 1.9）：副标题、说明文；最大宽度 34em。
- **UI**（PingFang SC，12–13px，字距 0.08em 用于标签）：字段标签 12px、seg/chip 13px、卡标题 17px/700、错误 12–13px。
- **Label/Mono**（Spline Sans Mono Variable，11px，字距 0.32em，大写，rgba(232,236,244,.72)）：品牌角标、环境注记（LOCAL DEMO · :8000）、系统规格、页脚、表单编号——只承载真实元数据。
- **Numeral**（mono，26px/1.15 用于天数读数；14px/.02em 用于日期输入）：一切"数据读出"用等宽。

### Named Rules
**The Tracked Mono Rule.** 拉丁字母与数字只以疏排等宽（.32em 小字语法）出现，且必须携带真实信息（数量、端口、时长、字段数）；没有信息量的装饰性 mono 标签不存在于这个世界。中文永远不用等宽，用 PingFang。

## Layout

桌面优先（基准 1440，演示场景投屏），两栏网格：`minmax(0, 1.05fr) / minmax(360px, 480px)`，列距 48px，舞台宽 `min(1240px, 100% - 80px)` 居中。左栏 = 超大单字 + 副题 + 规格清单；右栏 = 悬浮表单卡。页面骨架是纵向 flex：角标头（padding 26px 40px）→ 弹性舞台 → 细线页脚（padding 20px 40px，上缘 1px 分隔线）。

表单内部：双列网格，行距 18px 列距 20px；目的地与整行字段跨两列。间距实际使用的阶梯只有 8 / 10 / 18 / 20 / 26 / 40 / 48px。

响应式：≤960px 落为单列（标题 64px，舞台 `calc(100% - 40px)`）；≤560px 表单单列（标题 52px，隐藏角落注记，中文品牌字距收紧至 .2em）。着色器 DPR 上限：窄于 768px 用 1，否则 1.5（性能护栏）。

## Elevation & Depth

这个系统的深度不靠堆叠阴影层次，靠**活的背景 vs 悬浮的 UI** 这一层关系本身。唯一的实体阴影在表单卡上（`0 24px 60px rgba(0,0,0,.45)`），作用是把浮层从发光色场上"托起"。焦点深度用 2px ember 外描环（offset 2–3px），输入焦点用 1px ember 下划线加同色 0 1px 0 贴影。其余全部平面细线。

### Shadow Vocabulary
- **浮层托底**（`0 24px 60px rgba(0,0,0,.45)`）：仅表单卡等悬于色场之上的容器。
- **焦点贴影**（`0 1px 0 0 #ff7a45`）：仅下划线输入框获得焦点时，与 border-bottom 叠加成 2px 视觉线。

### Named Rules
**The Functional Blur Rule.** backdrop-blur(14px) + rgba(10,14,26,.55) 底只出现在"必须压住色场亮区保可读"的浮层上（webgl 不可用降级时同样保留）。它是可读性装置，禁止当毛玻璃装饰挪用到按钮、chip 或页面上。

## Shapes

近直角的细线形体。圆角阶梯：2px（seg 项）、3px（主按钮）、4px（卡片）、999px（偏好 chip 唯一 pill）；圆点（品牌点、chip 内指示点）是仅有的正圆。全部结构线是 1px：卡片边与分隔线 alpha 0.14，控件边 0.20，输入下划线 0.28，主按钮边 0.40——需要更强的存在感时提 alpha，不加粗。

### Named Rules
**The Hairline Rule.** 一切结构都是 1px 低alpha白线（0.10–0.40）。禁止 2px 以上实线边框、禁止块状描边；强调靠颜色变化（转 ember），不靠线宽。

## Components

### 主按钮 Go
- **Shape:** 近直角（3px），全宽，高 52px
- **Primary:** 透明底 + 0.40 alpha 白细边 + 高亮白字，Noto Sans SC 700 16px，字距 .35em（疏排中文是刻意的仪式感）
- **Hover:** 整钮转炽热橙（#ff7a45 底、夜幕色字、同色边）——全系统唯一的大面积 accent 填充，且只作为响应出现
- **Focus:** 2px ember outline，offset 3px；**Disabled:** 透明度 .6 + breath 呼吸动画（1.6s ease-in-out，opacity .45–.85），cursor: progress
- **忙碌文案：**「规划中 · 四专员出动」——按钮文案参与叙事

### 输入框 / 字段（下划线输入）
- **Style:** 全透明底、无边框、仅 1px 底线（alpha 0.28），0 圆角，padding 7px 2px；caret 炽热橙
- **Hover:** 底线提亮至 alpha 0.5；**Focus:** 底线转 ember + `0 1px 0 0` 贴影
- **Placeholder:** alpha 0.62；**Error:** 字段下方 12px 暖橙错误文案，说人话并指明恢复方式
- 日期输入用原生 date 控件但穿 mono 外衣（14px/.02em），日历图标 `filter: invert(.85) sepia(.3)` 调成世界色调

### Segments（交通/住宿单选）
- **Style:** 透明底 1px 细边（alpha 0.20），2px 圆角，13px PingFang，padding 8px 4px，等分排布
- **选中态:** ember 描边 + ember 文字变体（#ff9d6b）+ 8% ember 染底；**Hover:** 边与字提亮；**Focus:** 2px ember outline offset 2px

### Chips（旅行偏好多选）
- **Style:** 唯一 pill（999px），透明底细边，padding 8px 14px，内置 6px 空心圆指示点
- **选中态:** ember 边与文字，指示点实心填充 ember——状态读法与 seg 一致，形态区分单选/多选

### 卡片 / 容器（Sheet 悬浮表单卡）
- **Corner Style:** 4px；**Border:** 1px alpha 0.14 白线；**Background:** rgba(10,14,26,.55) + backdrop-blur 14px
- **Shadow:** 浮层托底（见 Elevation）；**Internal Padding:** 26px 28px 24px
- 头部：左侧 mono 编号（FORM · 8 FIELDS）+ 右侧 17px/700 卡标题，底部 1px 分隔线——"仪器面板"的读法

### 签名组件：呼吸色场（Breathing Field）
全屏 fixed WebGL 画布（`aria-hidden`），fbm 噪声黎明色场：基色 ≈ vec3(.031,.047,.090)，冷区 ≈ vec3(.13,.24,.38)，暖区 ≈ vec3(1.0,.42,.23)——三者均为**着色器程序常量，非 UI token**。光标位置以 0.05/帧 lerp 搅动场；`uSpeed` 默认 1，提交后目标 2.4（0.02/帧缓动）——"色场渐亮 = 四 Agent 进度"是预留接口。叠加 ±0.015 噪声颗粒防色带。降级链：无 WebGL → 静态曙光径向渐变（#2a1c10 暖区 / #12243c 冷区叠 #0a0e1a，一次性降级值，非 token）；`prefers-reduced-motion` → 只渲染一帧静态场（uTime=40）。入场时刻（全站唯一授权动效）：**黎明 stagger**——标题/副题/规格依次 dawn（1.6s cubic-bezier(.16,1,.3,1)：透明度 0→1、上移 14px、blur 6px→0，延迟 0/.15s/.3s），表单卡 rise（1.1s 同缓动，延迟 .35s，上移 24px）。

## Do's and Don'ts

### Do:
- **Do** 让一切新表面直接立在色场/夜幕基底（#0a0e1a）上，UI 以细字浮层出现；先问"它在色场的哪一层"，再排版。
- **Do** 把浏览器原生部件一起主题化：`::selection` ember 底夜幕字、`scrollbar-color`（alpha 0.3 白 / #0a0e1a）、`caret-color` ember、`:focus-visible` 2px ember 外描环——原生部件不在世界之外。
- **Do** 完整兑现 `prefers-reduced-motion: reduce`：入场/呼吸/呼吸加速全关，着色器只渲染一帧。
- **Do** 用颜色表达强调：状态转 ember、hover 转 ember 填充、文字提亮档（#ff9d6b/#ffb08f）承接深底小字。
- **Do** 让文案参与系统叙事（按钮忙碌态「规划中 · 四专员出动」、错误提示指明恢复方式）。

### Don't:
- **Don't** 引入第二个 accent 色相；暖调只由着色器程序生成，禁止把 shader 暖色抄成 CSS 固定色。
- **Don't** 增加第二种入场/大动效语法——黎明 stagger 是唯一授权时刻，其余交互动效 ≤0.25s。
- **Don't** 把 backdrop-blur 当风格挪用；它只属于"压住色场保可读"的浮层。
- **Don't** 使用粗边框、硬投影、渐变按钮等与细线形体冲突的部件；线宽永远 1px，强调靠颜色。
- **Don't** 从 Result 页（旧世界 Ant Design 壳，#001529）提取任何样式进新表面；旧壳待阶段一第二步统一迁移。
