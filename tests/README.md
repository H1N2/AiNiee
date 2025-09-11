# 测试文件目录

本目录包含AiNiee项目的所有测试和验证相关文件。

## 文件分类

### 单元测试文件
- `test_config_save.py` - 配置保存功能测试
- `test_final_run.py` - 最终运行流程测试
- `test_improved_apis.py` - 改进API功能测试
- `test_translation_api.py` - 翻译API通用测试
- `test_volcano_api.py` - 火山翻译API测试
- `test_volcano_keys.py` - 火山API密钥测试

### 验证脚本
- `final_verification.py` - 最终验证脚本
- `run_verification.py` - 运行验证脚本
- `verify_implementation.py` - 实现验证脚本

### 示例和调试文件
- `simple_test.py` - 简单测试示例
- `ok_tencent.py` - 腾讯翻译API示例
- `ok_test_volcaon.py` - 火山翻译API示例
- `check_api_status.py` - API状态检查工具
- `simple_verify.py` - 简单验证工具

## 使用说明

1. 运行单元测试：
   ```bash
   python tests/test_*.py
   ```

2. 运行验证脚本：
   ```bash
   python tests/verify_implementation.py
   ```

3. 查看API示例：
   参考 `ok_*.py` 文件了解各翻译API的使用方法

## 注意事项

- 运行测试前请确保已正确配置相关API密钥
- 部分测试可能需要网络连接
- 建议在测试环境中运行，避免影响生产数据