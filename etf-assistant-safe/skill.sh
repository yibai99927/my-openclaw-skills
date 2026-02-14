#!/bin/bash
# ETF投资助理 (安全版) - Clawdbot Skill
# 功能：ETF查询、行情、筛选、对比、定投计算
# 安全改进：仅使用 Yahoo Finance 公开API，无敏感操作

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 常用ETF列表
ETF_LIST="510300:沪深300ETF
510500:中证500ETF
159915:创业板ETF
159941:纳指ETF
513100:恒生ETF
510880:红利ETF
159919:科创50ETF
159997:芯片ETF
159995:新能源车ETF
512880:光伏ETF
512760:券商ETF
512170:医疗ETF
159845:中证1000ETF
511880:中证消费ETF"

show_help() {
    echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║      ETF投资助理 (安全版)              ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
    echo ""
    echo "用法: $0 <命令> [参数]"
    echo ""
    echo "命令:"
    echo "  list              显示常用ETF列表"
    echo "  price <代码>      查询ETF实时行情"
    echo "  hot               显示热门ETF"
    echo "  search <关键词>   搜索ETF"
    echo "  compare <代码1> <代码2>  对比两只ETF"
    echo "  calc <代码> <金额> <年限>  定投计算器"
    echo "  summary           ETF投资摘要"
    echo ""
    echo "数据来源: Yahoo Finance (公开API)"
}

get_etf_name() {
    local code=$1
    echo "$ETF_LIST" | grep "^${code}:" | cut -d: -f2 | sed 's/^/未知ETF/g'
}

cmd_list() {
    echo -e "${GREEN}📊 常用ETF列表${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━"
    printf "%-10s %-20s\n" "代码" "名称"
    echo "━━━━━━━━━━━━━━━━━━━━"
    echo "$ETF_LIST" | sort
    echo "━━━━━━━━━━━━━━━━━━━━"
}

