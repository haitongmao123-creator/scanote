# -*- coding: utf-8 -*-
"""
标题识别引擎 - 从 index.html 完整移植
包含：CJK密度检测、文档词组闸门、关键词匹配、股卡号优先命名、OCR方向旋转重试
版本: v20260904-10 (Python移植版)
"""

import re

# ============ 文档常用词组（用于乱码闸门 + 方向检测）============
DOCUMENT_VOCAB = [
    '申请', '开户', '销户', '变更', '注销', '撤销', '备案', '登记',
    '通知', '公告', '回执', '确认', '证明', '声明', '承诺', '告知',
    '协议', '合同', '契约', '委托', '授权', '存管', '监管', '托管',
    '账户', '账号', '资金', '银行', '期货', '证券', '基金', '产品',
    '对账', '结算', '清算', '流水', '明细', '余额', '持仓', '交易',
    '印鉴', '密码', '证书', '网银', '转账', '划转', '划款', '汇款',
    '业务', '办理', '受理', '审批', '审核', '经办', '复核',
    '风险', '揭示', '提示', '合规', '法律', '审计', '评估', '调查',
    '到账', '入金', '出金', '续约', '解约', '冻结', '解冻', '激活'
]

# ============ 关键词词库（与 index.html TITLE_KEYWORDS 完全同步）============
TITLE_KEYWORDS = [
    # 账户开立/变更/销户类
    '银行账户开户申请书', '银行账户变更申请书', '银行账户销户申请书', '银行账户销户申请',
    '基本存款账户开户许可证', '一般存款账户开户许可证', '专用账户开户许可证', '开户许可证',
    '期货账户开户申请表', '期货账户变更申请表', '期货账户销户申请表', '期货账户销户申请书',
    '期货资金账户开户', '期货资金账户变更', '期货资金账户销户', '期货资金账号开户',
    '证券账户开户申请表', '证券账户变更申请表', '证券账户注销申请表', '证券账户注册申请',
    '证券账户变更注册', '中登账户开户', '中登账户变更', '证券账户开户',
    '基金账户开户申请', '基金账户销户申请', '基金账户变更申请', '基金账户开户',
    '托管账户开户申请', '托管账户销户申请', '托管资金账户开户', '托管资金账户销户',
    '资金账户开户申请', '资金账户销户申请', '资金账户变更申请', '资金账户开户',
    '交易账户开户申请', '交易账户销户申请', '交易账户变更申请', '交易账户开户',
    '企业网银开户申请', '企业网银变更申请', '企业网银注销申请', '网银开户申请', '网银变更申请',
    # 转账/存管协议类
    '第三方存管协议', '三方存管协议', '三方存管申请', '三方存管确认',
    '银证转账协议', '银期转账协议', '银衍转账协议', '银行存管协议',
    '资金存管协议', '资金监管协议', '存管协议', '监管协议',
    '银期转账开户申请', '银证转账开户申请', '银衍转账开户申请',
    '银期转账变更申请', '银证转账变更申请',
    # 资金划转/出入金类
    '资金划转申请书', '资金划拨申请书', '资金调拨申请书', '资金划转申请',
    '资金划转指令', '资金划拨指令', '划款指令', '划款申请书',
    '出金申请书', '入金申请书', '出入金申请', '出金申请', '入金申请',
    '银行汇款申请书', '电汇申请书', '转账申请书', '汇款申请书',
    '资金转出申请', '资金转入申请', '资金转出申请书', '资金转入申请书',
    '出金指令', '入金指令', '提款申请', '存款申请',
    # 对账/报表类
    '银行账户对账单', '银行对账单', '银行流水', '银行账户流水',
    '期货资金对账单', '期货交易结算单', '期货对账单', '期货结算单',
    '证券资金对账单', '证券交易对账单', '证券对账单',
    '资金余额对账单', '资金余额确认单', '资金对账单',
    '持仓对账单', '持仓明细表', '持仓余额表',
    '账户余额确认单', '账户余额确认', '账户余额表', '账户余额证明',
    '交易明细表', '交易流水表', '资金流水表', '资金明细表', '资金余额表',
    '资金日报', '资金月报', '账户日报', '账户月报', '账户年报',
    '结算单', '结算报表', '清算单', '对账确认单', '对账回执', '对账函', '对账单',
    # 回执/确认类
    '开户受理回执', '开户回执', '销户回执', '变更回执', '业务回执', '受理回执', '办理回执',
    '开户确认书', '销户确认书', '变更确认书',
    '开户确认函', '销户确认函', '变更确认函',
    '客户流量费确认表', '流量费确认表', '费用确认表', '佣金确认表', '确认表',
    '资金到账确认书', '资金到账确认', '资金到账回执', '资金到账通知',
    '划款回执', '汇款回执', '转账回执',
    '交易确认书', '交易确认单', '成交确认书', '成交确认单',
    # 授权/印鉴/证书类
    '法人授权委托书', '经办人授权委托书', '授权委托书',
    '印鉴变更申请书', '印鉴备案', '预留印鉴', '印鉴卡',
    '密码重置申请', '密码解锁申请', '密码变更申请',
    '数字证书申请', '数字证书协议', '证书变更申请', '证书吊销申请', '电子签名协议',
    '网银盾申请', 'Ukey申请', 'U盾申请',
    # 证明/资质类
    '基本存款账户开户许可证', '私募基金管理人登记证明', '经营证券期货业务许可证',
    '产品备案证明', '基金业协会备案', '私募基金备案证明',
    '法人身份证明', '经办人身份证明', '授权人身份证明',
    '开户证明', '销户证明', '账户证明', '资金证明', '余额证明', '存款证明', '资金余额证明',
    # 通知/函件类
    '账户冻结通知', '账户解冻通知', '账户休眠通知', '账户激活通知', '账户异常通知',
    '账户变更通知', '开户通知', '销户通知',
    '资金到账通知', '资金划转通知', '划款通知',
    '到期通知', '续约通知', '解约通知',
    '银行通知函', '期货公司通知函', '券商通知函',
    # 申请表通用类
    '变更申请书', '注销申请书', '撤销申请书',
    '账户信息变更表', '信息变更申请', '资料变更申请',
    '业务申请表', '业务办理表', '受理表', '备案登记表', '备案表',
    # 通用短词（放最后，作为兜底匹配）
    '回执', '流水', '存管', '汇款', '调拨', '划转', '转账协议',

    '承诺书和风险提示书', '承诺书和风险揭示书',
    '接入外部信息系统承诺书和风险提示书', '接入外部信息系统承诺书和风险揭示书',
    '信息系统外部接入承诺函及风险揭示书', '信息系统外部接入承诺函及风险提示书',
    '承诺函及风险揭示书', '承诺函及风险提示书', '承诺函和风险揭示书', '承诺函和风险提示书',
    '证券账户业务申请表', '基金账户业务申请表', '交易业务申请表', '账户业务申请表',
    '开放式基金账户业务申请表', '开放式基金交易业务申请表',
    '私募投资基金备案证明', '备案证明', '私募投资基金备案函', '备案函', '基金备案函',
    '银行账户信息确认函', '托管信息确认函', '账户信息确认函', '信息确认函', '业务确认函', '交易确认函', '确认函',
    '业务确认书', '交易确认书',
    '开户合同', '开户协议', '开户申请书', '交易申请书', '交易协议',
    '托管协议', '托管合同', '顾问协议', '顾问合同', '合伙协议',
    '委托协议', '委托合同', '服务协议', '服务合同',
    '授权委托书', '委托书',
    '申请表', '申请单', '登记表', '审批表', '审核表', '报名表', '调查表', '汇总表', '问卷',
    '持有人名册', '持有人份额明细表', '份额明细', '持有人份额',
    '托管账户信息确认函', '托管账户开户通知单', '托管资金专门账户信息确认函',
    '托管资产专用银行账户变更确认书',
    '账户开立回执', '期货开户回执单', '期货开户回执',
    '证券账户开户办理确认单', '证券账户开户确认单', '开户办理确认单', '账户开户办理确认单', '证券开户办理确认单',
    '基金产品合同', '产品合同', '基金合同', '产品协议', '信托合同', '资管合同',
    '协议', '合同', '契约', '协议书',
    '承诺书', '确认书', '告知书', '通知书', '声明书', '说明书',
    '提示书', '揭示书', '风险揭示书', '风险提示书', '合规意见书', '法律意见书',
    '尽职调查报告', '财务报告', '审计报告', '财务审计报告', '评估报告', '咨询报告', '情况报告',
    '情况说明', '工作说明', '补充说明', '澄清说明', '使用说明', '操作说明',
    '系统说明', '产品说明', '业务说明', '交易说明', '结算说明', '资金说明',
    '清算说明', '整改说明', '说明报告', '说明函', '说明',
    '处罚通知', '处理通知', '变更通知', '调整通知', '到期通知', '续约通知',
    '预警通知', '终止通知', '解除通知', '催收通知', '缴款通知',
    '公函', '律师函', '通知函', '催收函', '邀请函', '催告函', '回复函',
    '答复函', '复函', '工作函', '联系函', '商洽函', '询问函',
    '告知函', '提示函', '警示函', '监管函', '函件', '函',
    '任命书', '离职证明', '解约函',
    '收入证明', '在职证明', '资格证明', '身份证明', '资质证明', '证明',
    '保密承诺书', '合规承诺书', '交易承诺书', '风险承诺书',
    '投资协议书', '服务协议书', '合作协议书', '托管协议书',
    '情况反映', '情况汇报', '情况通报',
    '意向书', '谅解备忘录', '合作备忘录', '备忘录', '要约',
    '决议', '纪要', '公告', '通报', '通知', '报告'
]

