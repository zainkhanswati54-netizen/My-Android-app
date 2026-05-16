import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'screens/splash_screen.dart';
import 'screens/login_screen.dart';
import 'screens/studio_screen.dart';
import 'utils/constants.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
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
        fontFamily: 'Inter',
        appBarTheme: const AppBarTheme(
          backgroundColor: cBg2,
          foregroundColor: cText,
          elevation: 0,
          titleTextStyle: TextStyle(
            fontSize: 18, fontWeight: FontWeight.w800, color: cText,
          ),
        ),
      ),
      home: const _AuthGate(),
    );
  }
}

// ── Auth Gate: decide which screen to show ────────────────────
// Splash → check auth → Login (if not logged in) OR Studio (if logged in)
class _AuthGate extends StatefulWidget {
  const _AuthGate();
  @override
  State<_AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<_AuthGate> {
  bool _splashDone = false;

  @override
  void initState() {
    super.initState();
    // Show splash for 2.5 seconds then check auth
    Future.delayed(const Duration(milliseconds: 2500), () {
      if (mounted) setState(() => _splashDone = true);
    });
  }

  @override
  Widget build(BuildContext context) {
    if (!_splashDone) return const SplashScreen(autoNavigate: false);

    return StreamBuilder<User?>(
      stream: FirebaseAuth.instance.authStateChanges(),
      builder: (context, snapshot) {
        // Still checking
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Scaffold(
            backgroundColor: Color(0xFF0A0F0D),
            body: Center(
              child: CircularProgressIndicator(color: Color(0xFF10B981)),
            ),
          );
        }
        // Logged in → Studio
        if (snapshot.hasData && snapshot.data != null) {
          return const StudioScreen();
        }
        // Not logged in → Login
        return const LoginScreen();
      },
    );
  }
}
