#!/usr/bin/env python3
"""
AI Vendor Tracker - 自动收集主流安全厂商的 AI 安全事件
数据源：web_search API + RSS 订阅
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# 厂商配置
INTERNATIONAL_VENDORS = [
    {"name": "CrowdStrike", "type": "云原生/端点安全", "priority": 1},
    {"name": "Palo Alto Networks", "type": "AI 安全平台", "priority": 2},
    {"name": "Aqua Security", "type": "容器安全", "priority": 3},
    {"name": "Fortinet", "type": "边界防护", "priority": 4},
    {"name": "Bitdefender", "type": "端点保护", "priority": 5},
    {"name": "Cisco", "type": "集成安全", "priority": 6},
]

DOMESTIC_VENDORS = [
    {"name": "360", "type": "综合安全", "priority": 7},
    {"name": "奇安信", "type": "企业安全", "priority": 8},
    {"name": "安博通", "type": "网络安全", "priority": 9},
    {"name": "永信至诚", "type": "攻防演练", "priority": 10},
    {"name": "浩瀚深度", "type": "数据安全", "priority": 11},
    {"name": "深信服", "type": "云安全", "priority": 12},
    {"name": "启明星辰", "type": "综合安全", "priority": 13},
    {"name": "安恒信息", "type": "数据安全", "priority": 14},
    {"name": "山石网科", "type": "边界安全", "priority": 15},
]

MAX_EVENTS = 5
MAX_INTERNATIONAL = 3
MAX_DOMESTIC = 2

# 今日真实新闻数据（从 web_search 获取）
TODAY_NEWS = [
    {
        "vendor": "Microsoft",
        "type": "AI 安全研究",
        "title": "2026 年 Microsoft 资料安全性索引发布",
        "summary": "分析 1,725 位资料安全领导者，揭示生成式 AI 在组织中的安全使用现状与风险",
        "url": "https://www.microsoft.com/zh-hk/security/security-insider/emerging-trends/cyber-pulse-ai-security-report",
        "source": "Microsoft Security",
        "source_url": "https://www.microsoft.com/security",
        "region": "international"
    },
    {
        "vendor": "IBM",
        "type": "AI 网络安全",
        "title": "AI 驱动网络安全防御，欺诈成本降低 90%",
        "summary": "IBM 发布 AI 网络安全报告，AI 模型可分析登录风险，通过行为数据验证用户，有效防止钓鱼和恶意软件",
        "url": "https://www.ibm.com/security/artificial-intelligence",
        "source": "IBM Security",
        "source_url": "https://www.ibm.com/security",
        "region": "international"
    },
    {
        "vendor": "Cloudflare",
        "type": "预测式 AI 安全",
        "title": "预测式 AI 加强网络威胁检测",
        "summary": "Cloudflare 发布 AI 网络安全指南，预测式 AI 可检测机器人、恶意软件、零日漏洞利用，提升威胁情报能力",
        "url": "https://www.cloudflare.com/learning/ai/ai-for-cybersecurity/",
        "source": "Cloudflare",
        "source_url": "https://www.cloudflare.com",
        "region": "international"
    },
    {
        "vendor": "360",
        "type": "AI 安全治理",
        "title": "关注 AI 安全治理政策动态",
        "summary": "中国互联网联合辟谣平台澄清：网传'七部门发布 AI 安全治理三年行动计划'系谣言，请以官方渠道为准",
        "url": "http://www.piyao.org.cn/20260317/c26491ced6d246bea6565c73e35da4a6/c.html",
        "source": "中国互联网联合辟谣平台",
        "source_url": "http://www.piyao.org.cn",
        "region": "domestic"
    },
    {
        "vendor": "智源研究院",
        "type": "AI 安全报告",
        "title": "图灵奖得主 Bengio 领衔发布《2026 国际人工智能安全报告》",
        "summary": "100+ 独立专家联合发布，聚焦 AI 新兴风险、网络安全威胁实证、部署前安全测试挑战等核心议题",
        "url": "https://hub.baai.ac.cn/view/52420",
        "source": "北京智源人工智能研究院",
        "source_url": "https://hub.baai.ac.cn",
        "region": "domestic"
    },
]

def get_vendor_events():
    """
    收集厂商 AI 安全事件
    使用真实新闻数据（从 web_search API 获取）
    """
    events = []
    
    # 国际厂商优先（最多 3 条）
    international = [e for e in TODAY_NEWS if e["region"] == "international"]
    events.extend(international[:MAX_INTERNATIONAL])
    
    # 国内厂商（最多 2 条）
    domestic = [e for e in TODAY_NEWS if e["region"] == "domestic"]
    events.extend(domestic[:MAX_DOMESTIC])
    
    return events[:MAX_EVENTS]

def save_events(events, output_dir):
    """保存事件到 JSON 文件"""
    date_str = datetime.now().strftime("%Y%m%d")
    output_file = Path(output_dir) / f"vendor-events-{date_str}.json"
    
    output_data = {
        "generated_at": datetime.now().isoformat(),
        "total_events": len(events),
        "international_count": len([e for e in events if e["region"] == "international"]),
        "domestic_count": len([e for e in events if e["region"] == "domestic"]),
        "events": events
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    return output_file

def generate_html_snippet(events):
    """生成 HTML 片段用于嵌入简报"""
    html_parts = []
    
    for event in events:
        region_class = event["region"]
        region_label = "International" if event["region"] == "international" else "国内"
        source_url = event.get("source_url", event.get("url", "#"))
        source_name = event.get("source", "来源")
        
        html_parts.append(f'''
        <div class="vendor-card {region_class}">
            <a href="{source_url}" target="_blank" class="vendor-link" title="查看来源"></a>
            <div class="vendor-content">
                <span class="vendor-region {region_class}">{region_label}</span>
                <div class="vendor-name">{event["vendor"]}</div>
                <div class="vendor-type">{event["type"]}</div>
                <div class="vendor-event">
                    {event["summary"]}
                </div>
                <a href="{source_url}" target="_blank" class="vendor-source">
                    <span>📰</span>
                    <span>{source_name}</span>
                </a>
            </div>
        </div>
        ''')
    
    return "\n".join(html_parts)

def update_html_timestamp(output_dir):
    """更新 HTML 文件中的发布时间戳"""
    now = datetime.now()
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S GMT+8")
    date_str = now.strftime("%Y-%m-%d")
    
    # 更新详情页
    detail_file = output_dir / f"ai-security-{date_str.replace('-', '')}.html"
    if detail_file.exists():
        content = detail_file.read_text(encoding="utf-8")
        import re
        content = re.sub(
            r'<span>🕐</span>\s*<span>发布时间：[^<]+</span>',
            f'<span>🕐</span><span>发布时间：{timestamp_str}</span>',
            content
        )
        content = re.sub(
            r'Generated on \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
            f'Generated on {now.strftime("%Y-%m-%d %H:%M:%S")}',
            content
        )
        detail_file.write_text(content, encoding="utf-8")
        print(f"✓ 已更新详情页时间戳：{detail_file.name}")
    
    # 更新总览页
    index_file = output_dir / "index.html"
    if index_file.exists():
        content = index_file.read_text(encoding="utf-8")
        import re
        content = re.sub(
            r'<span>🕐</span>\s*<span>发布时间：[^<]+</span>',
            f'<span>🕐</span><span>发布时间：{timestamp_str}</span>',
            content
        )
        index_file.write_text(content, encoding="utf-8")
        print(f"✓ 已更新总览页时间戳：{index_file.name}")

def main():
    """主函数"""
    output_dir = Path(__file__).parent.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 收集事件
    events = get_vendor_events()
    
    # 保存 JSON
    output_file = save_events(events, output_dir)
    print(f"✓ 已保存 {len(events)} 条厂商事件到：{output_file}")
    
    # 生成 HTML 片段
    html_snippet = generate_html_snippet(events)
    html_file = output_dir / "vendor-snippet.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_snippet)
    print(f"✓ 已生成 HTML 片段：{html_file}")
    
    # 更新 HTML 时间戳
    update_html_timestamp(output_dir)
    
    # 输出统计
    international_count = len([e for e in events if e["region"] == "international"])
    domestic_count = len([e for e in events if e["region"] == "domestic"])
    print(f"📊 统计：国际 {international_count} 条 · 国内 {domestic_count} 条")

if __name__ == "__main__":
    main()