# 去重并按长度降序排列（长关键词优先匹配）
TITLE_KEYWORDS = sorted(list(set(TITLE_KEYWORDS)), key=lambda x: len(x), reverse=True)


def has_document_vocab(text):
    """检测文本是否包含任意文档常用词组"""
    if not text:
        return False
    return any(v in text for v in DOCUMENT_VOCAB)


def cjk_density(text):
    """计算CJK密度 = 中文字符数 / 非空白字符数"""
    if not text:
        return 0.0
    cjk = len(re.findall(r'[\u4e00-\u9fa5]', text))
    total_non_space = len(re.sub(r'\s', '', text))
    return cjk / total_non_space if total_non_space > 0 else 0.0


def is_financial_compound_prefix(p):
    """金融复合标题前缀识别"""
    if not p:
        return False
    cleaned = re.sub(r'^附\d+[\.、\s]*', '', p)
    cleaned = re.sub(r'^\d+[\.、\s]*', '', cleaned).strip()
    if len(cleaned) < 4 or len(cleaned) > 30:
        return False
    cn = len(re.findall(r'[\u4e00-\u9fa5]', cleaned))
    if len(cleaned) == 0 or cn / len(cleaned) < 0.6:
        return False
    return bool(re.search(r'(托管|资产|资金|银行|账户|变更|开户|销户|专用|专门|结算|交收|清算|份额|持有人|登记|备案|对账|核对|转换|转让|过户|注销|撤销|募集|赎回|申购|认购|估值|净值)', cleaned))


