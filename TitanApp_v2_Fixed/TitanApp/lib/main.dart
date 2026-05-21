import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'screens/splash_screen.dart';
import 'screens/login_screen.dart';
import 'screens/studio_screen.dart';
import 'services/auth_service.dart';
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
  // Obsidian Neon system chrome
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.light,
    systemNavigationBarColor: Color(0xFF0B0F19),   // Obsidian
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
  bool _ready = false;
  bool _inactiveLogout = false;

  @override
  void initState() {
    super.initState();
    _init();
  }

  Future<void> _init() async {
    // ✅ FIX: 2000ms → 1000ms for faster startup
    await Future.delayed(const Duration(milliseconds: 1000));
    bool loggedOut = false;
    try {
      loggedOut = await AuthService.checkInactiveLogout()
          .timeout(const Duration(seconds: 5));
    } catch (_) {}

    if (!mounted) return;
    setState(() {
      _inactiveLogout = loggedOut;
      _ready = true;
    });
  }

  @override
  Widget build(BuildContext context) {
    // Jab tak _init() complete nahi hoti, SplashScreen dikhao
    if (!_ready) return const SplashScreen(autoNavigate: false);

    return StreamBuilder<User?>(
      stream: FirebaseAuth.instance.authStateChanges(),
      builder: (context, snapshot) {
        // ✅ FIX: ConnectionState.waiting mein blank screen ki jagah
        //         SplashScreen dikhao — koi bhi blank/flicker nahi aayega
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const SplashScreen(autoNavigate: false);
        }
        if (snapshot.hasData && !_inactiveLogout) return const StudioScreen();
        return LoginScreen(showInactiveMessage: _inactiveLogout);
      },
    );
  }
}
