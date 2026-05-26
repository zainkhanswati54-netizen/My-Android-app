# EmailJS Template — Exact Content

## Dashboard mein template kholo aur yeh fields fill karo:

### ✅ "To Email" field:
{{to_email}}

### ✅ "From Name" field:
Titan Studio PRO

### ✅ "Subject" field:
{{otp}} — Titan Studio PRO Verification Code

### ✅ "Message" / "Content" field (plain text mode mein yeh likho):

Hello {{to_name}},

Your Titan Studio PRO verification code is:

{{otp}}

This code is valid for {{expiry}}.

Do not share this code with anyone.

— Titan Studio PRO Team

---

## Ya HTML mode mein yeh paste karo:

<!DOCTYPE html>
<html>
<body style="background:#0F172A;font-family:Arial;padding:30px;margin:0">
<div style="max-width:480px;margin:auto;background:#1E293B;border-radius:16px;overflow:hidden">
  <div style="background:#0369A1;padding:24px;text-align:center">
    <h1 style="color:#fff;margin:0;font-size:22px">⚡ Titan Studio PRO</h1>
  </div>
  <div style="padding:32px">
    <p style="color:#94A3B8;font-size:15px">Hello <b style="color:#F1F5F9">{{to_name}}</b>,</p>
    <p style="color:#94A3B8;font-size:14px">Your verification code:</p>
    <div style="background:#0F172A;border-radius:12px;padding:24px;text-align:center;margin:20px 0">
      <span style="font-size:42px;font-weight:900;color:#38BDF8;letter-spacing:12px">{{otp}}</span>
      <p style="color:#64748B;font-size:12px;margin:8px 0 0">Valid for {{expiry}}</p>
    </div>
    <p style="color:#64748B;font-size:13px">Do not share this code with anyone.</p>
  </div>
</div>
</body>
</html>

## ✅ Save karo — Done!
