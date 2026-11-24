plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}
android {
    namespace = "com.egystickers"
    compileSdk = 34
    defaultConfig {
        applicationId = "com.egystickers.app"   // also the base of the content-provider authority
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }
    // WhatsApp reads stickers through openFd(), so assets must stay uncompressed
    androidResources { noCompress += listOf("webp", "png", "json") }
    compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
    kotlinOptions { jvmTarget = "17" }
}
