// 模拟 index.html 中的核心函数用于本地测试（与 index.html 同步）

function extractTitleFromOCRText(text, inputCjkDensity) {
  if (!text || text.trim().length === 0) return { title: '', source: '空' };

  const cjkCount = (text.match(/[\u4e00-\u9fa5]/g) || []).length;
  const nonSpaceCount = text.replace(/\s/g, '').length;
  const cjkDensityVal = typeof inputCjkDensity === 'number' ? inputCjkDensity : (nonSpaceCount > 0 ? cjkCount / nonSpaceCount : 0);
  if (cjkDensityVal < 0.15) return { title: '', source: '乱码(CJK密度过低)' };

  const rawKeywords = [
    // === 量化私募基金账户运营岗位专用词库（与 index.html TITLE_KEYWORDS 同步）===
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
    '第三方存管协议', '三方存管协议', '三方存管申请', '三方存管确认',
    '银证转账协议', '银期转账协议', '银衍转账协议', '银行存管协议',
    '资金存管协议', '资金监管协议', '存管协议', '监管协议',
    '银期转账开户申请', '银证转账开户申请', '银衍转账开户申请',
    '银期转账变更申请', '银证转账变更申请',
    '资金划转申请书', '资金划拨申请书', '资金调拨申请书', '资金划转申请',
    '资金划转指令', '资金划拨指令', '划款指令', '划款申请书',
    '出金申请书', '入金申请书', '出入金申请', '出金申请', '入金申请',
    '银行汇款申请书', '电汇申请书', '转账申请书', '汇款申请书',
    '资金转出申请', '资金转入申请', '资金转出申请书', '资金转入申请书',
    '出金指令', '入金指令', '提款申请', '存款申请',
    '银行账户对账单', '银行对账单', '银行流水', '银行账户流水',
    '期货资金对账单', '期货交易结算单', '期货对账单', '期货结算单',
    '证券资金对账单', '证券交易对账单', '证券对账单',
    '资金余额对账单', '资金余额确认单', '资金对账单',
    '持仓对账单', '持仓明细表', '持仓余额表',
    '账户余额确认单', '账户余额确认', '账户余额表', '账户余额证明',
    '交易明细表', '交易流水表', '资金流水表', '资金明细表', '资金余额表',
    '资金日报', '资金月报', '账户日报', '账户月报', '账户年报',
    '结算单', '结算报表', '清算单', '对账确认单', '对账回执', '对账函', '对账单',
    '开户受理回执', '开户回执', '销户回执', '变更回执', '业务回执', '受理回执', '办理回执',
    '开户确认书', '销户确认书', '变更确认书',
    '开户确认函', '销户确认函', '变更确认函',
    '资金到账确认书', '资金到账确认', '资金到账回执', '资金到账通知',
    '划款回执', '汇款回执', '转账回执',
    '交易确认书', '交易确认单', '成交确认书', '成交确认单',
    '法人授权委托书', '经办人授权委托书', '授权委托书',
    '印鉴变更申请书', '印鉴备案', '预留印鉴', '印鉴卡',
    '密码重置申请', '密码解锁申请', '密码变更申请',
    '数字证书申请', '数字证书协议', '证书变更申请', '证书吊销申请', '电子签名协议',
    '网银盾申请', 'Ukey申请', 'U盾申请',
    '基本存款账户开户许可证', '私募基金管理人登记证明', '经营证券期货业务许可证',
    '产品备案证明', '基金业协会备案', '私募基金备案证明',
    '法人身份证明', '经办人身份证明', '授权人身份证明',
    '开户证明', '销户证明', '账户证明', '资金证明', '余额证明', '存款证明', '资金余额证明',
    '账户冻结通知', '账户解冻通知', '账户休眠通知', '账户激活通知', '账户异常通知',
    '账户变更通知', '开户通知', '销户通知',
    '资金到账通知', '资金划转通知', '划款通知',
    '到期通知', '续约通知', '解约通知',
    '银行通知函', '期货公司通知函', '券商通知函',
    '变更申请书', '注销申请书', '撤销申请书',
    '账户信息变更表', '信息变更申请', '资料变更申请',
    '业务申请表', '业务办理表', '受理表', '备案登记表', '备案表',
    '回执', '流水', '存管', '汇款', '调拨', '划转', '转账协议',

    '承诺书和风险提示书', '承诺书和风险揭示书',
    '接入外部信息系统承诺书和风险提示书', '接入外部信息系统承诺书和风险揭示书',
    '证券账户业务申请表', '基金账户业务申请表', '账户业务申请表',
    '私募投资基金备案证明', '备案证明', '私募投资基金备案函', '备案函', '基金备案函',
    '银行账户信息确认函', '托管信息确认函', '账户信息确认函', '信息确认函', '业务确认函', '交易确认函', '确认函',
    '业务确认书', '交易确认书',
    '开户合同', '开户协议', '开户申请书', '交易申请书', '交易协议',
    '托管协议', '托管合同', '顾问协议', '顾问合同', '合伙协议',
    '委托协议', '委托合同', '服务协议', '服务合同',
    '授权委托书', '委托书',
    '申请表', '申请单', '登记表', '审批表', '审核表', '报名表', '调查表', '汇总表',
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
  ];
  const keywords = [...new Set(rawKeywords)].sort((a, b) => b.length - a.length);
  const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 0);
  const searchRange = Math.min(lines.length, 15);

  function stripLine(line) {
    return line
      .replace(/^版本号[:：]?\s*\S+\s*/, '')
      .replace(/^编号[:：]?\s*\S+\s*/, '')
      .replace(/^合同编号[:：]?\s*\S+\s*/, '')
      .replace(/^协议编号[:：]?\s*\S+\s*/, '')
      .replace(/^文号[:：]?\s*\S+\s*/, '')
      .replace(/^备案编码[:：]?\s*\S+\s*/, '')
      .replace(/^备案编号[:：]?\s*\S+\s*/, '')
      .replace(/^营业执照号码[:：]?\s*\S+\s*/, '')
      .replace(/^机构代码[:：]?\s*\S+\s*/, '')
      .replace(/^\d+[\.、\)\]\s\u3000]+/, '')
      .replace(/^[\(\（]\d+[\)\）]\s*/, '')
      .replace(/^[\s\u3000]+/, '')
      .trim();
  }

  function cleanTitle(title) {
    title = title.replace(/[A-Za-z]+/g, '');
    title = title.replace(/[A-Fa-f0-9]{6,}/g, '');
    title = title.replace(/[\u4e00-\u9fa5]{1,8}(?:有限|股份|合伙|集团)?(?:公司|企业)$/, '');
    title = title.replace(/[：:]\s*$/, '');
    title = title.replace(/\s+/g, '');
    return title.trim();
  }

  function isValidTitle(title) {
    const chineseCount = (title.match(/[\u4e00-\u9fa5]/g) || []).length;
    const totalCount = title.length;
    if (totalCount < 2) return false;
    if (chineseCount < 2) return false;
    if (chineseCount / totalCount < 0.5) return false;
    return true;
  }

  function isMeaningfulPrefix(p) {
    if (!p) return false;
    if (/(代码|编号|编码|号码|证号|信用代码|日期|申请日期|签发日期|版本号|文号|机构代码|营业执照|社会信用)/.test(p)) return false;
    if (/[:：]/.test(p)) return false;
    const hasYearDocNo = /\d{4}年/.test(p) || /\d{4}年度$/.test(p) || /第[一二三四五六七八九十百千0-9]+号/.test(p);
    if (p.length > 15) return hasYearDocNo && /^关于/.test(p) && /的$/.test(p);
    if (/^关于/.test(p) && /的$/.test(p)) return true;
    return hasYearDocNo;
  }

  // === 1. 跨行长关键词匹配（>=6字）===
  for (let i = 0; i < searchRange - 1; i++) {
    let lineA = stripLine(lines[i]);
    let lineB = stripLine(lines[i + 1]);
    let combined = lineA + lineB;
    if (combined.length < 4 || combined.length > 120) continue;
    for (const kw of keywords) {
      if (kw.length < 6) continue;
      if (combined.includes(kw)) {
        let kwIdx = combined.indexOf(kw);
        let beforeKw = combined.substring(0, kwIdx);
        let title;
        if (isMeaningfulPrefix(beforeKw) || beforeKw.length === 0) {
          title = combined.substring(0, kwIdx + kw.length);
        } else {
          title = kw;
        }
        if (beforeKw.length === 0 && kwIdx + kw.length < lineA.length) {
          const m = lineA.substring(kwIdx + kw.length).match(/^([\u4e00-\u9fa5]{1,20})/);
          if (m) title += m[1];
        }
        title = cleanTitle(title);
        if (isValidTitle(title)) return { title, source: `跨行长词[${i+1}+${i+2}] kw=${kw}` };
      }
    }
  }

  // === 1.5 跨行短关键词 + 有意义前缀（<=5字）===
  for (let i = 0; i < searchRange - 1; i++) {
    let lineA = stripLine(lines[i]);
    let lineB = stripLine(lines[i + 1]);
    let combined = lineA + lineB;
    if (combined.length < 6 || combined.length > 120) continue;
    for (const kw of keywords) {
      if (kw.length > 5 || kw.length < 2) continue;
      if (combined.includes(kw)) {
        let kwIdx = combined.indexOf(kw);
        let beforeKw = combined.substring(0, kwIdx);
        if (!(isMeaningfulPrefix(beforeKw) || beforeKw.length === 0)) continue;
        let title = combined.substring(0, kwIdx + kw.length);
        if (beforeKw.length === 0 && kwIdx + kw.length < lineA.length) {
          const m = lineA.substring(kwIdx + kw.length).match(/^([\u4e00-\u9fa5]{1,20})/);
          if (m) title += m[1];
        }
        title = cleanTitle(title);
        if (isValidTitle(title)) return { title, source: `跨行短词+前缀[${i+1}+${i+2}] kw=${kw}` };
      }
    }
  }

  // === 2. 单行匹配 ===
  for (let i = 0; i < searchRange; i++) {
    let stripped = stripLine(lines[i]);
    if (stripped.length < 2 || stripped.length > 80) continue;
    for (const kw of keywords) {
      if (kw.length <= 2 && i >= 5) continue;
      if (stripped.includes(kw)) {
        let kwIdx = stripped.indexOf(kw);
        let beforeKw = stripped.substring(0, kwIdx);
        let title;
        if (isMeaningfulPrefix(beforeKw) || beforeKw.length === 0) {
          title = stripped.substring(0, kwIdx + kw.length);
        } else {
          title = kw;
        }
        if (beforeKw.length === 0 && kwIdx + kw.length < stripped.length) {
          const m = stripped.substring(kwIdx + kw.length).match(/^([\u4e00-\u9fa5]{1,25})/);
          if (m) title += m[1];
        }
        title = cleanTitle(title);
        if (isValidTitle(title)) return { title, source: `单行[${i+1}] kw=${kw}` };
      }
    }
  }

  // === 2.5 单行短关键词 + 有意义前缀 ===
  for (let i = 0; i < searchRange; i++) {
    let stripped = stripLine(lines[i]);
    if (stripped.length < 6 || stripped.length > 80) continue;
    for (const kw of keywords) {
      if (kw.length > 5 || kw.length < 2) continue;
      if (kw.length <= 2 && i >= 5) continue;
      if (stripped.includes(kw)) {
        let kwIdx = stripped.indexOf(kw);
        let beforeKw = stripped.substring(0, kwIdx);
        if (!(isMeaningfulPrefix(beforeKw) || beforeKw.length === 0)) continue;
        let title = stripped.substring(0, kwIdx + kw.length);
        if (beforeKw.length === 0 && kwIdx + kw.length < stripped.length) {
          const m = stripped.substring(kwIdx + kw.length).match(/^([\u4e00-\u9fa5]{1,25})/);
          if (m) title += m[1];
        }
        title = cleanTitle(title);
        if (isValidTitle(title)) return { title, source: `单行短词+前缀[${i+1}] kw=${kw}` };
      }
    }
  }

  // === 2.9 文档词组闸门：回退评分前先检测整段OCR是否包含任意"文档常用词组" ===
  // 伪汉字乱码（横屏文档被竖向OCR）会凑出较高CJK密度绕过密度拦截，但几乎不会凑出
  // "申请/开户/通知/协议/账户/资金"这类2字组合词。正常金融文档必然命中至少一个。
  // 若全段无任何词组命中 → 视为乱码，直接跳过回退评分与最终回退，交由元数据/文件名兜底。
  const DOCUMENT_VOCAB = [
    '申请', '开户', '销户', '变更', '注销', '撤销', '备案', '登记',
    '通知', '公告', '回执', '确认', '证明', '声明', '承诺', '告知',
    '协议', '合同', '契约', '委托', '授权', '存管', '监管', '托管',
    '账户', '账号', '资金', '银行', '期货', '证券', '基金', '产品',
    '对账', '结算', '清算', '流水', '明细', '余额', '持仓', '交易',
    '印鉴', '密码', '证书', '网银', '转账', '划转', '划款', '汇款',
    '业务', '办理', '受理', '审批', '审核', '经办', '复核', '授权',
    '风险', '揭示', '提示', '合规', '法律', '审计', '评估', '调查',
    '到账', '入金', '出金', '续约', '解约', '冻结', '解冻', '激活'
  ];
  const fullText = text;
  const vocabHit = DOCUMENT_VOCAB.find(v => fullText.includes(v));
  if (!vocabHit) {
    return { title: '', source: '乱码(无文档词组)' };
  }

  // === 3. 回退：评分选标题 ===
  let bestLine = '', bestScore = -1;
  for (let i = 0; i < searchRange; i++) {
    let stripped = stripLine(lines[i]);
    if (stripped.length < 2) continue;
    if (/^[一二三四五六七八九十百千]+[、\.]/.test(stripped)) continue;
    if (/^\(?[（(]?(?:是|否|√|×)[）)]?/.test(stripped)) continue;
    if (/办理|业务|签约|撤销|账户|资金|客户|证券|期货|基金|代理|本人|机构|身份证/.test(stripped) && stripped.length > 20) continue;
    if (/[。，；、,;:：]/.test(stripped) && stripped.length > 30) continue;
    if (stripped.length > 60) continue;
    if (/^(根据|依据|按照|为了|为进一步|鉴于|经研究|现通知|现公告|现函|尊敬的|各部门|各营业部|客户|股东|全体|地址|电话|传真|邮编|邮箱|联系人|基金类型|基金名称|管理人|托管人|法定代表人|执行事务合伙人)/.test(stripped)) continue;
    let cleaned = cleanTitle(stripped);
    if (!isValidTitle(cleaned)) continue;
    // 【扫描件乱码防护】：只有 2 个汉字的行必须是文档型后缀结尾，否则"全区/人员/办公"这类乱码两字词会误当标题
    if (cleaned.length === 2 && !/[书表告函知议明同托诺证约章定卡案令]$/.test(cleaned)) continue;
    let score = 0;
    if (cleaned.length >= 4 && cleaned.length <= 50) score += 50;
    if (cleaned.length >= 10 && cleaned.length <= 40) score += 20;
    if (!/[。，；、,;]/.test(stripped)) score += 20;
    if (/[书|表|告|函|知|议|明|同|托|诺|证|约|定]/.test(cleaned)) score += 30;
    score += Math.max(0, 10 - i);
    if (score > bestScore) { bestScore = score; bestLine = cleaned; }
  }
  if (bestLine) return { title: bestLine, source: `回退评分 score=${bestScore} (词组:${vocabHit})` };

  // === 4. 最终回退 ===
  for (const line of lines) {
    let cleaned = cleanTitle(line);
    // 两字非文档后缀词也拦截
    if (cleaned.length === 2 && !/[书表告函知议明同托诺证约章定卡案令]$/.test(cleaned)) continue;
    if (isValidTitle(cleaned) && cleaned.length > 2 && cleaned.length < 80) {
      return { title: cleaned, source: `最终回退 (词组:${vocabHit})` };
    }
  }
  return { title: '', source: '空' };
}

