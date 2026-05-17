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

  // Firebase init with timeout
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
    systemNavigationBarColor: Color(0xFF0A0F0D),
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
        ).copyWith(surface: cBg, onSurface: cText),
        scaffoldBackgroundColor: cBg,
        appBarTheme: const AppBarTheme(
          backgroundColor: cBg2,
          foregroundColor: cText,
          elevation: 0,
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
    // Splash minimum 2 second dikhao
    await Future.delayed(const Duration(milliseconds: 2000));

    // 7 din inactive check — timeout ke saath
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
    // Splash screen jab tak ready nahi
    if (!_ready) {
      return const SplashScreen(autoNavigate: false);
    }

    return StreamBuilder<User?>(
      stream: FirebaseAuth.instance.authStateChanges(),
      builder: (context, snapshot) {
        // Max 3 second wait karo Firebase ke liye
        if (snapshot.connectionState == ConnectionState.waiting) {
          return FutureBuilder(
            future: Future.delayed(const Duration(seconds: 3)),
            builder: (ctx, snap) {
              if (snap.connectionState == ConnectionState.done) {
                // Timeout — login screen dikhao
                return const LoginScreen();
              }
              return const Scaffold(
                backgroundColor: Color(0xFF0A0F0D),
                body: Center(
                  child: CircularProgressIndicator(
                      color: Color(0xFF10B981)),
                ),
              );
            },
          );
        }

        // Logged in aur active → Studio
        if (snapshot.hasData && !_inactiveLogout) {
          return const StudioScreen();
        }

        // Login screen
        return LoginScreen(showInactiveMessage: _inactiveLogout);
      },
    );
  }
}
