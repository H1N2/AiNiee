#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64

def test_keys():
    """测试火山翻译API密钥格式"""
    access_key = "AKLTODc1YTIzYjg0MmIxNDc1NTljZTJiYWZjNGIyYjM0ZjM"
    secret_key = "TlRrek1UZzJZV0kzT1dGaU5HRXpOemxoTldKbVpURXpNemhtT1RWa09XTQ=="
    
    print(f"Access Key: {access_key}")
    print(f"Secret Key: {secret_key}")
    
    # 尝试base64解码secret key
    try:
        decoded_secret = base64.b64decode(secret_key).decode('utf-8')
        print(f"Decoded Secret Key: {decoded_secret}")
    except Exception as e:
        print(f"Secret Key解码失败: {e}")
    
    # 尝试base64解码access key
    try:
        decoded_access = base64.b64decode(access_key).decode('utf-8')
        print(f"Decoded Access Key: {decoded_access}")
    except Exception as e:
        print(f"Access Key解码失败: {e}")

if __name__ == "__main__":
    test_keys()