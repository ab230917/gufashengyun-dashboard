# 舞号门羽行韵 · 销售目标看板（前端源码）

纯静态看板，无需构建、无依赖，双击 index.html 即可本地打开查看。

## 数据加载与刷新

- 线上通过 `fetch + no-store` 动态加载 `data.js`，自动绕过 GitHub Pages 缓存（修复了旧版固定版本号导致的一直“数据加载中”问题）
- 本地双击打开（file://）时自动降级为传统 script 标签加载
- 页面每 10 分钟自动静默刷新一次，右上角有手动「刷新数据」按钮
- 右上角徽标显示相对更新时间（如“3 分钟前”），悬停可见完整数据时间

## 文件说明

| 文件 | 作用 |
|---|---|
| `index.html` | 页面结构（头部、总目标、双轨目标、团队卡片、渠道明细、趋势图容器） |
| `style.css` | 全部样式（白底卡片风格、响应式、成员配色） |
| `script.js` | 渲染逻辑 + 防缓存加载器 + 自动/手动刷新；标题月份跟随数据自动切换 |
| `data.js` | 数据文件，唯一需要每日更新的文件（当前为 2026年11月数据） |

## 数据更新方式

只需替换 `data.js` 一个文件，页面自动重新渲染，无需改动其他文件。

`data.js` 结构：

```javascript
const DASHBOARD_DATA = {
  lastUpdated: "2026-11-24T17:55:00+08:00",  // 最后更新时间
  month: "2026-11",                          // 统计月份，页面标题据此显示
  targets: {
    total: 600000,        // 总业绩目标
    regular: 371396,      // 常规业绩目标
    live: 228000,         // 直播业绩目标
    liveOrders: 100       // 直播单数目标
  },
  summary: {
    totalCompleted: 0,    // 累计业绩
    totalRate: 0,         // 总完成率(%)
    regularCompleted: 0,
    liveCompleted: 0,
    liveOrdersCompleted: 0,
    leadsCompleted: 0,    // 留资总数
    leadsTarget: 1010,    // 留资目标
    totalOrders: 0,       // 总单数
    avgOrderValue: 0      // 客单价
  },
  team: [                 // 团队成员卡片
    {
      name: "叶小鲲",
      avatar: "🥋",
      leads: 0,
      orders: 0,
      completed: 0,
      target: 300000,     // 目标为 0 时不显示进度条，只显示业绩
      rate: 0,
      conversionRate: 0,
      regular: { completed: 0, target: 185698, orders_completed: 0 },
      live:    { completed: 0, target: 114000, orders_completed: 0, orders_target: 50 }
    }
  ],
  channels: {             // 渠道明细
    regular: [{ name: "古法身韵抖音", amount: 0, orders: 0 }],
    live:    [{ name: "古法身韵抖音口播", amount: 0, orders: 0 }]
  },
  dailyTrend: [           // 每日走势
    { date: "11/01", total: 0, live: 0, regular: 0,
      live_orders: 0, regular_orders: 0, total_orders: 0 }
  ]
};
```

## 本地预览

直接双击 `index.html`。若浏览器限制本地文件读取，可在该目录执行：

```bash
python3 -m http.server 8000
```

然后访问 http://localhost:8000

## 线上部署

托管在 GitHub Pages：

- 线上地址：https://ab230917.github.io/gufashengyun-dashboard/
- 源码仓库：https://github.com/ab230917/gufashengyun-dashboard

更新方式：替换仓库中的 `data.js` 并提交，1–2 分钟后线上生效。

## 业务口径

- 业绩统计：叶小鲲、武艳阳计入目标；张涵之、刘蓉仅统计业绩，不设目标、不留资
- 课程范围：仅线上/线下/双报课程，剔除师资班、服装、住宿补差价
- 退款：剔除退款订单（实收金额 ≤ 0）
- 渠道划分：来源账号含"口播/直播"计入直播业绩，其余计入常规
