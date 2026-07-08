#!/usr/bin/env python3
"""
古法身韵7月销售目标看板 - 数据同步脚本
从飞书多维表格拉取数据，生成 data.js 供前端使用

数据源：
  - 01_客户主表 (tbl4pTcnUwsN819F) - 留咨数据
  - 04_成交订单表 (tbl6X7rDL5c9MkcZ) - 业绩数据

使用方式：
  python3 sync_data.py

环境变量（可选，优先使用环境变量中的凭证）：
  FEISHU_APP_ID - 飞书应用 App ID
  FEISHU_APP_SECRET - 飞书应用 App Secret
"""

import os
import json
import sys
import time
from datetime import datetime, timezone, timedelta
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# ============================================================
# 配置
# ============================================================
APP_ID = os.environ.get('FEISHU_APP_ID', 'cli_aac6033544a19bdf')
APP_SECRET = os.environ.get('FEISHU_APP_SECRET', '')
BASE_TOKEN = 'Zv4Gbp3TdaJwVDs9omEcN21xnEg'
LEADS_TABLE_ID = 'tbl4pTcnUwsN819F'   # 01_客户主表
ORDERS_TABLE_ID = 'tbl6X7rDL5c9MkcZ'  # 04_成交订单表

# 7月目标
TARGETS = {
    'total': 600000,
    'regular': 371396,
    'live': 228000,
    'leads': 1010,
    'liveOrders': 100
}

# 团队成员
TEAM_MEMBERS = ['叶小鲲', '武艳阳']

# 成员个人目标
MEMBER_TARGETS = {
    '叶小鲲': {
        'total': 360000,
        'regular': 245491,
        'live': 114000,
    },
    '武艳阳': {
        'total': 240000,
        'regular': 125905,
        'live': 114000,
    }
}

# 直播渠道分类关键词
LIVE_KEYWORDS = ['口播', '直播']
# 常规渠道分类
REGULAR_CHANNELS = [
    '古法身韵视频号', '抖音', '张涵之各渠道', '张涵之抖音', '张涵之视频号', '张涵之小红书',
    '小红书', '古法身韵抖音', '古法身韵小红书', '舞号门抖音', '舞号门公众号',
    '线上会员', '转介绍', '叶小鲲抖音', '叶小鲲视频号', '叶小鲲小红书'
]

# 输出文件路径
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.js')

# 北京时间
BJT = timezone(timedelta(hours=8))


# ============================================================
# 飞书 API
# ============================================================
def api_request(method, url, data=None, headers=None):
    """发送HTTP请求"""
    if headers is None:
        headers = {}
    
    if data:
        data = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json; charset=utf-8'
    
    req = Request(url, data=data, headers=headers, method=method)
    
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        print(f"HTTP Error {e.code}: {body}", file=sys.stderr)
        raise
    except URLError as e:
        print(f"URL Error: {e.reason}", file=sys.stderr)
        raise


def get_tenant_access_token():
    """获取 tenant_access_token"""
    url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
    resp = api_request('POST', url, {
        'app_id': APP_ID,
        'app_secret': APP_SECRET
    })
    
    if resp.get('code') != 0:
        raise Exception(f"获取token失败: {resp.get('msg', 'unknown error')}")
    
    return resp['tenant_access_token']


def list_records(token, table_id, page_size=200):
    """获取多维表格全部记录（分页）"""
    all_records = []
    page_token = None
    
    while True:
        url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{BASE_TOKEN}/tables/{table_id}/records'
        params = [f'page_size={page_size}']
        if page_token:
            params.append(f'page_token={page_token}')
        
        if params:
            url += '?' + '&'.join(params)
        
        headers = {
            'Authorization': f'Bearer {token}'
        }
        
        resp = api_request('GET', url, headers=headers)
        
        if resp.get('code') != 0:
            raise Exception(f"获取记录失败: {resp.get('msg', 'unknown error')}")
        
        data = resp.get('data', {})
        items = data.get('items', [])
        all_records.extend(items)
        
        if data.get('has_more'):
            page_token = data.get('page_token')
            if not page_token:
                break
            time.sleep(0.2)  # 避免限流
        else:
            break
    
    return all_records


# ============================================================
# 数据处理
# ============================================================
def extract_field_value(field_val):
    """提取字段值（处理数组/标量/日期等）"""
    if field_val is None:
        return None
    if isinstance(field_val, list):
        if len(field_val) == 0:
            return None
        # 人员字段
        if isinstance(field_val[0], dict):
            return field_val[0].get('text', field_val[0].get('name', str(field_val[0])))
        return field_val[0]
    if isinstance(field_val, dict):
        # 日期字段
        if 'text' in field_val:
            return field_val['text']
    return field_val


def parse_date(date_val):
    """解析日期值（时间戳或字符串）"""
    if date_val is None:
        return None
    if isinstance(date_val, (int, float)):
        # 毫秒时间戳
        return datetime.fromtimestamp(date_val / 1000, tz=BJT)
    if isinstance(date_val, str):
        for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y/%m/%d']:
            try:
                return datetime.strptime(date_val, fmt).replace(tzinfo=BJT)
            except ValueError:
                continue
    return None


