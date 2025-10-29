#!/bin/bash
# API 엔드포인트 테스트 스크립트

echo "=============================================="
echo "자금 이체 API 테스트"
echo "=============================================="
echo ""

# 1. 로그인
echo "1️⃣ 로그인 중..."
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:7000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"devjun","password":"devjun123"}')

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))")

if [ -z "$TOKEN" ]; then
  echo "❌ 로그인 실패"
  echo $LOGIN_RESPONSE
  exit 1
fi

echo "✅ 로그인 성공"
echo ""

# 2. 통합 잔고 조회
echo "2️⃣ 현물/선물 통합 잔고 조회..."
echo "GET /api/v1/trading/balances/all"
echo ""

BALANCE_RESPONSE=$(curl -s -X GET "http://localhost:7000/api/v1/trading/balances/all" \
  -H "Authorization: Bearer $TOKEN")

echo $BALANCE_RESPONSE | python3 -c "
import sys, json
data = json.load(sys.stdin)
spot = data.get('spot', {})
futures = data.get('futures', {})

print('📊 현물 지갑:')
if 'USDT' in spot:
    usdt = spot['USDT']
    print(f'  USDT: {usdt[\"total\"]:,.2f} (사용 가능: {usdt[\"free\"]:,.2f})')

if 'BTC' in spot and spot['BTC']['total'] > 0:
    btc = spot['BTC']
    print(f'  BTC: {btc[\"total\"]:.6f} (사용 가능: {btc[\"free\"]:.6f})')

print()
print('🚀 선물 지갑:')
if 'USDT' in futures:
    usdt = futures['USDT']
    print(f'  USDT: {usdt[\"total\"]:,.2f} (사용 가능: {usdt[\"free\"]:,.2f})')

if 'BTC' in futures and futures['BTC']['total'] > 0:
    btc = futures['BTC']
    print(f'  BTC: {btc[\"total\"]:.6f} (사용 가능: {btc[\"free\"]:.6f})')
"

echo ""
echo "=============================================="
echo "✅ API 테스트 완료"
echo "=============================================="
echo ""
echo "💡 다음 단계: Streamlit UI에서 이체 테스트"
echo "   cd ../streamlit_app && streamlit run Home.py"

