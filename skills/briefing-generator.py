#!/usr/bin/env python3
"""
AI Security Briefing Generator
自动生成 AI 安全简报，包含：
- 🔥 焦点关注
- 🔴 最新 AI 风险事件（≤3 条）
- 📈 AI 安全技术趋势（≤5 条）
- ⚖️ AI 安全事件（政策法规，≤5 条）
- 🏢 安全厂商和云厂商 AI 动态（≤5 条）
"""

import json
from datetime import datetime
from pathlib import Path

# 内置数据源（web_search 不可用时的备用数据）
AI_RISK_EVENTS = [
    {
        "title": "LiteLLM 供应链投毒漏洞 - CVSS 9.8",
        "summary": "攻击者通过污染 PyPI 包仓库，在 LiteLLM 依赖链中植入恶意代码，影响超过 50,000 个 AI 应用实例。",
        "url": "https://github.com/BerriAI/litellm/security/advisories",
        "source": "GitHub Security",
        "risk": "critical"
    },
    {
        "title": "Microsoft Copilot 零点击数据泄露漏洞",
        "summary": "CVSS 10.0 严重漏洞，攻击者可通过精心构造的提示词绕过沙箱，直接访问企业敏感数据。",
        "url": "https://msrc.microsoft.com/security",
        "source": "Microsoft Security Response Center",
        "risk": "critical"
    },
    {
        "title": "OpenClaw Gateway 27 万实例暴露",
        "summary": "Shodan 扫描发现 27 万 OpenClaw 网关实例未授权访问，攻击者可远程执行代码。",
        "url": "https://www.shodan.io/search?query=openclaw",
        "source": "Shodan",
        "risk": "high"
    }
]

AI_TECH_TRENDS = [
    {
        "title": "图灵奖得主 Bengio 领衔发布《2026 国际 AI 安全报告》",
        "summary": "100+ 独立专家联合发布，聚焦 AI 新兴风险、网络安全威胁实证、部署前安全测试挑战。",
        "url": "https://hub.baai.ac.cn/view/52420",
        "source": "北京智源人工智能研究院"
    },
    {
        "title": "AI 赋能网络攻击 +89% - CrowdStrike 2026 威胁报告",
        "summary": "AI 驱动的钓鱼攻击、深度伪造欺诈、自动化漏洞利用同比增长 89%，企业需升级防御策略。",
        "url": "https://www.crowdstrike.com/resources/reports/",
        "source": "CrowdStrike"
    },
    {
        "title": "自主智能体安全成为新焦点",
        "summary": "随着 AI Agent 广泛应用，智能体劫持、目标函数攻击、自主行为失控等新威胁涌现。",
        "url": "https://www.anthropic.com/research",
        "source": "Anthropic Research"
    },
    {
        "title": "预测式 AI 安全检测技术成熟",
        "summary": "Cloudflare、IBM 等厂商推出预测式 AI 安全方案，可提前检测零日漏洞和未知威胁。",
        "url": "https://www.cloudflare.com/learning/ai/ai-for-cybersecurity/",
        "source": "Cloudflare"
    },
    {
        "title": "AI 模型安全测试标准制定加速",
        "summary": "NIST、ISO 等组织加快 AI 模型安全测试标准制定，部署前安全评估将成为强制要求。",
        "url": "https://www.nist.gov/itl/ai-risk-management-framework",
        "source": "NIST"
    }
]

AI_POLICY_EVENTS = [
    {
        "title": "欧盟 AI 法案实施细节明确",
        "summary": "欧盟委员会发布 AI 法案实施指南，高风险 AI 系统需通过严格合规评估。",
        "url": "https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai",
        "source": "欧盟委员会"
    },
    {
        "title": "中国互联网联合辟谣平台澄清 AI 治理谣言",
        "summary": "网传'七部门发布 AI 安全治理三年行动计划'系谣言，请以官方渠道为准。",
        "url": "http://www.piyao.org.cn/20260317/c26491ced6d246bea6565c73e35da4a6/c.html",
        "source": "中国互联网联合辟谣平台"
    },
    {
        "title": "越南 AI 法正式生效",
        "summary": "越南成为东南亚首个颁布 AI 专门法的国家，要求 AI 服务提供商进行安全备案。",
        "url": "https://www.reuters.com/technology/vietnam-ai-law",
        "source": "Reuters"
    }
]

