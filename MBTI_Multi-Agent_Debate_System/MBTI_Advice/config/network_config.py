import os
from typing import Optional

class NetworkConfig:
    """网络配置类"""
    
    @staticmethod
    def disable_proxy():
        """禁用所有代理设置"""
        proxy_vars = [
            'HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy',
            'NO_PROXY', 'no_proxy'
        ]
        for var in proxy_vars:
            os.environ[var] = ''
    
    @staticmethod
    def set_proxy(http_proxy: Optional[str] = None, https_proxy: Optional[str] = None):
        """设置代理"""
        if http_proxy:
            os.environ['HTTP_PROXY'] = http_proxy
            os.environ['http_proxy'] = http_proxy
        if https_proxy:
            os.environ['HTTPS_PROXY'] = https_proxy
            os.environ['https_proxy'] = https_proxy
    
    @staticmethod
    def get_proxy_status():
        """获取当前代理状态"""
        return {
            'HTTP_PROXY': os.environ.get('HTTP_PROXY', ''),
            'HTTPS_PROXY': os.environ.get('HTTPS_PROXY', ''),
            'http_proxy': os.environ.get('http_proxy', ''),
            'https_proxy': os.environ.get('https_proxy', '')
        }

class SerpAPIConfig:
    """SerpAPI配置类"""
    
    @staticmethod
    def get_api_key() -> str:
        """获取SerpAPI密钥"""
        return os.getenv('SERPAPI_API_KEY', '')
    
    @staticmethod
    def is_configured() -> bool:
        """检查SerpAPI是否已配置"""
        return bool(SerpAPIConfig.get_api_key())

# 默认配置
DEFAULT_OFFLINE_MODE = True  # 默认使用离线模式避免网络问题
DEFAULT_USE_VECTOR_DB = False 