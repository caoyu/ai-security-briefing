#!/usr/bin/env python3
"""
AI Security Briefing Generator
自动生成 AI 安全简报，包含焦点事件、安全事件、行业趋势、政策法规和厂商动态。
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def run_web_search(query, count=10, freshness="week"):
    """调用 web_search API 获取最新新闻"""
    try:
        result = subprocess.run(
            ['openclaw', 'tool', 'web_search', '--query', query, '--count', str(count), '--freshness', freshness],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=60
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return None
    except Exception as e:
        print(f"Web search error: {e}")
        return None

def fetch_ai_security_news():
    """获取最新 AI 安全新闻"""
    queries = [
        "AI security vulnerability 2026 March artificial intelligence cyber attack",
        "AI supply chain poisoning attack LangFlow LiteLLM",
        "Microsoft Copilot vulnerability data exfiltration",
        "OpenClaw gateway security vulnerability exposure",
        "AI deepfake fraud voice cloning scam",
        "AI security report 2026 Yoshua Bengio CrowdStrike"
    ]
    
    all_results = []
    for query in queries:
        result = run_web_search(query, count=5, freshness="week")
        if result and 'pages' in result:
            all_results.extend(result['pages'][:3])
    
    # 去重（基于 URL）
    seen_urls = set()
    unique_results = []
    for item in all_results:
        url = item.get('url', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(item)
    
    return unique_results[:15]

def classify_risk_level(news_item):
    """根据内容分类风险等级"""
    title = (news_item.get('title', '') + news_item.get('snippet', '')).lower()
    
    critical_keywords = ['critical', 'cvss 10', 'zero-click', 'supply chain', 'poisoning', 'remote code execution', 'rce', 'data breach', 'exfiltration']
    high_keywords = ['high', 'cvss 9', 'vulnerability', 'exploit', 'attack', 'malware', 'ransomware', 'deepfake', 'fraud']
    
    for kw in critical_keywords:
        if kw in title:
            return 'critical'
    for kw in high_keywords:
        if kw in title:
            return 'high'
    return 'medium'

def generate_briefing_content(news_items):
    """生成简报内容结构"""
    briefing = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'critical': [],
        'high': [],
        'medium': []
    }
    
    for item in news_items:
        risk_level = classify_risk_level(item)
        briefing[risk_level].append({
            'title': item.get('title', 'Unknown'),
            'summary': item.get('snippet', '')[:500],
            'url': item.get('url', '#'),
            'source': item.get('hostname', 'Unknown')
        })
    
    # 限制每个类别的数量
    briefing['critical'] = briefing['critical'][:3]
    briefing['high'] = briefing['high'][:3]
    briefing['medium'] = briefing['medium'][:2]
    
    return briefing

def generate_html(briefing):
    """生成 HTML 简报"""
    date_str = briefing['date']
    total_events = len(briefing['critical']) + len(briefing['high']) + len(briefing['medium'])
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 安全简报 {date_str} - AI Security Briefing</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #ffffff;
            --bg-secondary: #f6f8fa;
            --bg-tertiary: #eaeef2;
            --border-color: #d0d7de;
            --text-primary: #1f2328;
            --text-secondary: #656d76;
            --text-muted: #8c959f;
            --accent-blue: #0969da;
            --accent-green: #1a7f37;
            --accent-red: #cf222e;
            --accent-orange: #9a6700;
            --danger-bg: rgba(207, 34, 46, 0.1);
            --warning-bg: rgba(210, 153, 34, 0.1);
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 0 24px; }}
        header {{ padding: 48px 0 32px; border-bottom: 1px solid var(--border-color); margin-bottom: 48px; }}
        .header-nav {{ display: flex; align-items: center; gap: 16px; margin-bottom: 24px; }}
        .back-link {{
            color: var(--text-secondary);
            text-decoration: none;
            font-size: 14px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            border-radius: 6px;
            border: 1px solid var(--border-color);
            background: var(--bg-secondary);
            transition: all 0.2s ease;
        }}
        .back-link:hover {{ border-color: var(--accent-blue); background: var(--bg-tertiary); }}
        .header-content h1 {{
            font-size: 32px;
            font-weight: 700;
            letter-spacing: -0.5px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .header-meta {{ display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }}
        .post-date {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
            color: var(--text-muted);
            background: var(--bg-tertiary);
            padding: 4px 12px;
            border-radius: 4px;
            border: 1px solid var(--border-color);
        }}
        .post-stats {{ color: var(--text-secondary); font-size: 14px; }}
        .focus-section {{
            background: linear-gradient(135deg, var(--bg-secondary) 0%, rgba(207, 34, 46, 0.08) 100%);
            border: 1px solid var(--border-color);
            border-left: 4px solid var(--accent-red);
            padding: 28px;
            margin-bottom: 48px;
            border-radius: 12px;
        }}
        .focus-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }}
        .focus-icon {{ font-size: 24px; }}
        .focus-title {{ font-size: 18px; font-weight: 600; }}
        .focus-summary {{ color: var(--text-secondary); font-size: 15px; line-height: 1.7; }}
        .content-section {{ margin-bottom: 48px; }}
        .section-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-bottom: 16px;
            margin-bottom: 24px;
            border-bottom: 1px solid var(--border-color);
        }}
        .section-header-left {{ display: flex; align-items: center; gap: 12px; }}
        .section-icon {{ font-size: 20px; }}
        .section-title {{ font-size: 20px; font-weight: 600; }}
        .section-count {{
            font-size: 13px;
            color: var(--text-muted);
            background: var(--bg-tertiary);
            padding: 4px 10px;
            border-radius: 4px;
        }}
        .event-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            transition: all 0.2s ease;
        }}
        .event-card:hover {{ border-color: var(--accent-blue); box-shadow: 0 4px 12px rgba(9, 105, 218, 0.1); transform: translateY(-2px); }}
        .event-card.critical {{
            border-left: 4px solid var(--accent-red);
            background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--danger-bg) 100%);
        }}
        .event-card.high {{
            border-left: 4px solid var(--accent-orange);
            background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--warning-bg) 100%);
        }}
        .event-card.medium {{ border-left: 4px solid var(--accent-blue); }}
        .event-header {{ display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; margin-bottom: 16px; }}
        .event-title {{ font-size: 18px; font-weight: 600; line-height: 1.4; }}
        .event-meta {{ display: flex; gap: 8px; flex-wrap: wrap; }}
        .risk-badge {{
            font-size: 12px;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 4px;
            text-transform: uppercase;
        }}
        .risk-critical {{ background: var(--accent-red); color: white; }}
        .risk-high {{ background: var(--accent-orange); color: white; }}
        .risk-medium {{ background: var(--accent-blue); color: white; }}
        .event-content {{ color: var(--text-secondary); font-size: 15px; line-height: 1.7; }}
        .event-content ul {{ margin: 12px 0 12px 24px; }}
        .event-content li {{ margin-bottom: 8px; }}
        .event-content strong {{ color: var(--text-primary); font-weight: 600; }}
        footer {{
            margin-top: 64px;
            padding-top: 32px;
            border-top: 1px solid var(--border-color);
            color: var(--text-muted);
            font-size: 13px;
            text-align: center;
        }}
        .footer-links {{ display: flex; justify-content: center; gap: 24px; margin-top: 16px; }}
        .footer-links a {{ color: var(--accent-blue); text-decoration: none; }}
        .footer-links a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <nav class="header-nav">
                <a href="index.html" class="back-link">← 返回总览</a>
            </nav>
            <div class="header-content">
                <h1><span>🛡️</span> AI 安全简报</h1>
                <div class="header-meta">
                    <span class="post-date">📅 {date_str}</span>
                    <span class="post-stats">📊 {total_events} 条事件</span>
                </div>
            </div>
        </header>
        <main>
            <section class="focus-section">
                <div class="focus-header">
                    <span class="focus-icon">🔥</span>
                    <h2 class="focus-title">焦点关注</h2>
                </div>
                <p class="focus-summary">
                    <strong>今日 AI 安全威胁概览：</strong>
                    {len(briefing['critical'])} 条严重风险 · 
                    {len(briefing['high'])} 条高危风险 · 
                    {len(briefing['medium'])} 条中危风险
                </p>
            </section>
'''
    
    # 严重风险
    if briefing['critical']:
        html += '''
            <section class="content-section">
                <div class="section-header">
                    <div class="section-header-left">
                        <span class="section-icon">🔴</span>
                        <h2 class="section-title">严重风险 (Critical)</h2>
                    </div>
                    <span class="section-count">''' + str(len(briefing['critical'])) + ''' 条</span>
                </div>
'''
        for item in briefing['critical']:
            html += f'''
                <article class="event-card critical">
                    <div class="event-header">
                        <h3 class="event-title">{item['title']}</h3>
                        <div class="event-meta">
                            <span class="risk-badge risk-critical">Critical</span>
                        </div>
                    </div>
                    <div class="event-content">
                        <p>{item['summary']}</p>
                        <p style="margin-top: 12px;"><strong>来源:</strong> <a href="{item['url']}" target="_blank">{item['source']}</a></p>
                    </div>
                </article>
'''
        html += '''
            </section>
'''
    
    # 高危风险
    if briefing['high']:
        html += '''
            <section class="content-section">
                <div class="section-header">
                    <div class="section-header-left">
                        <span class="section-icon">🟠</span>
                        <h2 class="section-title">高危风险 (High)</h2>
                    </div>
                    <span class="section-count">''' + str(len(briefing['high'])) + ''' 条</span>
                </div>
'''
        for item in briefing['high']:
            html += f'''
                <article class="event-card high">
                    <div class="event-header">
                        <h3 class="event-title">{item['title']}</h3>
                        <div class="event-meta">
                            <span class="risk-badge risk-high">High</span>
                        </div>
                    </div>
                    <div class="event-content">
                        <p>{item['summary']}</p>
                        <p style="margin-top: 12px;"><strong>来源:</strong> <a href="{item['url']}" target="_blank">{item['source']}</a></p>
                    </div>
                </article>
'''
        html += '''
            </section>
'''
    
    # 中危风险
    if briefing['medium']:
        html += '''
            <section class="content-section">
                <div class="section-header">
                    <div class="section-header-left">
                        <span class="section-icon">🟡</span>
                        <h2 class="section-title">中危风险 (Medium)</h2>
                    </div>
                    <span class="section-count">''' + str(len(briefing['medium'])) + ''' 条</span>
                </div>
'''
        for item in briefing['medium']:
            html += f'''
                <article class="event-card medium">
                    <div class="event-header">
                        <h3 class="event-title">{item['title']}</h3>
                        <div class="event-meta">
                            <span class="risk-badge risk-medium">Medium</span>
                        </div>
                    </div>
                    <div class="event-content">
                        <p>{item['summary']}</p>
                        <p style="margin-top: 12px;"><strong>来源:</strong> <a href="{item['url']}" target="_blank">{item['source']}</a></p>
                    </div>
                </article>
'''
        html += '''
            </section>
'''
    
    html += '''
        </main>
        <footer>
            <p><strong>来源:</strong> 公开安全情报、厂商公告、安全研究机构</p>
            <p><strong>编制:</strong> AI 安全简报自动化系统</p>
            <div class="footer-links">
                <a href="index.html">← 返回总览</a>
                <a href="https://github.com/caoyu/ai-security-briefing" target="_blank">GitHub 仓库</a>
                <a href="https://github.com/caoyu/ai-security-briefing/issues" target="_blank">反馈问题</a>
            </div>
        </footer>
    </div>
</body>
</html>
'''
    
    return html

def main():
    """主函数"""
    output_dir = Path(__file__).parent.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🔍 正在搜索最新 AI 安全新闻...")
    news_items = fetch_ai_security_news()
    
    if not news_items:
        print("⚠️ 未能获取新闻，使用备用数据")
        # 备用数据
        news_items = [
            {
                'title': 'AI Security Threat Report 2026',
                'snippet': 'Latest AI security threats and vulnerability trends',
                'url': 'https://example.com',
                'hostname': 'Security Research'
            }
        ]
    
    print(f"✓ 获取到 {len(news_items)} 条新闻")
    
    print("📊 正在生成简报内容...")
    briefing = generate_briefing_content(news_items)
    
    print("📄 正在生成 HTML 简报...")
    html_content = generate_html(briefing)
    
    # 保存文件
    date_str = datetime.now().strftime('%Y%m%d')
    output_file = output_dir / f"ai-security-{date_str}.html"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ 简报已保存到：{output_file}")
    print(f"📊 统计：严重 {len(briefing['critical'])} 条 · 高危 {len(briefing['high'])} 条 · 中危 {len(briefing['medium'])} 条")

if __name__ == "__main__":
    main()
