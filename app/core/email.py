"""
邮箱验证码模块
"""

import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from app.core.config import settings

try:
    import redis as redis_lib
except Exception:
    redis_lib = None


class VerificationCodeStore:
    """
    验证码存储

    - 优先使用 Redis
    - Redis 不可用时回退到内存
    """

    def __init__(self):
        self._store: Dict[str, dict] = {}
        self._ttl_seconds = 5 * 60
        self._max_attempts = 5
        self._redis_client: Optional[Any] = None
        self._key_prefix = "suanchao:verify_code"

        redis_url = (settings.REDIS_URL or "").strip()
        if redis_url and redis_lib is not None:
            try:
                self._redis_client = redis_lib.Redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=settings.REDIS_CONNECT_TIMEOUT_SECONDS,
                    socket_timeout=settings.REDIS_SOCKET_TIMEOUT_SECONDS,
                    retry_on_timeout=False,
                    health_check_interval=30,
                )
                self._redis_client.ping()
                print("验证码存储已切换到 Redis")
            except Exception as e:
                self._redis_client = None
                print(f"Redis 不可用，验证码回退内存存储: {e}")
        elif redis_url and redis_lib is None:
            print("检测到 REDIS_URL，但 redis 依赖未安装，验证码回退内存存储")

    def _build_key(self, email: str, purpose: str) -> str:
        return f"{self._key_prefix}:{purpose}:{email.strip().lower()}"

    def generate_code(self, email: str, purpose: str = "register") -> str:
        # 生成随机6位验证码
        code = "".join(random.choices(string.digits, k=6))
        key = self._build_key(email=email, purpose=purpose)

        if self._redis_client is not None:
            try:
                pipe = self._redis_client.pipeline()
                pipe.hset(key, mapping={"code": code, "attempts": 0})
                pipe.expire(key, self._ttl_seconds)
                pipe.execute()
                return code
            except Exception as e:
                print(f"Redis 写入验证码失败，回退内存存储: {e}")

        expire_at = datetime.utcnow() + timedelta(seconds=self._ttl_seconds)
        self._store[key] = {"code": code, "expire_at": expire_at, "attempts": 0}

        return code

    def verify_code(self, email: str, code: str, purpose: str = "register") -> bool:
        key = self._build_key(email=email, purpose=purpose)

        if self._redis_client is not None:
            try:
                record = self._redis_client.hgetall(key)
                if not record:
                    return False

                attempts = int(record.get("attempts", 0))
                if attempts >= self._max_attempts:
                    self._redis_client.delete(key)
                    return False

                if record.get("code") == code:
                    self._redis_client.delete(key)
                    return True

                attempts = int(self._redis_client.hincrby(key, "attempts", 1))
                if attempts >= self._max_attempts:
                    self._redis_client.delete(key)
                return False
            except Exception as e:
                print(f"Redis 校验验证码失败，回退内存校验: {e}")

        if key not in self._store:
            return False

        record = self._store[key]

        if datetime.utcnow() > record["expire_at"]:
            del self._store[key]
            return False

        if record["attempts"] >= self._max_attempts:
            del self._store[key]
            return False

        if record["code"] == code:
            del self._store[key]
            return True

        record["attempts"] += 1
        if record["attempts"] >= self._max_attempts:
            del self._store[key]
        return False

    def get_code(self, email: str, purpose: str = "register") -> Optional[str]:
        key = self._build_key(email=email, purpose=purpose)

        if self._redis_client is not None:
            try:
                value = self._redis_client.hget(key, "code")
                return value if value else None
            except Exception as e:
                print(f"Redis 读取验证码失败，回退内存读取: {e}")

        if key in self._store:
            return self._store[key]["code"]
        return None


class EmailService:
    def __init__(self):
        self.smtp_host = getattr(settings, "SMTP_HOST", "smtp.qq.com")
        self.smtp_port = getattr(settings, "SMTP_PORT", 587)
        self.smtp_user = getattr(settings, "SMTP_USER", "")
        self.smtp_password = getattr(settings, "SMTP_PASSWORD", "")
        self.from_name = getattr(settings, "SMTP_FROM_NAME", "算潮")
        self.smtp_timeout_seconds = getattr(settings, "SMTP_TIMEOUT_SECONDS", 10)

    def send_verification_code(self, email: str, code: str, purpose: str = "register") -> bool:
        if not self.smtp_user or not self.smtp_password:
            print(f"邮件配置未设置，开发模式: 验证码 {code} 发送到 {email}")
            return True

        try:
            msg = MIMEMultipart("alternative")
            purpose_text = {
                "register": "注册",
                "reset_password": "重置密码",
                "delete_account": "注销账号",
            }.get(purpose, "操作")

            msg["Subject"] = f"算潮 {purpose_text}验证码"
            msg["From"] = f"{self.from_name} <{self.smtp_user}>"
            msg["To"] = email

            html_content = f"""
            <html><body>
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px;">
                        <h1 style="color: white; margin: 0;">算潮</h1>
                    </div>
                    <div style="padding: 30px; background: #f8f9fa;">
                        <p>您好，您的{purpose_text}验证码是：</p>
                        <div style="background: #fff; padding: 20px; text-align: center; border-radius: 8px; margin: 20px 0;">
                            <span style="font-size: 32px; font-weight: bold; color: #667eea; letter-spacing: 8px;">{code}</span>
                        </div>
                        <p style="color: #666;">验证码有效期为 5 分钟</p>
                    </div>
                </div>
            </body></html>
            """

            msg.attach(MIMEText(html_content, "html", "utf-8"))

            server = smtplib.SMTP(
                self.smtp_host,
                self.smtp_port,
                timeout=self.smtp_timeout_seconds,
            )
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.smtp_user, self.smtp_password)
            server.sendmail(self.smtp_user, email, msg.as_string())
            server.quit()

            print(f"验证码已发送到 {email}")
            return True

        except Exception as e:
            print(f"发送邮件失败: {e}")
            return False


code_store = VerificationCodeStore()
email_service = EmailService()


def send_verification_code(email: str, purpose: str = "register") -> bool:
    code = code_store.generate_code(email=email, purpose=purpose)
    return email_service.send_verification_code(email=email, code=code, purpose=purpose)


def verify_code(email: str, code: str, purpose: str = "register") -> bool:
    return code_store.verify_code(email=email, code=code, purpose=purpose)