// universalCleanTitle
function universalCleanTitle(t) {
  if (!t) return '';
  t = t.replace(/^(?:备案编码|备案编号|版本号|合同编号|协议编号|营业执照号码|编号|统一社会信用代码|社会信用代码|身份证号|证件号|机构代码|营业执照|申请日期|签发日期|日期|文号|账户号码|客户编号)[:：]?\s*[A-Za-z0-9\-]{0,30}\s*/, '');
  t = t.replace(/^备案编码[A-Za-z0-9]+/, '');
  t = t.replace(/[A-Za-z]/g, '');
  t = t.replace(/[0-9]{6,}/g, '');
  t = t.replace(/\s+/g, ' ').trim();
  const cutKeywords = ['私募投资基金备案证明','备案证明','授权委托书','证券账户业务申请表','基金账户业务申请表','账户业务申请表','接入外部信息系统承诺书和风险提示书','接入外部信息系统承诺书和风险揭示书','承诺书和风险提示书','承诺书和风险揭示书','申请表','申请单','登记表','审批表','审核表','协议书','承诺书','确认书','告知书','通知书','声明书','说明书','风险揭示书','风险提示书','合规意见书','法律意见书','尽职调查报告','审计报告','财务审计报告','评估报告','咨询报告','情况报告','情况说明','工作说明','补充说明','澄清说明','使用说明','操作说明','业务说明','交易说明','说明函','律师函','通知函','催收函','邀请函','催告函','回复函','答复函','复函','工作函','联系函','商洽函','询问函','告知函','提示函','警示函','监管函','函件','委托书','授权书','任命书','离职证明','解约函','收入证明','在职证明','资格证明','身份证明','资质证明','证明','保密承诺书','合规承诺书','交易承诺书','风险承诺书','投资协议书','服务协议书','合作协议书','托管协议书','情况反映','情况汇报','情况通报','意向书','谅解备忘录','合作备忘录','备忘录','协议','合同','要约','决议','纪要','公告','通报','处罚通知','处理通知','变更通知','调整通知','到期通知','续约通知','预警通知','终止通知','解除通知','催收通知','缴款通知','备案函','私募投资基金备案函'];
  cutKeywords.sort((a, b) => b.length - a.length);
  for (const kw of cutKeywords) {
    const idx = t.indexOf(kw);
    if (idx >= 0) {
      const prefixUpToKw = t.substring(0, idx);
      const meaningfulBefore = (/^关于.+的$/.test(prefixUpToKw) ||
        /第[一二三四五六七八九十百千0-9]+号/.test(prefixUpToKw) ||
        /\d{4}年/.test(prefixUpToKw) ||
        /\d{4}年度$/.test(prefixUpToKw)) &&
        prefixUpToKw.length < 25;
      t = meaningfulBefore ? t.substring(0, idx + kw.length) : t.substring(idx, idx + kw.length);
      break;
    }
  }
  return t.trim();
}

