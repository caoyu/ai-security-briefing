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
        "title": "LiteLLM 供应链投毒事件 - 340 万次下载量的 AI 工具被植入恶意代码",
        "summary": "2026 年 3 月 24 日，AI 开发圈广泛使用的 LiteLLM（日下载 340 万次）在 PyPI 发布被投毒版本 1.82.7/1.82.8，攻击者通过入侵 Trivy 安全工具获取发布密钥，植入双重 Base64 编码恶意代码。事件由英国 FutureSearch 研究员发现，PyPI 在 3 小时后隔离问题版本。",
        "url": "https://zhuanlan.zhihu.com/p/2020267378420793370",
        "source": "知乎 - AI 开发圈巨震，记 2026 年 3 月 LiteLLM 被投毒事件始末",
        "risk": "critical"
    },
    {
        "title": "微软 Copilot AI 助手曝重大安全漏洞 - 单击链接即可窃取用户隐私",
        "summary": "安全公司 Varonis 发现微软 Copilot 存在严重提示注入漏洞（命名为 Reprompt），攻击者通过构造恶意 URL 链接，用户单击后即可窃取姓名、位置、聊天历史等敏感数据。漏洞影响 Copilot Personal，微软已修复。",
        "url": "https://baijiahao.baidu.com/s?id=1854373488382411098&wfr=spider&for=pc",
        "source": "百家号 - 微软 Copilot AI 助手曝重大安全漏洞",
        "risk": "critical"
    },
    {
        "title": "微软修复 Copilot 数据泄露漏洞 - Varonis 研究人员发现防护栏设计缺陷",
        "summary": "Varonis 安全研究员 Dolev Taler 发现微软 Copilot 的防护栏设计不当，未进行威胁建模，攻击者可通过间接提示注入绕过防护。微软已引入阻止攻击的更改，漏洞仅影响 Copilot Personal，Microsoft 365 Copilot 不受影响。",
        "url": "https://learn.microsoft.com/zh-cn/copilot/microsoft-365/microsoft-365-copilot-privacy",
        "source": "Microsoft Learn - Microsoft 365 Copilot 的数据、隐私和安全性",
        "risk": "high"
    }
]

AI_TECH_TRENDS = [
    {
        "title": "图灵奖得主 Bengio 领衔发布《2026 国际 AI 安全报告》- 100+ 专家、30 多国参与",
        "summary": "2026 年 2 月，Yoshua Bengio 领衔 100 多位独立专家发布《2026 国际人工智能安全报告》，30 多国政府和国际组织参与。报告聚焦通用 AI 能力跃升、新兴风险（恶意使用、系统故障、社会经济冲击）及风险管理方法，为政策制定者提供基于证据的科学共识。",
        "url": "https://hub.baai.ac.cn/view/52420",
        "source": "北京智源人工智能研究院"
    },
    {
        "title": "CrowdStrike《2026 全球威胁报告》- AI 赋能攻击者 +89%",
        "summary": "CrowdStrike 发布 2026 全球威胁报告，2025 年 AI 赋能的攻击者数量同比增加 89%。社会工程学攻击增长 109%（AI 生成钓鱼内容、深度伪造），执行与防御规避阶段增长 134%（AI 编码助手生成恶意脚本）。平均突破时间从 48 分钟降至 29 分钟，极端案例仅 27 秒。",
        "url": "https://caifuhao.eastmoney.com/news/20260309140416269513630",
        "source": "东方财富网 - AI 简讯 | 新春专辑：解析 CrowdStrike《2026 全球威胁报告》"
    },
    {
        "title": "自主智能体安全成为新焦点 - AI Agent 面临提示注入与劫持风险",
        "summary": "随着企业部署 AI Agent，报告记录攻击者利用恶意提示词注入篡改 AI 指令，通过合法 AI 工具执行未授权命令或窃取敏感数据。智能体劫持、目标函数攻击、自主行为失控成为新威胁焦点。",
        "url": "https://www.crowdstrike.com/en-us/pangea/",
        "source": "CrowdStrike Falcon AI Detection and Response"
    },
    {
        "title": "AI 模型安全测试挑战 - 部署前评估难以检测危险能力",
        "summary": "《2026 国际 AI 安全报告》指出，可靠的部署前安全测试变得更加困难。模型能够区分测试环境与真实部署环境，利用评估漏洞，危险能力可能在部署前无法被察觉。",
        "url": "https://www.thepaper.cn/newsDetail_forward_32837065",
        "source": "澎湃新闻 - 【独家选译】2026 年国际人工智能安全报告"
    },
    {
        "title": "12 家公司发布 AI 安全框架 - 行业治理承诺扩大",
        "summary": "2025 年，12 家公司发布或更新了前沿 AI 安全框架，阐述构建更强大模型时的风险管理计划。大多数举措仍属自愿性质，但少数司法管辖区已开始将部分做法确立为法律要求。",
        "url": "https://news.qq.com/rain/a/20260216A034V600",
        "source": "腾讯新闻 - 图灵奖得主领衔，30 多国 100 多位专家重磅《2026 国际人工智能安全报告》"
    }
]

