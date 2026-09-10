// ══════════ 前端"开机键" —— 整个店面的总开关 ══════════
// 【干什么用】三步：①创建Vue应用 ②注册路由表（网址↔页面的对应关系）③挂到index.html的#app上。
// 【类比】苍穹外卖管理端的 main.js：所有Vue项目都长这样——装插件、建路由、挂载，三件套。
// 【读法】路由表 = "门牌号→房间"的登记册：访问 / 显示Home表单页，访问 /result 显示结果页。

import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import App from './App.vue'
import Home from './views/Home.vue'
import Result from './views/Result.vue'

// 路由表：本店只有两个房间
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',          // 门牌号：首页
      name: 'Home',
      component: Home     // 房间里住着：表单页
    },
    {
      path: '/result',    // 门牌号：结果页（规划完成后跳过来）
      name: 'Result',
      component: Result
    }
  ]
})

const app = createApp(App)

app.use(router)   // 装上路由：页面可以互相跳转
app.use(Antd)     // 装上Ant Design组件库：a-card/a-form/a-button都是它提供的

app.mount('#app') // 把应用挂到 index.html 里那个 <div id="app"> 上——从此页面活了
