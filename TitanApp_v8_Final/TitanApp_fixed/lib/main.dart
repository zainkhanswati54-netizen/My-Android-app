import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'screens/splash_screen.dart';
import 'screens/login_screen.dart';
import 'screens/studio_screen.dart';
import 'screens/suspended_screen.dart';
import 'screens/admin_dashboard_screen.dart';
import 'services/auth_service.dart';
import 'services/admin_service.dart';
import 'services/ad_service.dart';
import 'utils/constants.dart';
import 'theme.dart';

// ── Global theme notifier ──
final ValueNotifier<ThemeMode> themeNotifier = ValueNotifier(ThemeMode.dark);

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  try {
    await Firebase.initializeApp()
        .timeout(const Duration(seconds: 10));
  } catch (e) {
    debugPrint('Firebase init error: $e');
  }

  // ── Initialize AdMob (reads config from Firebase) ──
  await AdService.initialize();

  SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp]);
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.dark,  // overridden per screen
  ));
  runApp(const TitanApp());
}

class TitanApp extends StatelessWidget {
  const TitanApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<ThemeMode>(
      valueListenable: themeNotifier,
      builder: (_, mode, __) => MaterialApp(
        title: 'Titan Studio PRO',
        debugShowCheckedModeBanner: false,
        themeMode: mode,
        theme: AppTheme.lightTheme,
        darkTheme: AppTheme.theme,
        home: const _AuthGate(),
        pageTransitionsTheme: const PageTransitionsTheme(
          builders: {
            TargetPlatform.android: CupertinoPageTransitionsBuilder(),
            TargetPlatform.iOS:     CupertinoPageTransitionsBuilder(),
          },
        ),
      ),
    );
  }
}

class _AuthGate extends StatefulWidget {
  const _AuthGate();
  @override
  State<_AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<_AuthGate> {
  bool _splashDone     = false;
  bool _inactiveLogout = false;
  bool _maintenance    = false;
  String _maintenanceMsg = 'App is under maintenance. Please check back later.';
  bool _suspended      = false;
  String _suspendReason = '';
  User? _user;

  Timer? _maintenanceTimer;

  @override
  void initState() {
    super.initState();
    _init();
  }

  @override
  void dispose() {
    _maintenanceTimer?.cancel();
    super.dispose();
  }

  Future<void> _init() async {
    bool loggedOut = false;
    try {
      loggedOut = await AuthService.checkInactiveLogout()
          .timeout(const Duration(seconds: 5));
    } catch (_) {}

    await _checkMaintenance();
    await _checkSuspension();

    _user = FirebaseAuth.instance.currentUser;

    // ── Refresh ad config after login ──
    if (_user != null) {
      AdService.refreshConfig();
    }

    if (!mounted) return;
    setState(() => _inactiveLogout = loggedOut);

    _maintenanceTimer?.cancel();
    _maintenanceTimer = Timer.periodic(
      const Duration(seconds: 20),
      (_) async {
        await _checkMaintenance();
        await _checkSuspension();
      },
    );
  }

  Future<void> _checkMaintenance() async {
    try {
      final m = await AdminService.getMaintenanceData()
          .timeout(const Duration(seconds: 8));
      if (mounted) {
        setState(() {
          _maintenance    = m.enabled;
          _maintenanceMsg = m.message;
        });
      }
    } catch (_) {}
  }

  Future<void> _checkSuspension() async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null) return;
      final data = await AdminService.getUserData(user.uid)
          .timeout(const Duration(seconds: 8));
      if (mounted) {
        setState(() {
          _suspended     = data['banned'] == true;
          _suspendReason = data['suspendReason'] ?? '';
        });
      }
    } catch (_) {}
  }

  void _onSplashComplete() {
    if (!mounted) return;
    setState(() => _splashDone = true);
  }

  @override
  Widget build(BuildContext context) {
    if (!_splashDone) {
      return SplashScreen(
        autoNavigate: false,
        onComplete: _onSplashComplete,
      );
    }

    if (_maintenance) {
      return _MaintenanceScreen(
        message: _maintenanceMsg,
        onTryAgain: _checkMaintenance,
      );
    }

    final user = FirebaseAuth.instance.currentUser;
    if (user != null && _suspended) {
      return SuspendedScreen(reason: _suspendReason);
    }
    if (user != null && !_inactiveLogout) {
      return const StudioScreen();
    }
    return LoginScreen(showInactiveMessage: _inactiveLogout);
  }
}

// ═══════════════════════════════════════════════════════
//  MAINTENANCE SCREEN
// ═══════════════════════════════════════════════════════

class _MaintenanceScreen extends StatefulWidget {
  final String message;
  final VoidCallback onTryAgain;
  const _MaintenanceScreen({required this.message, required this.onTryAgain});

  @override
  State<_MaintenanceScreen> createState() => _MaintenanceScreenState();
}

class _MaintenanceScreenState extends State<_MaintenanceScreen> {
  int _tapCount = 0;
  static const int _requiredTaps = 50;

  void _onIconTap() {
    setState(() => _tapCount++);
    if (_tapCount >= _requiredTaps) {
      _tapCount = 0;
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => const AdminDashboardScreen()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final remaining = _requiredTaps - _tapCount;
    return Scaffold(
      backgroundColor: cBg,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              GestureDetector(
                onTap: _onIconTap,
                child: Container(
                  width: 80, height: 80,
                  decoration: BoxDecoration(
                    color: cRed.withOpacity(0.1),
                    shape: BoxShape.circle,
                    border: Border.all(color: cRed.withOpacity(0.4)),
                  ),
                  child: const Icon(Icons.build_circle_rounded,
                      color: cRed, size: 40),
                ),
              ),
              const SizedBox(height: 24),
              const Text('Under Maintenance',
                  style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.w800,
                      color: cText)),
              const SizedBox(height: 12),
              Text(widget.message,
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 14, color: cText2)),
              if (_tapCount > 0) ...[
                const SizedBox(height: 16),
                Text(
                  '$remaining more...',
                  style: TextStyle(fontSize: 11, color: cMuted.withOpacity(0.5)),
                ),
              ],
              const SizedBox(height: 32),
              GestureDetector(
                onTap: widget.onTryAgain,
                child: Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 24, vertical: 12),
                  decoration: BoxDecoration(
                    gradient: kNeonGradient,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Text('Try Again',
                      style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w700)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