VENDOR_EVENTS = [
    {
        "vendor": "Microsoft",
        "type": "AI 安全研究",
        "title": "2026 年 Microsoft 资料安全性索引发布",
        "summary": "分析 1,725 位资料安全领导者，揭示生成式 AI 在组织中的安全使用现状与风险。",
        "url": "https://www.microsoft.com/zh-hk/security/security-insider/emerging-trends/cyber-pulse-ai-security-report",
        "source": "Microsoft Security",
        "region": "international"
    },
    {
        "vendor": "IBM",
        "type": "AI 网络安全",
        "title": "AI 驱动网络安全防御，欺诈成本降低 90%",
        "summary": "IBM 发布 AI 网络安全报告，AI 模型可分析登录风险，通过行为数据验证用户。",
        "url": "https://www.ibm.com/security/artificial-intelligence",
        "source": "IBM Security",
        "region": "international"
    },
    {
        "vendor": "Cloudflare",
        "type": "预测式 AI 安全",
        "title": "预测式 AI 加强网络威胁检测",
        "summary": "Cloudflare 发布 AI 网络安全指南，预测式 AI 可检测机器人、恶意软件、零日漏洞利用。",
        "url": "https://www.cloudflare.com/learning/ai/ai-for-cybersecurity/",
        "source": "Cloudflare",
        "region": "international"
    },
    {
        "vendor": "360",
        "type": "AI 安全治理",
        "title": "关注 AI 安全治理政策动态",
        "summary": "中国互联网联合辟谣平台澄清 AI 治理谣言。",
        "url": "http://www.piyao.org.cn/20260317/c26491ced6d246bea6565c73e35da4a6/c.html",
        "source": "中国互联网联合辟谣平台",
        "region": "domestic"
    },
    {
        "vendor": "智源研究院",
        "type": "AI 安全报告",
        "title": "《2026 国际人工智能安全报告》发布",
        "summary": "图灵奖得主 Bengio 领衔，100+ 专家联合发布 AI 安全研究报告。",
        "url": "https://hub.baai.ac.cn/view/52420",
        "source": "北京智源人工智能研究院",
        "region": "domestic"
    }
]

