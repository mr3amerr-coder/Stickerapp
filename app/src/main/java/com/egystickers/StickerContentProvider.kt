package com.egystickers

import android.content.ContentProvider
import android.content.ContentValues
import android.content.UriMatcher
import android.content.res.AssetFileDescriptor
import android.database.Cursor
import android.database.MatrixCursor
import android.net.Uri

/** Implements WhatsApp's Sticker Contract so WhatsApp can read our pack. */
class StickerContentProvider : ContentProvider() {
    private lateinit var matcher: UriMatcher
    private lateinit var authority: String
    private val pack by lazy { loadPack(context!!) }

    override fun onCreate(): Boolean {
        authority = context!!.packageName + ".stickercontentprovider"
        matcher = UriMatcher(UriMatcher.NO_MATCH).apply {
            addURI(authority, "metadata", 1)
            addURI(authority, "metadata/*", 2)
            addURI(authority, "stickers/*", 3)
            addURI(authority, "stickers_asset/*/*", 4)
        }
        return true
    }

    override fun query(uri: Uri, p: Array<String>?, s: String?, a: Array<String>?, o: String?): Cursor =
        when (matcher.match(uri)) {
            1, 2 -> MatrixCursor(arrayOf(
                "sticker_pack_identifier", "sticker_pack_name", "sticker_pack_publisher", "sticker_pack_icon",
                "android_play_store_link", "ios_app_download_link", "sticker_pack_publisher_email",
                "sticker_pack_publisher_website", "sticker_pack_privacy_policy_website",
                "sticker_pack_license_agreement_website", "image_data_version",
                "whatsapp_will_not_cache_stickers", "animated_sticker_pack"
            )).apply { addRow(arrayOf(pack.id, pack.name, pack.publisher, pack.tray, "", "", "", "", "", "", "1", 0, 1)) }
            3 -> MatrixCursor(arrayOf("sticker_file_name", "sticker_emoji", "sticker_accessibility_text")).apply {
                pack.stickers.forEach { addRow(arrayOf(it.file, it.emojis, it.label)) }
            }
            else -> throw IllegalArgumentException("Unknown URI: $uri")
        }

    override fun openAssetFile(uri: Uri, mode: String): AssetFileDescriptor? {
        if (matcher.match(uri) != 4) return null
        val seg = uri.pathSegments
        if (seg[seg.size - 2] != pack.id) return null
        val file = seg.last()
        val path = if (file == pack.tray) file else "stickers/$file"
        return context!!.assets.openFd(path)
    }

    override fun getType(uri: Uri): String = when (matcher.match(uri)) {
        1 -> "vnd.android.cursor.dir/vnd.$authority.metadata"
        2 -> "vnd.android.cursor.item/vnd.$authority.metadata"
        3 -> "vnd.android.cursor.dir/vnd.$authority.stickers"
        4 -> if (uri.lastPathSegment!!.endsWith(".png")) "image/png" else "image/webp"
        else -> throw IllegalArgumentException("Unknown URI: $uri")
    }

    override fun insert(uri: Uri, v: ContentValues?): Uri? = null
    override fun update(uri: Uri, v: ContentValues?, s: String?, a: Array<String>?) = 0
    override fun delete(uri: Uri, s: String?, a: Array<String>?) = 0
}
