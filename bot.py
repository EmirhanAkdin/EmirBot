import discord
from discord.ext import commands
import requests
import json
from yt_dlp import YoutubeDL
from discord import FFmpegPCMAudio

# FFmpeg'in tam yolunu belirtin, yola göre değişir
ffmpeg_path = r"C:\Users\akdin\Desktop\ffmpeg-7.1-essentials_build\bin\ffmpeg.exe"  # Burayı doğru şekilde yazın

# MP3 veya başka bir ses dosyasını oynatmak için:
audio_source = FFmpegPCMAudio('your_audio_file.mp3', executable=ffmpeg_path)

# Botun komut ön eki
bot = commands.Bot(command_prefix='*', intents=discord.Intents.all())

# Meme gönderme fonksiyonu
def get_meme():
    response = requests.get('https://meme-api.com/gimme')
    if response.status_code == 200:
        json_data = response.json()
        return json_data['url']
    else:
        return "Bir hata oluştu. Meme bulunamadı."

# Bot hazır olduğunda mesaj
@bot.event
async def on_ready():
    print(f'Bot giriş yaptı: {bot.user.name}')

# Meme komutu
@bot.command(name='meme')
async def meme(ctx):
    meme_url = get_meme()
    await ctx.send(meme_url)

# Ses kanalına katılma komutu
@bot.command(name='join')
async def join(ctx):
    if ctx.author.voice:  
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"{channel.name} kanalına katıldım!")
    else:
        await ctx.send("Lütfen önce bir ses kanalına katılın!")

# Ses kanalından ayrılma komutu
@bot.command(name='leave')
async def leave(ctx):
    if ctx.voice_client:  # Bot bir ses kanalında mı?
        await ctx.voice_client.disconnect()
        await ctx.send("Ses kanalından ayrıldım!")
    else:
        await ctx.send("Bir ses kanalında değilim.")

# Müzik çalma komutu
@bot.command(name='play')
async def play(ctx, *, query: str):
    if not ctx.voice_client:  
        await ctx.invoke(join)

    voice_client = ctx.voice_client
    ydl_opts = {
        'format': 'bestaudio/best',  
        'default_search': 'ytsearch',  # YouTube üzerinde arama yap
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,  # Daha fazla bilgi yazdırmayı engelle
        'noplaylist': True,  # Playlist yerine sadece tek bir video
        'extractaudio': True,  # Ses çıkarma işlemi
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)  # YouTube'da ara
        audio_url = info['entries'][0]['url'] if 'entries' in info else info['url']
        title = info['entries'][0]['title'] if 'entries' in info else info['title']
        voice_client.play(discord.FFmpegPCMAudio(audio_url, executable=ffmpeg_path), after=lambda e: print("Şarkı bitti!"))

    await ctx.send(f"Şimdi çalıyor: {title}")

# Durdurma komutu
@bot.command(name='stop')
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Şarkıyı durdurdum!")
    else:
        await ctx.send("Şu anda bir şey çalmıyorum.")

# Botun çalıştırılması
bot.run('Token')  # Token yerine botunuzun tokenini yazın.

