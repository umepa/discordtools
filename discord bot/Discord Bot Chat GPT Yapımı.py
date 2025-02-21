import discord
import os
from discord.ext import commands
import random
import asyncio

# Gelişmiş intentler
intents = discord.Intents.default()
intents.messages = True  
intents.message_content = True  
intents.voice_states = True  # Sesli kanal için gerekli
intents.guilds = True  # Sunucu bilgisi için gerekli
intents.members = True  # Üye bilgisi için gerekli

# Botu başlat
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ {bot.user} olarak giriş yaptım!')

# ✅ **Selamlaşma ve Durum Yanıtları**
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    msg = message.content.lower()

    # Selamlaşmalar
    if msg == "sa":
        await message.channel.send("as")
    elif msg == "selam":
        await message.channel.send("Aleyküm selam!")

    # Durum Yanıtları (Türkçe)
    elif msg in ["nasılsın", "nasılsınız"]:
        await message.channel.send("İyiyim, sen nasılsın?")
    
    # Durum Yanıtları (İngilizce)
    elif msg in ["how are you", "how are u"]:
        await message.channel.send("I'm fine, how about you?")
    
    # Küfürlü kelime var mı kontrolü
    küfürlü_kelime = ["oe", "amk", "sg"]  # Buraya küfürlü kelimeleri ekleyebilirsiniz.
    if any(küfür in msg for küfür in küfürlü_kelime):
        # Küfürlü mesajı siliyoruz
        await message.delete()
        
        # Kullanıcıya uyarı gönderiyoruz
        uyarı_mesajı = await message.channel.send(f"{message.author.mention}, Bu yazıyı yazamazsınız!")

        # 5 saniye sonra uyarıyı siliyoruz
        await asyncio.sleep(5)
        await uyarı_mesajı.delete()

    # Komutları çalıştırmaya devam et
    await bot.process_commands(message)

# ✅ **Sesli Kanala Girme Komutu**
@bot.command()
async def gir(ctx):
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send("✅ Sesli kanala girdim!")
    else:
        await ctx.send("❌ Sesli bir kanalda değilsin!")

# ✅ **Sesli Kanaldan Çıkma Komutu**
@bot.command()
async def cik(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("❌ Sesli kanaldan çıktım!")
    else:
        await ctx.send("❌ Zaten bir sesli kanalda değilim!")

# ✅ **Rastgele Yanıt Veren Komut**
yanitlar = ["Evet", "Hayır", "Bilmiyorum", "Kesinlikle!", "Belki", "Sanmıyorum"]

@bot.command()
async def sor(ctx):
    yanit = random.choice(yanitlar)
    await ctx.send(yanit)

# ✅ **Şaka Komutu**
@bot.command()
async def şaka(ctx):
    şakalar = [
        "Neden tavuk karşıya geçmek istedi? Çünkü diğer tarafta daha iyi bir hayat vardı!",
        "Bir karpuz neden üzgündü? Çünkü kabuğu vardı!",
        "Bir dondurma neden soğuktu? Çünkü serinlikti!"
    ]
    şaka = random.choice(şakalar)
    await ctx.send(şaka)

# ✅ **Taş-Kağıt-Makas Komutu**
@bot.command()
async def taşkgtmks(ctx):
    seçenekler = ["Taş", "Kağıt", "Makas"]
    bot_seçim = random.choice(seçenekler)
    await ctx.send(f"Bot seçimi: {bot_seçim}")
    
    def check(msg):
        return msg.author == ctx.author and msg.content.lower() in ["taş", "kağıt", "makas"]

    await ctx.send("Taş, Kağıt, Makas! Seçiminizi yapın!")

    try:
        msg = await bot.wait_for('message', check=check, timeout=30.0)
    except asyncio.TimeoutError:
        return await ctx.send("Zaman aşımına uğradınız! Lütfen daha hızlı yanıt verin.")
    
    kullanıcı_seçim = msg.content.lower()

    if kullanıcı_seçim == bot_seçim.lower():
        await ctx.send(f"Beraberlik! Hem sen hem ben {bot_seçim} seçtik.")
    elif (kullanıcı_seçim == "taş" and bot_seçim == "Makas") or \
         (kullanıcı_seçim == "kağıt" and bot_seçim == "Taş") or \
         (kullanıcı_seçim == "makas" and bot_seçim == "Kağıt"):
        await ctx.send(f"Tebrikler, kazandın! {kullanıcı_seçim.capitalize()} {bot_seçim} karşısında kazandı.")
    else:
        await ctx.send(f"Üzgünüm, kaybettin! {bot_seçim} {kullanıcı_seçim} karşısında kazandı.")

# ✅ **Yönetici Yardım Menüsü**
@bot.command()
async def admin(ctx):
    # Yalnızca yönetici yetkisi olanlar kullanabilir
    if ctx.author.guild_permissions.administrator:
        admin_yardim = """
        **Yönetici Yardım Menüsü:**
        **!temizle** - Mevcut kanalı siler ve yeniden oluşturur
        """
        await ctx.send(admin_yardim)
    else:
        await ctx.send("❌ Bu komutu kullanmaya yetkiniz yok!")

# ✅ **Bot Ekleme Filtresi** - Sunucu sahibinden başka kimse bot ekleyemez
@bot.event
async def on_guild_update(before, after):
    # Sunucu sahibi dışındaki kişiler bot ekleyemez
    if before.owner != after.owner:
        for entry in after.audit_logs(limit=1, action=discord.AuditLogAction.bot_add):
            bot_ekleyen = entry.user
            eklenen_bot = entry.target

            # Eğer botu ekleyen kişi sunucu sahibi değilse, botu at ve kişiyi uyar
            if bot_ekleyen != after.owner:
                await after.kick(eklenen_bot)
                channel = after.system_channel or after.text_channels[0]  # Uyarıyı gönderecek kanal
                await channel.send(f"{bot_ekleyen.mention}, Bot ekleyemezsin! {eklenen_bot} botu sunucudan atıldı.")
                break

# ✅ **Temizleme Komutu** (Yalnızca yöneticilere özel)
@bot.command()
async def temizle(ctx):
    # Yalnızca yönetici yetkisi olanlar kullanabilir
    if ctx.author.guild_permissions.administrator:
        # Mevcut kanal bilgilerini alıyoruz
        kanal = ctx.channel

        # Kanaldaki tüm mesajları siliyoruz
        await kanal.purge()

        # Kanalı siliyoruz ve tekrar oluşturuyoruz
        await kanal.delete()
        await ctx.guild.create_text_channel(kanal.name)

        # Kullanıcıya bilgi veriyoruz
        await ctx.send(f"✅ {kanal.name} kanalı temizlendi ve yeniden oluşturuldu!")
    else:
        await ctx.send("❌ Bu komutu kullanmaya yetkiniz yok!")

# ✅ **Yardım Komutu** (Admin komutları hariç)
@bot.command()
async def yardım(ctx):
    # Yardım menüsü (admin komutları hariç)
    genel_yardim = """
    **Genel Yardım Menüsü:**
    **!gir** - Sesli kanala girer
    **!cik** - Sesli kanaldan çıkar
    **!sor** - Rastgele yanıt verir
    **!şaka** - Bot şaka yapar
    **!taşkgtmks** - Taş, Kağıt, Makas oyunu oynar
    """
    await ctx.send(genel_yardim)

# Bot Tokenini Çalıştır
bot.run("Burayı silip tokeninizi yazın")
