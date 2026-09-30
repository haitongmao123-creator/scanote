# -*- coding: utf-8 -*-
"""
Tesseract OCR 一键安装脚本
自动下载安装 Tesseract 引擎 + 中文语言包（chi_sim）

使用方法：
  1. 右键 → 以管理员身份运行（必须，否则装不进 C:\\Program Files）
  2. 或在管理员 PowerShell 里执行：
     C:\\Users\\mycapital\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe install_tesseract.py
"""

import os
import sys
import subprocess
import urllib.request

# ============ 配置 ============
# 安装目录（和 config.py 的 TESSERACT_PATH 保持一致）
INSTALL_DIR = r"C:\Program Files\Tesseract-OCR"
TESSDATA_DIR = os.path.join(INSTALL_DIR, "tessdata")

# UB-Mannheim 官方安装包（固定版本，稳定）
TESSERACT_URL = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.4.20240603/tesseract-ocr-w64-setup-5.3.4.20240603.exe"

# GitHub 国内访问慢时用的镜像（自动回退）
MIRROR_PREFIX = "https://ghfast.top/"

# 需要的语言包
LANG_FILES = {
    "chi_sim.traineddata": "https://github.com/tesseract-ocr/tessdata/raw/main/chi_sim.traineddata",
    "eng.traineddata":     "https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata",
}


def download(url, dest):
    """带进度显示的下载"""
    print(f"  ↓ 下载: {url}")
    print(f"    保存到: {dest}")
    try:
        # 加 User-Agent 避免 GitHub 拒绝
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            done = 0
            with open(dest, "wb") as f:
                while True:
                    chunk = resp.read(64 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    done += len(chunk)
                    if total:
                        pct = done * 100 // total
                        print(f"\r    进度: {pct}% ({done//1024}KB/{total//1024}KB)", end="")
            print()
        return True
    except Exception as e:
        print(f"\n  ✗ 下载失败: {e}")
        return False


def download_with_mirror(url, dest):
    """先试原地址，失败则用镜像"""
    if download(url, dest):
        return True
    print("  ↻ 尝试镜像加速...")
    return download(MIRROR_PREFIX + url, dest)


def is_tesseract_installed():
    exe = os.path.join(INSTALL_DIR, "tesseract.exe")
    return os.path.exists(exe)


def is_admin():
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def main():
    print("=" * 60)
    print("  Tesseract OCR 一键安装 (含中文语言包)")
    print("=" * 60)

    # 0. 管理员权限检查（装到 Program Files 必须管理员）
    if not is_tesseract_installed() and not is_admin():
        print("⚠️  当前不是管理员权限，安装 Tesseract 到 C:\\Program Files 会失败！")
        print("   请右键此脚本 → 以管理员身份运行")
        print("   或在管理员 PowerShell 里执行：")
        print(f'   "{sys.executable}" "{os.path.abspath(__file__)}"')
        sys.exit(1)

    # 1. 安装 Tesseract 引擎
    if is_tesseract_installed():
        print(f"✅ Tesseract 已安装: {INSTALL_DIR}（跳过安装步骤）")
    else:
        print("⚠️  未检测到 Tesseract，开始下载安装...")
        installer = os.path.join(os.environ.get("TEMP", "."), "tesseract_setup.exe")
        if not download_with_mirror(TESSERACT_URL, installer):
            print("❌ 安装包下载失败，请手动下载：")
            print(f"   {TESSERACT_URL}")
            print(f"   双击运行，安装到 {INSTALL_DIR}")
            sys.exit(1)

        print("📦 静默安装中...")
        try:
            # /S 静默安装  /D 指定目录（必须放最后一个参数，且不带引号）
            subprocess.run([installer, "/S", f"/D={INSTALL_DIR}"], check=True)
            print("✅ 安装完成")
        except subprocess.CalledProcessError as e:
            print(f"❌ 静默安装失败: {e}")
            print("  请手动双击安装包运行，安装到默认路径")
            sys.exit(1)

    # 2. 检查/下载语言包
    print("\n📥 检查语言包...")
    os.makedirs(TESSDATA_DIR, exist_ok=True)
    for name, url in LANG_FILES.items():
        dest = os.path.join(TESSDATA_DIR, name)
        if os.path.exists(dest) and os.path.getsize(dest) > 1000000:
            print(f"✅ 已存在: {name}")
            continue
        print(f"\n📥 下载语言包: {name}")
        if download_with_mirror(url, dest):
            print(f"✅ 完成: {name}")
        else:
            print(f"❌ {name} 下载失败")
            print(f"  请手动下载 {url}")
            print(f"  放到 {dest}")

    # 3. 验证
    print("\n" + "=" * 60)
    if is_tesseract_installed():
        try:
            r = subprocess.run(
                [os.path.join(INSTALL_DIR, "tesseract.exe"), "--version"],
                capture_output=True, text=True
            )
            print(r.stdout.strip())
        except Exception:
            pass

        chi = os.path.join(TESSDATA_DIR, "chi_sim.traineddata")
        eng = os.path.join(TESSDATA_DIR, "eng.traineddata")
        if os.path.exists(chi) and os.path.exists(eng):
            print("\n✅ Tesseract + 中文/英文语言包 全部就绪！")
            print(f"   引擎路径: {os.path.join(INSTALL_DIR, 'tesseract.exe')}")
            print("   现在可以运行 main.py 了")
        elif os.path.exists(chi):
            print("\n✅ Tesseract + 中文包就绪（英文包缺失但不影响中文识别）")
        else:
            print("\n⚠️  Tesseract 已装，但中文包缺失，请按提示手动下载")
    else:
        print("❌ 安装未成功，请检查上方错误信息")
    print("=" * 60)


if __name__ == "__main__":
    main()
