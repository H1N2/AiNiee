import asyncio
import time
from typing import Optional, Dict, Any
import httpx
from Base.Base import Base


class ProxyTester(Base):
    """
    网络代理测试器
    用于测试代理连接的可用性和性能
    """
    
    def __init__(self):
        super().__init__()
        self.test_urls = [
            "https://httpbin.org/ip",
            "https://api.github.com",
            "https://www.google.com",
            "https://api.openai.com/v1/models"
        ]
    
    def test_proxy_sync(self, proxy_url: str, timeout: int = 10) -> Dict[str, Any]:
        """
        同步测试代理连接
        
        参数:
            proxy_url: 代理地址，格式如 http://127.0.0.1:7890
            timeout: 超时时间（秒）
            
        返回:
            测试结果字典
        """
        result = {
            "success": False,
            "proxy_url": proxy_url,
            "response_time": None,
            "error": None,
            "ip_info": None,
            "accessible_urls": []
        }
        
        try:
            start_time = time.time()
            
            # 测试基本连接
            with httpx.Client(proxy=proxy_url, timeout=timeout) as client:
                # 测试IP获取
                try:
                    response = client.get("https://httpbin.org/ip")
                    if response.status_code == 200:
                        result["ip_info"] = response.json()
                        result["success"] = True
                        result["accessible_urls"].append("https://httpbin.org/ip")
                except Exception as e:
                    self.debug(f"IP测试失败: {e}")
                
                # 测试其他URL
                for url in self.test_urls[1:]:
                    try:
                        response = client.get(url, timeout=5)
                        if response.status_code < 400:
                            result["accessible_urls"].append(url)
                    except Exception as e:
                        self.debug(f"URL {url} 测试失败: {e}")
                
                result["response_time"] = time.time() - start_time
                
        except Exception as e:
            result["error"] = str(e)
            self.error(f"代理测试失败: {e}")
        
        return result
    
    async def test_proxy_async(self, proxy_url: str, timeout: int = 10) -> Dict[str, Any]:
        """
        异步测试代理连接
        
        参数:
            proxy_url: 代理地址
            timeout: 超时时间（秒）
            
        返回:
            测试结果字典
        """
        result = {
            "success": False,
            "proxy_url": proxy_url,
            "response_time": None,
            "error": None,
            "ip_info": None,
            "accessible_urls": []
        }
        
        try:
            start_time = time.time()
            
            async with httpx.AsyncClient(proxy=proxy_url, timeout=timeout) as client:
                # 测试IP获取
                try:
                    response = await client.get("https://httpbin.org/ip")
                    if response.status_code == 200:
                        result["ip_info"] = response.json()
                        result["success"] = True
                        result["accessible_urls"].append("https://httpbin.org/ip")
                except Exception as e:
                    self.debug(f"异步IP测试失败: {e}")
                
                # 并发测试其他URL
                tasks = []
                for url in self.test_urls[1:]:
                    tasks.append(self._test_url_async(client, url))
                
                if tasks:
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    for i, res in enumerate(results):
                        if isinstance(res, str):  # 成功的URL
                            result["accessible_urls"].append(res)
                
                result["response_time"] = time.time() - start_time
                
        except Exception as e:
            result["error"] = str(e)
            self.error(f"异步代理测试失败: {e}")
        
        return result
    
    async def _test_url_async(self, client: httpx.AsyncClient, url: str) -> Optional[str]:
        """
        异步测试单个URL
        
        参数:
            client: HTTP客户端
            url: 测试URL
            
        返回:
            成功时返回URL，失败时返回None
        """
        try:
            response = await client.get(url, timeout=5)
            if response.status_code < 400:
                return url
        except Exception as e:
            self.debug(f"异步URL {url} 测试失败: {e}")
        return None
    
    def test_direct_connection(self, timeout: int = 10) -> Dict[str, Any]:
        """
        测试直连（无代理）网络连接
        
        参数:
            timeout: 超时时间（秒）
            
        返回:
            测试结果字典
        """
        result = {
            "success": False,
            "response_time": None,
            "error": None,
            "ip_info": None,
            "accessible_urls": []
        }
        
        try:
            start_time = time.time()
            
            with httpx.Client(timeout=timeout) as client:
                # 测试IP获取
                try:
                    response = client.get("https://httpbin.org/ip")
                    if response.status_code == 200:
                        result["ip_info"] = response.json()
                        result["success"] = True
                        result["accessible_urls"].append("https://httpbin.org/ip")
                except Exception as e:
                    self.debug(f"直连IP测试失败: {e}")
                
                # 测试其他URL
                for url in self.test_urls[1:]:
                    try:
                        response = client.get(url, timeout=5)
                        if response.status_code < 400:
                            result["accessible_urls"].append(url)
                    except Exception as e:
                        self.debug(f"直连URL {url} 测试失败: {e}")
                
                result["response_time"] = time.time() - start_time
                
        except Exception as e:
            result["error"] = str(e)
            self.error(f"直连测试失败: {e}")
        
        return result
    
    def format_test_result(self, result: Dict[str, Any]) -> str:
        """
        格式化测试结果为可读字符串
        
        参数:
            result: 测试结果字典
            
        返回:
            格式化的结果字符串
        """
        if result["success"]:
            ip_info = result.get("ip_info", {})
            current_ip = ip_info.get("origin", "未知")
            response_time = result.get("response_time", 0)
            accessible_count = len(result.get("accessible_urls", []))
            
            return f"✅ 连接成功\n" \
                   f"当前IP: {current_ip}\n" \
                   f"响应时间: {response_time:.2f}秒\n" \
                   f"可访问URL数量: {accessible_count}/{len(self.test_urls)}"
        else:
            error = result.get("error", "未知错误")
            return f"❌ 连接失败\n错误信息: {error}"