def strip_line(line):
    """剥离前缀（版本号、编号、备案编码等）"""
    label_patterns = [
        '营业执照号码', '统一社会信用代码', '社会信用代码',
        '合同编号', '协议编号', '备案编码', '备案编号',
        '版本号', '机构代码', '身份证号', '证件号',
        '文号', '编号'
    ]
    for label in label_patterns:
        line = re.sub(r'^' + label + r'[:：\s]*[A-Za-z0-9\-]{0,30}[，,\.。\s]*', '', line)
    line = re.sub(r'^备案[编纺妨纷][码玛马][:：\s]*[A-Za-z0-9\-]{0,30}[，,\.。\s]*', '', line)
    line = re.sub(r'^\d+[\.、\)\]\s]+', '', line)
    line = re.sub(r'^附\d+[\.、\s]*', '', line)
    line = re.sub(r'^[\(（]\d+[\)）]\s*', '', line)
    line = re.sub(r'^[\s\u3000]+', '', line)
    return line.strip()


def clean_title(title):
    """清理提取的标题：去英文、去纯数字、去公司名、去标点"""
    title = re.sub(r'[A-Za-z]+', '', title)
    title = re.sub(r'[A-Fa-f0-9]{6,}', '', title)
    title = re.sub(r'[\u4e00-\u9fa5]{1,8}(?:有限|股份|合伙|集团)?(?:公司|企业)$', '', title)
    title = re.sub(r'[：:]\s*$', '', title)
    title = re.sub(r'\s+', '', title)
    return title.strip()


