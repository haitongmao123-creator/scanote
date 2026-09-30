# -*- coding: utf-8 -*-
"""
OCR 模块 - PDF 转图片 + Tesseract OCR + 方向自动检测
完整移植 index.html 的方向检测与旋转重试逻辑
"""

import os
import io
import re
import sys
import tempfile
from PIL import Image
import pytesseract

import config
from title_engine import (
    has_document_vocab, cjk_density, extract_title_from_ocr_text,
    extract_stock_account, get_final_title, universal_clean_title
)

# 设置 Tesseract 路径
pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH


def _score_ocr_text(text):
    """评估OCR文本质量得分：中文汉字数 + 命中文档词组加权"""
    if not text:
        return 0
    cjk_count = len(re.findall(r'[\u4e00-\u9fa5]', text))
    score = cjk_count
    if has_document_vocab(text):
        score += 80
    return score


def pdf_to_images(pdf_path, dpi=200):
    """把PDF每页转成PIL图片列表"""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise RuntimeError("缺少 PyMuPDF 库，请运行: pip install PyMuPDF")

    images = []
    doc = fitz.open(pdf_path)
    for page in doc:
        # scale=2.0 对应 dpi≈200（与 index.html 一致）
        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        images.append(img.convert('RGB'))
    doc.close()
    return images


def ocr_image(img, lang=None):
    """对单张图片做OCR，返回识别文本"""
    if lang is None:
        lang = config.TESSERACT_LANG
    try:
        text = pytesseract.image_to_string(img, lang=lang)
        return text or ''
    except Exception as e:
        print(f"  ⚠️ OCR出错: {e}")
        return ''


def rotate_image(img, angle):
    """旋转图片（90/180/270度），逆时针"""
    if angle == 0:
        return img
    # PIL rotate 是逆时针；index.html 用 canvas.rotate 也是逆时针
    # 270°优先 = 逆时针270°（即顺时针90°）= "上部在左边"的横屏文档
    return img.rotate(angle, expand=True)


def crop_top_percent(img, percent):
    """裁剪图片顶部 percent% 区域"""
    w, h = img.size
    crop_h = int(h * percent)
    return img.crop((0, 0, w, crop_h))


def crop_bottom_percent(img, percent):
    """裁剪图片底部 percent% 区域"""
    w, h = img.size
    crop_h = int(h * percent)
    return img.crop((0, h - crop_h, w, h))


