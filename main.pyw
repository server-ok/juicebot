import asyncio
import discord
from discord import client
from discord import message
from discord.channel import VoiceChannel
from discord.enums import ContentFilter
from discord.errors import HTTPException
from discord.ext import commands
from discord.ext.commands import MissingPermissions
from discord.ext.commands.errors import ExpectedClosingQuoteError, MemberNotFound
import requests
from config import settings
from disputils import BotEmbedPaginator, BotConfirmation
import random
import json
import aiohttp
import nekos
from money import economy

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=settings["prefix"], intents=intents)
# Так как мы указали префикс в settings, обращаемся к словарю с ключом prefix.
bot.remove_command("help")

#############                            ХЕЛП:                     ##################


@bot.command(
    help="С помощью данной команды можно узнать, как\nиспользовать какую-либо команду.\nТакже можно увидеть список всех команд.\nПримеры использования:\n`*хелп пинг`\n`*хелп`"
)
async def хелп(ctx, commandname=None):
    if commandname == None:
        embeds = [
            discord.Embed(
                title="Основные \🔧",
                description=">>> пинг\nсервер\nюзер\nаватар",
                color=settings["embedcolor"],
            ).set_thumbnail(url=settings["bot_avatar_url"]),
            discord.Embed(
                title="Развлечения \😄",
                description=">>> привет\nгифка\nвкпост\nвидео\nобзови\nпогода",
                color=settings["embedcolor"],
            ).set_thumbnail(url=settings["bot_avatar_url"]),
            discord.Embed(
                title="РП-команды \💬",
                description=">>> обнять\nпоцеловать\nгладить\nдурак\nщекотать\nкормить",
                color=settings["embedcolor"],
            ).set_thumbnail(url=settings["bot_avatar_url"]),
            discord.Embed(
                title="Экономика \💵",
                description=">>> баланс\nтоп",
                color=settings["embedcolor"],
            ).set_thumbnail(url=settings["bot_avatar_url"]),
            discord.Embed(
                title="Для админа \💻",
                description=">>> скажи",
                color=settings["embedcolor"],
            ).set_thumbnail(url=settings["bot_avatar_url"]),
            discord.Embed(
                title="Для создателя \🍔",
                description=">>> выключись",
                color=settings["embedcolor"],
            ).set_thumbnail(url=settings["bot_avatar_url"]),
        ]

        paginator = BotEmbedPaginator(ctx, embeds)
        await paginator.run()
    else:
        try:
            commandhelp = discord.Embed(
                color=settings["embedcolor"],
                title=f"*{commandname}",
                description=bot.get_command(commandname).help,
            )
            commandhelp.set_thumbnail(url=settings["bot_avatar_url"])
            await ctx.send(embed=commandhelp)
        except AttributeError:
            commandhelp = discord.Embed(
                color=settings["embedcolor"],
                title="Такой команды не существует.",
                description="Чтобы посмотреть список всех команд, выполните `*хелп`.",
            )
            commandhelp.set_thumbnail(url=settings["bot_avatar_url"])
            await ctx.send(embed=commandhelp)


################       ПОЛЕЗНОСТИ (события, ивенты, функции и прочая фигня):      #################


