import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'screens/splash_screen.dart';
import 'screens/login_screen.dart';
import 'screens/studio_screen.dart';
import 'services/auth_service.dart';
import 'services/admin_service.dart';
import 'utils/constants.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  try {
    await Firebase.initializeApp()
        .timeout(const Duration(seconds: 10));
  } catch (e) {
    debugPrint('Firebase init error: $e');
  }

  SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp]);
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.light,
    systemNavigationBarColor: Color(0xFF0B0F19),
    systemNavigationBarIconBrightness: Brightness.light,
  ));
  runApp(const TitanApp());
}

class TitanApp extends StatelessWidget {
  const TitanApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Titan Studio PRO',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        colorScheme: ColorScheme.fromSeed(
          seedColor: cGreen,
          brightness: Brightness.dark,
        ).copyWith(
          surface: cBg,
          onSurface: cText,
          primary: cGreen,
          secondary: cGreen2,
        ),
        scaffoldBackgroundColor: cBg,
        appBarTheme: const AppBarTheme(
          backgroundColor: cBg2,
          foregroundColor: cText,
          elevation: 0,
        ),
        sliderTheme: SliderThemeData(
          activeTrackColor: cGreen,
          inactiveTrackColor: cBorder,
          thumbColor: cGreen,
          overlayColor: cGreen.withOpacity(0.15),
          trackHeight: 3,
        ),
        switchTheme: SwitchThemeData(
          thumbColor: WidgetStateProperty.resolveWith((s) =>
            s.contains(WidgetState.selected) ? cBg : cMuted),
          trackColor: WidgetStateProperty.resolveWith((s) =>
            s.contains(WidgetState.selected) ? cGreen : cBorder),
        ),
      ),
      home: const _AuthGate(),
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
  User? _user;

  // Periodic timer — checks maintenance every 20 sec while app is open
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

    _user = FirebaseAuth.instance.currentUser;

    if (!mounted) return;
    setState(() => _inactiveLogout = loggedOut);

    // Start periodic maintenance check (every 20 seconds)
    _maintenanceTimer?.cancel();
    _maintenanceTimer = Timer.periodic(
      const Duration(seconds: 20),
      (_) => _checkMaintenance(),
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

    // Maintenance mode — show full screen message
    if (_maintenance) {
      return Scaffold(
        backgroundColor: cBg,
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  width: 80, height: 80,
                  decoration: BoxDecoration(
                    color: cRed.withOpacity(0.1),
                    shape: BoxShape.circle,
                    border: Border.all(color: cRed.withOpacity(0.4)),
                  ),
                  child: const Icon(Icons.build_circle_rounded, color: cRed, size: 40),
                ),
                const SizedBox(height: 24),
                const Text('Under Maintenance',
                    style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: cText)),
                const SizedBox(height: 12),
                Text(_maintenanceMsg,
                    textAlign: TextAlign.center,
                    style: const TextStyle(fontSize: 14, color: cText2)),
                const SizedBox(height: 32),
                GestureDetector(
                  onTap: _checkMaintenance,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                    decoration: BoxDecoration(
                      gradient: kNeonGradient,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Text('Try Again',
                        style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700)),
                  ),
                ),
              ],
            ),
          ),
        ),
      );
    }

    final user = FirebaseAuth.instance.currentUser;
    if (user != null && !_inactiveLogout) {
      return const StudioScreen();
    }
    return LoginScreen(showInactiveMessage: _inactiveLogout);
  }
}
