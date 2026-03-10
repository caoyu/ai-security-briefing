# AI Vendor Tracker Skill

自动收集国际国内主流安全厂商的 AI 安全新产品、新技术、重点事件。

## 配置厂商列表

### 国际厂商（优先级高）
1. CrowdStrike - 云原生/端点安全
2. Palo Alto Networks - AI 安全平台
3. Aqua/NeuVector - 容器安全
4. Fortinet - 边界防护
5. Bitdefender - 端点保护
6. Cisco - 集成安全

### 国内厂商
- 360
- 奇安信
- 安博通
- 永信至诚
- 浩瀚深度
- 深信服
- 启明星辰
- 安恒信息
- 山石网科

## 使用方式

每日自动运行，最多收集 8 条厂商相关 AI 事件（国际优先）。

## 数据来源

- 厂商官方博客
- 安全媒体（安全客、FreeBuf、Threatpost 等）
- Twitter/X 官方账号
- RSS 订阅源

## 输出格式

生成 `vendor-events-YYYY-MM-DD.json` 文件，包含：
- 厂商名称
- 厂商类型
- 事件摘要
- 来源链接
- 时间戳
- 地区（international/domestic）
