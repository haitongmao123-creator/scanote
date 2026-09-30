# -*- coding: utf-8 -*-
"""
主程序 - 一键运行
功能：从邮箱抓取扫描件PDF → OCR识别+AI命名 → 保存到 E:\桌面
"""

import os
import sys
import shutil
import tempfile
import time
from datetime import datetime

import config
from email_fetcher import process_mailbox
from ocr_processor import process_pdf


def handle_pdf(original_filename, pdf_bytes):
    """处理单个PDF：保存临时文件 → OCR+命名 → 复制到目标目录"""
    print(f"\n{'='*60}")
    print(f"📄 开始处理: {original_filename}")
    print(f"{'='*60}")

    # 1. 保存到临时目录
    os.makedirs(config.TEMP_DIR, exist_ok=True)
    temp_pdf = os.path.join(config.TEMP_DIR, original_filename)
    with open(temp_pdf, 'wb') as f:
        f.write(pdf_bytes)

    # 2. OCR + 命名
    new_filename, debug_info = process_pdf(temp_pdf, original_filename)

    # 3. 打印调试信息
    print(f"\n📋 调试信息:")
    for line in debug_info:
        print(f"  {line}")

    # 4. 复制到目标目录（用新文件名）
    output_path = os.path.join(config.OUTPUT_DIR, new_filename)

    # 如果目标目录已存在同名文件，加时间戳避免覆盖
    if os.path.exists(output_path):
        timestamp = datetime.now().strftime("%H%M%S")
        name, ext = os.path.splitext(new_filename)
        output_path = os.path.join(config.OUTPUT_DIR, f"{name}_{timestamp}{ext}")

    shutil.copy2(temp_pdf, output_path)
    print(f"\n💾 已保存到: {output_path}")

    # 5. 清理临时文件
    try:
        os.remove(temp_pdf)
    except Exception:
        pass

    return new_filename


def check_config():
    """检查配置是否填写"""
    if config.EMAIL_AUTH_CODE == "在这里填你的授权码":
        print("❌ 错误：请先在 config.py 中填写邮箱授权码（EMAIL_AUTH_CODE）")
        print("   步骤：登录 mail.qiye.163.com → 设置 → 客户端设置 → 开启IMAP → 生成授权码")
        return False

    if not os.path.exists(config.TESSERACT_PATH):
        print(f"❌ 错误：找不到 Tesseract，路径: {config.TESSERACT_PATH}")
        print("   请安装 Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki")
        print("   安装后如果路径不同，修改 config.py 里的 TESSERACT_PATH")
        return False

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    os.makedirs(config.TEMP_DIR, exist_ok=True)
    return True


def check_dependencies():
    """检查依赖库是否安装"""
    missing = []
    try:
        import imaplib
    except ImportError:
        missing.append('imaplib')  # 标准库，一般不会缺

    try:
        import PIL
    except ImportError:
        missing.append('Pillow')

    try:
        import pytesseract
    except ImportError:
        missing.append('pytesseract')

    try:
        import fitz
    except ImportError:
        missing.append('PyMuPDF')

    if missing:
        print("❌ 缺少依赖库，请运行以下命令安装：")
        print(f"   pip install {' '.join(missing)}")
        print("\n或者直接运行：")
        print("   pip install -r requirements.txt")
        return False
    return True


def main():
    print("=" * 60)
    print("  识笺 Scannote - 邮箱扫描件自动命名工具")
    print("  版本: v20260904-10 (Python版)")
    print("=" * 60)

    # 检查配置和依赖
    if not check_dependencies():
        sys.exit(1)
    if not check_config():
        sys.exit(1)

    print(f"\n📌 配置信息:")
    print(f"   邮箱: {config.EMAIL_ADDRESS}")
    print(f"   监听发件人: {config.LISTEN_SENDER or '所有发件人'}")
    print(f"   保存目录: {config.OUTPUT_DIR}")
    print(f"   检查间隔: {config.CHECK_INTERVAL}秒")
    print(f"   单次处理上限: {config.MAX_PROCESS if config.MAX_PROCESS > 0 else '持续监听'}")
    print(f"\n💡 提示: 调试时建议 MAX_PROCESS=1，跑通后改为0持续监听")
    print(f"{'='*60}\n")

    # 开始监听邮箱
    try:
        process_mailbox(
            callback=handle_pdf,
            max_process=config.MAX_PROCESS,
            mark_as_read=config.MARK_AS_READ,
            interval=config.CHECK_INTERVAL,
            sender_filter=config.LISTEN_SENDER
        )
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，程序退出")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
