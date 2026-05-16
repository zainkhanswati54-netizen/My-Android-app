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

  // Firebase init + persistence (auto login)
  await Firebase.initializeApp();
  await FirebaseAuth.instance.setPersistence(Persistence.LOCAL);

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
  bool _splashDone = false;
  bool _checking = true;
  bool _inactiveLogout = false;

  @override
  void initState() {
    super.initState();
    _init();
  }

  Future<void> _init() async {
    await Future.delayed(const Duration(milliseconds: 2500));
    if (!mounted) return;
    setState(() => _splashDone = true);

    // 7 din inactive check
    final loggedOut = await AuthService.checkInactiveLogout();
    if (!mounted) return;
    setState(() {
      _inactiveLogout = loggedOut;
      _checking = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (!_splashDone) return const SplashScreen(autoNavigate: false);

    if (_checking) {
      return const Scaffold(
        backgroundColor: Color(0xFF0A0F0D),
        body: Center(
            child: CircularProgressIndicator(color: Color(0xFF10B981))),
      );
    }

    return StreamBuilder<User?>(
      stream: FirebaseAuth.instance.authStateChanges(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Scaffold(
            backgroundColor: Color(0xFF0A0F0D),
            body: Center(
                child: CircularProgressIndicator(color: Color(0xFF10B981))),
          );
        }

        // Auto login — agar user logged in hai aur inactive nahi
        if (snapshot.hasData && snapshot.data != null && !_inactiveLogout) {
          return const StudioScreen();
        }

        return LoginScreen(showInactiveMessage: _inactiveLogout);
      },
    );
  }
}
