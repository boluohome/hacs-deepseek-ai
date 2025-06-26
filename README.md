
hacs-deepseek-integration/
├── custom_components/
│   └── deepseek_integration/
│       ├── __init__.py              # 已更新
│       ├── manifest.json
│       ├── services.yaml
│       ├── brain.py                 # 已更新
│       ├── const.py
│       ├── device_classifier.py     # 已更新
│       └── config_flow.py           # 新增
├── docs/
│   └── README.md
├── hacs.json
└── LICENSE
安装后测试步骤
完全删除旧版本：

bash
# 删除旧集成文件
rm -rf custom_components/deepseek_integration

# 重启Home Assistant
重新安装集成：

通过HACS重新安装

或手动复制更新后的文件

配置集成：

转到 设置 > 设备与服务 > 添加集成

搜索 "DeepSeek Integration"

输入API密钥（32字符）

验证功能：

yaml
service: deepseek_integration.execute_command
data:
  command: "打开客厅的灯"
常见问题解决方案
仍然出现配置错误：

检查Home Assistant日志：/config/home-assistant.log

确保所有文件权限正确（644）

确保文件编码为UTF-8

API调用失败：

验证DeepSeek API密钥有效性

检查网络连接是否正常

设备分类不正确：

更新device_classifier.py中的分类逻辑

在配置中增加自定义分类规则

小爱音箱不响应：

确保已安装Xiaomi MIoT集成

验证小爱音箱实体ID是否正确

这个修复方案添加了正确的配置流处理，解决了Invalid handler specified错误，同时优化了设备分类逻辑和错误处理。
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# DeepSeek 智能家居集成

将 DeepSeek 的强大 AI 能力集成到 Home Assistant 中，实现自适应智能家居控制。

## 功能特性

- 🧠 **智能命令解析**：使用 DeepSeek 理解复杂自然语言命令
- 🔍 **设备自动发现**：自动识别并分类智能家居设备
- 📚 **持续学习**：系统会记住你的习惯并自动优化
- 🗣️ **语音反馈**：通过小爱音箱提供语音响应
- ⚡ **预测性自动化**：基于习惯预测并执行操作

## 安装

### 通过 HACS 安装

1. 打开 HACS
2. 转到 "集成" 部分
3. 点击右下角 "+ 浏览并添加存储库"
4. 搜索 "DeepSeek Integration" 并添加
5. 在集成页面安装

### 手动安装

1. 将 `custom_components/deepseek_integration` 复制到你的 Home Assistant 的 `custom_components` 目录
2. 重启 Home Assistant

## 配置

### 通过 UI 配置

1. 转到 **设置** > **设备与服务** > **添加集成**
2. 搜索 "DeepSeek Integration"
3. 输入你的 DeepSeek API 密钥
4. 根据需要调整设置

### 通过 configuration.yaml

```yaml
deepseek_integration:
  deepseek_api_key: "your_api_key_here"
  auto_discover_interval: 1800  # 每30分钟自动扫描一次设备
```

## 使用

### 基本命令

通过服务调用执行命令：

```yaml
service: deepseek_integration.execute_command
data:
  command: "打开客厅的灯"
```

### 与小爱音箱集成

1. 确保小爱音箱已集成到 Home Assistant
2. 通过对话代理与小爱交互：

```
你: "小爱同学，告诉DeepSeek我觉得有点热"
小爱: "好的，正在将空调温度调低2度"
```

### 自动化示例

```yaml
automation:
  - alias: "晚上回家自动开灯"
    trigger:
      - platform: state
        entity_id: binary_sensor.front_door
        to: "on"
        for:
          minutes: 1
    condition:
      - condition: sun
        after: sunset
    action:
      - service: deepseek_integration.execute_command
        data:
          command: "打开门厅和客厅的灯"
```

## 获取 API 密钥

1. 访问 [DeepSeek 官网](https://www.deepseek.com)
2. 创建账户
3. 在开发者控制台获取 API 密钥

## 支持

如有问题，请在 [GitHub Issues](https://github.com/boluohome/hacs-deepseek-integration/issues) 报告