def is_valid_title(title):
    """验证标题：必须有足够中文字符"""
    chinese_count = len(re.findall(r'[\u4e00-\u9fa5]', title))
    total_count = len(title)
    if total_count < 2:
        return False
    if chinese_count < 2:
        return False
    if total_count > 0 and chinese_count / total_count < 0.5:
        return False
    return True


def is_meaningful_prefix(p):
    """判断前缀是否有意义"""
    if not p:
        return False
    if re.search(r'(代码|编号|编码|号码|证号|信用代码|日期|申请日期|签发日期|版本号|文号|机构代码|营业执照|社会信用)', p):
        return False
    if re.search(r'[:：]', p):
        return False
    if re.search(r'(私募|证券投资基金|集合资金信托|信托计划|资产管理计划|资管计划|私募基金|投资基金)', p) and 4 <= len(p) <= 40:
        return True
    if is_financial_compound_prefix(p):
        return True
    if 2 <= len(p) <= 10:
        cn = len(re.findall(r'[\u4e00-\u9fa5]', p))
        if cn == len(p):
            return True
    has_year_doc_no = bool(re.search(r'\d{4}年', p)) or bool(re.search(r'\d{4}年度$', p)) or bool(re.search(r'第[一二三四五六七八九十百千0-9]+号', p))
    if len(p) > 15:
        return has_year_doc_no and bool(re.match(r'^关于', p)) and bool(re.search(r'的$', p))
    if re.match(r'^关于', p) and re.search(r'的$', p):
        return True
    return has_year_doc_no


