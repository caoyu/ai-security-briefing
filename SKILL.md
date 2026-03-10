# AI Security Briefing Skill

自动生成 AI 安全简报，包含焦点事件、安全事件、行业趋势、政策法规和厂商动态。

## 功能特性

- 📰 每日自动生成 AI 安全简报 HTML
- 🔥 焦点关注板块
- 🔴 最新 AI 风险事件（≤3 条）
- 📈 AI 安全技术趋势（≤5 条）
- ⚖️ AI 安全事件（≤5 条）
- 🏢 安全厂商和云厂商 AI 动态（≤5 条）

## 内容优先级

1. **最新 AI 风险事件**（最多 3 条）- 漏洞、数据泄露、攻击事件
2. **AI 安全技术趋势**（最多 5 条）- 技术发展、行业影响、产品发布
3. **AI 安全事件**（最多 5 条）- 政策法规、监管动态、标准制定
4. **安全厂商和云厂商 AI 动态**（最多 5 条）- 厂商新产品、新技术、重点事件

## 厂商配置

### 国际厂商（优先级高，最多 3 条）
1. CrowdStrike - 云原生/端点安全
2. Palo Alto Networks - AI 安全平台
3. Aqua/NeuVector - 容器安全
4. Fortinet - 边界防护
5. Bitdefender - 端点保护
6. Cisco - 集成安全

### 国内厂商（最多 2 条）
- 360 - 综合安全
- 奇安信 - 企业安全
- 安博通 - 网络安全
- 永信至诚 - 攻防演练
- 浩瀚深度 - 数据安全
- 深信服 - 云安全
- 启明星辰 - 综合安全
- 安恒信息 - 数据安全
- 山石网科 - 边界安全

## 使用方法

### 生成简报
```bash
python skills/tracker.py
```

### 输出文件
- `vendor-events-YYYY-MM-DD.json` - 厂商事件数据
- `vendor-snippet.html` - HTML 片段
- `ai-security-YYYYMMDD.html` - 完整简报页面

## 数据来源

- 安全客 (anquanke.com)
- IT 之家 (ithome.com)
- 中国政府网 (gov.cn)
- 厂商官方博客
- FreeBuf、Threatpost 等安全媒体

## 定时任务

建议配置每日 09:00 自动生成：
```bash
0 9 * * * cd /path/to/ai-security-briefing && python skills/vendor-tracker/tracker.py
```

## 输出示例

每日最多 5 条厂商事件：
- 国际厂商：3 条（优先）
- 国内厂商：2 条

格式：
```json
{
  "generated_at": "2026-03-10T16:50:00",
  "total_events": 5,
  "international_count": 3,
  "domestic_count": 2,
  "events": [...]
}
```
