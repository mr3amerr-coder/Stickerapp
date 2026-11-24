package com.egystickers

import android.content.Context
import org.json.JSONObject

data class Sticker(val file: String, val emojis: String, val label: String)
data class Pack(val id: String, val name: String, val publisher: String, val tray: String, val stickers: List<Sticker>)

/** Reads assets/pack.json (written by tools/make_stickers.py). Add stickers by editing that file. */
fun loadPack(c: Context): Pack {
    val o = JSONObject(c.assets.open("pack.json").bufferedReader().use { it.readText() })
    val a = o.getJSONArray("stickers")
    val list = (0 until a.length()).map {
        val s = a.getJSONObject(it)
        val e = s.getJSONArray("emojis")
        Sticker(s.getString("file"), (0 until e.length()).joinToString(",") { i -> e.getString(i) }, s.getString("label"))
    }
    return Pack(o.getString("id"), o.getString("name"), o.getString("publisher"), o.getString("tray"), list)
}