def is_july(dt):
    """判断日期是否在7月"""
    if dt is None:
        return False
    return dt.year == 2026 and dt.month == 7


def classify_channel(source, course=None):
    """将来源账号分类到常规/直播渠道"""
    if source is None:
        return 'regular', '其他'
    
    source_str = str(source)
    
    # 判断是否直播
    for kw in LIVE_KEYWORDS:
        if kw in source_str:
            return 'live', source_str
    
    # 归入常规渠道
    # 合并张涵之相关渠道
    if '张涵之' in source_str:
        return 'regular', '张涵之各渠道'
    
    # 抖音（非张涵之）
    if '抖音' in source_str and '张涵之' not in source_str:
        return 'regular', '抖音'
    
    # 小红书（非张涵之）
    if '小红书' in source_str and '张涵之' not in source_str:
        return 'regular', '小红书'
    
    # 视频号（古法身韵）
    if '视频号' in source_str:
        return 'regular', source_str
    
    return 'regular', source_str


def is_live_order(source):
    """判断是否为直播订单"""
    if source is None:
        return False
    source_str = str(source)
    for kw in LIVE_KEYWORDS:
        if kw in source_str:
            return True
    return False


def process_data(leads, orders):
    """处理原始数据，生成看板数据"""
    now = datetime.now(BJT)
    
    # ---- 留资统计 ----
    july_leads = []
    member_leads = {m: 0 for m in TEAM_MEMBERS}
    
    for record in leads:
        fields = record.get('fields', {})
        
        # 留资时间
        lead_time = parse_date(extract_field_value(fields.get('首次留资时间')))
        if not is_july(lead_time):
            continue
        
        july_leads.append(record)
        
        # 跟进人
        follower = extract_field_value(fields.get('跟进人'))
        if follower and str(follower) in member_leads:
            member_leads[str(follower)] += 1
    
    # ---- 订单统计 ----
    july_orders = []
    member_stats = {}
    for m in TEAM_MEMBERS:
        member_stats[m] = {
            'regular': 0,
            'live': 0,
            'live_orders': 0,
            'total': 0
        }
    
    channel_amounts = {}  # 渠道 -> 金额
    channel_orders = {}   # 渠道 -> 单数
    daily_totals = {}     # 日期 -> {total, live, regular}
    
    for record in orders:
        fields = record.get('fields', {})
        
        # 付款时间
        pay_time = parse_date(extract_field_value(fields.get('付款时间')))
        if not is_july(pay_time):
            continue
        
        july_orders.append(record)
        
        # 实收金额
        amount = extract_field_value(fields.get('实收金额'))
        if amount is None:
            amount = extract_field_value(fields.get('应收金额'))
        amount = float(amount) if amount else 0
        
        # 成交归属
        owner = extract_field_value(fields.get('成交归属'))
        owner_str = str(owner) if owner else ''
        
        # 来源账号
        source = extract_field_value(fields.get('来源账号'))
        source_str = str(source) if source else ''
        
        # 分类渠道
        channel_type, channel_name = classify_channel(source)
        
        # 是否为直播订单
        is_live = is_live_order(source)
        
        # 统计成员业绩
        # 注意：一个订单可能归属多人，需要按人头分
        if owner_str in TEAM_MEMBERS:
            if is_live:
                member_stats[owner_str]['live'] += amount
                member_stats[owner_str]['live_orders'] += 1
            else:
                member_stats[owner_str]['regular'] += amount
            member_stats[owner_str]['total'] += amount
        
        # 统计渠道金额
        if channel_name not in channel_amounts:
            channel_amounts[channel_name] = 0
            channel_orders[channel_name] = 0
        channel_amounts[channel_name] += amount
        channel_orders[channel_name] += 1
        
        # 统计每日趋势
        day_key = pay_time.strftime('%Y-%m-%d')
        if day_key not in daily_totals:
            daily_totals[day_key] = {'total': 0, 'live': 0, 'regular': 0}
        daily_totals[day_key]['total'] += amount
        if is_live:
            daily_totals[day_key]['live'] += amount
        else:
            daily_totals[day_key]['regular'] += amount
    
    # ---- 汇总 ----
    total_completed = sum(m['total'] for m in member_stats.values())
    regular_completed = sum(m['regular'] for m in member_stats.values())
    live_completed = sum(m['live'] for m in member_stats.values())
    live_orders_total = sum(m['live_orders'] for m in member_stats.values())
    leads_total = len(july_leads)
    orders_total = len(july_orders)
    avg_order = int(total_completed / orders_total) if orders_total > 0 else 0
    total_rate = round((total_completed / TARGETS['total']) * 100, 2) if TARGETS['total'] > 0 else 0
    
    # 常规渠道明细
    regular_channels = []
    for ch_name in sorted(channel_amounts.keys()):
        ch_type, _ = classify_channel(ch_name)
        if ch_type == 'regular' and channel_amounts[ch_name] > 0:
            regular_channels.append({
                'name': ch_name,
                'amount': int(channel_amounts[ch_name])
            })
    
    # 合并同类渠道
    merged_regular = {}
    for ch in regular_channels:
        # 合并逻辑
        name = ch['name']
        if '张涵之' in name:
            key = '张涵之各渠道'
        elif '抖音' in name and '张涵之' not in name:
            key = '抖音'
        elif '小红书' in name and '张涵之' not in name:
            key = '小红书'
        else:
            key = name
        
        if key not in merged_regular:
            merged_regular[key] = 0
        merged_regular[key] += ch['amount']
    
    regular_channel_list = [
        {'name': k, 'amount': int(v)} 
        for k, v in sorted(merged_regular.items(), key=lambda x: -x[1])
    ]
    
    # 直播渠道明细
    live_channels = []
    for ch_name in sorted(channel_amounts.keys()):
        ch_type, _ = classify_channel(ch_name)
        if ch_type == 'live' and channel_amounts[ch_name] > 0:
            live_channels.append({
                'name': ch_name,
                'orders': int(channel_orders[ch_name]),
                'amount': int(channel_amounts[ch_name])
            })
    
    # 团队数据
    team_data = []
    for member in TEAM_MEMBERS:
        stats = member_stats[member]
        targets = MEMBER_TARGETS[member]
        m_total = stats['total']
        m_rate = round((m_total / targets['total']) * 100, 2) if targets['total'] > 0 else 0
        
        team_data.append({
            'name': member,
            'avatar': member[0],
            'target': targets['total'],
            'completed': int(m_total),
            'rate': m_rate,
            'leads': member_leads[member],
            'regular': {
                'target': targets['regular'],
                'completed': int(stats['regular'])
            },
            'live': {
                'target': targets['live'],
                'completed': int(stats['live']),
                'orders': int(stats['live_orders'])
            }
        })
    
    # 每日趋势
    daily_trend = []
    for day_key in sorted(daily_totals.keys()):
        d = daily_totals[day_key]
        daily_trend.append({
            'date': day_key,
            'total': int(d['total']),
            'live': int(d['live']),
            'regular': int(d['regular'])
        })
    
    # 最终数据
    dashboard_data = {
        'lastUpdated': now.isoformat(),
        'month': '2026-07',
        'targets': TARGETS,
        'summary': {
            'totalCompleted': int(total_completed),
            'totalRate': total_rate,
            'regularCompleted': int(regular_completed),
            'liveCompleted': int(live_completed),
            'liveOrdersCompleted': int(live_orders_total),
            'leadsCompleted': leads_total,
            'totalOrders': orders_total,
            'avgOrderValue': avg_order
        },
        'team': team_data,
        'channels': {
            'regular': regular_channel_list,
            'live': live_channels
        },
        'dailyTrend': daily_trend
    }
    
    return dashboard_data