@bot.event
async def on_message(message):
    if (
        len(message.content) > 20
        and message.content[0] != settings["prefix"]
        and message.author.id in economy
        and economy[message.author.id] == 0
    ):  # за каждое сообщение длиной > 20 символов которое НЕ НАЧИНАЕТСЯ С ПРЕФИКСА АКА НЕ КОМАНДА
        economy[message.author.id] += (len(message.content) // 4)
              # выдавать деньги наверное (да)
              # прикол в том что выдаст только 25 процентов
              # чтобы люди не фармили много денег себе
        newbalance = economy[message.author.id]
        with open("money.py", "r+") as f:  # ебать какой же это говнокод блябуду
            text = "".join(
                [
                    line.replace(
                        f"{message.author.id}: 0,",
                        f"{message.author.id}: {newbalance},",
                    )
                    for line in f.readlines()
                ]
            )
            f.seek(0)
            f.write(text)  # аж глаза режет, пиздец(
    elif (
        len(message.content) > 20
        and message.content[0]
        != settings["prefix"]  # раньше резало, я отблэкил :sunglasses:
        and message.author.id in economy
        and message.author.id != settings["id"]
        and economy[message.author.id] > 0
    ):
        economy[message.author.id] += (len(message.content) // 4)
        newbalance = economy[message.author.id]
        oldbalance = economy[message.author.id] - len(message.content)
        with open("money.py", "r+") as f:
            text = "".join(
                [
                    line.replace(
                        f"{message.author.id}: {oldbalance}",
                        f"{message.author.id}: {newbalance}",
                    )
                    for line in f.readlines()
                ]
            )
            f.seek(0)
            f.write(text)
    elif message.author.id not in economy:
        pass
    else:
        pass
    await bot.process_commands(message)


#                           КОМАНДЫ:


@bot.command(help="Привет, юзер!")
async def привет(ctx):
    author = ctx.message.author
    answers = (
        f"Привет, {author.mention}!" f"Ку, {author.mention}!",
        f"Здравствуй, {author.mention}!",
        f"И тебе привет, {author.mention}!",
        f"Салют, {author.mention}!",
        f"Прив, {author.mention}!",
        f"qq, {author.mention}!",
    )
    await ctx.send(random.choice(answers))


@bot.command(help="Данная команда позволяет узнать пинг бота.")
async def пинг(ctx):
    await ctx.send(
        random.choice(
            [
                "Понг! Пинг бота: {0} мс".format(round(bot.latency * 1000)),
                "Пинг! Понг бота: {0} мс".format(round(bot.latency * 1000)),
            ]
        )
    )


@bot.command(
    help="Отправляет сообщение от лица бота.\n**Доступно только администраторам!**"
)
@commands.has_permissions(administrator=True)
async def скажи(ctx, *, text):
    message = ctx.message
    await message.delete()
    await ctx.send(f"{text}")


@скажи.error
async def скажи_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send(
            random.choice(
                [
                    "Тебе не хватает прав, дружище.",
                    "Эй, но ты же не администратор!",
                    "Не выйдет, прав не хватает(",
                    "Не-а, я ничего не скажу!",
                ]
            )
        )


@bot.command(help="Выключает бота.\n**Доступно только создателю!**")
async def выключись(ctx):
    if ctx.message.author.id == settings["author-id"]:
        message = await ctx.send("Выключение...")
        await asyncio.sleep(2)
        await message.edit(content="Бот выключен!")
        await ctx.bot.logout()
    else:
        await ctx.send(
            random.choice(
                [
                    "Это не твой бот!",
                    "Не-а, ты не мой владелец!",
                    "Выключение.. \n бип-бип, ошибка выполнения: недостаточно прав!",
                ]
            )
        )


@bot.command(
    help="Показывает информацию о сервере, \nна котором сейчас находится бот.\n**Не работает в лс!**"
)
async def сервер(ctx):
    try:
        name = str(ctx.guild.name)

        owner = str(ctx.guild.owner)
        id = str(ctx.guild.id)
        region = str(ctx.guild.region)
        memberCount = str(ctx.guild.member_count)

        icon = str(ctx.guild.icon_url)

        embed = discord.Embed(
            title='Информация о сервере "' + name + '"', color=settings["embedcolor"]
        )
        embed.set_thumbnail(url=icon)
        embed.add_field(name="Владелец", value=owner, inline=False)
        embed.add_field(name="ID сервера", value=id, inline=False)
        embed.add_field(name="Регион", value=region, inline=False)
        embed.add_field(name="Кол-во участников", value=memberCount, inline=False)

        await ctx.send(embed=embed)
    except AttributeError:
        await ctx.send(
            random.choice(
                [
                    f"Как ты думаешь, {ctx.message.author.name}, что я должен тебе __здесь__ ответить?",
                    "Не-а, мы же не на сервере!",
                    "У меня для тебя не лучшие новости...\nМы сейчас не на сервере.",
                ]
            )
        )


@bot.command(
    help="Показывает информацию о пользователе.\nПримеры:\n`*юзер` - выведет информацию об отправителе.\n`*юзер @ИмяПользователя#6969` - выведет информацию об упомянутом.\n`*юзер 872115341931720795` - более тихий вариант. Выведет информацию о пользователе с помощью его айди."
)
async def юзер(ctx, *, user: discord.Member = None):
    if user is None:
        user = ctx.author
    date_format = "%d %b %Y %R"
    embed = discord.Embed(
        color=settings["embedcolor"],
        description="Информация об участнике " + user.mention,
    )
    embed.set_author(name=str(user), icon_url=user.avatar_url)
    embed.set_thumbnail(url=user.avatar_url)
    embed.add_field(
        name="Присоединился", value=user.joined_at.strftime(date_format), inline=False
    )
    members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
    embed.add_field(name="Зашел", value=str(members.index(user) + 1), inline=False)
    embed.add_field(
        name="Зарегистрировался",
        value=user.created_at.strftime(date_format),
        inline=False,
    )
    if len(user.roles) > 1:
        role_string = " ".join([r.mention for r in user.roles][1:])
        embed.add_field(
            name="Роли [{}]".format(len(user.roles) - 1),
            value=role_string,
            inline=False,
        )
    embed.set_footer(text="ID: " + str(user.id))
    return await ctx.send(embed=embed)


@юзер.error
async def юзер_error(ctx, error):
    if isinstance(error, MemberNotFound):
        await ctx.send("Пользователя не существует.")


@bot.command(
    help="Показывает баланс пользователя.\nЕсли пользователь ещё не заводил кошелёк, то предложит его создать.\nПримеры:\n`*баланс` - покажет ваш баланс.\n`*баланс ПетяВаськин420#6969` - покажет баланс упомянутого."
)
async def баланс(ctx, *, author: discord.Member = None):
    if author == None:
        author = ctx.message.author

    if author.id in economy:
        balance = economy[author.id]
        embed = discord.Embed(title="Баланс", color=settings["embedcolor"])
        embed.set_thumbnail(url=settings["bot_avatar_url"])
        embed.add_field(name="Пользователь: ", value=author.mention, inline=False)
        embed.add_field(name="Баланс: ", value=balance, inline=False)
        await ctx.send(embed=embed)

    elif author.id not in economy and author.id == ctx.message.author.id:
        confirmation = BotConfirmation(ctx, settings["embedcolor"])
        await confirmation.confirm("Кошелёк ещё не был создан!\nСоздать?")

        if confirmation.confirmed:
            newbalance = 0
            newfuckingline = f"    {author.id}: {newbalance},\n" + "}"
            try:
                with open("money.py", "r+") as f:
                    text = "".join(
                        [line.replace("}", newfuckingline) for line in f.readlines()]
                    )
                    f.seek(0)
                    f.write(text)
                economy[author.id] = 0
                await confirmation.update(
                    "Кошелёк создан! \nТеперь ты можешь просмотривать баланс и зарабатывать деньги."
                )
            except FileNotFoundError:
                await confirmation.update(
                    f"Кошелёк не был создан! \nПроизошла ошибка. Пожалуйста, расскажите о ней \nсоздателю бота.\n\n__FileNotFoundError__"
                )

        else:
            await confirmation.update(
                "Кошелёк не создан.\nПользователь отменил процесс."
            )

    elif author.id not in economy and author.id != ctx.message.author.id:
        coolembed = discord.Embed(
            color=settings["embedcolor"],
            title="Ошибка!",
            description="У этого пользователя нет кошелька.\nОн сможет завести его, если сам выполнит эту команду.",
        )
        await ctx.send(embed=coolembed)
    else:
        embed = discord.Embed(title='Ошибка!', description='Произошла неизвестная ошибка.')
        await ctx.send(embed=embed)


@bot.command(
    help="Выведет аватар умомянутого.\nЕсли никто не упомянут, выведет аватар автора сообщения."
)
async def аватар(ctx, *, user: discord.Member = None):
    if user is None:
        user = ctx.author
    embed = discord.Embed(color=settings["embedcolor"])
    embed.set_image(url=user.avatar_url)
    embed.set_footer(text="Запросил: " + ctx.message.author.name)
    await ctx.send(embed=embed)


@bot.command(
    help='Отправляет гифки!\nПримеры использования:\n`*гифка` - отправит рандомную гифку.\n`*гифка танец` - отправит гифку по запросу "танец".'
)
async def гифка(ctx, *, search=None):
    embed = discord.Embed(color=settings["embedcolor"])
    session = aiohttp.ClientSession()
    try:
        if search == None:
            response = await session.get(
                "https://api.giphy.com/v1/gifs/random?api_key=x7Qc8HcccUTR11FnPlHKkA5YtUbZdoxK"
            )
            data = json.loads(await response.text())
            embed.set_image(url=data["data"]["images"]["original"]["url"])
            embed.set_footer(
                text=f"{ctx.message.author.name} желает увидеть случайную гифку"
            )
        else:
            search.replace(" ", "+")
            response = await session.get(
                "http://api.giphy.com/v1/gifs/search?q="
                + search
                + "&api_key=x7Qc8HcccUTR11FnPlHKkA5YtUbZdoxK&limit=10"
            )
            data = json.loads(await response.text())
            gif_choice = random.randint(0, 9)
            embed.set_image(url=data["data"][gif_choice]["images"]["original"]["url"])
            embed.set_footer(text=f'{ctx.message.author.name} ищет "{search}"')

        await session.close()

        await ctx.send(embed=embed)
    except IndexError:
        await ctx.send(
            f'Гифка по запросу "{search}" не найдена.\nПопробуйте выполнить команду снова, перепроверив правильность запроса. :confused: '
        )


@bot.command(
    help="Позволяет отправить виртуальные объятия упомянутому человеку!\nПример:\n`*обнять @КрутойЧелик#1234` - отправить упомянутому виртуальное объятие."
)
async def обнять(ctx, user: discord.Member = None):
    hugger = ctx.message.author.name
    if user == None:
        hugged = "кого-то.."
    else:
        hugged = user.name
    embed = discord.Embed(color=settings["embedcolor"])
    embed.set_image(url=nekos.img("hug"))
    embed.set_footer(text=f"{hugger} обнимает {hugged} 🤗")
    await ctx.send(embed=embed)


@bot.command(
    help="Позволяет поцеловать упомянутого человека.\nПример:\n`*поцеловать @КрасиваяДевушка#0420` - поцеловать упомянутого."
)
async def поцеловать(ctx, user: discord.Member = None):
    kisser = ctx.message.author.name
    if user == None:
        kissed = "кого-то.."
    else:
        kissed = user.name
    embed = discord.Embed(color=settings["embedcolor"])
    embed.set_image(url=nekos.img("kiss"))
    embed.set_footer(text=f"{kisser} целует {kissed} ❤️")
    await ctx.send(embed=embed)


@bot.command(
    help="Позволяет погладить по голове упомянутого человека.\nПример:\n`*гладить @МилыйПесёль#1423` - погладить упомянутого."
)
async def гладить(ctx, user: discord.Member = None):
    patter = ctx.message.author.name
    if user == None:
        patted = "кого-то.."
    else:
        patted = user.name
    embed = discord.Embed(color=settings["embedcolor"])
    embed.set_image(url=nekos.img("pat"))
    embed.set_footer(text=f"{patter} гладит {patted} ")
    await ctx.send(embed=embed)


@bot.command(
    help="Позволяет назвать кого-либо дураком.\nПример:\n`*дурак @xXx666МистирКрипир666xXx#2013` - назвать упомянутого дураком."
)
async def дурак(ctx, user: discord.Member = None):
    bakker = ctx.message.author.name
    if user == None:
        bakked = "кого-то"
    else:
        bakked = user.name
    embed = discord.Embed(color=settings["embedcolor"])
    embed.set_image(url=nekos.img("baka"))
    embed.set_footer(text=f"{bakker} называет {bakked} дураком! 😡")
    await ctx.send(embed=embed)


@bot.command(
    help="Позволяет пощекотать упомянутого.\nПример:\n`*щекотать @БоюсьЩекотки#6942` - пощекотать упомянутого."
)
async def щекотать(ctx, user: discord.Member = None):
    tickler = ctx.message.author.name
    if user == None:
        tickled = "кого-то.."
    else:
        tickled = user.name
    embed = discord.Embed(color=settings["embedcolor"])
    embed.set_image(url=nekos.img("tickle"))
    embed.set_footer(text=f"{tickler} щекочет {tickled} 😄")
    await ctx.send(embed=embed)


@bot.command(
    help="Позволяет виртуально покормить упомянутого.\nПример:\n`*кормить @ЛюблюЧипсы#1212` - покормить упомянутого."
)
async def кормить(ctx, user: discord.Member = None):
    feeder = ctx.message.author.name
    if user == None:
        feeded = "кого-то.."
    else:
        feeded = user.name
    embed = discord.Embed(color=settings["embedcolor"])
    embed.set_image(url=nekos.img("feed"))
    embed.set_footer(text=f"{feeder} кормит {feeded} 🍔")
    await ctx.send(embed=embed)


@bot.command(
    help="Магический шар, отвечающий на подходящие вопросы.\nИногда несёт бред.\nПосле команды необходимо задать вопрос."
)
async def шар(ctx, *, text=None):
    answers = [
        "Возможно.",
        "Скорее всего - да.",
        "Я так не думаю.",
        "Скорее да, чем нет.",
        "Спроси позже.",
        "Не лучшие перспективы.",
        "Конечно!",
        "Ответ кроется в тебе.",
        "Я не уверен, но по-моему всё-таки да.",
        "Скорее нет, чем да.",
        "Кажется, ты уже знаешь ответ на этот вопрос.",
    ]
    if text == None:
        await ctx.send("Ты не задал вопрос.")
    else:
        await ctx.send(random.choice(answers))


@bot.command(help="Ищет пост во ВКонтакте по ключевому слову.")
async def вкпост(ctx, *, q=None):
    session = aiohttp.ClientSession()
    if q == None:
        emb = discord.Embed(
            color=settings["embedcolor"],
            title="Ошибка!",
            description="Вы не указали запрос.",
        ).set_thumbnail(url=settings["bot_avatar_url"])
        await ctx.send(embed=emb)
        await session.close()
    else:
        try:
            q.replace(" ", "+")
            method = "newsfeed.search"
            param1 = "?q="
            param2 = "&count=10"
            endpoint = (
                "https://api.vk.com/method/"
                + method
                + param1
                + q
                + param2
                + "&access_token="
                + settings["vk-api-token"]
                + "&v=5.131"
            )
            response = requests.get(endpoint)
            responsejson = response.json()
            endedvkpost = False
            if responsejson["response"]["items"][0]["post_type"] == "post":
                rightpost = 0
            elif (
                responsejson["response"]["items"][1]["post_type"] == "post"
            ):  # да, говнокод. мне просто было лень думать и я решил действовать.
                rightpost = 1  # возможно потому-что я вчера устал писать эту фигню, психанул и пошёл в тф.
            elif (
                responsejson["response"]["items"][2]["post_type"] == "post"
            ):  # энивей, эта фигня даже десяти процентов от кода не составляет, так что норм
                rightpost = 2
            elif responsejson["response"]["items"][3]["post_type"] == "post":
                rightpost = 3
            elif responsejson["response"]["items"][4]["post_type"] == "post":
                rightpost = 4
            elif responsejson["response"]["items"][5]["post_type"] == "post":
                rightpost = 5
            elif responsejson["response"]["items"][6]["post_type"] == "post":
                rightpost = 6
            elif responsejson["response"]["items"][7]["post_type"] == "post":
                rightpost = 7
            elif responsejson["response"]["items"][8]["post_type"] == "post":
                rightpost = 8
            elif responsejson["response"]["items"][9]["post_type"] == "post":
                rightpost = 9
            else:
                await ctx.send("Пост не найден.")
                endedvkpost = True

            if endedvkpost == False:
                ownerid = responsejson["response"]["items"][rightpost]["owner_id"]
                postid = responsejson["response"]["items"][rightpost]["id"]
                posturl = f"https://vk.com/wall{ownerid}_{postid}"
                if responsejson["response"]["items"][rightpost]["text"] != "":
                    posttext = (
                        responsejson["response"]["items"][rightpost]["text"]
                        + f"\n\nИсточник: {posturl}"
                    )
                else:
                    posttext = (
                        "Этот пост не содержит текста.\nОн содержит вложение.\nЕго можно просмотреть в источнике.\n *Вложения не показываются в эмбедах бота, так как могут содержать NSFW-контент.*"
                        + f"\n\nИсточник: {posturl}"
                    )
                q = str(ownerid)
                if "-" in q:
                    q = q.replace("-", "")
                    method = "groups.getById"
                    param1 = "?group_ids="
                    param2 = "&fields=photo_50"
                    author_type = "group"
                else:
                    method = "users.get"
                    param1 = "?user_ids="
                    param2 = "&fields=photo_50"
                    author_type = "user"
                endpoint = (
                    "https://api.vk.com/method/"
                    + method
                    + param1
                    + q
                    + param2
                    + "&access_token="
                    + settings["vk-api-token"]
                    + "&v=5.131"
                )
                response = requests.get(endpoint)
                responsejson = response.json()
                if author_type == "group":
                    ownername = responsejson["response"][0]["name"]
                    owneravatar = responsejson["response"][0]["photo_50"]
                elif author_type == "user":
                    ownername = (
                        responsejson["response"][0]["first_name"]
                        + " "
                        + responsejson["response"][0]["last_name"]
                    )
                    owneravatar = responsejson["response"][0]["photo_50"]
                embed = discord.Embed(
                    url=posturl, description=posttext, color=settings["embedcolor"]
                )
                embed.set_author(name=ownername, icon_url=owneravatar)
                await ctx.send(embed=embed)
                endedvkpost = True

            if endedvkpost == True:
                await session.close()
        except IndexError or HTTPException:
            await session.close()
            await ctx.send("Пост не найден.")


@bot.command(help="Ищет видео в YouTube по запросу.")
async def видео(ctx, *, q=None):
    session = aiohttp.ClientSession()
    if q != None:
        try:
            q = q.replace(" ", "+")
            endpoint = (
                "https://youtube.googleapis.com/youtube/v3/search?part=snippet&maxResults=5&order=relevance&q="
                + q
                + "&type=video&key="
                + settings["youtube_apikey"]
            )
            response = requests.get(endpoint)
            responsejson = response.json()
            videonum = random.randint(0, 5)
            videotitle = responsejson["items"][videonum]["snippet"]["title"]
            videourl = (
                "https://youtu.be/" + responsejson["items"][videonum]["id"]["videoId"]
            )
            videodescription = responsejson["items"][videonum]["snippet"]["description"]
            thumbnail = responsejson["items"][videonum]["snippet"]["thumbnails"][
                "high"
            ]["url"]
            channeltitle = responsejson["items"][videonum]["snippet"]["channelTitle"]
            embed = (
                discord.Embed(
                    title=videotitle,
                    description=videodescription,
                    color=settings["embedcolor"],
                    url=videourl,
                )
                .set_author(name=channeltitle)
                .set_image(url=thumbnail)
            )
            await ctx.send(embed=embed)
            await session.close()
        except IndexError:
            if 0 in responsejson["items"]:
                videonum = 0
                videotitle = responsejson["items"][videonum]["snippet"]["title"]
                videourl = (
                    "https://youtu.be/"
                    + responsejson["items"][videonum]["id"]["videoId"]
                )
                videodescription = responsejson["items"][videonum]["snippet"][
                    "description"
                ]
                thumbnail = responsejson["items"][videonum]["snippet"]["thumbnails"][
                    "high"
                ]["url"]
                channeltitle = responsejson["items"][videonum]["snippet"][
                    "channelTitle"
                ]
                embed = (
                    discord.Embed(
                        title=videotitle,
                        description=videodescription,
                        color=settings["embedcolor"],
                        url=videourl,
                    )
                    .set_author(name=channeltitle)
                    .set_image(url=thumbnail)
                )
                await ctx.send(embed=embed)
                await session.close()
            else:
                embed = discord.Embed(
                    title="Ошибка!",
                    color=settings["embedcolor"],
                    description=random.choice(
                        [
                            "Видео не найдено.",
                            "Мы искали вдоль и поперёк, но так ничего и не нашли!",
                            "Такого видео не существует!",
                            "И тут представляете, товарищ инспектор,\n**видео испарилось прямо у меня на глазах!**",
                            "Увы, такого видео не существует.",
                            "Увы, мы не нашли такое видео.",
                        ]
                    ),
                ).set_thumbnail(url=settings["bot_avatar_url"])
                await ctx.send(embed=embed)
                await session.close()
    else:
        embederror = discord.Embed(
            title="Ошибка!",
            description="Вы не указали запрос.",
            color=settings["embedcolor"],
        ).set_thumbnail(url=settings["bot_avatar_url"])
        await ctx.send(embed=embederror)
        await session.close()
        pass


@bot.command(help="Эта команда поможет вам подобрать ругательство.")
async def обзови(ctx):
    session = aiohttp.ClientSession()
    response = requests.get(
        "https://evilinsult.com/generate_insult.php?lang=ru&type=json"
    )
    responsejson = response.json()
    insult = responsejson["insult"]
    insult = insult.replace("*", "\*").replace("_", "\_")
    number = responsejson["number"]
    embed = (
        discord.Embed(description="||" + insult + "||", color=settings["embedcolor"])
        .set_thumbnail(url=settings["bot_avatar_url"])
        .set_footer(text=f"Обзывательство №{number}")
    )
    await ctx.send(embed=embed)
    await session.close()


@bot.command(
    help="С помощью этой команды ты можешь узнать текущую погоду.\nПосле команды необходимо написать название города."
)
async def погода(ctx, *, q=None):
    session = aiohttp.ClientSession()
    if q != None:
        q = q.replace(" ", "+")
        endpoint = (
            "https://api.openweathermap.org/data/2.5/weather?q="
            + q
            + "&lang=ru&units=metric&appid="
            + settings["weather_token"]
        )
        response = requests.get(endpoint)
        responsejson = response.json()
        cod = responsejson["cod"]
        if cod == 200:
            weather = responsejson["weather"][0]["description"]
            weather_icon = (
                "https://openweathermap.org/img/w/"
                + responsejson["weather"][0]["icon"]
                + ".png?size=1024"
            )
            temp = str(responsejson["main"]["temp"]) + " °C"
            feels_like = "> " + str(responsejson["main"]["feels_like"]) + " °C"
            pressure = "> " + str(responsejson["main"]["pressure"]) + " мм"
            humidity = "> " + str(responsejson["main"]["humidity"]) + " %"
            wind_speed = "> " + str(responsejson["wind"]["speed"]) + " м/с"
            sunrise = "> " + "<t:" + str(responsejson["sys"]["sunrise"]) + ":t>"
            sunset = "> " + "<t:" + str(responsejson["sys"]["sunset"]) + ":t>"

            embed = (
                discord.Embed(title=f"{weather}, {temp}", color=settings["embedcolor"])
                .add_field(name="Ощущается как", value=feels_like, inline=True)
                .add_field(name="Давление", value=pressure, inline=True)
                .add_field(name="Влажность", value=humidity, inline=True)
                .add_field(name="Скорость ветра", value=wind_speed, inline=True)
                .add_field(name="Восход", value=sunrise, inline=True)
                .add_field(name="Закат", value=sunset, inline=True)
                .set_thumbnail(url=weather_icon)
                .set_footer(
                    text=ctx.message.author.name + f' ищет погоду по запросу "{q}"'
                )
            )
            await ctx.send(embed=embed)
            await session.close()
        else:
            embed = discord.Embed(
                title="Ошибка!",
                description="Город не найден.",
                color=settings["embedcolor"],
            ).set_thumbnail(url=settings["bot_avatar_url"])
            await ctx.send(embed=embed)
            await session.close()
    else:
        embed = discord.Embed(
            title="Ошибка!",
            description="Вы не указали запрос.",
            color=settings["embedcolor"],
        ).set_thumbnail(url=settings["bot_avatar_url"])
        await ctx.send(embed=embed)
        await session.close()

@bot.command(help='Выводит топ участников по деньгам. Выводит только первую десятку.')
async def топ(ctx):
    coolswag = dict(sorted(economy.items(), key=lambda item: item[1], reverse=True))
    number = 0
    number2 = number + 1
    embed = discord.Embed(title='Топ пользователей', color=settings['embedcolor']).set_thumbnail(url=settings['bot_avatar_url'])
    for item in coolswag:
        balance = economy[item]

        embed.add_field(name=str(number2) + ' место - ' + str(balance) + ' монет', value=f'<@{item}>', inline=False)
        if number == 9:
            break
        else:
            number += 1
            number2 += 1
    await ctx.send(embed=embed)

@bot.command(help='Обнуляет все балансы.\n**Доступна только создателю.**')
async def обнулить(ctx):
    if ctx.message.author.id == settings["author-id"]:
        with open("money.py", "w") as f:
                text = "economy = {\n}"
                f.write(text)
        economy.clear()
        embed = discord.Embed(title='Успешно!', description='Балансы успешно обнулены.', color=settings['embedcolor']
        ).set_thumbnail(url=settings['bot_avatar_url'])
        await ctx.send(embed = embed)
    else:
        await ctx.send(random.choice([
            'Не-а, у тебя недостаточно прав!',
            'Ты не мой владелец!',
            'Не, так не пойдёт. Тебе не хватает прав для этого.'
        ]))


bot.run(settings["token"])
# Обращаемся к словарю settings с ключом token, для получения токена