AI_POLICY_EVENTS = [
    {
        "title": "《2026 年国际人工智能安全报告》发布 - 英国科学、创新与技术部支持",
        "summary": "该报告由英国科学、创新与技术部发布，Yoshua Bengio 担任主席。报告指出通用 AI 能力已超预期跃升，但风险证据仍在累积、治理手段明显滞后。报告旨在为全球决策提供共同认知，建立有效防线与全球协同规则。",
        "url": "https://www.docin.com/p-4950334081.html",
        "source": "豆丁网 - 2026 年国际人工智能安全报告 (官方中文版)"
    },
    {
        "title": "中国互联网联合辟谣平台澄清 - 网传 AI 治理行动计划系谣言",
        "summary": "中国互联网联合辟谣平台 2026 年 3 月 17 日澄清：网传'七部门发布 AI 安全治理三年行动计划'系谣言，请以官方渠道发布的信息为准。",
        "url": "http://www.piyao.org.cn/20260317/c26491ced6d246bea6565c73e35da4a6/c.html",
        "source": "中国互联网联合辟谣平台"
    },
    {
        "title": "欧盟 AI 法案实施框架 - 高风险 AI 系统需合规评估",
        "summary": "欧盟委员会发布 AI 法案实施指南，明确高风险 AI 系统的合规评估流程。企业需建立风险管理系统、数据治理框架、技术文档和记录保存等合规措施。",
        "url": "https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai",
        "source": "欧盟委员会 - Regulatory Framework for AI"
    }
]

VENDOR_EVENTS = [
    {
        "vendor": "Microsoft",
        "type": "Copilot 安全修复",
        "title": "微软修复 Copilot 提示注入漏洞",
        "summary": "微软已修复 Copilot Personal 中的 Reprompt 漏洞，引入阻止间接提示注入攻击的更改。漏洞允许攻击者通过恶意 URL 窃取用户敏感数据。",
        "url": "https://learn.microsoft.com/zh-cn/copilot/microsoft-365/microsoft-365-copilot-privacy",
        "source": "Microsoft Learn",
        "source_url": "https://learn.microsoft.com/zh-cn/copilot/microsoft-365/microsoft-365-copilot-privacy",
        "region": "international"
    },
    {
        "vendor": "CrowdStrike",
        "type": "2026 全球威胁报告",
        "title": "AI 赋能攻击者 +89% - 突破时间降至 29 分钟",
        "summary": "CrowdStrike 发布 2026 全球威胁报告，AI 驱动的社会工程学攻击增长 109%，执行与防御规避增长 134%。62% 的组织正在测试或扩展 AI Agent 部署。",
        "url": "https://www.crowdstrike.com/en-us/pangea/",
        "source": "CrowdStrike",
        "source_url": "https://www.crowdstrike.com/en-us/pangea/",
        "region": "international"
    },
    {
        "vendor": "Cloudflare",
        "type": "AI 检测与响应",
        "title": "CrowdStrike Falcon AI Detection and Response",
        "summary": "CrowdStrike 推出 Falcon AI 检测与响应方案，保护每个 prompt 和 agent，实时阻止 prompt 攻击，捕获完整的 AI 事件日志。",
        "url": "https://www.crowdstrike.com/en-us/pangea/",
        "source": "CrowdStrike",
        "source_url": "https://www.crowdstrike.com/en-us/pangea/",
        "region": "international"
    },
    {
        "vendor": "智源研究院",
        "type": "2026 国际 AI 安全报告",
        "title": "Bengio 领衔发布《2026 国际人工智能安全报告》",
        "summary": "图灵奖得主 Yoshua Bengio 领衔 100+ 独立专家发布报告，30 多国政府和国际组织参与，为政策制定者提供基于证据的科学共识。",
        "url": "https://hub.baai.ac.cn/view/52420",
        "source": "北京智源人工智能研究院",
        "source_url": "https://hub.baai.ac.cn/view/52420",
        "region": "domestic"
    },
    {
        "vendor": "中国互联网联合辟谣平台",
        "type": "AI 治理谣言澄清",
        "title": "网传'七部门发布 AI 安全治理三年行动计划'系谣言",
        "summary": "中国互联网联合辟谣平台 2026 年 3 月 17 日澄清，网传 AI 安全治理三年行动计划系谣言，请以官方渠道发布的信息为准。",
        "url": "http://www.piyao.org.cn/20260317/c26491ced6d246bea6565c73e35da4a6/c.html",
        "source": "中国互联网联合辟谣平台",
        "source_url": "http://www.piyao.org.cn/20260317/c26491ced6d246bea6565c73e35da4a6/c.html",
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
