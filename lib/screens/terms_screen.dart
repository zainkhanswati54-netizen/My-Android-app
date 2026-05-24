import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../utils/constants.dart';

// ═══════════════════════════════════════════════════════
//  TERMS & CONDITIONS SCREEN
// ═══════════════════════════════════════════════════════

class TermsScreen extends StatefulWidget {
  /// If [mustAccept] is true, user must agree before proceeding.
  /// [onAccepted] callback fires when user taps "Agree & Continue".
  final bool mustAccept;
  final VoidCallback? onAccepted;
  const TermsScreen({super.key, this.mustAccept = false, this.onAccepted});
  @override
  State<TermsScreen> createState() => _TermsScreenState();
}

class _TermsScreenState extends State<TermsScreen> {
  bool _agreed = false;
  final _scrollCtrl = ScrollController();
  bool _scrolledToEnd = false;

  @override
  void initState() {
    super.initState();
    _scrollCtrl.addListener(_onScroll);
  }

  void _onScroll() {
    if (_scrollCtrl.position.pixels >=
        _scrollCtrl.position.maxScrollExtent - 40) {
      if (!_scrolledToEnd) setState(() => _scrolledToEnd = true);
    }
  }

  @override
  void dispose() {
    _scrollCtrl.removeListener(_onScroll);
    _scrollCtrl.dispose();
    super.dispose();
  }

