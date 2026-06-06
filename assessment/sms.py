"""
Tencent Cloud SMS integration for phone verification.
Handles sending verification codes and validating them.
"""
import os
import time
import random
import logging

logger = logging.getLogger(__name__)

# In-memory code store: {phone: {code, expires_at, attempts}}
_code_store: dict[str, dict] = {}

# Rate limit: {phone: last_send_time}
_rate_limit: dict[str, float] = {}

CODE_LENGTH = 6
CODE_TTL_SECONDS = 300  # 5 minutes
RATE_LIMIT_SECONDS = 60
MAX_VERIFY_ATTEMPTS = 5


def _generate_code() -> str:
    return "".join([str(random.randint(0, 9)) for _ in range(CODE_LENGTH)])


def _cleanup_expired():
    """Remove expired codes to prevent memory leak."""
    now = time.time()
    expired = [p for p, v in _code_store.items() if v["expires_at"] < now]
    for p in expired:
        del _code_store[p]


async def send_verification_code(phone: str) -> dict:
    """
    Send a 6-digit verification code via Tencent Cloud SMS.
    Returns {"success": True} or {"success": False, "error": "reason"}.
    """
    # Rate limit check
    now = time.time()
    if phone in _rate_limit:
        elapsed = now - _rate_limit[phone]
        if elapsed < RATE_LIMIT_SECONDS:
            remaining = int(RATE_LIMIT_SECONDS - elapsed)
            return {"success": False, "error": f"请{remaining}秒后再试"}

    _cleanup_expired()

    code = _generate_code()

    # Try sending via Tencent Cloud SMS
    secret_id = os.getenv("TENCENT_SMS_SECRET_ID")
    secret_key = os.getenv("TENCENT_SMS_SECRET_KEY")
    app_id = os.getenv("TENCENT_SMS_APP_ID")
    sign_name = os.getenv("TENCENT_SMS_SIGN")
    template_id = os.getenv("TENCENT_SMS_TEMPLATE_ID")

    if not all([secret_id, secret_key, app_id, sign_name, template_id]):
        # Dev fallback: store code but don't actually send SMS
        logger.warning(f"[SMS] Tencent SMS not configured, code for {phone}: {code}")
        _code_store[phone] = {
            "code": code,
            "expires_at": now + CODE_TTL_SECONDS,
            "attempts": 0,
        }
        _rate_limit[phone] = now
        return {"success": True, "_dev_code": code}

    try:
        from tencentcloud.common import credential
        from tencentcloud.sms.v20210111 import sms_client, models

        cred = credential.Credential(secret_id, secret_key)
        client = sms_client.SmsClient(cred, "ap-guangzhou")

        req = models.SendSmsRequest()
        req.SmsSdkAppId = app_id
        req.SignName = sign_name
        req.TemplateId = template_id
        # Template params: {1}=code, {2}=validity in minutes
        req.TemplateParamSet = [code, str(CODE_TTL_SECONDS // 60)]
        # Phone number must have +86 prefix for mainland China
        phone_with_prefix = phone if phone.startswith("+") else f"+86{phone}"
        req.PhoneNumberSet = [phone_with_prefix]

        resp = client.SendSms(req)
        status = resp.SendStatusSet[0]

        if status.Code == "Ok":
            _code_store[phone] = {
                "code": code,
                "expires_at": now + CODE_TTL_SECONDS,
                "attempts": 0,
            }
            _rate_limit[phone] = now
            return {"success": True}
        else:
            logger.error(f"[SMS] Send failed: {status.Code} - {status.Message}")
            return {"success": False, "error": f"发送失败: {status.Message}"}

    except ImportError:
        # tencentcloud SDK not installed — dev mode
        logger.warning(f"[SMS] SDK not installed, code for {phone}: {code}")
        _code_store[phone] = {
            "code": code,
            "expires_at": now + CODE_TTL_SECONDS,
            "attempts": 0,
        }
        _rate_limit[phone] = now
        return {"success": True, "_dev_code": code}
    except Exception as e:
        logger.error(f"[SMS] Exception: {e}")
        return {"success": False, "error": "短信服务异常，请稍后重试"}


def verify_code(phone: str, code: str) -> bool:
    """Verify a code for the given phone number."""
    now = time.time()
    entry = _code_store.get(phone)
    if not entry:
        return False
    if entry["expires_at"] < now:
        del _code_store[phone]
        return False
    if entry["attempts"] >= MAX_VERIFY_ATTEMPTS:
        del _code_store[phone]
        return False

    entry["attempts"] += 1

    if entry["code"] == code:
        del _code_store[phone]  # One-time use
        return True
    return False
