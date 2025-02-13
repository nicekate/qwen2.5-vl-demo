import json
import base64
from PIL import Image, ImageDraw, ImageFont
from PIL import ImageColor
from openai import OpenAI

def encode_image(image_path):
    """将图片转换为 base64 编码"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def smart_resize(height, width, min_pixels=512*28*28, max_pixels=2048*28*28):
    """智能调整图片尺寸"""
    pixels = height * width
    if pixels < min_pixels:
        scale = (min_pixels / pixels) ** 0.5
        return int(height * scale), int(width * scale)
    elif pixels > max_pixels:
        scale = (max_pixels / pixels) ** 0.5
        return int(height * scale), int(width * scale)
    return height, width

def inference_with_api(image_path, prompt, sys_prompt="您是一位助手。", model_id="qwen2.5-vl-72b-instruct", min_pixels=512*28*28, max_pixels=2048*28*28):
    """使用 API 进行推理"""
    base64_image = encode_image(image_path)
    client = OpenAI(
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    messages = [
        {
            "role": "system",
            "content": [{"type": "text", "text": sys_prompt}]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "min_pixels": min_pixels,
                    "max_pixels": max_pixels,
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
                {"type": "text", "text": prompt},
            ],
        }
    ]
    
    completion = client.chat.completions.create(
        model=model_id,
        messages=messages,
    )
    return completion.choices[0].message.content

def extract_json_from_text(text):
    """从文本中提取 JSON 内容"""
    # 尝试多种格式的 JSON 提取
    if "```json" in text:
        # 提取 markdown 代码块中的 JSON
        start_idx = text.find("```json") + 7
        end_idx = text.rfind("```")
        json_str = text[start_idx:end_idx].strip()
    else:
        # 尝试直接解析文本中的 JSON 部分
        json_str = text.strip()
        
    try:
        # 尝试直接解析
        return json.loads(json_str)
    except json.JSONDecodeError:
        # 如果解析失败，尝试清理和修复 JSON 字符串
        import re
        # 移除换行符和多余的空白字符
        cleaned_text = re.sub(r'[\n\r\t\s]+', ' ', json_str)
        # 确保是一个数组格式
        if not cleaned_text.startswith('['):
            cleaned_text = f"[{cleaned_text}"
        if not cleaned_text.endswith(']'):
            cleaned_text = f"{cleaned_text}]"
        return json.loads(cleaned_text)

def plot_bounding_boxes(image, bounding_boxes, input_width, input_height):
    """绘制边界框"""
    width, height = image.size
    draw = ImageDraw.Draw(image)
    
    colors = ['red', 'green', 'blue', 'yellow', 'orange', 'pink', 'purple', 
              'brown', 'gray', 'beige', 'turquoise', 'cyan', 'magenta']
    
    # 打印 API 返回内容以便调试
    print("API 返回内容：")
    print(bounding_boxes)
    
    try:
        # 使用提取函数获取 JSON 数据
        json_output = extract_json_from_text(bounding_boxes)
        print("解析后的 JSON：")
        print(json_output)
    except Exception as e:
        print(f"JSON 解析错误：{e}")
        return image
    
    font = ImageFont.load_default()
    
    for i, box in enumerate(json_output):
        color = colors[i % len(colors)]
        
        try:
            # 转换坐标，添加错误处理
            bbox = box.get("bbox_2d", box.get("bbox", []))
            if not bbox or len(bbox) != 4:
                print(f"警告：第 {i+1} 个边界框数据格式不正确")
                continue
                
            abs_y1 = int(float(bbox[1])/input_height * height)
            abs_x1 = int(float(bbox[0])/input_width * width)
            abs_y2 = int(float(bbox[3])/input_height * height)
            abs_x2 = int(float(bbox[2])/input_width * width)
            
            if abs_x1 > abs_x2:
                abs_x1, abs_x2 = abs_x2, abs_x1
            if abs_y1 > abs_y2:
                abs_y1, abs_y2 = abs_y2, abs_y1
                
            # 绘制边界框
            draw.rectangle(((abs_x1, abs_y1), (abs_x2, abs_y2)), outline=color, width=4)
            
            # 绘制标签
            if "label" in box:
                draw.text((abs_x1 + 8, abs_y1 + 6), box["label"], fill=color, font=font)
        except Exception as e:
            print(f"处理第 {i+1} 个边界框时出错：{e}")
            continue
    
    return image

# 使用示例
if __name__ == "__main__":
    # 图片路径和参数设置
    image_path = "./assets/spatial_understanding/boat.png"
    min_pixels = 512*28*28
    max_pixels = 2048*28*28
    
    # 加载图片并调整大小
    image = Image.open(image_path)
    width, height = image.size
    input_height, input_width = smart_resize(height, width, min_pixels, max_pixels)
    
    # 设置提示词，强调需要识别每个独立的船
    prompt = """请详细分析图片中的每一个船，识别它们的具体位置。要求：
1. 必须单独框选出每一个船
2. 以 JSON 数组格式输出，每个船的坐标使用 bbox_2d 字段
3. 确保识别所有船，不要遗漏
4. 返回格式示例：[{"bbox_2d":[x1,y1,x2,y2],"label":"船1"},...]"""
    
    # 进行推理
    response = inference_with_api(image_path, prompt, min_pixels=min_pixels, max_pixels=max_pixels)
    
    # 绘制结果
    result_image = plot_bounding_boxes(image, response, input_width, input_height)
    
    # 保存结果
    result_image.save("result-boat.png")
    print("处理完成，结果已保存为 result-boat.png")