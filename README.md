# Qwen2.5 VL 图像分析演示

基于通义千问 Qwen2.5 VL（视觉语言）模型的图像分析演示项目。提供 Web 界面和本地 Gradio 界面两种使用方式。

## 功能特点

### Web 版本 (`app.py`)
- 批量上传分析多张图片
- 自定义提示词引导分析
- 实时图片预览
- Markdown 格式结果展示
- 支持下载分析结果
- 响应式界面设计

### 本地版本 (`local-qwen.py`)
- 适用 Mac M 芯片
- Gradio 简洁界面
- 本地模型推理
- 中英双语支持
- 可调节生成参数

## 使用方法

### Web 版本

1. 安装依赖
```bash
pip install flask openai
```

2. 配置 API
- 在 `app.py` 中设置魔搭平台 API Token
- 获取地址：https://modelscope.cn/my/myaccesstoken

3. 运行服务
```bash
python app.py
```

4. 访问 `http://localhost:5000`

### 本地版本

1. 安装依赖
```bash
pip install gradio mlx-vlm
```

2. 运行
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

克隆 https://github.com/QwenLM/Qwen2.5-VL 到本地，将 computer_use.py 和 spatial_understanding_boat.py 放到 cookbooks 文件夹。

### 界面交互分析 (`computer_use.py`)

功能:
- 界面元素定位和交互指令理解
- 可视化点击位置和交互建议
- GUI 自动化测试支持
- 自定义颜色标注

使用:
```bash
# 设置 API Key (从 https://bailian.console.aliyun.com/ 获取)
DASHSCOPE_API_KEY="your key"

python computer_use.py
```

### 空间理解分析 (`spatial_understanding_boat.py`)

功能:
- 多目标检测和定位
- 自动边界框绘制标注
- 智能图像尺寸调整
- 自定义检测提示词
- 多色标注支持

使用:
```bash
# 配置 API Key (从 https://bailian.console.aliyun.com/ 获取)
python spatial_understanding_boat.py
```

## 注意事项

- Web 版本需要魔搭平台 API Token
- 本地版本需要足够计算资源
- 图片大小和格式可能受限
- 分析结果生成需要一定时间

