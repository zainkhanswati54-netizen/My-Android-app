import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../utils/constants.dart';

// ═══════════════════════════════════════════════════════
//  SUSPENDED SCREEN
//  Shows when admin has banned/suspended a user account.
// ═══════════════════════════════════════════════════════

class SuspendedScreen extends StatelessWidget {
  final String reason;
  const SuspendedScreen({super.key, this.reason = ''});

  @override
  Widget build(BuildContext context) {
    final hasReason = reason.trim().isNotEmpty;

    return Scaffold(
      backgroundColor: cBg,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // ── Icon ──
              Container(
                width: 96,
                height: 96,
                decoration: BoxDecoration(
                  color: cRed.withOpacity(0.1),
                  shape: BoxShape.circle,
                  border: Border.all(color: cRed.withOpacity(0.45), width: 1.5),
                  boxShadow: [
                    BoxShadow(
                      color: cRed.withOpacity(0.2),
                      blurRadius: 32,
                      spreadRadius: 4,
                    ),
                  ],
                ),
                child: const Icon(
                  Icons.gavel_rounded,
                  color: cRed,
                  size: 44,
                ),
              ),

              const SizedBox(height: 28),

              // ── Title ──
              const Text(
                'Account Suspended',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.w900,
                  color: cText,
                  letterSpacing: -0.5,
                ),
                textAlign: TextAlign.center,
              ),

              const SizedBox(height: 12),

              // ── Subtitle ──
              const Text(
                'Your account has been suspended by the administrator.',
                style: TextStyle(fontSize: 14, color: cText2, height: 1.5),
                textAlign: TextAlign.center,
              ),

              // ── Reason box (only if provided) ──
              if (hasReason) ...[
                const SizedBox(height: 20),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: cRed.withOpacity(0.06),
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: cRed.withOpacity(0.3)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(children: [
                        const Icon(Icons.info_outline_rounded,
                            color: cRed, size: 14),
                        const SizedBox(width: 6),
                        const Text(
                          'REASON',
                          style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.w800,
                            color: cRed,
                            letterSpacing: 1.5,
                          ),
                        ),
                      ]),
                      const SizedBox(height: 8),
                      Text(
                        reason.trim(),
                        style: const TextStyle(
                          fontSize: 13,
                          color: cText,
                          height: 1.5,
                        ),
                      ),
                    ],
                  ),
                ),
              ],

              const SizedBox(height: 32),

              // ── Contact info ──
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: cSurface,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: cBorder),
                ),
                child: const Row(children: [
                  Icon(Icons.mail_outline_rounded, color: cGreen, size: 18),
                  SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      'If you believe this is a mistake, please contact support.',
                      style: TextStyle(fontSize: 12, color: cText2, height: 1.4),
                    ),
                  ),
                ]),
              ),

              const SizedBox(height: 40),

              // ── Sign out button ──
              GestureDetector(
                onTap: () async {
                  await FirebaseAuth.instance.signOut();
                  if (context.mounted) {
                    Navigator.of(context).pushNamedAndRemoveUntil(
                        '/', (route) => false);
                  }
                },
                child: Container(
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  decoration: BoxDecoration(
                    color: cSurface,
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: cBorder),
                  ),
                  child: const Center(
                    child: Text(
                      'Sign Out',
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w700,
                        color: cText2,
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
