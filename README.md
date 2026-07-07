# 古法身韵 · 7月销售目标看板

一个实时同步飞书多维表格数据的销售目标看板网页，部署在 GitHub Pages 上。

## 📊 功能特点

- **实时数据同步**：每30分钟自动从飞书多维表格拉取最新数据
- **目标追踪**：清晰展示团队总目标、个人目标、渠道目标的完成进度
- **双轨业绩**：分别展示常规业绩和直播业绩
- **每日趋势**：可视化每日成交金额变化
- **响应式设计**：支持手机、平板、桌面设备访问

## 🏗️ 项目结构

```
├── index.html              # 前端页面
├── style.css               # 样式文件
├── script.js               # 前端逻辑
├── data.js                 # 数据文件（自动生成）
├── sync_data.py            # 数据同步脚本
├── .github/
│   └── workflows/
│       └── sync.yml        # GitHub Actions 配置
└── README.md               # 说明文档
```

## 🚀 部署步骤

### 1. 创建 GitHub 仓库

```bash
# 在本地初始化仓库
cd dashboard_project
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/ab230917/gufashengyun-dashboard.git
git push -u origin main
```

### 2. 配置 GitHub Secrets

在 GitHub 仓库的 `Settings → Secrets and variables → Actions` 中添加：

| Secret 名称 | 说明 |
|------------|------|
| `FEISHU_APP_ID` | 飞书应用的 App ID |
| `FEISHU_APP_SECRET` | 飞书应用的 App Secret |

### 3. 启用 GitHub Pages

1. 进入仓库的 `Settings → Pages`
2. Source 选择 `Deploy from a branch`
3. Branch 选择 `main`，目录选择 `/ (root)`
4. 保存后等待部署完成

### 4. 手动触发数据同步

可以通过以下方式手动触发数据同步：
- 在 GitHub 仓库的 `Actions` 页面，选择 `Sync Data from Feishu` workflow
- 点击 `Run workflow` 按钮

## 📈 数据源说明

### 飞书多维表格

- **Base Token**: `Zv4Gbp3TdaJwVDs9omEcN21xnEg`
- **01_客户主表** (`tbl4pTcnUwsN819F`): 留咨数据
  - 关键字段：首次留资时间、跟进人、来源账号
- **04_成交订单表** (`tbl6X7rDL5c9MkcZ`): 业绩数据
  - 关键字段：付款时间、实收金额、成交归属、来源账号

### 7月目标

| 指标 | 目标值 |
|------|--------|
| 总业绩 | ¥380,000 |
| 常规业绩 | ¥185,000 |
| 直播业绩 | ¥194,000 |
| 留资数 | 1,010条 |
| 直播单量 | 85单 |

## 🔧 本地开发

```bash
# 安装依赖（无额外依赖，纯Python标准库）
# 设置环境变量
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"

# 运行同步脚本
python3 sync_data.py

# 本地预览（使用任意静态服务器）
python3 -m http.server 8000
# 访问 http://localhost:8000
```

## 📋 团队成员

| 成员 | 目标 | 负责渠道 |
|------|------|----------|
| 叶小鲲 | ¥228,000 | 常规 + 直播 |
| 武艳阳 | ¥152,000 | 常规 + 直播 |

## ⚠️ 注意事项

- 数据**不含师资班业绩**，师资班业绩统一计入8月核算
- 同步频率：每30分钟自动同步一次
- 飞书应用需要具有多维表格的读取权限

## 📝 License

Private - 古法身韵内部使用
