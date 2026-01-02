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

    channel_id = 1456559459865202782 # 送信先のチャンネルID
    # 環境変数からトークンを取得
    TOKEN = os.getenv("DISCORD_TOKEN")

    
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
        # 自分のメッセージを無視
        if message.author == client.user:
            return
        # 他のBotのメッセージを無視
        if message.author.bot:
            return
        tanimura = ['黙れ', 'おい、谷村　姿勢正せ（山田風）', 'ダカラナニー']
        content = message.content

        if 'ワイ' in content or 'イッチ' in content or 'pixiv' in content or '次回にかける' in content or 'ジョジョ' in content or (('みな' in content or '皆' in content) and 'さん' in content and '一緒に' in content):
            response = random.choice(tanimura)
            await message.channel.send(f'<@1273962567642910733> {response}')
        if 'command' in content:
            await message.reply('コマンドは応答しませんでした⚠')
        #鸚鵡返し
        if message.content.strip():  # メッセージが空でない場合
            try:
                channel = await client.fetch_channel(channel_id)  # チャンネルを取得
                
                print(f'メッセージを受信しました: {content}')
                print(f'チャンネル {channel.name} にメッセージを送信しようとしています: {content}')
                
                send_task = channel.send(f'【{message.guild.name}】サーバーの#{message.channel.name}で@{message.author.name}からのメッセージ：{content}') # メッセージを送信 
                await send_task  # 送信タスクが完了するまで待機
                print('送信タスクが完了しました')

            except Exception as e:  # エラーが発生した場合
                print(f'エラー: {e}')
            
            # -----------------
            # スラッシュコマンド
            # -----------------
    @tree.command(name='call', description='呼び出す')
    async def test(interaction: discord.Interaction, user: discord.Member):
        await interaction.response.send_message(f'{user.id}おい{user.display_name}ァ！（唐突）')


    
    # --- Botの実行 ---
    if TOKEN:
        try:
            # 元のコードにあった bot.run(TOKEN) のみを実行
            client.run(TOKEN)
        except Exception as e:
            print(f'Discord Bot 起動失敗: {e}')
    else:
        print('エラー: Botトークンが設定されていません。')

# -----------------
# Webサーバーのエンドポイント (gunicornがアクセスする場所)
# -----------------
@app.route('/', methods=['GET', 'HEAD'])
def home():
    global bot_start_attempted
    
    # Botがまだ起動を試みていない場合のみ、Botを別スレッドで起動
    if not bot_start_attempted:
        print('Webアクセスを検知。Discord Botの起動を試みます...')
        bot_start_attempted = True
        
        # Botを別スレッドで起動
        Thread(target=run_discord_bot).start()
        
        return 'Discord Bot is initializing...'
    
    # Bot起動試行済みの場合は、Renderのヘルスチェックに応答
    return 'Bot is alive!'
