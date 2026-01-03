import discord
import os
import random
from flask import Flask
from threading import Thread
import time
from discord import app_commands
from datetime import timedelta

# Flaskのアプリケーションインスタンスを作成（gunicornが実行するWebサーバー）
app = Flask(__name__) 

# グローバルフラグ：Botが起動を試みたかを示す
bot_start_attempted = False

# Bot をアプリ起動時に1回だけ起動する
def start_bot():
    TOKEN = os.getenv("DISCORD_TOKEN")
    intents = discord.Intents.all()
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)
    channel_id = 1456559459865202782 # 送信先のチャンネルID

    # ---定義---
    intents = discord.Intents.all()
    client = discord.Client(intents=intents)
    intents.message_content = True  # メッセージ内容の受信を有効化
    intents.messages = True  # メッセージの受信を有効化
    tree = app_commands.CommandTree(client)

    @client.event
    async def on_ready():
        # ログ出力（元のコードのまま）
        print(f'We have logged in as {client.user}')
        await tree.sync()
        print('Slash commands synced.')

    @client.event
    async def on_message(message):
        if message.author == client.user: #自分自身のメッセージを無視
            return
        if message.author.bot: #他のBotのメッセージを無視
            return
        if not message.content.strip() and not message.attachments: #メッセージとファイルがないときは無視
            return
        if message.webhook_id: #ウェブフックを無視
            return
            
        # ---定義---
        tanimura = ['黙れ', 'おい、お前　姿勢正せ（山田風）', 'ダカラナニー']
        content = message.content
        att = message.attachments
        
        # ---谷村を黙らせる---
        if 'ワイ' in content or 'イッチ' in content or 'pixiv' in content or '次回にかける' in content or 'ジョジョ' in content:
            response = random.choice(tanimura) #tanimuraの要素から１つランダムに選ぶ
            await message.reply(f'{response}')

        # ---メッセージの履歴を残す---
        if content.strip() or att: #メッセージまたはファイルを受け取ったとき
            try:
                channel = await client.fetch_channel(channel_id) #チャンネルを取得
                jst_time = message.created_at #時刻
                
                embed = discord.Embed(title="メッセージログ", description=f"{content}", color=0x3498db, timestamp=jst_time) #embedを定義
                
                embed.add_field(name="サーバー", value=f"{message.guild.name}", inline=True) #送信されたサーバー
                embed.add_field(name="チャンネル", value=f"#{message.channel.name}", inline=True) #送信されたチャンネル
                embed.add_field(name="送信者", value=f"**{message.author.display_name}**\n{message.author.mention}", inline=False) #送信した人

                if len(att) == 1: #ファイル数が１つのとき
                    file_text = f"1件のファイル: {att[0].filename}"
                elif len(att) > 1: #ファイルが複数あるとき
                    file_text = f"{len(att)} 件のファイル"
                else: #ファイルが存在しないとき
                    file_text = None
                if file_text: #ファイルについての文章が存在するとき
                    embed.add_field(name="ファイル", value=file_text, inline=False)
                    
                if message.author.display_avatar: #メッセージを書いた人のアバターが存在するとき
                    embed.set_thumbnail(url=message.author.display_avatar.url)
                    
                embed.set_footer(text=f"User ID: {message.author.id} | Channel ID: {message.channel.id} | Server ID: {message.guild.id}") #サーバー、チャンネル、ユーザーのIDを表示

                send_task = channel.send(embed=embed) #送信タスク
                await send_task #タスクを送信

            except Exception as e: #エラーが発生した場合
                print(f'エラー: {e}')
            
    # ---スラッシュコマンド---
    @tree.command(name='call', description='他人を呼び出します')
    async def test(interaction: discord.Interaction, user: discord.Member):
        await interaction.response.send_message(f'<@{user.id}> おい{user.display_name}ァ！（唐突）')

    client.run(TOKEN)
    
# Flask 起動時に Bot を1回だけ起動
Thread(target=start_bot).start()
        
# Webサーバーのエンドポイント (gunicornがアクセスする場所)
@app.route('/', methods=['GET', 'HEAD'])
def home():
    # Bot起動試行済みの場合は、Renderのヘルスチェックに応答
    return 'Bot is alive!'
