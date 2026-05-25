package com.titanstudio.pro

import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import android.media.MediaScannerConnection

class MainActivity : FlutterActivity() {

  override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
    super.configureFlutterEngine(flutterEngine)

    MethodChannel(
      flutterEngine.dartExecutor.binaryMessenger,
      "titan/media_scan"
    ).setMethodCallHandler { call, result ->
      if (call.method == "scanFile") {
        val path = call.argument<String>("path")
        if (path != null) {
          MediaScannerConnection.scanFile(this, arrayOf(path), null) { _, _ -> }
          result.success(null)
        } else {
          result.error("INVALID_PATH", "Path is null", null)
        }
      } else {
        result.notImplemented()
      }
    }
  }
}
