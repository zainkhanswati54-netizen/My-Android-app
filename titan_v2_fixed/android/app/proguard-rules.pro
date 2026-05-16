# Flutter
-keep class io.flutter.** { *; }
-keep class io.flutter.plugins.** { *; }
-dontwarn io.flutter.**

# Keep all app classes
-keep class com.zainkhan.titanstudiopro.** { *; }

# just_audio
-keep class com.google.android.exoplayer2.** { *; }
-dontwarn com.google.android.exoplayer2.**

# General
-keepattributes *Annotation*
-keepattributes SourceFile,LineNumberTable
-dontwarn javax.**
-dontwarn org.conscrypt.**
