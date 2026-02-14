#!/usr/bin/env python3
"""
Scholar Push - Google Scholar 文献推送
从 Gmail 获取 Google Scholar 推送，输出精确期刊信息
"""

import os
import sys
import json
import base64
import re
import urllib.parse
import time
import requests
from datetime import datetime, timedelta

# Gmail API
try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    print("⚠️ 需要安装 google-api-python-client")

# CrossRef cache
crossref_cache = {}

def get_venue_from_doi(url, title):
    """通过 DOI 获取精确期刊信息"""
    url_lower = url.lower()
    
    # 提取 DOI
    doi_match = re.search(r'(10\.\d{4,}/[a-zA-Z0-9._\-]+)', url)
    if doi_match:
        doi = doi_match.group(1)
        doi = re.sub(r'/(pdf|abs|html?)$', '', doi, flags=re.I)
        
        # 查缓存
        if doi in crossref_cache:
            return crossref_cache[doi]
        
        # 查询 CrossRef
        try:
            resp = requests.get(f"https://api.crossref.org/works/{doi}", timeout=5)
            if resp.status_code == 200:
                msg = resp.json().get('message', {})
                container = msg.get('container-title', [])
                venue = container[0] if container else None
                
                # 会议论文
                if msg.get('type') == 'proceedings-article':
                    event = msg.get('event', {})
                    if isinstance(event, dict):
                        event_name = event.get('name', '')
                        if event_name:
                            venue = event_name
                
                if venue:
                    crossref_cache[doi] = venue
                    return venue
        except:
            pass
    
    # 标题搜索备选
    try:
        resp = requests.get("https://api.crossref.org/works", 
                           params={"query": title, "rows": 2}, timeout=5)
        if resp.status_code == 200:
            items = resp.json().get('message', {}).get('items', [])
            for item in items:
                if 'review' not in item.get('DOI', '').lower():
                    container = item.get('container-title', [])
                    venue = container[0] if container else None
                    if item.get('type') == 'proceedings-article':
                        event = item.get('event', {})
                        if isinstance(event, dict):
                            event_name = event.get('name', '')
                            if event_name:
                                venue = event_name
                    if venue:
                        return venue
    except:
        pass
    
    # URL 模式匹配
    if 'science.org' in url_lower:
        return "Science Advances" if 'sciadv' in url_lower else "Science"
    if 'nature.com' in url_lower or 'nature.org' in url_lower:
        return "Nature"
    if 'wiley' in url_lower:
        if 'adma' in url_lower: return "Advanced Materials"
        if 'adfm' in url_lower: return "Advanced Functional Materials"
        if 'advelectromater' in url_lower or 'aelm' in url_lower: return "Advanced Electronic Materials"
        return "Wiley"
    if 'ieeexplore' in url_lower: return "IEEE"
    if 'acm.org' in url_lower: return "ACM"
    if 'arxiv' in url_lower: return "arXiv"
    if 'researchsquare' in url_lower: return "Research Square"
    if 'sciencedirect' in url_lower: return "ScienceDirect"
    if 'iopscience' in url_lower: return "IOP"
    
    return "未知"

def get_gmail_service():
    """获取 Gmail 服务"""
    token_path = os.path.expanduser('~/.config/gmail/token.json')
    if not os.path.exists(token_path):
        print("❌ 请先配置 Gmail 认证 (~/.config/gmail/token.json)")
        return None
    
    with open(token_path) as f:
        token_data = json.load(f)['token']
    
    creds = Credentials(
        token=token_data['access_token'],
        refresh_token=token_data.get('refresh_token'),
        token_uri=token_data['token_uri'],
        client_id=token_data['client_id'],
        client_secret=token_data['client_secret'],
        scopes=token_data['scopes']
    )
    
    return build('gmail', 'v1', credentials=creds)

def parse_date(date_str):
    """解析日期格式"""
    # 格式: "Tue, 10 Feb 2026 12:39:04 -0800"
    try:
        # 提取日期部分
        parts = date_str.split()
        if len(parts) >= 4:
            day = parts[1]
            month = parts[2]
            year = parts[3]
            return f"{year}.{month_to_num(month)}.{int(day):02d}"
    except:
        pass
    return date_str[:10]

def month_to_num(month):
    months = {
        'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
        'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
        'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
    }
    return months.get(month, '01')

def fetch_articles(days=7):
    """获取最近N天的文章"""
    service = get_gmail_service()
    if not service:
        return []
    
    # 计算时间戳
    since = int((datetime.now() - timedelta(days=days)).timestamp())
    
    results = service.users().messages().list(
        userId='me',
        q=f'from:scholaralerts-noreply@google.com after:{since}',
        maxResults=20
    ).execute()
    
    messages = results.get('messages', [])
    articles = []
    
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        headers = msg_data['payload']['headers']
        
        subject = [h['value'] for h in headers if h['name'] == 'Subject'][0]
        author = subject.replace(' - 新文章', '')
        date_str = [h['value'] for h in headers if h['name'] == 'Date'][0]
        
        body_data = msg_data['payload']['body']['data']
        body = urllib.parse.unquote(base64.urlsafe_b64decode(body_data.encode('ASCII')).decode('utf-8')).replace('&amp;', '&')
        
        for url_enc, title_enc in re.findall(r'href="https?://scholar\.google\.com/scholar_share\?[^"]*url=([^&]+)&rt=([^&"]+)', body):
            url = urllib.parse.unquote(url_enc)
            title = urllib.parse.unquote(title_enc).replace('+', ' ')
            if title and len(title) > 10:
                articles.append({
                    'title': title,
                    'author': author,
                    'url': url,
                    'date_raw': date_str
                })
        time.sleep(0.2)
    
    # 去重
    seen = set()
    unique = []
    for a in articles:
        key = a['title'][:50]
        if key not in seen:
            seen.add(key)
            unique.append(a)
    
    return unique

def format_output(articles):
    """格式化输出"""
    # 获取期刊信息
    for a in articles:
        a['venue'] = get_venue_from_doi(a['url'], a['title'])
        a['date'] = parse_date(a['date_raw'])
        time.sleep(0.3)
    
    output = []
    output.append("=" * 65)
    output.append("📬 Google Scholar 文献推送")
    output.append("=" * 65)
    output.append(f"\n共 {len(articles)} 篇新文章\n")
    
    for i, a in enumerate(articles, 1):
        output.append(f"【{i}】{a['title']}")
        output.append(f"作者：{a['author']}")
        output.append(f"期刊/会议：{a['venue']}")
        output.append(f"推送时间：{a['date']}")
        output.append("")
    
    return "\n".join(output)

def main():
    if not GMAIL_AVAILABLE:
        print("❌ 需要安装: pip3 install google-api-python-client requests")
        return
    
    # 解析参数
    days = 7
    if len(sys.argv) > 1:
        if sys.argv[1] == 'days' and len(sys.argv) > 2:
            days = int(sys.argv[2])
        elif sys.argv[1] == 'help':
            print(__doc__)
            return
    
    print(f"正在获取最近 {days} 天的推送...\n")
    articles = fetch_articles(days)
    
    if not articles:
        print("未找到新的文献推送")
        return
    
    print(format_output(articles))

if __name__ == "__main__":
    main()