  void _handleAccept() {
    if (!_agreed) return;
    HapticFeedback.lightImpact();
    if (widget.onAccepted != null) {
      widget.onAccepted!();
    } else {
      Navigator.pop(context, true);
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark   = Theme.of(context).brightness == Brightness.dark;
    final bgColor  = isDark ? cBg    : cLBg;
    final bg2Color = isDark ? cBg2   : cLBg2;
    final cardColor= isDark ? cCard  : cLCard;
    final textColor= isDark ? cText  : cLText;
    final text2    = isDark ? cText2 : cLText2;
    final muted    = isDark ? cMuted : cLMuted;
    final border   = isDark ? cBorder: cLBorder;
    final accent   = isDark ? cGreen : cLAccent;

    return Scaffold(
      backgroundColor: bgColor,
      appBar: AppBar(
        backgroundColor: isDark ? cBg2 : cLBg,
        elevation: 0,
        surfaceTintColor: Colors.transparent,
        leading: widget.mustAccept
            ? const SizedBox()
            : IconButton(
                icon: Icon(Icons.arrow_back_rounded, color: textColor),
                onPressed: () => Navigator.pop(context),
              ),
        title: Text(
          'Terms & Conditions',
          style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w700,
              color: textColor),
        ),
        centerTitle: true,
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(1),
          child: Container(height: 1, color: border),
        ),
      ),
      body: Column(
        children: [
          // ── Content ──────────────────────────────────────
          Expanded(
            child: SingleChildScrollView(
              controller: _scrollCtrl,
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Header banner
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: accent.withOpacity(0.08),
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: accent.withOpacity(0.25)),
                    ),
                    child: Row(children: [
                      Container(
                        width: 40, height: 40,
                        decoration: BoxDecoration(
                          color: accent.withOpacity(0.15),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Icon(Icons.gavel_rounded, color: accent, size: 22),
                      ),
                      const SizedBox(width: 12),
                      Expanded(child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('User Agreement',
                              style: TextStyle(
                                  fontSize: 14, fontWeight: FontWeight.w700,
                                  color: textColor)),
                          const SizedBox(height: 2),
                          Text('Last updated: May 2026',
                              style: TextStyle(fontSize: 12, color: muted)),
                        ],
                      )),
                    ]),
                  ),

                  const SizedBox(height: 24),

                  _Section(
                    number: '1',
                    title: 'Acceptance of Terms',
                    isDark: isDark,
                    textColor: textColor,
                    text2: text2,
                    accent: accent,
                    content:
                        'By downloading, installing, or using Titan Studio PRO ("the App"), you agree to be bound by these Terms and Conditions. If you do not agree, please do not use the App.',
                  ),

                  _Section(
                    number: '2',
                    title: 'Use of Service',
                    isDark: isDark,
                    textColor: textColor,
                    text2: text2,
                    accent: accent,
                    content:
                        'Titan Studio PRO provides AI-powered text-to-speech services. You may use the App only for lawful purposes. You agree not to use the App to generate content that is harmful, abusive, defamatory, or violates any applicable laws.',
                  ),

                  _Section(
                    number: '3',
                    title: 'Account & Security',
                    isDark: isDark,
                    textColor: textColor,
                    text2: text2,
                    accent: accent,
                    content:
                        'You are responsible for maintaining the confidentiality of your account credentials. You agree to notify us immediately of any unauthorized use of your account. We reserve the right to suspend or terminate accounts that violate these terms.',
                  ),

                  _Section(
                    number: '4',
                    title: 'Generated Content',
                    isDark: isDark,
                    textColor: textColor,
                    text2: text2,
                    accent: accent,
                    content:
                        'You retain ownership of the text you input. The audio files generated by the App are for your personal or commercial use. You must not use the App to generate content that impersonates real individuals without consent, or content that infringes on third-party intellectual property rights.',
                  ),

                  _Section(
                    number: '5',
                    title: 'Privacy & Data',
                    isDark: isDark,
                    textColor: textColor,
                    text2: text2,
                    accent: accent,
                    content:
                        'We collect minimal data necessary to provide our service, including your email address and usage analytics. We do not sell your personal data to third parties. Audio files and input text may be temporarily processed on our servers but are not stored permanently.',
                  ),

                  _Section(
                    number: '6',
                    title: 'Subscription & Payments',
                    isDark: isDark,
                    textColor: textColor,
                    text2: text2,
                    accent: accent,
                    content:
                        'Titan Studio PRO offers both free and premium tiers. Premium features require an active subscription. Subscriptions are billed according to the plan selected. Refunds are subject to our refund policy. We reserve the right to change pricing with reasonable notice.',
                  ),

                  _Section(
                    number: '7',
                    title: 'Prohibited Uses',
                    isDark: isDark,
                    textColor: textColor,
                    text2: text2,
                    accent: accent,
                    content:
                        'You may not: (a) reverse engineer or attempt to extract the App\'s source code; (b) use the App for automated bulk generation without authorization; (c) share, sell, or sublicense API access; (d) generate deepfake audio of real persons without consent; (e) use the service to spread misinformation or harmful content.',
                  ),

                  _Section(
                    number: '8',
                    title: 'Limitation of Liability',
                    isDark: isDark,
                    textColor: textColor,
                    text2: text2,
                    accent: accent,
                    content:
                        'Titan Studio PRO is provided "as is" without warranties of any kind. We are not liable for any indirect, incidental, or consequential damages arising from your use of the App. Our maximum liability shall not exceed the amount you paid in the 12 months preceding the claim.',
                  ),

                  _Section(
                    number: '9',
                    title: 'Modifications',
                    isDark: isDark,
                    textColor: textColor,
                    text2: text2,
                    accent: accent,
                    content:
                        'We reserve the right to modify these Terms at any time. Continued use of the App after changes constitutes acceptance of the new terms. We will notify users of significant changes via email or in-app notification.',
                  ),

                  _Section(
                    number: '10',
                    title: 'Governing Law',
                    isDark: isDark,
                    textColor: textColor,
                    text2: text2,
                    accent: accent,
                    content:
                        'These Terms are governed by and construed in accordance with applicable laws. Any disputes arising from these terms will be resolved through binding arbitration unless otherwise required by law.',
                  ),

                  const SizedBox(height: 16),

                  // Contact info
                  Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: isDark ? cBg2 : cLCard2,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: border),
                    ),
                    child: Row(children: [
                      Icon(Icons.mail_outline_rounded, color: muted, size: 18),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          'Questions? Contact us at support@titanstudio.app',
                          style: TextStyle(fontSize: 12, color: text2),
                        ),
                      ),
                    ]),
                  ),

                  const SizedBox(height: 24),
                ],
              ),
            ),
          ),

          // ── Bottom Agreement Bar ─────────────────────────
          if (widget.mustAccept) ...[
            Container(
              decoration: BoxDecoration(
                color: isDark ? cBg2 : cLBg,
                border: Border(top: BorderSide(color: border)),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(isDark ? 0.3 : 0.08),
                    blurRadius: 12,
                    offset: const Offset(0, -4),
                  ),
                ],
              ),
              padding: const EdgeInsets.fromLTRB(20, 16, 20, 24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  // Scroll hint
                  if (!_scrolledToEnd)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.keyboard_arrow_down_rounded,
                              color: muted, size: 16),
                          const SizedBox(width: 4),
                          Text('Scroll down to read all terms',
                              style: TextStyle(fontSize: 12, color: muted)),
                        ],
                      ),
                    ),

                  // Checkbox row
                  GestureDetector(
                    onTap: () => setState(() => _agreed = !_agreed),
                    child: Row(children: [
                      AnimatedContainer(
                        duration: const Duration(milliseconds: 200),
                        width: 22, height: 22,
                        decoration: BoxDecoration(
                          color: _agreed ? accent : Colors.transparent,
                          borderRadius: BorderRadius.circular(6),
                          border: Border.all(
                              color: _agreed ? accent : border, width: 2),
                        ),
                        child: _agreed
                            ? const Icon(Icons.check_rounded,
                                color: Colors.white, size: 14)
                            : null,
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: RichText(
                          text: TextSpan(
                            style: TextStyle(
                                fontSize: 13, color: text2, height: 1.4),
                            children: [
                              const TextSpan(
                                  text: 'I have read and agree to the '),
                              TextSpan(
                                text: 'Terms & Conditions',
                                style: TextStyle(
                                    color: accent,
                                    fontWeight: FontWeight.w600),
                              ),
                              const TextSpan(text: ' of Titan Studio PRO'),
                            ],
                          ),
                        ),
                      ),
                    ]),
                  ),

                  const SizedBox(height: 16),

                  // Agree button
                  GestureDetector(
                    onTap: _agreed ? _handleAccept : null,
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 200),
                      height: 52,
                      decoration: BoxDecoration(
                        gradient: _agreed
                            ? LinearGradient(
                                colors: isDark
                                    ? [cGreen, cGreen2]
                                    : [cLAccent, cLAccent2],
                                begin: Alignment.centerLeft,
                                end: Alignment.centerRight,
                              )
                            : null,
                        color: _agreed ? null : (isDark ? cBg2 : cLCard2),
                        borderRadius: BorderRadius.circular(14),
                        border: _agreed
                            ? null
                            : Border.all(color: border),
                        boxShadow: _agreed
                            ? [
                                BoxShadow(
                                    color: accent.withOpacity(0.35),
                                    blurRadius: 16,
                                    offset: const Offset(0, 4))
                              ]
                            : [],
                      ),
                      child: Center(
                        child: Text(
                          'Agree & Continue',
                          style: TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.w700,
                            color: _agreed ? Colors.white : muted,
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }
}

// ── Section widget ────────────────────────────────────────────
class _Section extends StatelessWidget {
  final String number;
  final String title;
  final String content;
  final bool isDark;
  final Color textColor;
  final Color text2;
  final Color accent;
  const _Section({
    required this.number,
    required this.title,
    required this.content,
    required this.isDark,
    required this.textColor,
    required this.text2,
    required this.accent,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(crossAxisAlignment: CrossAxisAlignment.center, children: [
            Container(
              width: 26, height: 26,
              decoration: BoxDecoration(
                color: accent.withOpacity(0.15),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Center(
                child: Text(number,
                    style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w800,
                        color: accent)),
              ),
            ),
            const SizedBox(width: 10),
            Text(title,
                style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w700,
                    color: textColor)),
          ]),
          const SizedBox(height: 8),
          Padding(
            padding: const EdgeInsets.only(left: 36),
            child: Text(content,
                style: TextStyle(
                    fontSize: 13, color: text2, height: 1.6)),
          ),
        ],
      ),
    );
  }
}
