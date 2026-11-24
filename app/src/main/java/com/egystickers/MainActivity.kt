package com.egystickers

import android.app.Activity
import android.content.ActivityNotFoundException
import android.content.Intent
import android.graphics.BitmapFactory
import android.graphics.ImageDecoder
import android.graphics.Typeface
import android.graphics.drawable.AnimatedImageDrawable
import android.graphics.drawable.GradientDrawable
import android.os.Build
import android.os.Bundle
import android.view.Gravity
import android.view.View
import android.widget.*

class MainActivity : Activity() {
    private lateinit var pack: Pack
    private val REQ = 200

    override fun onCreate(b: Bundle?) {
        super.onCreate(b)
        pack = loadPack(this)
        val dp = resources.displayMetrics.density
        fun px(v: Int) = (v * dp).toInt()
        fun card(color: Int, r: Int) = GradientDrawable().apply { setColor(color); cornerRadius = px(r).toFloat() }

        val col = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(px(16), px(32), px(16), px(24))
            layoutDirection = View.LAYOUT_DIRECTION_RTL
        }
        col.addView(TextView(this).apply {
            text = "🇪🇬 ستيكرز مصرية متحركة"; textSize = 24f; setTypeface(null, Typeface.BOLD); setTextColor(0xFF2A1D0E.toInt())
        })
        col.addView(TextView(this).apply {
            text = "${pack.stickers.size} ستيكر متحرك بدون خلفية — ضيفهم لواتساب بضغطة واحدة"
            textSize = 14f; setTextColor(0xFF7A6A55.toInt()); setPadding(0, px(4), 0, px(12))
        })
        col.addView(Button(this).apply {
            text = "➕ ضيف الباك لواتساب"; textSize = 17f; setTextColor(0xFF2A1D0E.toInt()); isAllCaps = false
            background = card(0xFFFFB92E.toInt(), 16)
            setOnClickListener { addToWhatsApp() }
        }, LinearLayout.LayoutParams(-1, px(56)).apply { bottomMargin = px(16) })

        val cell = (resources.displayMetrics.widthPixels - px(32)) / 3
        val grid = GridLayout(this).apply { columnCount = 3 }
        pack.stickers.forEach { s ->
            val iv = ImageView(this).apply {
                background = card(0xFFFFFFFF.toInt(), 16); setPadding(px(8), px(8), px(8), px(8))
                contentDescription = s.label; scaleType = ImageView.ScaleType.FIT_CENTER
            }
            preview(iv, "stickers/${s.file}")
            grid.addView(iv, GridLayout.LayoutParams().apply { width = cell - px(8); height = cell - px(8); setMargins(px(4), px(4), px(4), px(4)) })
        }
        col.addView(grid)
        setContentView(ScrollView(this).apply { setBackgroundColor(0xFFFFF8EC.toInt()); addView(col) })
    }

    private fun preview(iv: ImageView, path: String) {
        if (Build.VERSION.SDK_INT >= 28) {
            val d = ImageDecoder.decodeDrawable(ImageDecoder.createSource(assets, path))
            iv.setImageDrawable(d)
            (d as? AnimatedImageDrawable)?.apply { repeatCount = AnimatedImageDrawable.REPEAT_INFINITE; start() }
        } else iv.setImageBitmap(BitmapFactory.decodeStream(assets.open(path)))   // static preview on Android < 9
    }

    private fun addToWhatsApp() {
        val i = Intent("com.whatsapp.intent.action.ENABLE_STICKER_PACK").apply {
            putExtra("sticker_pack_id", pack.id)
            putExtra("sticker_pack_authority", "$packageName.stickercontentprovider")
            putExtra("sticker_pack_name", pack.name)
        }
        try { startActivityForResult(i, REQ) }
        catch (e: ActivityNotFoundException) { Toast.makeText(this, "واتساب مش متثبت على الموبايل", Toast.LENGTH_LONG).show() }
    }

    @Deprecated("Deprecated in Java")
    override fun onActivityResult(req: Int, res: Int, data: Intent?) {
        super.onActivityResult(req, res, data)
        if (req != REQ) return
        val err = data?.getStringExtra("validation_error")
        when {
            res == RESULT_OK -> Toast.makeText(this, "تمت إضافة الباك ✅ افتح واتساب ← ستيكرز", Toast.LENGTH_LONG).show()
            err != null -> Toast.makeText(this, "واتساب رفض الباك: $err", Toast.LENGTH_LONG).show()
        }
    }
}
