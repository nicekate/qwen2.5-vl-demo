import base64
import os
from flask import Flask, request, render_template, jsonify
from openai import OpenAI

app = Flask(__name__)

# 确保上传文件夹存在
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def analyze_image_with_qwen(image_path, prompt):
    # 将图片转换为base64
    with open(image_path, 'rb') as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')

    client = OpenAI(
        base_url='https://api-inference.modelscope.cn/v1/',
        api_key='xxx'  #魔搭平台的Token,https://modelscope.cn/my/myaccesstoken
    )

    # 如果没有提供提示词，使用默认的
    if not prompt:
        prompt = '描述这幅图'

    response = client.chat.completions.create(
        model='Qwen/Qwen2.5-VL-72B-Instruct',  # ModelScope Model-Id
        messages=[{
            'role': 'user',
            'content': [{
                'type': 'text',
                'text': prompt,
            }, {
                'type': 'image_url',
                'image_url': {
                    'url': f'data:image/jpeg;base64,{base64_image}'
                },
            }],
        }],
        stream=False  # 改为非流式以便获取完整响应
    )

    return response.choices[0].message.content

@app.route('/')
def index():
    return '''
    <!doctype html>
    <html>
    <head>
        <title>图片分析</title>
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/github-markdown-css/github-markdown.css">
        <style>
            body { margin: 0; padding: 20px; font-family: Arial, sans-serif; }
            .container { display: flex; gap: 20px; height: calc(100vh - 40px); }
            .left-panel { flex: 1; overflow-y: auto; padding: 20px; }
            .right-panel { flex: 1; overflow-y: auto; padding: 20px; }
            .upload-form { margin-bottom: 20px; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
            .result { margin-bottom: 20px; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
            .loading { display: none; }
            .form-group { margin-bottom: 15px; }
            textarea { width: 100%; height: 100px; margin: 10px 0; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            .btn { background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px; }
            .btn:hover { background-color: #45a049; }
            .image-preview { margin: 15px 0; }
            .image-preview img { max-width: 100%; max-height: 300px; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 10px; }
            .preview-container { margin-bottom: 20px; }
            .markdown-body { padding: 20px; background-color: white; border-radius: 5px; }
            pre { background-color: #f6f8fa; padding: 16px; border-radius: 6px; overflow-x: auto; }
            code { font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace; }
            .result-actions { margin-top: 10px; }
            #allResults { margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="left-panel">
                <h2>图片上传与预览</h2>
                <div class="upload-form">
                    <form id="uploadForm" enctype="multipart/form-data">
                        <div class="form-group">
                            <label>选择图片（可多选）：</label>
                            <input type="file" name="files" accept="image/*" required id="imageInput" multiple>
                        </div>
                        <div class="preview-container" id="previewContainer"></div>
                        <div class="form-group">
                            <label>输入提示词（可选）：</label>
                            <textarea name="prompt" placeholder="输入您的提示词，例如：请详细描述这幅图片中的内容"></textarea>
                        </div>
                        <button type="submit" class="btn">批量上传并分析</button>
                    </form>
                </div>
            </div>
            <div class="right-panel">
                <h2>分析结果</h2>
                <div id="loading" class="loading">分析中，请稍候...</div>
                <div id="allResults"></div>
            </div>
        </div>

        <script>
        // 图片预览功能
        document.getElementById('imageInput').onchange = function(e) {
            const previewContainer = document.getElementById('previewContainer');
            previewContainer.innerHTML = ''; // 清除之前的预览
            
            if (this.files) {
                Array.from(this.files).forEach(file => {
                    const previewDiv = document.createElement('div');
                    previewDiv.className = 'image-preview';
                    
                    const img = document.createElement('img');
                    img.src = URL.createObjectURL(file);
                    previewDiv.appendChild(img);
                    
                    // 添加文件名
                    const fileName = document.createElement('div');
                    fileName.textContent = file.name;
                    previewDiv.appendChild(fileName);
                    
                    previewContainer.appendChild(previewDiv);
                    
                    // 释放 URL 对象
                    img.onload = function() {
                        URL.revokeObjectURL(this.src);
                    }
                });
            }
        };

        // 下载Markdown文件
        function downloadMarkdown(content, filename) {
            const blob = new Blob([content], { type: 'text/markdown' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }

        document.getElementById('uploadForm').onsubmit = async function(e) {
            e.preventDefault();
            const files = document.getElementById('imageInput').files;
            const prompt = document.querySelector('textarea[name="prompt"]').value;
            const loading = document.getElementById('loading');
            const allResults = document.getElementById('allResults');
            
            loading.style.display = 'block';
            allResults.innerHTML = '';
            
            for (let i = 0; i < files.length; i++) {
                const formData = new FormData();
                formData.append('file', files[i]);
                formData.append('prompt', prompt);
                
                try {
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await response.json();
                    
                    const resultDiv = document.createElement('div');
                    resultDiv.className = 'result markdown-body';
                    
                    // 添加文件名
                    const fileNameHeader = document.createElement('h3');
                    fileNameHeader.textContent = files[i].name;
                    resultDiv.appendChild(fileNameHeader);
                    
                    // 添加分析结果
                    const contentDiv = document.createElement('div');
                    contentDiv.innerHTML = marked.parse(data.result);
                    resultDiv.appendChild(contentDiv);
                    
                    // 添加下载按钮
                    const actions = document.createElement('div');
                    actions.className = 'result-actions';
                    const downloadBtn = document.createElement('button');
                    downloadBtn.className = 'btn';
                    downloadBtn.textContent = '下载Markdown';
                    downloadBtn.onclick = () => downloadMarkdown(data.result, `${files[i].name}_分析结果.md`);
                    actions.appendChild(downloadBtn);
                    resultDiv.appendChild(actions);
                    
                    allResults.appendChild(resultDiv);
                } catch (error) {
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'result';
                    errorDiv.textContent = `处理 ${files[i].name} 时发生错误：${error}`;
                    allResults.appendChild(errorDiv);
                }
            }
            
            loading.style.display = 'none';
        };
        </script>
    </body>
    </html>
    '''

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件被上传'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'})
    
    if file:
        # 保存上传的文件
        filename = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filename)
        
        try:
            # 获取提示词
            prompt = request.form.get('prompt', '')
            # 分析图片
            result = analyze_image_with_qwen(filename, prompt)
            # 删除临时文件
            os.remove(filename)
            return jsonify({'result': result})
        except Exception as e:
            # 确保清理临时文件
            if os.path.exists(filename):
                os.remove(filename)
            return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)