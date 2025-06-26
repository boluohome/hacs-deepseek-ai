
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
