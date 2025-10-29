"""
AXIS Capital - API Client
FastAPI 백엔드 호출
"""
import requests
from typing import Optional, Dict, Any


class APIClient:
    """FastAPI 백엔드 API 클라이언트"""

    def __init__(self, base_url: str = "http://localhost:7000"):
        self.base_url = base_url
        self.token: Optional[str] = None

    def set_token(self, token: str):
        """JWT 토큰 설정"""
        self.token = token

    def _get_headers(self) -> Dict[str, str]:
        """요청 헤더 생성"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    # ===== Health Check =====
    def health_check(self) -> Dict[str, Any]:
        """시스템 상태 확인"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # ===== 회원가입 =====
    def register(
        self,
        username: str,
        email: str,
        password: str,
        binance_api_key: str,
        binance_api_secret: str,
        risk_profile: str = "balanced"
    ) -> Dict[str, Any]:
        """
        회원가입

        Returns:
            dict: 성공 시 사용자 정보, 실패 시 에러
        """
        try:
            data = {
                "username": username,
                "email": email,
                "password": password,
                "binance_api_key": binance_api_key,
                "binance_api_secret": binance_api_secret,
                "risk_profile": risk_profile,
            }
            response = requests.post(
                f"{self.base_url}/api/v1/auth/register",
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.HTTPError as e:
            return {"success": False, "error": e.response.json().get("detail", str(e))}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ===== 로그인 =====
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        로그인

        Returns:
            dict: 성공 시 토큰 정보, 실패 시 에러
        """
        try:
            data = {
                "username": username,
                "password": password,
            }
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json=data,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            # 토큰 저장
            self.set_token(result["access_token"])
            return {"success": True, "data": result}
        except requests.exceptions.HTTPError as e:
            return {"success": False, "error": e.response.json().get("detail", str(e))}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ===== 내 정보 조회 =====
    def get_me(self) -> Dict[str, Any]:
        """
        내 정보 조회 (인증 필요)

        Returns:
            dict: 성공 시 사용자 정보, 실패 시 에러
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/users/me",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.HTTPError as e:
            return {"success": False, "error": e.response.json().get("detail", str(e))}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ===== 내 정보 수정 =====
    def update_me(self, email: Optional[str] = None, risk_profile: Optional[str] = None) -> Dict[str, Any]:
        """
        내 정보 수정 (인증 필요)

        Returns:
            dict: 성공 시 수정된 사용자 정보, 실패 시 에러
        """
        try:
            data = {}
            if email:
                data["email"] = email
            if risk_profile:
                data["risk_profile"] = risk_profile

            response = requests.put(
                f"{self.base_url}/api/v1/users/me",
                headers=self._get_headers(),
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.HTTPError as e:
            return {"success": False, "error": e.response.json().get("detail", str(e))}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ===== API 키 수정 =====
    def update_api_keys(self, binance_api_key: str, binance_api_secret: str) -> Dict[str, Any]:
        """
        API 키 수정 (인증 필요)

        Returns:
            dict: 성공 시 메시지, 실패 시 에러
        """
        try:
            data = {
                "binance_api_key": binance_api_key,
                "binance_api_secret": binance_api_secret,
            }
            response = requests.put(
                f"{self.base_url}/api/v1/users/me/api-keys",
                headers=self._get_headers(),
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.HTTPError as e:
            return {"success": False, "error": e.response.json().get("detail", str(e))}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ===== AI 의사결정 =====
    def get_my_decisions(self, limit: int = 10) -> Dict[str, Any]:
        """
        내 AI 의사결정 목록 조회 (인증 필요)

        Args:
            limit: 조회 개수 (기본 10)

        Returns:
            dict: 성공 시 의사결정 목록, 실패 시 에러
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/ai/decisions?limit={limit}",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.HTTPError as e:
            return {"success": False, "error": e.response.json().get("detail", str(e))}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_decision(self, decision_id: int) -> Dict[str, Any]:
        """
        특정 AI 의사결정 상세 조회 (인증 필요)

        Args:
            decision_id: 의사결정 ID

        Returns:
            dict: 성공 시 의사결정 상세, 실패 시 에러
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/ai/decisions/{decision_id}",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.HTTPError as e:
            return {"success": False, "error": e.response.json().get("detail", str(e))}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_latest_regime(self) -> Dict[str, Any]:
        """
        최신 시장 레짐 조회

        Returns:
            dict: 성공 시 레짐 정보, 실패 시 에러
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/ai/regime/latest",
                timeout=10
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.HTTPError as e:
            return {"success": False, "error": e.response.json().get("detail", str(e))}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_regime_history(self, limit: int = 10) -> Dict[str, Any]:
        """
        시장 레짐 변경 이력 조회

        Args:
            limit: 조회 개수 (기본 10)

        Returns:
            dict: 성공 시 레짐 이력, 실패 시 에러
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/ai/regime?limit={limit}",
                timeout=10
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.HTTPError as e:
            return {"success": False, "error": e.response.json().get("detail", str(e))}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ===== Market Data =====
    def get_ohlcv(self, symbol: str = "BTC/USDT", timeframe: str = "15m",
                   exchange: str = "binance", limit: int = 100) -> Dict[str, Any]:
        """
        OHLCV 캔들 데이터 조회

        Args:
            symbol: 심볼 (기본: BTC/USDT)
            timeframe: 시간프레임 (기본: 15m)
            exchange: 거래소 (기본: binance)
            limit: 조회 개수 (기본: 100)

        Returns:
            dict: 성공 시 캔들 데이터 목록, 실패 시 에러
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/market/ohlcv/{symbol}",
                params={"timeframe": timeframe, "exchange": exchange, "limit": limit},
                timeout=10
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.HTTPError as e:
            return {"success": False, "error": e.response.json().get("detail", str(e))}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_portfolio_history(self, hours: int = 24) -> Dict[str, Any]:
        """
        내 포트폴리오 가치 이력 조회 (인증 필요)

        Args:
            hours: 조회 기간 (시간 단위, 기본: 24)

        Returns:
            dict: 성공 시 포트폴리오 이력, 실패 시 에러
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/market/portfolio-history",
                headers=self._get_headers(),
                params={"hours": hours},
                timeout=10
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.HTTPError as e:
            return {"success": False, "error": e.response.json().get("detail", str(e))}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_latest_price(self, symbol: str = "BTC/USDT",
                          exchange: str = "binance") -> Dict[str, Any]:
        """
        최신 가격 조회

        Args:
            symbol: 심볼 (기본: BTC/USDT)
            exchange: 거래소 (기본: binance)

        Returns:
            dict: 성공 시 최신 가격 정보, 실패 시 에러
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/market/latest-price/{symbol}",
                params={"exchange": exchange},
                timeout=10
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.HTTPError as e:
            return {"success": False, "error": e.response.json().get("detail", str(e))}
        except Exception as e:
            return {"success": False, "error": str(e)}

