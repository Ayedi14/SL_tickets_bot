import discord
from discord.ext import commands
from discord.ui import Button, View, Select

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

class TicketCategorySelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="دعم عام", 
                description="مساعدة عامة أو استفسارات حول السيرفر", 
                emoji="💬", 
                value="general"
            ),
            discord.SelectOption(
                label="الإبلاغ عن لاعب", 
                description="تقديم شكوى أو الإبلاغ عن مخالفة", 
                emoji="⚠️", 
                value="report"
            ),
            discord.SelectOption(
                label="المبيعات والشراء", 
                description="استفسارات الرتب، التبرعات، أو المشتريات", 
                emoji="🛒", 
                value="buy"
            ),
        ]
        super().__init__(placeholder="اختر نوع التذكرة...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user

        category_name = "تذاكر الدعم"
        category = discord.utils.get(guild.categories, name=category_name)
        if not category:
            category = await guild.create_category(category_name)

        channel_name = f"ticket-{user.name}".lower().replace(" ", "-")
        existing_channel = discord.utils.get(guild.channels, name=channel_name)
        
        if existing_channel:
            await interaction.response.send_message(f"❌ لديك تذكرة مفتوحة بالفعل: {existing_channel.mention}", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }

        ticket_channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            topic=f"تذكرة {self.values[0]} الخاصة بـ {user.name}"
        )

        await interaction.response.send_message(f"✅ تم إنشاء تذكرتك بنجاح: {ticket_channel.mention}", ephemeral=True)

        embed = discord.Embed(
            title=f"📩 تذكرة جديدة | {user.name}",
            description="مرحباً بك! يرجى كتابة تفاصيل مشكلتك هنا وسيقوم فريق الدعم بالرد عليك في أقرب وقت.",
            color=discord.Color.green()
        )
        embed.add_field(name="القسم المختارات:", value=f"**{self.values[0]}**", inline=False)
        embed.set_footer(text="اضغط على الزر أدناه لإغلاق التذكرة.")

        await ticket_channel.send(content=f"{user.mention}", embed=embed, view=CloseTicketView())

class CloseTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="إغلاق التذكرة 🔒", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("🔒 سيتم إغلاق هذه التذكرة بعد 5 ثوانٍ...")
        import asyncio
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketPanelLink(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketCategorySelect())

@bot.event
async def on_ready():
    print(f"✅ Le bot est connecté avec succès sous le nom: {bot.user}")

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_ticket(ctx):
    embed = discord.Embed(
        title="🎫 نظام الدعم الفني والتذاكر",
        description="إذا كنت بحاجة إلى مساعدة، يرجى اختيار القسم المناسب من القائمة المنسدلة أدناه لفتح تذكرة خاصة بك.",
        color=discord.Color.blue()
    )
    embed.set_footer(text="SL Ticket System • نظام التذاكر")
    
    await ctx.send(embed=embed, view=TicketPanelLink())
    await ctx.message.delete()
import os

bot.run(os.getenv("TOKEN"))