// extractFilingCode
function extractFilingCode(text) {
  if (!text) return '';
  const patterns = [
    /备案编码[:：]?\s*([A-Za-z0-9]{6})/,
    /备案编号[:：]?\s*([A-Za-z0-9]{6})/,
    /备案代码[:：]?\s*([A-Za-z0-9]{6})/,
  ];
  for (const p of patterns) {
    const m = text.match(p);
    if (m && m[1]) return m[1].toUpperCase();
  }
  return '';
}

// ======== 测试用例 ========
const testCases = [
  {
    name: 'Case 1: 授权委托书（跨行拆分）',
    ocrText: `海通证券股份有限公司\nHT SECURITIES CO., LTD.\n授 权 委 托 书\n（自然人客户专用）\n账户号码：88888888\n客户姓名：张三\n身份证号：110101199001011234`,
    expect: '授权委托书'
  },
  {
    name: 'Case 2: 接入外部信息系统承诺书和风险提示书',
    ocrText: `版本号：V1.0\n编号：EXT-2024-001\n接入外部信息系统承诺书\n和风险提示书\n（完整版）\n甲方：某某证券有限公司\n乙方：某某科技有限公司`,
    expect: '接入外部信息系统承诺书和风险提示书'
  },
  {
    name: 'Case 3: 私募投资基金备案证明 + 备案编码SVD248',
    ocrText: `中国证券投资基金业协会\nCHINA SECURITIES INVESTMENT FUND ASSOCIATION\n私募投资基金备案证明\n备案编码：SVD248\n基金名称：茂源信领量化中证红利指数增强1号私募证券投资基金\n管理人名称：某某投资管理有限公司`,
    expect: '私募投资基金备案证明SVD248'
  },
  {
    name: 'Case 4: 证券账户业务申请表（含公司名、统一社会信用代码前缀）',
    ocrText: `华泰证券股份有限公司\nHUATAI SECURITIES CO., LTD.\n统一社会信用代码：91440300087037980F\n证券账户业务申请表\n（机构客户版）\n申请日期：2024年01月15日`,
    expect: '证券账户业务申请表'
  },
  {
    name: 'Case 5: 情况说明（"关于+修饰过长"，去掉不必要前缀）',
    ocrText: `关于某某智能交易系统\n正式上线运行的情况说明\n各相关部门：\n为进一步提升交易效率...`,
    expect: '情况说明'
  },
  {
    name: 'Case 6: 授权委托书（和公司名连在一起跨行）',
    ocrText: `某某证券有限\n公司授权委托书\n委托人：张三\n受托人：李四`,
    expect: '授权委托书'
  },
  {
    name: 'Case 7: 关于XX的通知（保留关于...的前缀，跨两行）',
    ocrText: `文件编号：2024-001\n关于2024年春节假期\n交易安排的通知\n各营业部、各部门：\n根据国务院办公厅通知...`,
    expect: '关于2024年春节假期交易安排的通知'
  },
  {
    name: 'Case 8: 关于调整交易费率的函（单行）',
    ocrText: `某某证券股份有限公司\n文件\n文号：证字〔2024〕第15号\n关于调整交易费率的函\n尊敬的客户：\n为进一步提升服务质量...`,
    expect: '关于调整交易费率的函'
  },
  {
    name: 'Case 9: 私募投资基金备案函 + 备案编码ABC123',
    ocrText: `某某基金管理有限公司\n地址：北京市朝阳区建国路88号\n电话：010-88888888\n传真：010-88888889\n私募投资基金备案函\n备案编码：ABC123\n基金类型：私募证券投资基金`,
    expect: '私募投资基金备案函ABC123'
  },
  {
    name: 'Case 10: 2024年度财务审计报告（跨行，带年度年份）',
    ocrText: `华兴会计师事务所（特殊普通合伙）\nHUAXING CERTIFIED PUBLIC ACCOUNTANTS\n2024年度\n财务审计报告\n某某科技股份有限公司\n全体股东：\n我们审计了后附的财务报表...`,
    expect: '2024年度财务审计报告'
  },
  {
    name: 'Case 11: 银行账户信息确认函（正文含"公告"干扰词）',
    ocrText: `银行账户信息确认函\n尊敬的管理人：\n贵公司管理的"茂源信淮量化选股7号私募证券投资基金"银行\n账户相关信息如下：\n账户户名:中信建投证券股份有限公司茂源信淮量化选股7号\n银行账号:110062159018800358952\n开户行:交通银行北京三里河支行\n大额支付系统号:301100000347\n银行账户开户利率:按0.385%计息。\n注: 计息期若遇银行调整利率, 调整后账户利率以开户银行最新公告为准。\n银证关联需要券商营业部在开立三方账户时直接将上述营业执照号发送银行并预指定\n托管部联系方式: 010-56161929-4tuoguan@csc.com.cn\n中信建投证券股份有限公司托管部\n2021-09-27`,
    expect: '银行账户信息确认函'
  },
  {
    name: 'Case 12: 伪汉字乱码（横屏文档竖向OCR）→ 应返回空走文件名兜底',
    ocrText: `三2站国生汪汪8\n= "\n将互革 SDDS =\n°g 人 SN 开\n E 人类本 ReE\n只长3由\n§# ee si/ 员\nS = 8 NS\n& 区员 w B`,
    expect: ''
  },
  {
    name: 'Case 13: 纯伪汉字乱码（高频字但无文档词组）→ 应返回空',
    ocrText: `三二三四\n五六七八\n九十百千\n甲乙丙丁\n子丑寅卯\n金木水火`,
    expect: ''
  }
];

console.log('===================== 标题识别测试 =====================\n');

let passed = 0, failed = 0;
for (const tc of testCases) {
  const { title, source } = extractTitleFromOCRText(tc.ocrText);
  const afterUniversal = universalCleanTitle(title);
  const code = extractFilingCode(tc.ocrText);
  const final = afterUniversal + (code || '');
  const ok = final === tc.expect;
  if (ok) passed++; else failed++;
  console.log(`${tc.name}`);
  console.log(`  期望: "${tc.expect}"`);
  console.log(`  实际: "${final}"  [${source}]  [cleanTitle="${title}" | universal="${afterUniversal}" | 备案编码="${code}"]`);
  console.log(`  结果: ${ok ? '✅ 通过' : '❌ 失败'}\n`);
}
console.log('=======================================================');
console.log(`✅ ${passed}/${passed+failed} 通过，❌ ${failed} 失败`);
console.log('=======================================================');
process.exit(failed > 0 ? 1 : 0);