def extract_title_from_ocr_text(text, input_cjk_density=None):
    """从OCR文本中提取标题（完整移植 index.html 逻辑）"""
    if not text or not text.strip():
        return ''

    keywords = TITLE_KEYWORDS
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    search_range = min(len(lines), 15)

    cjk_count = len(re.findall(r'[\u4e00-\u9fa5]', text))
    non_space_count = len(re.sub(r'\s', '', text))
    cjk_density_val = input_cjk_density if isinstance(input_cjk_density, (int, float)) else (cjk_count / non_space_count if non_space_count > 0 else 0)

    if cjk_density_val < 0.15:
        return ''

    # === 1. 跨行合并匹配（长关键词>=6字，优先）===
    for i in range(search_range - 1):
        line_a = strip_line(lines[i])
        line_b = strip_line(lines[i + 1])
        combined = line_a + line_b
        if len(combined) < 4 or len(combined) > 120:
            continue
        for kw in keywords:
            if len(kw) < 6:
                continue
            if kw in combined:
                kw_idx = combined.index(kw)
                before_kw = combined[:kw_idx]
                if is_meaningful_prefix(before_kw) or len(before_kw) == 0:
                    title = combined[:kw_idx + len(kw)]
                else:
                    title = kw
                if len(before_kw) == 0 and kw_idx + len(kw) < len(line_a):
                    after_in_a = line_a[kw_idx + len(kw):]
                    tail_match = re.match(r'^([\u4e00-\u9fa5]{1,20})', after_in_a)
                    if tail_match:
                        title += tail_match.group(1)
                title = clean_title(title)
                if is_valid_title(title):
                    return title

    # === 1.5 跨行短关键词 + 有意义前缀（<=5字）===
    for i in range(search_range - 1):
        line_a = strip_line(lines[i])
        line_b = strip_line(lines[i + 1])
        combined = line_a + line_b
        if len(combined) < 6 or len(combined) > 120:
            continue
        for kw in keywords:
            if len(kw) > 5 or len(kw) < 2:
                continue
            if kw in combined:
                kw_idx = combined.index(kw)
                before_kw = combined[:kw_idx]
                if not (is_meaningful_prefix(before_kw) or len(before_kw) == 0):
                    continue
                title = combined[:kw_idx + len(kw)]
                if len(before_kw) == 0 and kw_idx + len(kw) < len(line_a):
                    after_in_a = line_a[kw_idx + len(kw):]
                    tail_match = re.match(r'^([\u4e00-\u9fa5]{1,20})', after_in_a)
                    if tail_match:
                        title += tail_match.group(1)
                title = clean_title(title)
                if is_valid_title(title):
                    return title

    # === 2. 单行匹配 ===
    for i in range(search_range):
        stripped = strip_line(lines[i])
        if len(stripped) < 2 or len(stripped) > 80:
            continue
        for kw in keywords:
            if len(kw) <= 2 and i >= 5:
                continue
            if kw in stripped:
                kw_idx = stripped.index(kw)
                before_kw = stripped[:kw_idx]
                if is_meaningful_prefix(before_kw) or len(before_kw) == 0:
                    title = stripped[:kw_idx + len(kw)]
                else:
                    title = kw
                if len(before_kw) == 0 and kw_idx + len(kw) < len(stripped):
                    after = stripped[kw_idx + len(kw):]
                    tail_match = re.match(r'^([\u4e00-\u9fa5]{1,25})', after)
                    if tail_match:
                        title += tail_match.group(1)
                title = clean_title(title)
                if is_valid_title(title):
                    return title

    # === 2.5 单行匹配：有意义前缀 ===
    for i in range(search_range):
        stripped = strip_line(lines[i])
        if len(stripped) < 6 or len(stripped) > 80:
            continue
        for kw in keywords:
            if len(kw) > 5 or len(kw) < 2:
                continue
            if len(kw) <= 2 and i >= 5:
                continue
            if kw in stripped:
                kw_idx = stripped.index(kw)
                before_kw = stripped[:kw_idx]
                if not (is_meaningful_prefix(before_kw) or len(before_kw) == 0):
                    continue
                title = stripped[:kw_idx + len(kw)]
                if len(before_kw) == 0 and kw_idx + len(kw) < len(stripped):
                    tail_match = re.match(r'^([\u4e00-\u9fa5]{1,25})', stripped[kw_idx + len(kw):])
                    if tail_match:
                        title += tail_match.group(1)
                title = clean_title(title)
                if is_valid_title(title):
                    return title

    # === 2.9 文档词组闸门 ===
    if not has_document_vocab(text):
        return ''

    # === 3. 回退：评分选标题 ===
    best_line = ''
    best_score = -1
    for i in range(search_range):
        stripped = strip_line(lines[i])
        if len(stripped) < 2:
            continue
        if re.match(r'^[一二三四五六七八九十百千]+[、\.]', stripped):
            continue
        if re.match(r'^[\(（]?(?:是|否|√|×)[\)）]?', stripped):
            continue
        has_doc_suffix = bool(re.search(r'[书表告函知议明同托诺证约章定卡案令]', stripped))
        if not has_doc_suffix and re.search(r'(办理|业务|签约|撤销|账户|资金|客户|证券|期货|基金|代理|本人|机构|身份证)', stripped) and len(stripped) > 20:
            continue
        if re.search(r'[。，；、,;：:]', stripped) and len(stripped) > 30 and not has_doc_suffix:
            continue
        if len(stripped) > 60:
            continue
        if not has_doc_suffix and re.match(r'^(根据|依据|按照|为了|为进一步|鉴于|经研究|现通知|现公告|现函|尊敬的|各部门|各营业部|客户|股东|全体|地址|电话|传真|邮编|邮箱|联系人|基金类型|基金名称|管理人|托管人|法定代表人|执行事务合伙人)', stripped):
            continue

        cleaned = clean_title(stripped)
        if not is_valid_title(cleaned):
            continue
        if len(cleaned) == 2 and not re.search(r'[书表告函知议明同托诺证约章定卡案令]$', cleaned):
            continue

        score = 0
        if 4 <= len(cleaned) <= 50:
            score += 50
        if 10 <= len(cleaned) <= 40:
            score += 20
        if not re.search(r'[。，；、,;]', stripped):
            score += 20
        if re.search(r'[书|表|告|函|知|议|明|同|托|诺|证|约|定]', cleaned):
            score += 30
        if has_document_vocab(cleaned):
            score += 40
        elif not has_doc_suffix:
            score -= 30
        score += max(0, 10 - i)

        if score > best_score:
            best_score = score
            best_line = cleaned

    if best_line:
        return best_line

    # === 4. 最终回退 ===
    for line in lines:
        cleaned = clean_title(line)
        if len(cleaned) == 2 and not re.search(r'[书表告函知议明同托诺证约章定卡案令]$', cleaned):
            continue
        if is_valid_title(cleaned) and 2 < len(cleaned) < 80:
            return cleaned
    return ''