# ============================================================
# 输出
# ============================================================
def write_data_js(data, output_path):
    """将数据写入 data.js"""
    now = datetime.now(BJT)
    time_str = now.strftime('%Y-%m-%d %H:%M')
    
    js_content = f"""// 古法身韵7月销售目标看板 - 数据文件
// 此文件由 sync_data.py 自动生成，请勿手动修改
// 最后更新: {time_str}

const DASHBOARD_DATA = {json.dumps(data, ensure_ascii=False, indent=2)};
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"✅ data.js 已更新: {output_path}")
    print(f"   总业绩: ¥{data['summary']['totalCompleted']:,} / ¥{data['targets']['total']:,} ({data['summary']['totalRate']}%)")
    print(f"   留资数: {data['summary']['leadsCompleted']}")
    print(f"   成交单数: {data['summary']['totalOrders']}")


# ============================================================
# 主流程
# ============================================================
def main():
    print("=" * 50)
    print("古法身韵7月销售目标看板 - 数据同步")
    print("=" * 50)
    
    # 检查凭证
    if not APP_SECRET:
        print("❌ 错误: 未设置飞书 App Secret")
        print("   请设置环境变量 FEISHU_APP_SECRET")
        sys.exit(1)
    
    try:
        # 获取 token
        print("\n📡 获取飞书访问令牌...")
        token = get_tenant_access_token()
        print("   ✅ Token 获取成功")
        
        # 获取留资数据
        print("\n📋 拉取留资数据 (01_客户主表)...")
        leads = list_records(token, LEADS_TABLE_ID)
        print(f"   ✅ 获取 {len(leads)} 条记录")
        
        # 获取订单数据
        print("\n📋 拉取订单数据 (04_成交订单表)...")
        orders = list_records(token, ORDERS_TABLE_ID)
        print(f"   ✅ 获取 {len(orders)} 条记录")
        
        # 处理数据
        print("\n🔄 处理数据...")
        data = process_data(leads, orders)
        
        # 输出
        print("\n💾 写入 data.js...")
        write_data_js(data, OUTPUT_FILE)
        
        print("\n" + "=" * 50)
        print("✅ 同步完成!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 同步失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
