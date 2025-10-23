from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import os
import subprocess
import shutil
import threading
import time
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Global variable to store processing status
processing_status = {}

def check_ffmpeg():
    """Check if FFmpeg is installed and available in PATH."""
    return shutil.which("ffmpeg") is not None

def convert_mkv_to_mp4(input_file, output_file=None, task_id=None):
    """Convert an MKV file to MP4 using FFmpeg."""
    if not output_file:
        output_dir = os.path.join(app.config['OUTPUT_FOLDER'], "mp4")
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.basename(input_file)
        output_file = os.path.join(output_dir, os.path.splitext(filename)[0] + ".mp4")

    if task_id:
        processing_status[task_id] = {"status": "processing", "message": f"Converting {os.path.basename(input_file)} to MP4..."}

    command = [
        "ffmpeg",
        "-i", input_file,
        "-c:v", "copy",
        "-c:a", "aac",
        "-strict", "experimental",
        output_file,
        "-y"
    ]
    
    try:
        subprocess.run(command, check=True, capture_output=True)
        if task_id:
            processing_status[task_id] = {"status": "completed", "message": "Conversion to MP4 complete.", "output_file": output_file}
        return output_file
    except subprocess.CalledProcessError as e:
        if task_id:
            processing_status[task_id] = {"status": "error", "message": f"Error during conversion: {str(e)}"}
        raise

def extract_mp3_from_mp4(input_file, output_file=None, task_id=None):
    """Extract MP3 audio from an MP4 file using FFmpeg."""
    if not output_file:
        output_dir = os.path.join(app.config['OUTPUT_FOLDER'], "mp3")
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.basename(input_file)
        output_file = os.path.join(output_dir, os.path.splitext(filename)[0] + ".mp3")

    if task_id:
        processing_status[task_id] = {"status": "processing", "message": f"Extracting MP3 from {os.path.basename(input_file)}..."}

    command = [
        "ffmpeg",
        "-i", input_file,
        "-q:a", "0",
        "-map", "a",
        output_file,
        "-y"
    ]
    
    try:
        subprocess.run(command, check=True, capture_output=True)
        if task_id:
            processing_status[task_id] = {"status": "completed", "message": "MP3 extraction complete.", "output_file": output_file}
        return output_file
    except subprocess.CalledProcessError as e:
        if task_id:
            processing_status[task_id] = {"status": "error", "message": f"Error during MP3 extraction: {str(e)}"}
        raise

def compress_mp4(input_file, output_file=None, task_id=None):
    """Compress an MP4 file using FFmpeg with H.264 codec."""
    if not output_file:
        output_dir = os.path.join(app.config['OUTPUT_FOLDER'], "mp4", "compressed")
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.basename(input_file)
        output_file = os.path.join(output_dir, os.path.splitext(filename)[0] + "_compressed.mp4")

    if task_id:
        processing_status[task_id] = {"status": "processing", "message": f"Compressing {os.path.basename(input_file)}..."}

    command = [
        "ffmpeg",
        "-i", input_file,
        "-c:v", "libx264",
        "-crf", "23",
        "-preset", "medium",
        "-c:a", "aac",
        "-b:a", "128k",
        output_file,
        "-y"
    ]
    
    try:
        subprocess.run(command, check=True, capture_output=True)
        if task_id:
            processing_status[task_id] = {"status": "completed", "message": "Compression complete.", "output_file": output_file}
        return output_file
    except subprocess.CalledProcessError as e:
        if task_id:
            processing_status[task_id] = {"status": "error", "message": f"Error during compression: {str(e)}"}
        raise

def process_video_async(input_file, operation, task_id):
    """Process video file asynchronously."""
    try:
        _, ext = os.path.splitext(input_file)
        ext = ext.lower()
        
        if ext == ".mp4":
            if operation == "compress":
                compress_mp4(input_file, task_id=task_id)
            elif operation == "extract_mp3":
                extract_mp3_from_mp4(input_file, task_id=task_id)
        else:
            # For non-MP4 files, convert to MP4 first
            mp4_file = convert_mkv_to_mp4(input_file, task_id=task_id)
            
            if operation == "compress":
                compress_mp4(mp4_file, task_id=task_id)
            elif operation == "extract_mp3":
                extract_mp3_from_mp4(mp4_file, task_id=task_id)
    except Exception as e:
        processing_status[task_id] = {"status": "error", "message": f"Error: {str(e)}"}

@app.route('/')
def index():
    return render_template('index.html', ffmpeg_available=check_ffmpeg())

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    
    file = request.files['file']
    operation = request.form.get('operation')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not operation:
        return jsonify({'error': 'No operation selected'}), 400
    
    if not check_ffmpeg():
        return jsonify({'error': 'FFmpeg is not installed'}), 500
    
    # Save uploaded file
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    # Generate task ID
    task_id = str(int(time.time() * 1000))
    
    # Start processing in background
    thread = threading.Thread(target=process_video_async, args=(file_path, operation, task_id))
    thread.start()
    
    return jsonify({'task_id': task_id, 'message': 'Processing started'})

@app.route('/status/<task_id>')
def get_status(task_id):
    if task_id in processing_status:
        return jsonify(processing_status[task_id])
    else:
        return jsonify({'status': 'not_found', 'message': 'Task not found'}), 404

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['OUTPUT_FOLDER'], filename), as_attachment=True)

@app.route('/results')
def results():
    # Get all output files
    results = []
    for root, dirs, files in os.walk(app.config['OUTPUT_FOLDER']):
        for file in files:
            if file.endswith(('.mp4', '.mp3')):
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                results.append({
                    'name': file,
                    'path': file_path,
                    'size': file_size,
                    'relative_path': os.path.relpath(file_path, app.config['OUTPUT_FOLDER'])
                })
    
    return render_template('results.html', results=results)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)