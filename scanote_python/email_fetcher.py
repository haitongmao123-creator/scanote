# -*- coding: utf-8 -*-
"""
邮件抓取模块 - 通过 IMAP 连接网易企业邮箱，下载 PDF 附件
"""

import imaplib
import email
import os
import time
from email.header import decode_header
from email.utils import parseaddr

import config


def decode_str(s):
    """解码邮件头部字符串"""
    if not s:
        return ''
    parts = decode_header(s)
    result = []
    for content, charset in parts:
        if isinstance(content, bytes):
            try:
                result.append(content.decode(charset or 'utf-8', errors='replace'))
            except (LookupError, TypeError):
                result.append(content.decode('utf-8', errors='replace'))
        else:
            result.append(content)
    return ''.join(result)


def connect_mailbox():
    """连接邮箱，返回 IMAP 对象"""
    print(f"🔗 连接邮箱 {config.EMAIL_ADDRESS} @ {config.IMAP_SERVER}:{config.IMAP_PORT} ...")
    mail = imaplib.IMAP4_SSL(config.IMAP_SERVER, config.IMAP_PORT)
    mail.login(config.EMAIL_ADDRESS, config.EMAIL_AUTH_CODE)
    mail.select('INBOX')
    print("✅ 邮箱连接成功")
    return mail


def get_unread_emails(mail, sender_filter=''):
    """获取未读邮件ID列表
    sender_filter: 只抓这个发件人的邮件，空字符串=抓所有
    """
    # 先按未读筛选
    if sender_filter:
        # 按发件人 + 未读筛选
        status, data = mail.search(None, 'UNSEEN', f'FROM "{sender_filter}"')
    else:
        status, data = mail.search(None, 'UNSEEN')

    if status != 'OK':
        return []

    mail_ids = data[0].split()
    return mail_ids


def fetch_email(mail, mail_id):
    """抓取一封邮件，返回邮件对象"""
    status, data = mail.fetch(mail_id, '(RFC822)')
    if status != 'OK':
        return None
    raw = data[0][1]
    return email.message_from_bytes(raw)


def extract_pdf_attachments(msg):
    """从邮件对象中提取 PDF 附件，返回 [(文件名, 内容bytes), ...]"""
    pdfs = []
    for part in msg.walk():
        content_disposition = part.get('Content-Disposition', '')
        if 'attachment' not in content_disposition and 'attachment' not in (part.get('Content-Disposition') or ''):
            continue
        filename = part.get_filename()
        if not filename:
            continue
        filename = decode_str(filename)
        if not filename.lower().endswith('.pdf'):
            continue
        content = part.get_payload(decode=True)
        if content:
            pdfs.append((filename, content))
    return pdfs


def mark_as_read(mail, mail_id):
    """标记邮件为已读"""
    mail.store(mail_id, '+FLAGS', '\\Seen')


def process_mailbox(callback, max_process=0, mark_as_read=True, interval=60, sender_filter=''):
    """监听邮箱，处理新邮件
    callback: 处理函数，签名为 callback(filename, pdf_bytes) -> new_filename
    max_process: 处理多少封后停止（0=一直循环）
    interval: 检查间隔（秒）
    """
    processed_count = 0

    while True:
        try:
            mail = connect_mailbox()
            mail_ids = get_unread_emails(mail, sender_filter)
            print(f"📬 发现 {len(mail_ids)} 封未读邮件" + (f"（发件人: {sender_filter}）" if sender_filter else ""))

            if not mail_ids:
                print(f"⏳ 无新邮件，{interval}秒后重试...")
            else:
                for mail_id in mail_ids:
                    msg = fetch_email(mail, mail_id)
                    if not msg:
                        continue

                    subject = decode_str(msg.get('Subject', ''))
                    from_addr = parseaddr(msg.get('From', ''))[1]
                    print(f"\n📧 处理邮件: {subject}")
                    print(f"   发件人: {from_addr}")

                    pdfs = extract_pdf_attachments(msg)
                    if not pdfs:
                        print("   ⚠️ 该邮件无PDF附件，跳过")
                        if mark_as_read:
                            mark_as_read(mail, mail_id)
                        continue

                    print(f"   📎 发现 {len(pdfs)} 个PDF附件")
                    for pdf_filename, pdf_bytes in pdfs:
                        try:
                            new_name = callback(pdf_filename, pdf_bytes)
                            print(f"   ✅ {pdf_filename} → {new_name}")
                        except Exception as e:
                            print(f"   ❌ 处理 {pdf_filename} 失败: {e}")

                    if mark_as_read:
                        mark_as_read(mail, mail_id)
                    processed_count += 1
                    if max_process > 0 and processed_count >= max_process:
                        print(f"\n🏁 已处理 {processed_count} 封邮件，达到上限，停止")
                        mail.logout()
                        return

            mail.logout()
        except Exception as e:
            print(f"❌ 邮箱连接/处理出错: {e}")

        if max_process > 0 and processed_count >= max_process:
            return

        print(f"\n⏳ {interval}秒后再次检查邮箱...\n")
        time.sleep(interval)
