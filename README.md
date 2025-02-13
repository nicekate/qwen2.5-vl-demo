# Qwen2.5 VL 图像分析演示

这是一个基于通义千问 Qwen2.5 VL（视觉语言）模型的图像分析演示项目。项目提供了两种使用方式：Web 界面和本地 Gradio 界面，方便用户通过不同方式体验模型的图像分析能力。

## 功能特点

### Web 版本 (`app.py`)
- 支持批量上传和分析多张图片
- 自定义提示词引导模型分析
- 实时图片预览功能
- Markdown 格式的分析结果展示
- 支持下载分析结果为 Markdown 文件
- 美观的响应式界面设计

### 本地版本 (`local-qwen.py`)
- 适用Mac M 芯片电脑
- 基于 Gradio 的简洁界面
- 使用本地模型进行推理
- 自动语言检测（中英双语支持）
- 可调节生成参数（最大长度、采样温度等）


## 使用方法

### Web 版本

1. 安装依赖：
```bash
pip install flask openai
```

2. 配置 API：
- 在 `app.py` 中设置魔搭平台的 API Token
- Token 获取地址：https://modelscope.cn/my/myaccesstoken

3. 运行服务：
```bash
python app.py
```

4. 打开浏览器访问：`http://localhost:5000`

### 本地版本

1. 安装依赖：
```bash
pip install gradio mlx-vlm
```

2. 运行程序：
```bash
python local-qwen.py
```

3. 打开浏览器访问 Gradio 界面

## 注意事项

1. Web 版本需要有效的魔搭平台 API Token
2. 本地版本需要足够的计算资源来运行模型
3. 上传图片大小和格式可能有限制
4. 分析结果的生成可能需要一定时间，请耐心等待


## 高级功能演示

请先克隆 https://github.com/QwenLM/Qwen2.5-VL 到本地，然后将 computer_use.py 和 spatial_understanding_boat.py 放到 cookbooks 文件夹下，然后运行。

### 界面交互分析 (`computer_use.py`)

这个模块展示了模型在理解和交互界面元素方面的能力：

- 支持界面元素定位和交互指令理解
- 可视化点击位置和交互建议
- 适用于GUI自动化测试场景
- 支持自定义颜色的可视化标注

使用方法：

# 设置 API Key
DASHSCOPE_API_KEY="your key"  # 从 https://bailian.console.aliyun.com/ 获取

# 运行演示
python computer_use.py


### 空间理解分析 (`spatial_understanding_boat.py`)

这个模块展示了模型在空间关系理解和目标检测方面的能力：

- 支持多目标检测和定位
- 自动边界框绘制和标注
- 智能图像尺寸调整
- 支持自定义检测提示词
- 多种颜色标注支持

使用方法：

# 配置文件中设置 API Key（来自 https://bailian.console.aliyun.com/）
# 运行演示
python spatial_understanding_boat.py

