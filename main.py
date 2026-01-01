import discord
import os
import random
from flask import Flask
from threading import Thread
import time

# Flaskのアプリケーションインスタンスを作成（gunicornが実行するWebサーバー）
app = Flask(__name__) 

# グローバルフラグ：Botが起動を試みたかを示す
bot_start_attempted = False

# -----------------
# Discord Bot本体の起動関数
# -----------------
def run_discord_bot():
    global bot_start_attempted

    tanimura = ['黙れ', 'おい、谷村　姿勢正せ（山田風）', 'ダカラナニー']
    # 環境変数からトークンを取得
    TOKEN = os.getenv("DISCORD_TOKEN")
    
    # 元のコードで使用されていた Intents.all() を使用
    
    client = discord.Client(intents=discord.Intents.default())
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

        if 'ワイ' in content or 'イッチ' in content or 'pixiv' in content or '次回にかける' in content or 'ジョジョ' in content or (('みな' in content or '皆' in content) and 'さん' in content and '一緒に' in content):
            response = random.choice(tanimura)
            await message.channel.send(f'<@1273962567642910733> {response}')
        if 'command' in content:
            await message.reply('コマンドは応答しませんでした⚠')
            
            # -----------------
            # スラッシュコマンド
            # -----------------
    @tree.command(name="call", description="呼び出す")
    async def call(interaction: discord.Interaction, name: str):
        await interaction.response.send_message(f"おい {name}！（唐突）")


    
    # --- Botの実行 ---
    if TOKEN:
        try:
            # 元のコードにあった bot.run(TOKEN) のみを実行
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
