# -*- coding: utf-8 -*-
"""
测试脚本 - 用之前OCR的实际文本验证Python版标题提取逻辑
运行: python test_engine.py
"""

from title_engine import (
    extract_title_from_ocr_text, extract_stock_account,
    get_final_title, cjk_density, has_document_vocab
)


def test_case(name, ocr_text, expected_title, pdf_meta='', filename='测试'):
    """运行单个测试用例"""
    print(f"\n{'='*60}")
    print(f"测试: {name}")
    print(f"{'='*60}")
    print(f"OCR文本(前200字): {ocr_text[:200]}")

    final_title, debug = get_final_title(ocr_text, pdf_meta, filename)
    for line in debug:
        print(f"  {line}")

    status = "✅ 通过" if final_title == expected_title else f"❌ 失败 (期望: {expected_title}, 实际: {final_title})"
    print(f"\n结果: {final_title}  {status}")
    return final_title == expected_title


def main():
    print("=" * 60)
    print("  识笺 Scannote Python版 - 标题引擎测试")
    print("=" * 60)

    passed = 0
    total = 0

    # 测试1: 证券账户开户办理确认单（横屏，股卡号识别）
    total += 1
    ocr1 = """7结算 or，
74 CE5¢ TEAIPEPEAS rtghiy
流水号 : 2023101001724932一码通证券账户号码 : 190001714302子账户类别 : 沪市 A 股账户子账户号码 : B886100491客户名称 : 茂源量化 〈 海南 ) 私募基金管理合伙企业 (有限合伙 ) 一茂源韶光量化对冲1号私募证券投资基金客户类型 : 产品客户国籍或地区 : 中国主要身份证明文件类型 : 营业执照主要各从 ER BRii: 91440300087037980F
FTESOHEN SAEALE F: 3000-12-31 (人 "和辅助身份证明文件类型 : 组织机构代码证 Ci"""
    if test_case("证券账户开户办理确认单(股卡号)", ocr1, "沪市B886100491"):
        passed += 1

    # 测试2: 客户流量费确认表
    total += 1
    ocr2 = """国泰海通证券股份有限公司重庆分公司营业部 : 重庆中山三路客户流量费确认表
[rmeera
CC
wrn  wn an
回沪 A 回股票
[了
We eg 口沪 A 口 ETF 口 LOF JE—"""
    if test_case("客户流量费确认表", ocr2, "客户流量费确认表"):
        passed += 1

    # 测试3: 伪汉字乱码（应走文件名兜底）
    total += 1
    ocr3 = """三2站国生汪汪8
= "
将互革 SDDS =
°g 人 SN 开
 E 人类本 ReE
只长3由
§# ee si/ 员
S = 8 NS
& 区员 w B"""
    if test_case("伪汉字乱码(走文件名兜底)", ocr3, "测试文件", filename="测试文件"):
        passed += 1

    # 测试4: 简单申请表
    total += 1
    ocr4 = """银行账户开户申请书
申请人：张三
账号：6228123456789012"""
    if test_case("银行账户开户申请书", ocr4, "银行账户开户申请书"):
        passed += 1

    # 测试5: 跨行标题
    total += 1
    ocr5 = """关于修改托管协议的
通知函
各相关单位："""
    if test_case("跨行标题(关于...的通知函)", ocr5, "关于修改托管协议的通知函"):
        passed += 1

    print(f"\n{'='*60}")
    print(f"  测试结果: {passed}/{total} 通过")
    print(f"{'='*60}")
    return passed == total


if __name__ == '__main__':
    main()
