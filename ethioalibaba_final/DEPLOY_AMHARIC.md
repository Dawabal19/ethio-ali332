############################################
# DEPLOY — GitHub + Render (ነጻ 24/7)
#  Bot-ህ ሁልጊዜ online · Order ሲደረግ ወዲያውኑ ወደ Telegram-ህ ይመጣል
############################################

⚠️ አስፈላጊ ሀሳብ: GitHub ራሱ ቦትን አያሄድም (ኮድ ብቻ ያዛል)።
   GitHub + Render ብትጠቀም Render ነው app-ውን የሚያሄደው — በነጻ!

==================================================
STEP 1 — GitHub repo ፍጠር (2 ደቂቃ)
==================================================
1. https://github.com → Sign up (ነጻ)
2. ላይ ቀኝ → "+" → "New repository"
3. ስም:  ethioalibaba  → Public → "Create repository"
4. "uploading an existing file" link ጠቅ አድርግ
5. እነዚህን files ብቻ drag-drop አድርግ (ZIP አይደለም — unzip አድርገህ!):
      app.py
      Procfile
      requirements.txt
      .gitignore
      wsgi.py
      (START_HERE.txt / README.md — optional)
   ❌ ".env" አይጫን! (ቶክን-ህ ለሁሉም ይታያል — Render ላይ እንጂ)
6. "Commit changes" ጠቅ አድርግ

==================================================
STEP 2 — Render.com account (1 ደቂቃ)
==================================================
1. https://render.com → "Get Started" → **Sign up with GitHub** (ቀላል!)
2. GitHub ጋር ፍቀድ (Authorize)

==================================================
STEP 3 — Web Service ፍጠር (3 ደቂቃ)
==================================================
1. Render dashboard → "New +" → "Web Service"
2. Repo-ህን ("ethioalibaba") ምረጥ → Connect
3. እነዚህ ያረጋግጥ:
      Name:            ethioalibaba  (ወይም ሌላ)
      Region:          Oregon (US West)
      Branch:          main
      Build Command:   pip install -r requirements.txt
      Start Command:   gunicorn app:app
4. Instance Type: **Free** ← አስፈላጊ!
5. "Environment Variables" (ቁልፍ!) — እነዚህን ጨምር (New Environment Variable):

      TELEGRAM_BOT_TOKEN      = 8986314898:AAEgiwry5TOIxT1c52qr5y4g2NKl_dRmDAc
      TELEGRAM_CHAT_ID        = 1931570585        ← የእርስዎ ID (@userinfobot ጽፈው ያረጋግጡ!)
      TELEGRAM_BOT_USERNAME   = ethioalibaba_bot
      PUBLIC_URL              = https://ethioalibaba.onrender.com
      SECRET_KEY              = ethioalibaba-secret-key-2026

   (↑ PUBLIC_URL: Name-ህ ምን ስትል እንደፈጠርክ እንዲህ ይሆናል:
      https://[NAME].onrender.com — ምሳሌ: https://ethioalibaba.onrender.com)
6. "Create Web Service" → Deploy ይጀምራል (3-5 ደቂቃ ቆይ)

==================================================
STEP 4 — ቦትህን ፈትሽ! ✅
==================================================
1. Render log ላይ ይህን መፈለግ:  🔗 Webhook auto-set → ቢወርድ ማለት ቦት-ህ online ነው!
2. https://[NAME].onrender.com ክፈት → website-ህ ይታያል
3. Telegram → @ethioalibaba_bot → /start → መልስ ይመጣል!
4. Website ላይ order አድርግ → ወዲያውኑ ቦት-ህ ላይ ይደርስሃል! 🛒

==================================================
⚠️ FREE tier ማስታወሻ
==================================================
• Render free 15 ደቂቃ ባዶ ሲሆን ያልቃል → የመጀመሪያ request ዘገየ ሊሆን ይችላል (1 ደቂቃ)
• ይሄ normal ነው — Telegram webhook retry ያደርጋል ስለዚህ መልእክት አይጠፋም
• ማስታወሻ: ወደ ቦትህ /start ከጻፉ Bot free instance ይነቃል

==================================================
TROUBLESHOOTING
==================================================
• "Build failed"? → log ላይ ምን እንደተሳሳተ ተመልከት (ብዙው ጊዜ typing ስህተት)
• Bot መልስ የለው? → PUBLIC_URL ትክክል መሆኑን አረጋግጥ (https:// እና .onrender.com)
• Order አልመጣም? → TELEGRAM_CHAT_ID = የእርስዎ Telegram ID መሆኑን አረጋግጥ
• Website error? → Render → Logs ክፈት እና error-ውን ላክልኝ
