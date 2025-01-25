import os
import sys
import subprocess
import time
import logfire

from tqdm import tqdm
from loguru import logger
from dotenv import load_dotenv


load_dotenv()
logfire.configure()
logger.configure(handlers=[logfire.loguru_handler()])


def convert_video_to_mp4(input_file, output_dir, convert_mp3=False, delete_original=False):
    """
    Convert video files (FLV, TS, etc.) to MP4 format and optionally to MP3.
    If delete_original is True, delete the original file after successful conversion.
    """
    # 展开用户目录符号 "~"
    output_dir = os.path.expanduser(output_dir)
    logger.info(f"Output directory expanded to: {output_dir}")

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Ensured output directory exists: {output_dir}")

    # 提取文件名（不带扩展名）
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    logger.info(f"Base file name extracted: {base_name}")

    # 生成输出文件路径
    output_mp4 = os.path.join(output_dir, f"{base_name}.mp4")
    conversion_success = True

    # 检查 MP4 文件是否已存在
    if os.path.exists(output_mp4):
        logger.info(f"MP4 file already exists, skipping conversion: {output_mp4}")
    else:
        # 转换为 mp4，使用 -c copy 直接复制流
        print(f"Starting MP4 conversion for {input_file}...")
        with logfire.span(f"convert {input_file} to mp4"):
            try:
                subprocess.run(
                    ["ffmpeg", "-i", input_file, "-c", "copy", output_mp4], check=True
                )
                logger.info(f"MP4 conversion complete! File saved at: {output_mp4}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Error during MP4 conversion: {e}")
                conversion_success = False

    # 如果需要转换为 mp3
    if convert_mp3 and conversion_success:
        output_mp3 = os.path.join(output_dir, f"{base_name}.mp3")
        if os.path.exists(output_mp3):
            logger.info(f"MP3 file already exists, skipping conversion: {output_mp3}")
        else:
            with logfire.span(f"convert {input_file} to mp3"):
                try:
                    subprocess.run(
                        ["ffmpeg", "-i", input_file, "-q:a", "0", "-map", "a", output_mp3],
                        check=True,
                    )
                    logger.info(f"MP3 conversion complete! File saved at: {output_mp3}")
                except subprocess.CalledProcessError as e:
                    logger.error(f"Error during MP3 conversion: {e}")
                    conversion_success = False
    else:
        logger.info("MP3 conversion skipped as --mp3 argument was not provided.")

    # 如果转换成功且需要删除原文件
    if delete_original and conversion_success:
        try:
            os.remove(input_file)
            logger.info(f"Original file deleted: {input_file}")
        except OSError as e:
            logger.error(f"Error deleting original file: {e}")

    return conversion_success


def process_directory(input_dir, output_dir, convert_mp3=False, delete_original=False):
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
                logger.warning(
                    f"Skipping {filename} (size: {file_size/1024/1024:.2f}MB - smaller than 100MB)"
                )
                total_skipped += 1
                continue
            files_to_process.append((input_file, file_size))

    # 使用tqdm显示进度
    for input_file, file_size in tqdm(
        files_to_process, desc="Converting files", unit="file"
    ):
        filename = os.path.basename(input_file)
        with logfire.span(f"process {filename}"):
            logger.info(f"Processing file: {filename} (size: {file_size/1024/1024:.2f}MB)")
            convert_video_to_mp4(input_file, output_dir, convert_mp3, delete_original)
        total_processed += 1

    # 处理完成后显示统计信息
    elapsed_time = time.time() - start_time
    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    seconds = int(elapsed_time % 60)

    logger.info(f"Total files processed: {total_processed}")
    logger.info(f"Total files skipped: {total_skipped}")
    logger.info(f"Total time elapsed: {hours:02d}:{minutes:02d}:{seconds:02d}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Convert video files to MP4 format')
    parser.add_argument('input_path', help='Input file or directory path')
    parser.add_argument('output_dir', help='Output directory path')
    parser.add_argument('--mp3', action='store_true', help='Extract audio to MP3 format')
    parser.add_argument('--delete', action='store_true', help='Delete original file after successful conversion')
    args = parser.parse_args()

    input_path = args.input_path
    output_dir = args.output_dir
    convert_mp3 = args.mp3
    delete_original = args.delete

    if os.path.isdir(input_path):
        logger.info(f"Processing directory: {input_path}")
        process_directory(input_path, output_dir, convert_mp3, delete_original)
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
            print(
                f"File size ({file_size/1024/1024:.2f}MB) is smaller than 100MB. Skipping..."
            )
            sys.exit(1)

        print("Processing single file...")
        print(f"Input file: {input_path} (size: {file_size/1024/1024:.2f}MB)")
        print(f"Output directory: {output_dir}")
        print(f"Convert to MP3: {'Yes' if convert_mp3 else 'No'}")
        print(f"Delete original: {'Yes' if delete_original else 'No'}")
        
        with logfire.span(f"process file {input_path}"):
            convert_video_to_mp4(input_path, output_dir, convert_mp3, delete_original)

    logger.success("All conversion processes completed.")
