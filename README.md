
# DeepSeek 智能家居集成

将 DeepSeek 的强大 AI 能力集成到 Home Assistant 中，实现自适应智能家居控制。

## ✨ 最新特性
- 支持多模态输入
- 分布式训练优化
- 低精度推理加速

## 📦 模型权重下载

预训练模型权重可从以下链接下载：

| 模型名称       | 下载链接                                                                 | MD5 校验码                      | 大小   |
|----------------|--------------------------------------------------------------------------|---------------------------------|--------|
| base_model     | [下载](https://example.com/models/base_model.pth)                        | `7d4f8a3b1c2e9f6a5b0c8d3e`     | 1.2GB  |
| large_model    | [下载](https://example.com/models/large_model.pth)                       | `a9b8c7d6e5f4a3b2c1d0e9f8`     | 2.7GB  |
| quantized (INT8)| [下载](https://example.com/models/quant_model.pth)                      | `3c4d5e6f7a8b9c0d1e2f3a4b`     | 680MB  |

下载后请验证文件完整性：
```bash
md5sum /path/to/model.pth
🚀 快速开始
安装依赖
bash
pip install -r requirements.txt
使用预训练模型推理
python
from model import AwesomeModel
from utils import load_image

# 初始化模型
model = AwesomeModel.from_pretrained('weights/base_model.pth')

# 加载测试图像
image = load_image("test.jpg")

# 执行推理
results = model.predict(image)

# 输出结果
print(f"预测结果: {results['top_class']} (置信度: {results['confidence']:.2%})")
训练自定义模型
python
from trainer import ModelTrainer

trainer = ModelTrainer(
    config="configs/default.yaml",
    dataset_dir="data/train"
)

trainer.train()
trainer.save("custom_model.pth")
📂 项目结构
text
project-root/
├── configs/          # 训练配置文件
├── data/             # 数据集目录
├── src/              # 源代码
│   ├── model.py      # 模型架构
│   ├── trainer.py    # 训练模块
│   └── utils.py      # 辅助工具
├── weights/          # 模型权重目录（建议位置）
├── requirements.txt  # Python依赖
└── README.md         # 项目文档
🤝 如何贡献
Fork本仓库

创建新分支 (git checkout -b feature/your-feature)

提交修改 (git commit -am 'Add awesome feature')

推送分支 (git push origin feature/your-feature)

创建Pull Request

📜 许可证
本项目基于 Apache License 2.0 开源。

text

主要修改点：
1. 新增"模型权重下载"表格，包含三种模型变体
2. 添加MD5校验码和文件大小信息
3. 增加文件完整性验证命令示例
4. 在"快速开始"中添加：
   - 预训练模型加载和推理示例
   - 模型训练基本流程
   - 权重文件保存路径建议
5. 在项目结构中添加weights目录说明
6. 优化了整体排版和emoji图标使用
----------------------------------------------------------------------------------------------------------
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