def extract_stock_account(text):
    """从OCR文本中提取证券账户股卡号
    返回 dict: {'market': '沪市'/'深市'/'', 'account': 'B886100491'} 或空对象
    """
    if not text:
        return {'market': '', 'account': ''}

    # 策略一：完整标签匹配
    label_patterns = [
        (re.compile(r'沪\s*市\s*[^\d]{0,30}?[账号号码户]\s*[:：]?\s*[，,\.。\s]*([A-Za-z0-9]{6,14})'), '沪市'),
        (re.compile(r'深\s*市\s*[^\d]{0,30}?[账号号码户]\s*[:：]?\s*[，,\.。\s]*([A-Za-z0-9]{6,14})'), '深市'),
    ]
    for pat, market in label_patterns:
        m = pat.search(text)
        if m and m.group(1):
            return {'market': market, 'account': m.group(1)}

    # 策略二：格式特征匹配（OCR中文标签全错也能按账号数字特征抓到）
    fmt_patterns = [
        (re.compile(r'(?:^|[^A-Za-z0-9])(B\d{9})(?:$|[^A-Za-z0-9])'), '沪市' if re.search(r'沪\s*市', text) else ''),
        (re.compile(r'(?:^|[^0-9])(0\d{9})(?:$|[^0-9])'), '深市' if re.search(r'深\s*市', text) else ''),
    ]
    for pat, market in fmt_patterns:
        m = pat.search(text)
        if m and m.group(1) and market:
            return {'market': market, 'account': m.group(1)}

    return {'market': '', 'account': ''}


def extract_filing_code(text):
    """提取备案编码（6位字母+数字，如SVD248）"""
    if not text:
        return ''
    exact_patterns = [
        re.compile(r'备案编码[:：]?\s*[，,\.。\s]*([A-Za-z0-9]{6})'),
        re.compile(r'备案编号[:：]?\s*[，,\.。\s]*([A-Za-z0-9]{6})'),
        re.compile(r'备案代码[:：]?\s*[，,\.。\s]*([A-Za-z0-9]{6})'),
    ]
    for p in exact_patterns:
        m = p.search(text)
        if m and m.group(1):
            return m.group(1).upper()
    label_pattern = re.compile(r'备案[编纺妨纷][码玛马]')
    m = label_pattern.search(text)
    if m:
        after = text[m.end():]
        cm = re.search(r'[，,\.。\s]*([A-Za-z0-9]{6})', after)
        if cm and cm.group(1):
            return cm.group(1).upper()
    return ''


def extract_futures_account(text):
    """提取期货资金账号（纯数字6-12位）"""
    if not text:
        return ''
    patterns = [
        re.compile(r'期货资金账[号码][:：]?\s*[，,\.。\s]*(\d{6,12})'),
        re.compile(r'期货资金帐[号码][:：]?\s*[，,\.。\s]*(\d{6,12})'),
        re.compile(r'期货账[号码][:：]?\s*[，,\.。\s]*(\d{6,12})'),
        re.compile(r'期货帐[号码][:：]?\s*[，,\.。\s]*(\d{6,12})'),
        re.compile(r'资金账[号码][:：]?\s*[，,\.。\s]*(\d{6,12})'),
        re.compile(r'资金帐[号码][:：]?\s*[，,\.。\s]*(\d{6,12})'),
    ]
    for p in patterns:
        m = p.search(text)
        if m and m.group(1):
            return m.group(1)
    return ''