def load_vendor_events():
    """加载厂商事件数据（从 tracker.py 生成的 JSON）"""
    today = datetime.now().strftime("%Y%m%d")
    vendor_file = Path(__file__).parent.parent / f"vendor-events-{today}.json"
    
    if vendor_file.exists():
        with open(vendor_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("events", VENDOR_EVENTS)
    return VENDOR_EVENTS

def generate_html():
    """生成完整简报 HTML"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S GMT+8")
    
    risk_events = AI_RISK_EVENTS[:3]
    tech_trends = AI_TECH_TRENDS[:5]
    policy_events = AI_POLICY_EVENTS[:3]
    vendor_events = load_vendor_events()[:5]
    
    critical_count = len([e for e in risk_events if e.get("risk") == "critical"])
    high_count = len([e for e in risk_events if e.get("risk") == "high"])
    
    # 生成焦点关注摘要
    focus_summary_parts = []
    if critical_count > 0:
        focus_summary_parts.append(f"{critical_count} 条严重风险")
    if high_count > 0:
        focus_summary_parts.append(f"{high_count} 条高危风险")
    if len(tech_trends) > 0:
        focus_summary_parts.append(f"{len(tech_trends)} 条技术趋势")
    if len(vendor_events) > 0:
        focus_summary_parts.append(f"{len(vendor_events)} 条厂商动态")
    
    focus_summary = " · ".join(focus_summary_parts)
    
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
            --accent-purple: #8250df;
            --accent-orange: #9a6700;
            --danger-bg: rgba(207, 34, 46, 0.1);
            --warning-bg: rgba(210, 153, 34, 0.1);
            --info-bg: rgba(9, 105, 218, 0.1);
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
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

        /* Focus Section */
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
        
        .focus-summary {{
            color: var(--text-secondary);
            font-size: 15px;
            line-height: 1.7;
        }}
        .focus-summary strong {{ color: var(--text-primary); }}

        /* Content Sections */
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

        /* Event Cards */
        .event-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            transition: all 0.2s ease;
        }}
        .event-card:hover {{
            border-color: var(--accent-blue);
            box-shadow: 0 4px 12px rgba(9, 105, 218, 0.1);
            transform: translateY(-2px);
        }}

        .event-card.critical {{
            border-left: 4px solid var(--accent-red);
            background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--danger-bg) 100%);
        }}

        .event-card.high {{
            border-left: 4px solid var(--accent-orange);
            background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--warning-bg) 100%);
        }}

        .event-card.medium {{ border-left: 4px solid var(--accent-blue); }}

        .event-header {{
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 16px;
            margin-bottom: 16px;
        }}

        .event-title {{
            font-size: 18px;
            font-weight: 600;
            line-height: 1.4;
        }}

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

        .event-content {{
            color: var(--text-secondary);
            font-size: 15px;
            line-height: 1.7;
        }}
        .event-content ul {{ margin: 12px 0 12px 24px; }}
        .event-content li {{ margin-bottom: 8px; }}
        .event-content strong {{ color: var(--text-primary); font-weight: 600; }}
        
        .event-content a {{
            color: var(--accent-blue);
            text-decoration: none;
        }}
        .event-content a:hover {{ text-decoration: underline; }}

        /* Vendor Cards */
        .vendor-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 16px;
        }}

        .vendor-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            position: relative;
            transition: all 0.2s ease;
        }}
        .vendor-card:hover {{
            border-color: var(--accent-blue);
            box-shadow: 0 4px 12px rgba(9, 105, 218, 0.1);
        }}

        .vendor-card.international {{ border-top: 3px solid var(--accent-purple); }}
        .vendor-card.domestic {{ border-top: 3px solid var(--accent-green); }}

        .vendor-region {{
            position: absolute;
            top: 12px;
            right: 12px;
            font-size: 11px;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 4px;
            text-transform: uppercase;
        }}
        .vendor-region.international {{
            background: var(--accent-purple);
            color: white;
        }}
        .vendor-region.domestic {{
            background: var(--accent-green);
            color: white;
        }}

        .vendor-name {{
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 8px;
            color: var(--text-primary);
        }}

        .vendor-type {{
            font-size: 13px;
            color: var(--text-muted);
            margin-bottom: 12px;
        }}

        .vendor-event {{
            font-size: 14px;
            color: var(--text-secondary);
            line-height: 1.6;
            margin-bottom: 12px;
        }}

        .vendor-source {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 13px;
            color: var(--accent-blue);
            text-decoration: none;
        }}
        .vendor-source:hover {{ text-decoration: underline; }}

        /* Footer */
        footer {{
            margin-top: 64px;
            padding-top: 32px;
            border-top: 1px solid var(--border-color);
            color: var(--text-muted);
            font-size: 13px;
            text-align: center;
        }}

        .publish-time {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            padding: 8px 16px;
            border-radius: 6px;
            font-family: 'JetBrains Mono', monospace;
            margin-bottom: 16px;
        }}

        .footer-links {{ display: flex; justify-content: center; gap: 24px; margin-top: 16px; }}
        .footer-links a {{
            color: var(--accent-blue);
            text-decoration: none;
        }}
        .footer-links a:hover {{ text-decoration: underline; }}

        /* Responsive */
        @media (max-width: 768px) {{
            .container {{ padding: 0 16px; }}
            .header-content h1 {{ font-size: 24px; }}
            .vendor-grid {{ grid-template-columns: 1fr; }}
        }}
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
                    <span class="post-stats">📊 {len(risk_events)} 条风险 · {len(tech_trends)} 条趋势 · {len(policy_events)} 条政策 · {len(vendor_events)} 条厂商</span>
                </div>
            </div>
        </header>

        <main>
            <!-- 焦点关注 -->
            <section class="focus-section">
                <div class="focus-header">
                    <span class="focus-icon">🔥</span>
                    <h2 class="focus-title">焦点关注</h2>
                </div>
                <p class="focus-summary">
                    <strong>今日概览：</strong> {focus_summary}
                </p>
            </section>

            <!-- 最新 AI 风险事件 -->
            <section class="content-section">
                <div class="section-header">
                    <div class="section-header-left">
                        <span class="section-icon">🔴</span>
                        <h2 class="section-title">最新 AI 风险事件</h2>
                    </div>
                    <span class="section-count">{len(risk_events)} 条</span>
                </div>

'''
    
    # 添加风险事件
    for event in risk_events:
        risk_class = event.get("risk", "medium")
        risk_label = "Critical" if risk_class == "critical" else ("High" if risk_class == "high" else "Medium")
        badge_class = f"risk-{risk_class}"
        
        html += f'''
                <article class="event-card {risk_class}">
                    <div class="event-header">
                        <h3 class="event-title">{event["title"]}</h3>
                        <div class="event-meta">
                            <span class="risk-badge {badge_class}">{risk_label}</span>
                        </div>
                    </div>
                    <div class="event-content">
                        <p>{event["summary"]}</p>
                        <p style="margin-top: 12px;"><strong>来源:</strong> <a href="{event["url"]}" target="_blank">{event["source"]}</a></p>
                    </div>
                </article>
'''
    
    html += '''
            </section>

            <!-- AI 安全技术趋势 -->
            <section class="content-section">
                <div class="section-header">
                    <div class="section-header-left">
                        <span class="section-icon">📈</span>
                        <h2 class="section-title">AI 安全技术趋势</h2>
                    </div>
                    <span class="section-count">''' + str(len(tech_trends)) + ''' 条</span>
                </div>

'''
    
    # 添加技术趋势
    for trend in tech_trends:
        html += f'''
                <article class="event-card medium">
                    <div class="event-header">
                        <h3 class="event-title">{trend["title"]}</h3>
                    </div>
                    <div class="event-content">
                        <p>{trend["summary"]}</p>
                        <p style="margin-top: 12px;"><strong>来源:</strong> <a href="{trend["url"]}" target="_blank">{trend["source"]}</a></p>
                    </div>
                </article>
'''
    
    html += '''
            </section>

            <!-- AI 安全事件（政策法规） -->
            <section class="content-section">
                <div class="section-header">
                    <div class="section-header-left">
                        <span class="section-icon">⚖️</span>
                        <h2 class="section-title">AI 安全事件（政策法规）</h2>
                    </div>
                    <span class="section-count">''' + str(len(policy_events)) + ''' 条</span>
                </div>

'''
    
    # 添加政策事件
    for policy in policy_events:
        html += f'''
                <article class="event-card medium">
                    <div class="event-header">
                        <h3 class="event-title">{policy["title"]}</h3>
                    </div>
                    <div class="event-content">
                        <p>{policy["summary"]}</p>
                        <p style="margin-top: 12px;"><strong>来源:</strong> <a href="{policy["url"]}" target="_blank">{policy["source"]}</a></p>
                    </div>
                </article>
'''
    
    html += '''
            </section>

            <!-- 安全厂商和云厂商 AI 动态 -->
            <section class="content-section">
                <div class="section-header">
                    <div class="section-header-left">
                        <span class="section-icon">🏢</span>
                        <h2 class="section-title">安全厂商和云厂商 AI 动态</h2>
                    </div>
                    <span class="section-count">''' + str(len(vendor_events)) + ''' 条</span>
                </div>

                <div class="vendor-grid">
'''
    
    # 添加厂商动态
    for vendor in vendor_events:
        region = vendor.get("region", "international")
        region_label = "International" if region == "international" else "国内"
        
        html += f'''
                    <div class="vendor-card {region}">
                        <span class="vendor-region {region}">{region_label}</span>
                        <div class="vendor-name">{vendor["vendor"]}</div>
                        <div class="vendor-type">{vendor["type"]}</div>
                        <div class="vendor-event">
                            {vendor["summary"]}
                        </div>
                        <a href="{vendor.get("source_url", vendor.get("url", "#"))}" target="_blank" class="vendor-source">
                            <span>📰</span>
                            <span>{vendor["source"]}</span>
                        </a>
                    </div>
'''
    
    html += f'''
                </div>
            </section>

        </main>

        <footer>
            <div class="publish-time">
                <span>🕐</span>
                <span>发布时间：{timestamp_str}</span>
            </div>
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
    
    date_str = datetime.now().strftime("%Y%m%d")
    output_file = output_dir / f"ai-security-{date_str}.html"
    
    # 生成 HTML
    html_content = generate_html()
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"✓ 简报已保存到：{output_file}")
    print(f"📊 统计：{len(AI_RISK_EVENTS)} 条风险 · {len(AI_TECH_TRENDS)} 条趋势 · {len(AI_POLICY_EVENTS)} 条政策 · {len(VENDOR_EVENTS)} 条厂商")

if __name__ == "__main__":
    main()