def detect_direction_and_ocr(img):
    """方向检测 + OCR（移植 index.html 逻辑）
    返回: (最佳OCR文本, 调试信息列表)
    """
    debug = []

    # 1. 0° OCR（裁剪顶部50%快速判断）
    top50 = crop_top_percent(img, 0.5)
    text_0 = ocr_image(top50)
    score_0 = _score_ocr_text(text_0)
    vocab_0 = has_document_vocab(text_0)
    debug.append(f"📝 OCR结果(0° 顶50%) [得分{score_0}, 词组{'✓' if vocab_0 else '✗'}]")
    debug.append(f"   {text_0[:120]}")

    # 2. 判断0°是否为伪汉字乱码（得分够但无文档词组 → 强制旋转重试）
    if score_0 >= 8 and not vocab_0:
        debug.append("🔄 0°结果疑似伪汉字乱码: 得分≥8但不含文档词组，强制触发旋转重试")
        need_rotate = True
    elif score_0 >= 16 and vocab_0:
        # 0°方向正确且含文档词组 → 直接用
        debug.append(f"⚡ 命中正确方向 0°得分{score_0}≥16且含文档词组，提前结束")
        full_text = ocr_image(img)
        debug.append(f"📝 完整页面OCR(0°) ...")
        return full_text, debug
    else:
        need_rotate = True

    if not need_rotate:
        full_text = ocr_image(img)
        return full_text, debug

    # 3. 旋转重试：270°优先 → 90° → 180°，每个方向裁剪顶部50%
    best_text = text_0
    best_score = score_0
    best_angle = 0
    best_has_vocab = vocab_0

    # 270°优先（"上部在左边"的常见横屏方向）
    for angle in [270, 90, 180]:
        rotated = rotate_image(img, angle)
        top50 = crop_top_percent(rotated, 0.5)
        text = ocr_image(top50)
        score = _score_ocr_text(text)
        has_vocab = has_document_vocab(text)
        debug.append(f"🔄 OCR结果({angle}° 顶50%) [得分{score}, 词组{'✓' if has_vocab else '✗'}]")
        debug.append(f"   {text[:120]}")

        # 命中正确方向（得分≥16且含文档词组）→ 提前结束
        if score >= 16 and has_vocab:
            debug.append(f"⚡ 命中正确方向 {angle}°得分{score}≥16且含文档词组，提前结束方向检测")
            # 对该方向做完整页面OCR
            full_text = ocr_image(rotated)
            debug.append(f"📝 完整页面OCR({angle}°) [{len(full_text)}字]")
            return full_text, debug

        # 记录最佳方向（含词组优先于纯分数）
        if has_vocab and not best_has_vocab:
            best_text = text
            best_score = score
            best_angle = angle
            best_has_vocab = True
        elif has_vocab == best_has_vocab and score > best_score:
            best_text = text
            best_score = score
            best_angle = angle

    debug.append(f"✅ 方向检测完成: 最佳方向{best_angle}°, 得分{best_score}, 词组{'✓' if best_has_vocab else '✗'}")

    # 若最佳方向含词组 → 对该方向做完整页面OCR
    if best_has_vocab and best_angle != 0:
        rotated = rotate_image(img, best_angle)
        full_text = ocr_image(rotated)
        debug.append(f"📝 完整页面OCR({best_angle}°) [{len(full_text)}字]")
        return full_text, debug
    elif best_angle == 0:
        # 0°就是最佳 → 完整页面OCR
        full_text = ocr_image(img)
        debug.append(f"📝 完整页面OCR(0°) [{len(full_text)}字]")
        return full_text, debug
    else:
        # 所有方向都不含文档词组 → 放弃OCR结果
        debug.append("⚠️ OCR全方向均无文档词组，放弃OCR结果，走元数据/文件名兜底")
        return '', debug


def process_pdf(pdf_path, original_filename):
    """处理一个PDF文件：OCR + 方向检测 + 标题提取
    返回: (新文件名, 调试信息列表)
    """
    debug = []
    filename_without_ext = os.path.splitext(original_filename)[0]
    # 去掉常见的"扫描件_"前缀
    if filename_without_ext.startswith('扫描件_'):
        filename_without_ext = filename_without_ext[4:]

    # 1. PDF转图片
    try:
        images = pdf_to_images(pdf_path)
    except Exception as e:
        debug.append(f"❌ PDF转图片失败: {e}")
        return original_filename, debug

    if not images:
        debug.append("❌ PDF无页面")
        return original_filename, debug

    # 只处理第一页（与 index.html 一致）
    first_page = images[0]
    debug.append(f"📄 PDF第一页尺寸: {first_page.size}")

    # 2. 方向检测 + OCR
    ocr_text, ocr_debug = detect_direction_and_ocr(first_page)
    debug.extend(ocr_debug)

    if ocr_text:
        debug.append(f"📝 OCR结果(清理后):\n{ocr_text[:500]}")

    # 3. 提取PDF元数据标题（兜底用）
    pdf_metadata_title = ''
    try:
        import fitz
        doc = fitz.open(pdf_path)
        meta = doc.metadata
        if meta and meta.get('title'):
            pdf_metadata_title = meta['title']
        doc.close()
    except Exception:
        pass

    # 4. 标题提取（股卡号优先 → 关键词 → 元数据 → 文件名）
    final_title, title_debug = get_final_title(
        ocr_text, pdf_metadata_title, filename_without_ext
    )
    debug.extend(title_debug)

    # 5. 组装新文件名
    # 清理文件名中的非法字符
    safe_title = re.sub(r'[\\/:*?"<>|]', '_', final_title)
    new_filename = f"扫描件_{safe_title}.pdf"

    return new_filename, debug
