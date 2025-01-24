import os
import sys
import subprocess
import time
from tqdm import tqdm


def convert_video_to_mp4(input_file, output_dir, convert_mp3=False):
    """
    Convert video files (FLV, TS, etc.) to MP4 format and optionally to MP3.
    """
    # 展开用户目录符号 "~"
    output_dir = os.path.expanduser(output_dir)
    print(f"Output directory expanded to: {output_dir}")

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    print(f"Ensured output directory exists: {output_dir}")

    # 提取文件名（不带扩展名）
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    print(f"Base file name extracted: {base_name}")

    # 生成输出文件路径
    output_mp4 = os.path.join(output_dir, f"{base_name}.mp4")

    # 转换为 mp4，使用 -c copy 直接复制流
    print(f"Starting MP4 conversion for {input_file}...")
    try:
        subprocess.run(
            ["ffmpeg", "-i", input_file, "-c", "copy", output_mp4], check=True
        )
        print(f"MP4 conversion complete! File saved at: {output_mp4}")
    except subprocess.CalledProcessError as e:
        print(f"Error during MP4 conversion: {e}")

    # 如果需要转换为 mp3
    if convert_mp3:
        output_mp3 = os.path.join(output_dir, f"{base_name}.mp3")
        print(f"Starting MP3 conversion for {input_file}...")
        try:
            subprocess.run(
                ["ffmpeg", "-i", input_file, "-q:a", "0", "-map", "a", output_mp3],
                check=True,
            )
            print(f"MP3 conversion complete! File saved at: {output_mp3}")
        except subprocess.CalledProcessError as e:
            print(f"Error during MP3 conversion: {e}")
    else:
        print("MP3 conversion skipped as --mp3 argument was not provided.")


def process_directory(input_dir, output_dir, convert_mp3=False):
    """
    Process all supported video files in the input directory.
    """
    input_dir = os.path.expanduser(input_dir)
    supported_formats = [".flv", ".ts"]
    min_size = 100 * 1024 * 1024  # 100MB in bytes

    # 统计信息初始化
    start_time = time.time()
    total_processed = 0
    total_skipped = 0
    
    # 首先收集所有需要处理的文件
    files_to_process = []
    for filename in os.listdir(input_dir):
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext in supported_formats:
            input_file = os.path.join(input_dir, filename)
            file_size = os.path.getsize(input_file)
            if file_size < min_size:
                print(f"\nSkipping {filename} (size: {file_size/1024/1024:.2f}MB - smaller than 100MB)")
                total_skipped += 1
                continue
            files_to_process.append((input_file, file_size))
            
    # 使用tqdm显示进度
    for input_file, file_size in tqdm(files_to_process, desc="Converting files", unit="file"):
        filename = os.path.basename(input_file)
        print(f"\nProcessing file: {filename} (size: {file_size/1024/1024:.2f}MB)")
        convert_video_to_mp4(input_file, output_dir, convert_mp3)
        total_processed += 1

    # 处理完成后显示统计信息
    elapsed_time = time.time() - start_time
    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    seconds = int(elapsed_time % 60)
    
    print("\n=== Conversion Summary ===")
    print(f"Total files processed: {total_processed}")
    print(f"Total files skipped: {total_skipped}")
    print(f"Total time elapsed: {hours:02d}:{minutes:02d}:{seconds:02d}")
    print("========================")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "Usage: python convert_video.py <input_path> <output_directory> [--mp3]\n"
            "Note: input_path can be either a single file or a directory"
        )
        sys.exit(1)

    input_path = sys.argv[1]
    output_dir = sys.argv[2]
    convert_mp3 = "--mp3" in sys.argv

    if os.path.isdir(input_path):
        print(f"Processing directory: {input_path}")
        process_directory(input_path, output_dir, convert_mp3)
    else:
        # 单文件处理逻辑
        file_ext = os.path.splitext(input_path)[1].lower()
        supported_formats = [".flv", ".ts"]
        if file_ext not in supported_formats:
            print(
                f"Unsupported file format. Supported formats are: {', '.join(supported_formats)}"
            )
            sys.exit(1)

        # 检查文件大小
        file_size = os.path.getsize(input_path)
        min_size = 100 * 1024 * 1024  # 100MB in bytes
        if file_size < min_size:
            print(f"File size ({file_size/1024/1024:.2f}MB) is smaller than 100MB. Skipping...")
            sys.exit(1)

        print(
            f"Processing single file...\nInput file: {input_path} (size: {file_size/1024/1024:.2f}MB)\nOutput directory: {output_dir}\nConvert to MP3: {'Yes' if convert_mp3 else 'No'}"
        )
        convert_video_to_mp4(input_path, output_dir, convert_mp3)

    print("\nAll conversion processes completed.")
