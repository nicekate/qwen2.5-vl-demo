# -*- coding: utf-8 -*-
import gradio as gr
from mlx_vlm.generate import main as generate_main
import sys
from dataclasses import dataclass
import re
from io import StringIO
import contextlib

@dataclass
class Args:
    model: str = "/Users/katemac/.cache/lm-studio/models/mlx-community/Qwen2.5-VL-7B-Instruct-8bit"
    max_tokens: int = 100
    temp: float = 0.0
    prompt: str = "仔细分析描述这张图."
    image: str = None

@contextlib.contextmanager
def capture_output():
    # 创建StringIO对象来捕获输出
    stdout, stderr = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = stdout, stderr
        yield stdout, stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err

def extract_response(text):
    if not text:  # 处理None或空字符串的情况
        return "生成失败，请重试"
    
    # 清理特殊标记
    text = re.sub(r'<\|vision_start\|><\|image_pad\|><\|vision_end\|><\|im_end\|>\s*<\|im_start\|>assistant\s*', '', text)
    # 提取生成的文本内容
    match = re.search(r'<\|im_start\|>assistant\s*(.*?)(?=\n=+\nPrompt:|$)', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text

def is_chinese(text):
    # 检查文本是否包含中文字符
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            return True
    return False

def format_prompt(prompt):
    # 根据用户输入自动判断语言
    use_chinese = is_chinese(prompt)
    
    if use_chinese:
        system_prompt = """你是一个中文AI助手。请用中文回答问题。"""
    else:
        system_prompt = """You are an English AI assistant. Please answer in English."""
    
    return f"""<|im_start|>system
{system_prompt}
<|im_end|>
<|im_start|>user
{prompt}
<|im_end|>
<|im_start|>assistant
"""

def process_image(image, prompt, max_tokens, temp):
    if not image:
        return "请先上传图片" if is_chinese(prompt) else "Please upload an image first"
        
    # 保存原始参数
    old_argv = sys.argv[:]
    
    # 构建新的命令行参数
    sys.argv = [
        sys.argv[0],
        "--model", Args.model,
        "--max-tokens", str(max_tokens),
        "--temp", str(temp),
        "--prompt", format_prompt(prompt),
        "--image", image
    ]
    
    try:
        # 捕获输出
        with capture_output() as (out, err):
            generate_main()
            output = out.getvalue()
        
        if not output:
            return "生成失败，请重试"
            
        # 提取有效的回复内容
        return extract_response(output)
    except Exception as e:
        return f"发生错误: {str(e)}"
    finally:
        # 恢复原始参数
        sys.argv = old_argv

demo = gr.Interface(
    fn=process_image,
    inputs=[
        gr.Image(type="filepath", label="上传图片"),
        gr.Textbox(value="仔细分析描述这张图.", label="提示词"),
        gr.Slider(minimum=1, maximum=500, value=100, step=1, label="最大生成长度"),
        gr.Slider(minimum=0.0, maximum=1.0, value=0.0, step=0.1, label="采样温度"),
    ],
    outputs=gr.Textbox(label="生成结果", max_lines=10),
    title="Qwen-VL 图像分析",
    description="上传图片并输入提示词，AI将根据提示词语言自动选择回复语言"
)

if __name__ == "__main__":
    demo.launch(share=False) 