cmd_price() {
    local code=$1
    if [ -z "$code" ]; then
        echo -e "${RED}❌ 请输入ETF代码${NC}"
        return 1
    fi
    
    local name=$(get_etf_name "$code")
    echo -e "${GREEN}📈 $name ($code) 实时行情${NC}"
    echo ""
    
    # 使用curl获取数据 (添加User-Agent避免限流)
    local response=$(curl -s --max-time 10 -H "User-Agent: Mozilla/5.0" -H "User-Agent: Mozilla/5.0" "https://query1.finance.yahoo.com/v8/finance/chart/${code}.SS" 2>/dev/null)
    
    if echo "$response" | grep -q "timestamp"; then
        local current=$(echo "$response" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    result = data.get('chart', {}).get('result', [{}])[0]
    meta = result.get('meta', {})
    print(meta.get('regularMarketPrice', 'N/A'))
except: print('N/A')
" 2>/dev/null)
        
        local prev_close=$(echo "$response" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    result = data.get('chart', {}).get('result', [{}])[0]
    meta = result.get('meta', {})
    print(meta.get('previousClose', 'N/A'))
except: print('N/A')
" 2>/dev/null)
        
        local change=$(echo "$response" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    result = data.get('chart', {}).get('result', [{}])[0]
    meta = result.get('meta', {})
    diff = float(meta.get('regularMarketPrice', 0)) - float(meta.get('previousClose', 0))
    pct = diff / float(meta.get('previousClose', 1)) * 100
    print(f'{diff:+.4f} ({pct:+.2f}%)')
except: print('N/A')
" 2>/dev/null)
        
        echo -e "当前价格: ${GREEN}$current${NC}"
        echo -e "昨收: $prev_close"
        echo -e "涨跌: $change"
        
        if [[ "$change" == +* ]]; then
            echo -e "${GREEN}📈 上涨${NC}"
        else
            echo -e "${RED}📉 下跌${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ 暂时无法获取行情数据${NC}"
    fi
}

cmd_hot() {
    echo -e "${GREEN}🔥 热门ETF推荐${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━"
    echo "1. 沪深300ETF (510300) - 蓝筹白马"
    echo "2. 科创50ETF (159919) - 科技创新"
    echo "3. 纳指ETF (159941) - 美股科技"
    echo "4. 恒生ETF (513100) - 港股核心"
    echo "5. 芯片ETF (159997) - 半导体"
    echo "━━━━━━━━━━━━━━━━━━━━"
}

cmd_search() {
    local keyword=$1
    if [ -z "$keyword" ]; then
        echo -e "${RED}❌ 请输入搜索关键词${NC}"
        return 1
    fi
    
    echo -e "${GREEN}🔍 搜索: $keyword${NC}"
    local results=$(echo "$ETF_LIST" | grep -i "$keyword")
    
    if [ -z "$results" ]; then
        echo "未找到相关ETF"
    else
        echo "$results"
    fi
}

cmd_compare() {
    local code1=$1
    local code2=$2
    
    if [ -z "$code1" ] || [ -z "$code2" ]; then
        echo -e "${RED}❌ 请输入两个ETF代码${NC}"
        return 1
    fi
    
    echo -e "${GREEN}📊 ETF对比${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━"
    
    local price1=$(curl -s --max-time 10 -H "User-Agent: Mozilla/5.0" "https://query1.finance.yahoo.com/v8/finance/chart/${code1}.SS" 2>/dev/null | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    result = data.get('chart', {}).get('result', [{}])[0]
    print(result.get('meta', {}).get('regularMarketPrice', 'N/A'))
except: print('N/A')
" 2>/dev/null)
    
    local price2=$(curl -s --max-time 10 -H "User-Agent: Mozilla/5.0" "https://query1.finance.yahoo.com/v8/finance/chart/${code2}.SS" 2>/dev/null | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    result = data.get('chart', {}).get('result', [{}])[0]
    print(result.get('meta', {}).get('regularMarketPrice', 'N/A'))
except: print('N/A')
" 2>/dev/null)
    
    echo -e "$code1: $price1"
    echo -e "$code2: $price2"
    echo "━━━━━━━━━━━━━━━━━━━━"
}

cmd_calc() {
    local code=$1
    local amount=$2
    local years=$3
    
    if [ -z "$code" ] || [ -z "$amount" ] || [ -z "$years" ]; then
        echo -e "${RED}❌ 用法: $0 calc <代码> <月投金额> <年限>${NC}"
        return 1
    fi
    
    echo -e "${GREEN}🧮 定投计算器${NC}"
    echo "代码: $code"
    echo "月投: $amount 元"
    echo "年限: $years 年"
    echo ""
    echo "📝 假设年均收益率 7%"
    echo ""
    
    local months=$((years * 12))
    local total=$((amount * months))
    # 简化计算: FV = PMT * (((1+r)^n - 1) / r)
    local rate=0.07
    local monthly_rate=$(echo "scale=6; $rate/12" | bc)
    local future=$(echo "scale=2; $amount * ((1+$monthly_rate)^$months - 1) / $monthly_rate" | bc 2>/dev/null || echo "计算需要bc")
    
    echo "总投入: $total 元"
    echo "预估价值: $future 元"
    echo ""
    echo "⚠️ 仅供参考，不构成投资建议"
}

cmd_summary() {
    echo -e "${GREEN}📋 ETF投资摘要${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━"
    echo "宽基指数:"
    echo "  510300 沪深300ETF - A股核心蓝筹"
    echo "  510500 中证500ETF - 中盘成长"
    echo "  159915 创业板ETF - 新兴产业"
    echo ""
    echo "行业主题:"
    echo "  159919 科创50ETF - 科技创新"
    echo "  159997 芯片ETF - 半导体"
    echo "  159995 新能源车ETF - 新能源"
    echo ""
    echo "海外ETF:"
    echo "  159941 纳指ETF - 美股科技"
    echo "  513100 恒生ETF - 港股"
    echo "━━━━━━━━━━━━━━━━━━━━"
    echo "⚠️ 投资有风险，入市需谨慎"
}

# 主逻辑
COMMAND=${1:-help}
case $COMMAND in
    list) cmd_list ;;
    price) cmd_price "$2" ;;
    hot) cmd_hot ;;
    search) cmd_search "$2" ;;
    compare) cmd_compare "$2" "$3" ;;
    calc) cmd_calc "$2" "$3" "$4" ;;
    summary) cmd_summary ;;
    help|--help|-h) show_help ;;
    *) show_help ;;
esac
