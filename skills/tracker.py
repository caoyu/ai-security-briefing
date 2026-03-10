#!/usr/bin/env python3
"""
AI Vendor Tracker - 自动收集主流安全厂商的 AI 安全事件
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

def get_vendor_events():
    """
    收集厂商 AI 安全事件
    实际使用时会调用 web_search 或 RSS 订阅
    这里提供示例数据结构
    """
    events = []
    
    # 示例数据 - 实际使用时替换为真实数据源
    sample_international = [
        {
            "vendor": "CrowdStrike",
            "type": "云原生/端点安全",
            "title": "Falcon AI 威胁检测 2.0 发布",
            "summary": "集成生成式 AI 分析能力，端点检测响应速度提升 40%",
            "url": "https://www.crowdstrike.com/blog/",
            "source": "CrowdStrike Blog",
            "region": "international"
        },
        {
            "vendor": "Palo Alto Networks",
            "type": "AI 安全平台",
            "title": "Cortex XSIAM 新增 AI 模型保护模块",
            "summary": "支持 LLM 应用运行时安全防护",
            "url": "https://www.paloaltonetworks.com/blog/",
            "source": "Palo Alto Blog",
            "region": "international"
        },
        {
            "vendor": "Aqua Security",
            "type": "容器安全",
            "title": "NeuVector 5.0 发布",
            "summary": "增强 Kubernetes AI 工作负载安全策略自动化",
            "url": "https://blog.aquasec.com/",
            "source": "Aqua Blog",
            "region": "international"
        },
        {
            "vendor": "Fortinet",
            "type": "边界防护",
            "title": "FortiGate 7000E 系列集成 AI 引擎",
            "summary": "AI 驱动的网络威胁情报分析",
            "url": "https://www.fortinet.com/blog",
            "source": "Fortinet Blog",
            "region": "international"
        },
        {
            "vendor": "Bitdefender",
            "type": "端点保护",
            "title": "GravityZone Elite 引入深度学习技术",
            "summary": "反勒索软件技术，误报率降低 60%",
            "url": "https://www.bitdefender.com/blog/",
            "source": "Bitdefender Blog",
            "region": "international"
        },
    ]
    
    sample_domestic = [
        {
            "vendor": "360",
            "type": "综合安全",
            "title": "360 智脑安全大模型升级",
            "summary": "支持 AI 生成内容深度伪造检测",
            "url": "https://www.360.cn/",
            "source": "360 官方",
            "region": "domestic"
        },
        {
            "vendor": "奇安信",
            "type": "企业安全",
            "title": "AI 安全治理平台 3.0 发布",
            "summary": "符合《生成式 AI 服务管理暂行办法》合规要求",
            "url": "https://www.qianxin.com/",
            "source": "奇安信官方",
            "region": "domestic"
        },
        {
            "vendor": "安恒信息",
            "type": "数据安全",
            "title": "明御 AI 安全网关升级",
            "summary": "新增大模型输入输出审计功能，支持敏感数据识别",
            "url": "https://www.dbappsecurity.com.cn/",
            "source": "安恒信息官方",
            "region": "domestic"
        },
    ]
    
    # 国际优先，最多 5 条
    events.extend(sample_international[:MAX_INTERNATIONAL])
    # 国内最多 3 条
    events.extend(sample_domestic[:MAX_DOMESTIC])
    
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
        
        html_parts.append(f'''
        <div class="vendor-card {region_class}">
            <span class="vendor-region {region_class}">{region_label}</span>
            <div class="vendor-name">{event["vendor"]}</div>
            <div class="vendor-type">{event["type"]}</div>
            <div class="vendor-event">
                {event["summary"]}
            </div>
        </div>
        ''')
    
    return "\n".join(html_parts)

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
    
    # 输出统计
    international_count = len([e for e in events if e["region"] == "international"])
    domestic_count = len([e for e in events if e["region"] == "domestic"])
    print(f"📊 统计：国际 {international_count} 条 · 国内 {domestic_count} 条")

if __name__ == "__main__":
    main()
