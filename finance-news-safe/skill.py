#!/usr/bin/env python3
"""
财经新闻汇总 (全面版)
整合多个数据源：AKShare + 新浪 + Yahoo Finance
"""

import sys
import urllib.request
import ssl
import json
from datetime import datetime

# 尝试导入 AKShare
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False
    print("⚠️ AKShare 未安装，部分功能受限")

SSL_CONTEXT = ssl.create_default_context()

def fetch_url(url, timeout=10):
    """安全获取URL内容"""
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; OpenClaw-News/1.0)'
        })
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CONTEXT) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return None

def get_zh_a_stock():
    """A股主要指数行情"""
    print("\n📈 A股主要指数")
    print("=" * 50)
    
    if not AKSHARE_AVAILABLE:
        print("需要安装 AKShare: pip3 install akshare")
        return
    
    try:
        # 沪深300
        df = ak.stock_zh_index_daily_em(symbol="sh000300")
        if not df.empty:
            latest = df.iloc[-1]
            print(f"沪深300 (000300): {latest['close']:.2f} ({latest['close']-latest['open']:+.2f}, {((latest['close']-latest['open'])/latest['open']*100):+.2f}%)")
    except Exception as e:
        print(f"获取失败: {e}")

def get_stock_news(keyword="半导体"):
    """获取个股/板块新闻"""
    print(f"\n📰 热点新闻 ({keyword})")
    print("=" * 50)
    
    if not AKSHARE_AVAILABLE:
        print("需要安装 AKShare")
        return
    
    try:
        df = ak.stock_news_em(symbol=keyword)
        for i, row in df.head(5).iterrows():
            print(f"\n• {row['新闻标题'][:60]}")
            print(f"  {row['发布时间']} | {row['文章来源']}")
    except Exception as e:
        print(f"获取失败: {e}")

def get_ggt_news():
    """港股新闻"""
    print("\n📰 港股新闻")
    print("=" * 50)
    
    if not AKSHARE_AVAILABLE:
        return
    
    try:
        df = ak.stock_news_em(symbol="港股")
        for i, row in df.head(3).iterrows():
            print(f"• {row['新闻标题'][:50]}")
    except Exception as e:
        print(f"获取失败: {e}")

def get_market_overview():
    """市场整体情况"""
    print("\n🏠 市场整体")
    print("=" * 50)
    
    if not AKSHARE_AVAILABLE:
        return
    
    try:
        # 涨停板分析
        df = ak.stock_zt_pool_em(date="最新")
        print(f"今日涨停: {len(df)} 家")
        
        # 跌停板分析
        try:
            df_dt = ak.stock_dt_pool_em(date="最新")
            print(f"今日跌停: {len(df_dt)} 家")
        except:
            pass
    except Exception as e:
        print(f"获取失败: {e}")

def get_us_market():
    """美股行情"""
    print("\n🇺🇸 美股行情")
    print("=" * 50)
    
    symbols = {
        "^GSPC": "S&P 500",
        "^DJI": "道琼斯", 
        "^IXIC": "纳斯达克"
    }
    
    for symbol, name in symbols.items():
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        data = fetch_url(url)
        if data:
            try:
                result = json.loads(data)
                meta = result.get('chart', {}).get('result', [{}])[0].get('meta', {})
                price = meta.get('regularMarketPrice', 'N/A')
                print(f"{name}: {price}")
            except:
                print(f"{name}: 获取失败")

def get_a_stock_industry():
    """A股板块轮动"""
    print("\n📊 板块轮动")
    print("=" * 50)
    print("板块数据获取较慢，跳过")
    print("提示: 使用 etf-assistant-safe price <code> 查询具体ETF")

def show_help():
    print("""
📰 财经新闻汇总 (全面版)

用法: finance-news-full.py <命令>

命令:
  all         全部概览 (默认)
  a股         A股指数
  行业        板块轮动
  新闻 <关键词>  个股/板块新闻 (默认: 半导体)
  港股        港股新闻
  美股        美股行情
  帮助        显示帮助

需要: pip3 install akshare --break-system-packages
""")

def main():
    if len(sys.argv) < 2:
        command = "all"
    else:
        command = sys.argv[1].lower()
    
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if command == "all":
        get_zh_a_stock()
        get_a_stock_industry()
        get_stock_news("半导体")
        get_us_market()
    elif command == "a股":
        get_zh_a_stock()
    elif command == "行业":
        get_a_stock_industry()
    elif command == "新闻":
        keyword = sys.argv[2] if len(sys.argv) > 2 else "半导体"
        get_stock_news(keyword)
    elif command == "港股":
        get_ggt_news()
    elif command == "美股":
        get_us_market()
    else:
        show_help()

if __name__ == "__main__":
    main()
