#!/usr/bin/env python3
"""
AI Vendor Tracker - 自动收集主流安全厂商的 AI 安全事件
数据源：web_search API
"""

import json
import subprocess
import sys
from datetime import datetime
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

def run_web_search(query, count=10, freshness="week"):
    """调用 web_search API 获取最新新闻"""
    try:
        result = subprocess.run(
            ['openclaw', 'tool', 'web_search', '--query', query, '--count', str(count), '--freshness', freshness],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=60
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if data.get('ok') and 'result' in data:
                result_data = json.loads(data['result']['content'][0]['text'])
                return result_data.get('pages', [])
        return []
    except Exception as e:
        print(f"Web search error: {e}")
        return []

def fetch_vendor_news():
    """获取厂商 AI 安全新闻"""
    queries = [
        "CrowdStrike AI security 2026",
        "Palo Alto Networks AI cybersecurity",
        "360 奇安信 AI 安全",
        "AI security vendor news March 2026",
        "网络安全厂商 AI 产品发布"
    ]
    
    all_results = []
    for query in queries:
        results = run_web_search(query, count=5, freshness="week")
        all_results.extend(results[:2])
    
    # 去重（基于 URL）
    seen_urls = set()
    unique_results = []
    for item in all_results:
        url = item.get('url', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(item)
    
    return unique_results[:10]

def classify_vendor(vendor_name, title, snippet):
    """根据内容分类厂商"""
    text = (vendor_name + title + snippet).lower()
    
    # 国内厂商关键词
    domestic_keywords = ['360', '奇安信', '安恒', '深信服', '启明星辰', '山石', '腾讯', '阿里', '华为', '中国', '国内']
    
    for kw in domestic_keywords:
        if kw in text:
            return 'domestic'
    
    return 'international'

def get_vendor_events():
    """收集厂商 AI 安全事件"""
    events = []
    
    # 获取最新新闻
    news_items = fetch_vendor_news()
    
    for item in news_items:
        title = item.get('title', '')
        snippet = item.get('snippet', '')[:500]
        url = item.get('url', '#')
        hostname = item.get('hostname', '')
        
        # 分类厂商
        region = classify_vendor(hostname, title, snippet)
        
        # 提取厂商名称（简化处理）
        vendor = hostname if hostname else 'Unknown Vendor'
        vendor_type = 'AI 安全'
        
        events.append({
            "vendor": vendor,
            "type": vendor_type,
            "title": title,
            "summary": snippet,
            "url": url,
            "source": hostname or '安全媒体',
            "source_url": url,
            "region": region
        })
    
    # 国际优先，最多 5 条
    international = [e for e in events if e["region"] == "international"][:MAX_INTERNATIONAL]
    domestic = [e for e in events if e["region"] == "domestic"][:MAX_DOMESTIC]
    
    result = international + domestic
    return result[:MAX_EVENTS]

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
    
    print("🔍 正在搜索厂商 AI 安全新闻...")
    events = get_vendor_events()
    
    if not events:
        print("⚠️ 未能获取新闻，使用备用数据")
        # 备用数据
        events = [
            {
                "vendor": "Security Vendor",
                "type": "AI 安全",
                "title": "AI Security Update",
                "summary": "Latest AI security developments",
                "url": "https://example.com",
                "source": "Security News",
                "source_url": "https://example.com",
                "region": "international"
            }
        ]
    
    print(f"✓ 获取到 {len(events)} 条厂商事件")
    
    # 保存 JSON
    output_file = save_events(events, output_dir)
    print(f"✓ 已保存厂商事件到：{output_file}")
    
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
