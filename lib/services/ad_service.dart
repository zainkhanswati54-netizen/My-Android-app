import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';
import 'admin_service.dart';

// ═══════════════════════════════════════════════════════
//  AD SERVICE v1.1  (google_mobile_ads 5.x compatible)
// ═══════════════════════════════════════════════════════

class AdService {
  static AdminAdData? _config;
  static bool _initialized = false;
  static int  _generationCount = 0;

  // ── Google Official Test IDs ─────────────────────────
  static const _testBannerId       = 'ca-app-pub-3940256099942544/6300978111';
  static const _testInterstitialId = 'ca-app-pub-3940256099942544/1033173712';
  static const _testRewardedId     = 'ca-app-pub-3940256099942544/5224354917';

  // ── YOUR REAL AdMob IDs ──────────────────────────────
  static const _realBannerId       = 'ca-app-pub-9019700052213764/7651237804';
  static const _realInterstitialId = 'ca-app-pub-9019700052213764/7268094427';
  static const _realRewardedId     = 'ca-app-pub-9019700052213764/6777139837';

  static InterstitialAd? _interstitialAd;
  static RewardedAd?     _rewardedAd;

  // ══════════════════════════════════════════════════════
  //  INITIALIZE
  // ══════════════════════════════════════════════════════
  static Future<void> initialize() async {
    if (_initialized) return;
    try {
      _config = await AdminService.getAdData();
      if (_config?.adsEnabled == true) {
        await MobileAds.instance.initialize();
        _initialized = true;
        _preloadInterstitial();
        _preloadRewarded();
      }
    } catch (_) {}
  }

  static Future<void> refreshConfig() async {
    try {
      _config = await AdminService.getAdData();
      if (_config?.adsEnabled == true && !_initialized) {
        await MobileAds.instance.initialize();
        _initialized = true;
      }
    } catch (_) {}
  }

  // ══════════════════════════════════════════════════════
  //  BANNER AD WIDGET
  // ══════════════════════════════════════════════════════
  static Widget? buildBannerAd() {
    if (!_adsActive || _config?.bannerEnabled != true) return null;

    // Use real ID directly if config bannerAdUnitId is empty
    final unitId = _isTest
        ? _testBannerId
        : (_config!.bannerAdUnitId.isNotEmpty
            ? _config!.bannerAdUnitId
            : _realBannerId);

    if (unitId.isEmpty) return null;

    final banner = BannerAd(
      adUnitId: unitId,
      size:     AdSize.banner,
      request:  const AdRequest(),
      listener: BannerAdListener(
        onAdFailedToLoad: (ad, _) => ad.dispose(),
      ),
    )..load();

    return SizedBox(
      height: 50,
      child: AdWidget(ad: banner),
    );
  }

  // ══════════════════════════════════════════════════════
  //  INTERSTITIAL
  // ══════════════════════════════════════════════════════
  static Future<void> onGenerationComplete() async {
    if (!_adsActive || _config?.interstitialEnabled != true) return;
    _generationCount++;
    final freq = _config?.interstitialFrequency ?? 5;
    if (_generationCount % freq == 0) {
      await showInterstitial();
    }
  }

  static Future<void> showInterstitial() async {
    if (!_adsActive || _config?.interstitialEnabled != true) return;
    if (_interstitialAd == null) {
      await _preloadInterstitial();
      await Future.delayed(const Duration(milliseconds: 600));
    }
    _interstitialAd?.show();
    _interstitialAd = null;
    _preloadInterstitial();
  }

  static Future<void> _preloadInterstitial() async {
    if (!_adsActive) return;
    final unitId = _isTest
        ? _testInterstitialId
        : (_config?.interstitialAdUnitId.isNotEmpty == true
            ? _config!.interstitialAdUnitId
            : _realInterstitialId);
    if (unitId.isEmpty) return;
    try {
      await InterstitialAd.load(
        adUnitId: unitId,
        request:  const AdRequest(),
        adLoadCallback: InterstitialAdLoadCallback(
          onAdLoaded:       (ad) => _interstitialAd = ad,
          onAdFailedToLoad: (_) => _interstitialAd = null,
        ),
      );
    } catch (_) {}
  }

  // ══════════════════════════════════════════════════════
  //  REWARDED
  // ══════════════════════════════════════════════════════
  static Future<bool> showRewarded({
    required void Function(int extraRequests) onRewarded,
  }) async {
    if (!_adsActive || _config?.rewardedEnabled != true) return false;
    if (_rewardedAd == null) {
      await _preloadRewarded();
      await Future.delayed(const Duration(milliseconds: 600));
    }
    if (_rewardedAd == null) return false;
    _rewardedAd!.show(
      onUserEarnedReward: (ad, reward) => onRewarded(5),
    );
    _rewardedAd = null;
    _preloadRewarded();
    return true;
  }

  static Future<void> _preloadRewarded() async {
    if (!_adsActive) return;
    final unitId = _isTest
        ? _testRewardedId
        : (_config?.rewardedAdUnitId.isNotEmpty == true
            ? _config!.rewardedAdUnitId
            : _realRewardedId);
    if (unitId.isEmpty) return;
    try {
      await RewardedAd.load(
        adUnitId: unitId,
        request:  const AdRequest(),
        rewardedAdLoadCallback: RewardedAdLoadCallback(
          onAdLoaded:       (ad) => _rewardedAd = ad,
          onAdFailedToLoad: (_) => _rewardedAd = null,
        ),
      );
    } catch (_) {}
  }

  static bool get _adsActive => _initialized && (_config?.adsEnabled == true);
  static bool get _isTest    => _config?.testMode == true || kDebugMode;
}