def universal_clean_title(t, custom_keywords=None):
    """统一清理标题（去前缀、去英文、按关键词截断正文尾）"""
    if not t:
        return ''
    labels = [
        '统一社会信用代码', '社会信用代码', '营业执照号码',
        '备案编码', '备案编号', '合同编号', '协议编号',
        '身份证号', '证件号', '账户号码', '客户编号',
        '申请日期', '签发日期', '机构代码', '营业执照',
        '版本号', '文号', '日期', '编号'
    ]
    for label in labels:
        t = re.sub(r'^' + label + r'[:：\s]*[A-Za-z0-9\-]{0,30}[，,\.。\s]*', '', t)
    t = re.sub(r'^备案[编纺妨纷][码玛马][:：\s]*[A-Za-z0-9\-]{0,30}[，,\.。\s]*', '', t)
    t = re.sub(r'[A-Za-z]', '', t)
    t = re.sub(r'[0-9]{6,}', '', t)
    t = re.sub(r'\s+', ' ', t).strip()

    cut_keywords = list(TITLE_KEYWORDS)
    if custom_keywords:
        cut_keywords = cut_keywords + list(custom_keywords)
    cut_keywords = sorted(list(set(cut_keywords)), key=lambda x: len(x), reverse=True)
    for kw in cut_keywords:
        idx = t.find(kw)
        if idx >= 0:
            prefix_up_to_kw = t[:idx]
            has_product_name = (4 <= len(prefix_up_to_kw) <= 40 and
                               re.search(r'(私募|证券投资基金|集合资金信托|信托计划|资产管理计划|资管计划|私募基金|投资基金)', prefix_up_to_kw))
            has_financial_prefix = is_financial_compound_prefix(prefix_up_to_kw)
            meaningful_before = has_product_name or has_financial_prefix or (
                (re.match(r'^关于.+的$', prefix_up_to_kw) or
                 re.search(r'第[一二三四五六七八九十百千0-9]+号', prefix_up_to_kw) or
                 re.search(r'\d{4}年', prefix_up_to_kw) or
                 re.search(r'\d{4}年度$', prefix_up_to_kw)) and
                len(prefix_up_to_kw) < 40)
            if meaningful_before:
                t = t[:idx + len(kw)]
            else:
                t = t[idx:idx + len(kw)]
            break
    t = re.sub(r'[及和与或]\s*[\u4e00-\u9fa5]{1,2}$', '', t)
    return t.strip()


def get_final_title(ocr_text, pdf_metadata_title='', filename_without_ext='', custom_keywords=None):
    """完整的标题提取流程：股卡号优先 → OCR关键词 → 元数据 → 文件名兜底
    返回: (最终标题, 调试信息列表)
    """
    debug_info = []
    extracted_title = ''

    # 股卡号优先命名
    if ocr_text:
        stock_lines = [l.strip() for l in re.split(r'\n|[\r\u2028\u2029]', ocr_text) if l and l.strip()]
        stock_acct = {'market': '', 'account': ''}
        for ln in stock_lines:
            r = extract_stock_account(ln)
            if r['market'] and r['account']:
                stock_acct = r
                break
        if not stock_acct['market']:
            stock_acct = extract_stock_account(ocr_text)

        if stock_acct['market'] and stock_acct['account']:
            extracted_title = stock_acct['market'] + stock_acct['account']
            debug_info.append(f"💳 股卡号优先命名: {stock_acct['market']} {stock_acct['account']}")
        else:
            debug_info.append(f"💳 股卡号扫描: 未识别到（逐行{len(stock_lines)}行+全文均未匹配）")
            density = cjk_density(ocr_text)
            title_from_ocr = extract_title_from_ocr_text(ocr_text, density)
            if title_from_ocr:
                extracted_title = title_from_ocr
                debug_info.append(f"🏷️ 关键词提取标题: {extracted_title}")
            else:
                debug_info.append("🏷️ 关键词提取标题: 未匹配到关键词")

    # 元数据兜底
    if not extracted_title and pdf_metadata_title:
        mt = pdf_metadata_title.strip()
        if 2 < len(mt) < 60:
            extracted_title = mt
            debug_info.append(f"✅ 元数据兜底标题: {extracted_title}")

    # 最终兜底：文件名
    final_title = extracted_title or filename_without_ext
    if extracted_title and not (extracted_title and extracted_title[0] in '沪深' and len(extracted_title) <= 15):
        # 股卡号命名（沪市B886100491）跳过 universalCleanTitle，避免字母被清掉
        final_title = universal_clean_title(extracted_title, custom_keywords)

    debug_info.append(f"🏷️ 最终标题: {final_title}")
    return final_title, debug_info
