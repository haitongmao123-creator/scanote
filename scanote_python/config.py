# -*- coding: utf-8 -*-
"""
配置文件 - 把你的邮箱和授权码填到这里
"""

# ============ 邮箱配置 ============
# 网易企业邮箱 IMAP 服务器
IMAP_SERVER = "imaphz.qiye.163.com"
IMAP_PORT = 993

# 你的邮箱地址
EMAIL_ADDRESS = "ht.mao@mycapital.net"

# 授权码（不是邮箱登录密码！去 mail.qiye.163.com 后台开IMAP服务后生成的16位字母码）
# 步骤：登录网页版 → 设置 → 客户端设置 → 开启IMAP/SMTP → 生成客户端授权码
EMAIL_AUTH_CODE = "在这里填你的授权码"

# 只监听这个发件人发来的邮件（填你的扫描仪邮箱）；想抓所有邮件就填空字符串 ""
LISTEN_SENDER = "scan@mycapital.net"

# 检查间隔（秒）
CHECK_INTERVAL = 60

# ============ 保存配置 ============
# 处理好的 PDF 保存到这里（重命名后的文件）
OUTPUT_DIR = r"E:\桌面"

# 下载的原始 PDF 临时存放（处理完会自动清理）
TEMP_DIR = r"E:\桌面\_scanote_temp"

# ============ OCR 配置 ============
# Tesseract 可执行文件路径（默认安装路径，如果改了请更新）
# Windows 默认: r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Tesseract 语言包（chi_sim=简体中文，eng=英文）
TESSERACT_LANG = "chi_sim+eng"

# ============ 运行模式 ============
# True = 处理完一封就标记为已读，下次不再处理
# False = 每次都重新处理所有邮件
MARK_AS_READ = True

# 处理完多少封邮件后停止（0 = 一直循环监听）
# 建议调试时设为 1，跑通后改 0
MAX_PROCESS = 1
