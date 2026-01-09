
import discord
import os
import random
from flask import Flask
from threading import Thread
import time
from discord import app_commands

# Flaskのアプリケーションインスタンスを作成（gunicornが実行するWebサーバー）
app = Flask(__name__) 

# グローバルフラグ：Botが起動を試みたかを示す
bot_start_attempted = False

# -----------------
# Discord Bot本体の起動関数
# -----------------

def run_discord_bot():
    global bot_start_attempted
    
    # 環境変数からトークンを取得
    TOKEN = os.getenv("DISCORD_TOKEN")
    
    # 元のコードで使用されていた Intents.all() を使用
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
        print("Slash commands synced.")
        
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
            
        content = message.content

        if 'こんにちは' in content:
            await message.reply('木下だよ！よろしくね♡')

    @tree.command(name="server_list", description="Botが参加しているサーバー一覧を表示します")
    async def server_list(interaction: discord.Interaction):

        guilds = client.guilds
        text = "\n".join([f"{g.name} : {g.id}" for g in guilds])

        await interaction.response.send_message(f"**参加中のサーバー（{len(guilds)}件）**\n{text}")

    # --- Botの実行 ---
    if TOKEN:
        try:
            # 元のコードにあった client.run(TOKEN) のみを実行
            client.run(TOKEN)
        except Exception as e:
            print(f"Discord Bot 起動失敗: {e}")
    else:
        print("エラー: Botトークンが設定されていません。")

# -----------------
# Webサーバーのエンドポイント (gunicornがアクセスする場所)
# -----------------
@app.route('/', methods=['GET', 'HEAD'])
def home():
    global bot_start_attempted
    
    # Botがまだ起動を試みていない場合のみ、Botを別スレッドで起動
    if not bot_start_attempted:
        print("Webアクセスを検知。Discord Botの起動を試みます...")
        bot_start_attempted = True
        
        # Botを別スレッドで起動
        Thread(target=run_discord_bot).start()
        
        return "Discord Bot is initializing..."
    
    # Bot起動試行済みの場合は、Renderのヘルスチェックに応答
    return "Bot is alive!"
