/**
 * 古法身韵 · 7月销售目标看板
 * 前端逻辑
 */

(function() {
  'use strict';

  // ============ 工具函数 ============
  function formatCurrency(amount) {
    if (amount >= 10000) {
      return '¥' + (amount / 10000).toFixed(1) + '万';
    }
    return '¥' + amount.toLocaleString('zh-CN');
  }

  function formatNumber(num) {
    return num.toLocaleString('zh-CN');
  }

  function formatPercent(rate) {
    return rate.toFixed(1) + '%';
  }

  function formatDate(dateStr) {
    const d = new Date(dateStr);
    const month = d.getMonth() + 1;
    const day = d.getDate();
    return month + '月' + day + '日';
  }

  // ============ 数据渲染 ============
  function renderDashboard(data) {
    if (!data) return;

    // 更新时间
    const updateTime = new Date(data.lastUpdated);
    const timeStr = updateTime.getFullYear() + '年' + 
      (updateTime.getMonth() + 1) + '月' + 
      updateTime.getDate() + '日 ' + 
      String(updateTime.getHours()).padStart(2, '0') + ':' + 
      String(updateTime.getMinutes()).padStart(2, '0');
    document.getElementById('lastUpdate').textContent = '最后更新：' + timeStr;

    // Hero区域
    const targets = data.targets;
    const summary = data.summary;

    document.getElementById('heroCurrent').textContent = formatCurrency(summary.totalCompleted);
    document.getElementById('heroTarget').textContent = formatCurrency(targets.total);
    document.getElementById('heroRate').textContent = formatPercent(summary.totalRate);
    
    setTimeout(() => {
      document.getElementById('heroProgressBar').style.width = summary.totalRate + '%';
    }, 300);

    document.getElementById('heroLeads').textContent = formatNumber(summary.leadsCompleted);
    document.getElementById('heroOrders').textContent = formatNumber(summary.totalOrders);
    document.getElementById('heroAvg').textContent = formatCurrency(summary.avgOrderValue);
    
    const conversionRate = summary.leadsCompleted > 0 
      ? ((summary.totalOrders / summary.leadsCompleted) * 100).toFixed(1) 
      : '0.0';
    document.getElementById('heroConversion').textContent = conversionRate + '%';

    // 双轨目标
    const regularCompleted = data.channels.regular.reduce((sum, c) => sum + c.amount, 0);
    const liveCompleted = data.channels.live.reduce((sum, c) => sum + c.amount, 0);
    const liveOrdersCompleted = data.channels.live.reduce((sum, c) => sum + c.orders, 0);

    document.getElementById('regularCurrent').textContent = formatCurrency(regularCompleted);
    document.getElementById('regularTarget').textContent = formatCurrency(targets.regular);
    const regularRate = targets.regular > 0 ? ((regularCompleted / targets.regular) * 100) : 0;
    document.getElementById('regularRate').textContent = formatPercent(regularRate);
    
    document.getElementById('liveCurrent').textContent = formatCurrency(liveCompleted);
    document.getElementById('liveTarget').textContent = formatCurrency(targets.live);
    const liveRate = targets.live > 0 ? ((liveCompleted / targets.live) * 100) : 0;
    document.getElementById('liveRate').textContent = formatPercent(liveRate);
    document.getElementById('liveOrders').textContent = liveOrdersCompleted + ' / ' + targets.liveOrders + '单';

    setTimeout(() => {
      document.getElementById('regularBar').style.width = Math.min(regularRate, 100) + '%';
      document.getElementById('liveBar').style.width = Math.min(liveRate, 100) + '%';
    }, 500);

    // 团队成员
    renderTeam(data.team);

    // 渠道明细
    renderChannels(data.channels);

    // 每日趋势
    renderTrend(data.dailyTrend);
  }

  function renderTeam(teamData) {
    const grid = document.getElementById('teamGrid');
    grid.innerHTML = '';

    teamData.forEach((member, index) => {
      const isYe = member.name.includes('叶');
      const avatarClass = isYe ? 'ye' : 'wu';
      const fillClass = isYe ? 'ye' : 'wu';

      // 计算各部分完成率
      const totalRate = member.rate || 0;
      const regularRate = member.regular.target > 0 
        ? ((member.regular.completed / member.regular.target) * 100) : 0;
      const liveRate = member.live.target > 0 
        ? ((member.live.completed / member.live.target) * 100) : 0;

      const card = document.createElement('div');
      card.className = 'team-card';
      card.innerHTML = `
        <div class="team-card-header">
          <div class="team-avatar ${avatarClass}">${member.avatar}</div>
          <div class="team-info">
            <div class="team-name">${member.name}</div>
            <div class="team-meta">留资${formatNumber(member.leads)}条 · 成交${member.orders}单</div>
          </div>
        </div>
        
        <div class="team-total-section">
          <div class="team-total-amount">${formatCurrency(member.completed)}</div>
          <div class="team-total-target">目标 ${formatCurrency(member.target)} · ${formatPercent(totalRate)}</div>
          <div class="team-progress-bar total-bar">
            <div class="team-progress-fill ${fillClass}" style="width: 0%" data-width="${Math.min(totalRate, 100)}"></div>
          </div>
        </div>

        <div class="team-channel-section">
          <div class="team-channel-item">
            <div class="channel-icon">📺</div>
            <div class="channel-content">
              <div class="channel-title">直播转化</div>
              <div class="channel-orders">目标 ${member.live.orders_target} 单 · 已成交 ${member.live.orders_completed} 单 · ${formatPercent(member.live.target > 0 ? (member.live.completed / member.live.target * 100) : 0)}</div>
              <div class="channel-amount-row">
                <span class="channel-current">${formatCurrency(member.live.completed)}</span>
                <span class="channel-target">目标${formatCurrency(member.live.target)}</span>
              </div>
              <div class="team-progress-bar channel-bar">
                <div class="team-progress-fill ${fillClass}" style="width: 0%" data-width="${Math.min(liveRate, 100)}"></div>
              </div>
            </div>
          </div>
          
          <div class="team-channel-item">
            <div class="channel-icon">💬</div>
            <div class="channel-content">
              <div class="channel-title">日常咨询转化</div>
              <div class="channel-orders">已成交 ${member.regular.orders_completed} 单 · ${formatPercent(member.regular.target > 0 ? (member.regular.completed / member.regular.target * 100) : 0)}</div>
              <div class="channel-amount-row">
                <span class="channel-current">${formatCurrency(member.regular.completed)}</span>
                <span class="channel-target">目标${formatCurrency(member.regular.target)}</span>
              </div>
              <div class="team-progress-bar channel-bar">
                <div class="team-progress-fill ${fillClass}" style="width: 0%" data-width="${Math.min(regularRate, 100)}"></div>
              </div>
            </div>
          </div>
        </div>
      `;
      grid.appendChild(card);
    });

    // 动画
    setTimeout(() => {
      document.querySelectorAll('.team-progress-fill').forEach(el => {
        el.style.width = el.dataset.width + '%';
      });
    }, 700);
  }

  function renderChannels(channels) {
    // 常规渠道
    const regularContainer = document.getElementById('regularChannels');
    regularContainer.innerHTML = '';
    const maxRegular = Math.max(...channels.regular.map(c => c.amount));
    
    channels.regular.forEach(ch => {
      const pct = maxRegular > 0 ? ((ch.amount / maxRegular) * 100) : 0;
      const item = document.createElement('div');
      item.className = 'channel-item';
      item.innerHTML = `
        <div class="channel-name">${ch.name}</div>
        <div class="channel-value">
          <div class="channel-amount">${formatCurrency(ch.amount)}</div>
        </div>
      `;
      regularContainer.appendChild(item);
    });

    // 直播渠道
    const liveContainer = document.getElementById('liveChannels');
    liveContainer.innerHTML = '';
    
    channels.live.forEach(ch => {
      const item = document.createElement('div');
      item.className = 'channel-item';
      item.innerHTML = `
        <div class="channel-name">${ch.name}</div>
        <div class="channel-value">
          <div class="channel-amount">${formatCurrency(ch.amount)}</div>
          <div class="channel-orders">${ch.orders}单</div>
        </div>
      `;
      liveContainer.appendChild(item);
    });
  }

  function renderTrend(dailyTrend) {
    const chart = document.getElementById('trendChart');
    chart.innerHTML = '';

    if (!dailyTrend || dailyTrend.length === 0) return;

    const maxTotal = Math.max(...dailyTrend.map(d => d.total));

    dailyTrend.forEach(day => {
      const group = document.createElement('div');
      group.className = 'trend-bar-group';

      const liveHeight = maxTotal > 0 ? (day.live / maxTotal) * 140 : 0;
      const regularHeight = maxTotal > 0 ? (day.regular / maxTotal) * 140 : 0;

      group.innerHTML = `
        <div class="trend-bars">
          <div class="trend-bar live" style="height: ${liveHeight}px">
            <div class="trend-bar-tooltip">📺 直播: ${formatCurrency(day.live)}</div>
          </div>
          <div class="trend-bar regular" style="height: ${regularHeight}px">
            <div class="trend-bar-tooltip">💬 常规: ${formatCurrency(day.regular)}</div>
          </div>
        </div>
        <div class="trend-date">${formatDate(day.date)}</div>
        <div class="trend-total">${formatCurrency(day.total)}</div>
      `;
      chart.appendChild(group);
    });
  }

  // ============ 初始化 ============
  function init() {
    if (typeof DASHBOARD_DATA !== 'undefined') {
      renderDashboard(DASHBOARD_DATA);
    } else {
      console.error('DASHBOARD_DATA 未加载');
      document.getElementById('lastUpdate').textContent = '数据加载失败';
    }
  }

  // DOM Ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
