import os
import mimetypes
from flask import Blueprint, jsonify, request, send_file
import base64

file_browser_bp = Blueprint('file_browser', __name__)

# 支持的图片格式
SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif'}

def is_image_file(filename):
    """检查文件是否为图片"""
    _, ext = os.path.splitext(filename.lower())
    return ext in SUPPORTED_IMAGE_FORMATS

def generate_thumbnail_placeholder(image_path):
    """生成图片缩略图占位符"""
    try:
        # 简单的base64编码的1x1像素透明图片
        placeholder = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        return placeholder
    except Exception as e:
        print(f"Error generating thumbnail for {image_path}: {e}")
        return None

@file_browser_bp.route('/browse', methods=['GET'])
def browse_directory():
    """浏览目录内容"""
    path = request.args.get('path', '/')
    
    # 安全检查：确保路径是绝对路径
    if not os.path.isabs(path):
        path = os.path.abspath(path)
    print(path)
    # 检查路径是否存在
    if not os.path.exists(path):
        return jsonify({'error': 'Path does not exist'}), 404
    
    # 检查是否为目录
    if not os.path.isdir(path):
        return jsonify({'error': 'Path is not a directory'}), 400
    
    try:
        items = []
        images = []
        
        # 获取目录内容
        for item_name in sorted(os.listdir(path)):
            item_path = os.path.join(path, item_name)
            
            # 跳过隐藏文件
            if item_name.startswith('.'):
                continue
            
            try:
                stat_info = os.stat(item_path)
                is_dir = os.path.isdir(item_path)
                
                item_info = {
                    'name': item_name,
                    'path': item_path,
                    'is_directory': is_dir,
                    'size': stat_info.st_size if not is_dir else 0,
                    'modified': stat_info.st_mtime
                }
                
                items.append(item_info)
                
                # 如果是图片文件，生成缩略图
                if not is_dir and is_image_file(item_name):
                    thumbnail = generate_thumbnail_placeholder(item_path)
                    if thumbnail:
                        image_info = {
                            'name': item_name,
                            'path': item_path,
                            'thumbnail': thumbnail,
                            'size': stat_info.st_size
                        }
                        images.append(image_info)
                        
            except (OSError, PermissionError) as e:
                print(f"Error accessing {item_path}: {e}")
                continue
        
        return jsonify({
            'current_path': path,
            'parent_path': os.path.dirname(path) if path != '/' else None,
            'items': items,
            'images': images
        })
        
    except PermissionError:
        return jsonify({'error': 'Permission denied'}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@file_browser_bp.route('/image/<path:image_path>')
def serve_image(image_path):
    """提供图片文件"""
    if not os.path.exists(image_path):
        return "Image not found", 404
    
    if not is_image_file(image_path):
        return "Not an image file", 400
    
    try:
        return send_file(image_path)
    except Exception as e:
        return f"Error serving image: {str(e)}", 500

@file_browser_bp.route('/thumbnail/<path:image_path>')
def serve_thumbnail(image_path):
    """提供图片缩略图"""
    if not os.path.exists(image_path):
        return "Image not found", 404
    
    if not is_image_file(image_path):
        return "Not an image file", 400
    
    try:
        thumbnail = generate_thumbnail(image_path)
        if thumbnail:
            return jsonify({'thumbnail': thumbnail})
        else:
            return "Error generating thumbnail", 500
    except Exception as e:
        return f"Error generating thumbnail: {str(e)}", 500

