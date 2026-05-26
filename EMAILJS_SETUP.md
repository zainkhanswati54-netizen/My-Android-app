# EmailJS Setup Guide — FREE OTP System

## Step 1: EmailJS Account Banao (FREE)
1. https://www.emailjs.com par jao
2. "Sign Up Free" click karo
3. 200 emails/month bilkul FREE

## Step 2: Email Service Connect Karo
1. Dashboard → "Email Services" → "Add New Service"
2. "Gmail" select karo
3. Apna Gmail account connect karo
4. **Service ID** note karo (e.g. `service_abc123`)

## Step 3: Email Template Banao
1. Dashboard → "Email Templates" → "Create New Template"
2. Template fill karo:

**Subject:**
```
Your Titan Studio PRO Verification Code
```

**Body (HTML):**
```html
<div style="font-family: Arial; max-width: 500px; margin: 0 auto;">
  <h2 style="color: #38BDF8;">Titan Studio PRO</h2>
  <p>Hello {{to_name}},</p>
  <p>Your verification code is:</p>
  <div style="background: #1E293B; padding: 20px; text-align: center; 
              border-radius: 12px; margin: 20px 0;">
    <span style="font-size: 36px; font-weight: bold; 
                 color: #38BDF8; letter-spacing: 8px;">{{otp}}</span>
  </div>
  <p>This code expires in <b>{{expiry}}</b>.</p>
  <p>If you did not request this, please ignore this email.</p>
  <p>— {{app_name}} Team</p>
</div>
```

3. To Email field mein: `{{to_email}}`
4. Save karo → **Template ID** note karo (e.g. `template_xyz789`)

## Step 4: Public Key Copy Karo
1. Dashboard → "Account" → "General"
2. **Public Key** copy karo (e.g. `user_XXXXXXXXXXXXXXX`)

## Step 5: App Mein IDs Update Karo
File: `lib/services/email_otp_service.dart`

```dart
static const _emailjsServiceId  = 'service_abc123';   // ← apna ID
static const _emailjsTemplateId = 'template_xyz789';  // ← apna ID
static const _emailjsPublicKey  = 'user_XXXXXXX';     // ← apna key
```

## Step 6: Firebase Database Rules Update Karo
1. Firebase Console → Realtime Database → Rules
2. `firebase_database_rules.json` ka content paste karo
3. "Publish" click karo

## Done! ✅
Ab registration mein:
- User email + password fill kare
- OTP automatically email aaye
- User OTP verify kare → account bane

## FREE Limits:
- EmailJS: 200 emails/month FREE
- Firebase Realtime DB: 1GB storage FREE
- OTP 10 minutes mein auto-expire hote hain
