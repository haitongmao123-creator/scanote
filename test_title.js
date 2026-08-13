// 模拟 index.html 中的核心函数用于本地测试（与 index.html 同步）

function extractTitleFromOCRText(text) {
  if (!text || text.trim().length === 0) return '';

  const rawKeywords = [
    '承诺书和风险提示书', '承诺书和风险揭示书',
    '接入外部信息系统承诺书和风险提示书', '接入外部信息系统承诺书和风险揭示书',
    '证券账户业务申请表', '基金账户业务申请表', '账户业务申请表',
    '私募投资基金备案证明', '备案证明', '私募投资基金备案函', '备案函', '基金备案函',
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
    '告知函', '提示函', '警示函', '监管函', '函件',
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
    let combined = stripLine(lines[i]) + stripLine(lines[i + 1]);
    if (combined.length < 4 || combined.length > 120) continue;
    for (const kw of keywords) {
      if (kw.length < 6) continue;
      if (combined.includes(kw)) {
        let beforeKw = combined.substring(0, combined.indexOf(kw));
        let title = kw;
        if (isMeaningfulPrefix(beforeKw)) title = combined.substring(0, combined.indexOf(kw) + kw.length);
        title = cleanTitle(title);
        if (isValidTitle(title)) return { title, source: `跨行长词[${i+1}+${i+2}] kw=${kw}` };
      }
    }
  }

  // === 1.5 跨行短关键词 + 有意义前缀（<=5字）===
  for (let i = 0; i < searchRange - 1; i++) {
    let combined = stripLine(lines[i]) + stripLine(lines[i + 1]);
    if (combined.length < 6 || combined.length > 120) continue;
    for (const kw of keywords) {
      if (kw.length > 5 || kw.length < 2) continue;
      if (combined.includes(kw)) {
        let beforeKw = combined.substring(0, combined.indexOf(kw));
        if (!isMeaningfulPrefix(beforeKw)) continue;
        let title = combined.substring(0, combined.indexOf(kw) + kw.length);
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
      if (stripped.includes(kw)) {
        let beforeKw = stripped.substring(0, stripped.indexOf(kw));
        let title = kw;
        if (isMeaningfulPrefix(beforeKw)) title = stripped.substring(0, stripped.indexOf(kw) + kw.length);
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
      if (stripped.includes(kw)) {
        let beforeKw = stripped.substring(0, stripped.indexOf(kw));
        if (!isMeaningfulPrefix(beforeKw)) continue;
        let title = stripped.substring(0, stripped.indexOf(kw) + kw.length);
        title = cleanTitle(title);
        if (isValidTitle(title)) return { title, source: `单行短词+前缀[${i+1}] kw=${kw}` };
      }
    }
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
    let score = 0;
    if (cleaned.length >= 4 && cleaned.length <= 50) score += 50;
    if (cleaned.length >= 10 && cleaned.length <= 40) score += 20;
    if (!/[。，；、,;]/.test(stripped)) score += 20;
    if (/[书|表|告|函|知|议|明|同|托|诺|证|约|定]/.test(cleaned)) score += 30;
    score += Math.max(0, 10 - i);
    if (score > bestScore) { bestScore = score; bestLine = cleaned; }
  }
  if (bestLine) return { title: bestLine, source: `回退评分 score=${bestScore}` };

  // === 4. 最终回退 ===
  for (const line of lines) {
    let cleaned = cleanTitle(line);
    if (isValidTitle(cleaned) && cleaned.length > 2 && cleaned.length < 80) {
      return { title: cleaned, source: '最终回退' };
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
