import discord
from discord import app_commands

intents = discord.Intents.default()
intents.message_content = True

class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # 因為第一階段按鈕需要動態產生樓層，我們只要註冊 StatusView 確保按鈕永久有效
        self.add_view(StatusView(floor=""))
        await self.tree.sync()
        print("已同步斜線指令與按鈕監聽！")

    async def on_ready(self):
        print(f'目前登入身份 --> {self.user}')
        activity = discord.Game(name="輸入 /選單 開啟私人通報面板")
        await self.change_presence(activity=activity)

client = MyBot()

# --- 第一階段：選擇狀況（帶入所選樓層）---
class StatusView(discord.ui.View):
    def __init__(self, floor: str):
        super().__init__(timeout=None)
        self.floor = floor

    @discord.ui.button(label="垃圾桶滿了", style=discord.ButtonStyle.red, custom_id="status_full")
    async def full_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.send_report(interaction, "垃圾桶滿了")

    @discord.ui.button(label="垃圾桶故障", style=discord.ButtonStyle.blurple, custom_id="status_broken")
    async def broken_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.send_report(interaction, "垃圾桶故障")

    async def send_report(self, interaction: discord.Interaction, status: str):
        await interaction.response.send_message(f"已收到回報：**{self.floor} - {status}**！已通知管理者。", ephemeral=True)

        # 管理員 ID 清單 (可填入多位管理員)
        ADMIN_USER_IDS = [1506627795038634075]
        for admin_id in ADMIN_USER_IDS:
            try:
                admin_user = interaction.client.get_user(admin_id) or await interaction.client.fetch_user(admin_id)
                if admin_user:
                    await admin_user.send(
                        f"🚨 **管理員注意**：收到來自 [{interaction.user.name}] 的通報！\n"
                        f"📍 **地點**：{self.floor}\n"
                        f"⚠️ **狀況**：{status}"
                    )
            except Exception as e:
                print(f"發送私訊給管理員失敗: {e}")


# --- 第二階段：選擇樓層（1~3樓）---
class FloorView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="1樓", style=discord.ButtonStyle.green, custom_id="floor_1")
    async def floor_1_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = StatusView(floor="1樓")
        await interaction.response.send_message("請選擇 **1樓** 的狀況回報：", view=view, ephemeral=True)

    @discord.ui.button(label="2樓", style=discord.ButtonStyle.green, custom_id="floor_2")
    async def floor_2_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = StatusView(floor="2樓")
        await interaction.response.send_message("請選擇 **2樓** 的狀況回報：", view=view, ephemeral=True)

    @discord.ui.button(label="3樓", style=discord.ButtonStyle.green, custom_id="floor_3")
    async def floor_3_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = StatusView(floor="3樓")
        await interaction.response.send_message("請選擇 **3樓** 的狀況回報：", view=view, ephemeral=True)


# --- 斜線指令：/選單 ---
@client.tree.command(name="選單", description="開啟智慧垃圾桶私人通報面板")
async def menu(interaction: discord.Interaction):
    view = FloorView()
    await interaction.response.send_message("請選擇垃圾桶所在樓層：", view=view, ephemeral=True)


# --- 管理員專用指令：發布純文字公告說明 ---
@client.tree.command(name="發布公用面板", description="發布智慧垃圾桶通報說明")
@app_commands.default_permissions(administrator=True)
async def post_panel(interaction: discord.Interaction):
    await interaction.channel.send(
        "🗑️ **【智慧垃圾桶回報系統】**\n\n"
        "若發現垃圾桶滿了或故障，請直接在聊天室輸入 **`/選單`** 即可開啟專屬您的私人回報面板進行通報！\n"
        "*(所有回報與介面皆為私人顯示，僅您與管理者可見)*"
    )
    await interaction.response.send_message("通報說明已成功發布！", ephemeral=True)
    
import os
# 這樣就可以安全地從 Render 的環境變數中讀取 Token，不用寫死在程式碼裡
client.run(os.environ.get('DISCORD_TOKEN'))