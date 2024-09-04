import re
from collections import defaultdict
from typing import Dict, List

import coc
import disnake
import pendulum as pd

from assets.army_ids import size, spell_ids, troop_ids
from classes.bot import CustomClient
from exceptions.CustomExceptions import MessageException
from utility.constants import EMBED_COLOR_CLASS, MAX_ARMY_CAMP, MAX_NUM_SPELLS
from utility.discord_utils import iter_embed_creation


def army_embed(
    bot: CustomClient,
    nick: str,
    link: str,
    clan_castle: str,
    embed_color: disnake.Color = EMBED_COLOR_CLASS,
):
    valid = is_link_valid(link)
    if not valid:
        raise MessageException('Not a valid army link')
    troops_patten = 'u([\d+x-]+)'
    armycomp = re.split(troops_patten, link)

    sieges = '**Sieges:**\n'
    troop_string = ''
    troops_used = []
    eightTroops = ['Valkyrie', 'Golem', 'P.E.K.K.A']
    isEight = False

    troopSpace = 0
    troop_string += '**Troops:**\n'
    if len(armycomp) > 1 and armycomp[1] != '':
        troops = armycomp[1]
        troops_str = troops.split('-')
        for troop in troops_str:
            split_num_and_id = troop.split('x')
            num = split_num_and_id[0]
            id = split_num_and_id[1]
            troops_used.append(id)
            troop_name = troop_ids(int(id))
            if troop_name in eightTroops:
                isEight = True
            troop_emoji = bot.fetch_emoji(troop_name)
            if troop_name not in coc.SIEGE_MACHINE_ORDER:
                troopSpace += size(troop_name) * int(num)
                troop_string += f'{troop_emoji}`x {str(num)}` {troop_name}\n'
            else:
                sieges += f'{troop_emoji}`x {str(num)}` {troop_name}\n'
    else:
        troop_string += 'None'

    spells_patten = 's([\d+x-]+)'
    armycomp = re.split(spells_patten, link)

    spell_string = '**Spells:**\n'
    spells_used = []
    spell_space = 0
    if len(armycomp) > 1 and armycomp[1] != '':
        spells = armycomp[1]
        spells_str = spells.split('-')
        for spell in spells_str:
            split_num_and_id = spell.split('x')
            num = split_num_and_id[0]
            id = split_num_and_id[1]
            spells_used.append(id)
            spell_name = spell_ids(int(id))
            spell_emoji = bot.fetch_emoji(spell_name)
            spell_space += size(spell_name) * int(num)
            spell_string += f'{spell_emoji}`x {str(num)}` {spell_name}\n'
    else:
        spell_string += 'None'

    if sieges == '**Sieges:**\n':
        sieges += 'None'

    army = ''
    townhall_lv = townhall_army(troopSpace)
    townhall_lv = townhall_lv[0]
    if townhall_lv == 'TH7-8' and isEight:
        townhall_lv = 'TH8'

    army += townhall_lv + f' Army Composition\n{bot.emoji.blank}'

    army += f'\n{bot.emoji.troop} {troopSpace} {bot.emoji.spells} {spell_space}\n{bot.emoji.blank}\n'

    army += troop_string + f'{bot.emoji.blank}\n'
    army += spell_string + f'{bot.emoji.blank}\n'
    army += sieges + f'{bot.emoji.blank}\n'
    army += f'**Clan Castle:**\n{bot.emoji.clan_castle.emoji_string} {clan_castle}'
    embed = disnake.Embed(title=nick, description=army, color=embed_color)
    embed.timestamp = pd.now(pd.UTC).now()
    return embed


def townhall_army(size: int):
    if size <= 20:
        return ['TH1', 1]
    elif size <= 30:
        return ['TH2', 2]
    elif size <= 70:
        return ['TH3', 3]
    elif size <= 80:
        return ['TH4', 4]
    elif size <= 135:
        return ['TH5', 5]
    elif size <= 150:
        return ['TH6', 6]
    elif size <= 200:
        return ['TH7-8', 7]
    elif size <= 220:
        return ['TH9', 9]
    elif size <= 240:
        return ['TH10', 10]
    elif size <= 260:
        return ['TH11', 11]
    elif size <= 280:
        return ['TH12', 12]
    elif size <= 300:
        return ['TH13-14', 13]
    elif size <= 320:
        return ['TH15+', 15]


def is_link_valid(link: str):
    if 'https://link.clashofclans.com/' not in link:
        return False

    if '?action=CopyArmy&army=' not in link:
        return False

    spot = link.find('=', link.find('=') + 1)
    link = link[spot + 1 :]

    if 'u' not in link and 's' not in link:
        return False

    letter_u_count = 0
    letter_s_count = 0
    for letter in link:
        if letter == 'u':
            letter_u_count += 1
        if letter == 's':
            letter_s_count += 1

    if letter_u_count > 1:
        return False
    if letter_s_count > 1:
        return False

    for character in link:
        if character == 'u' or character == 'x' or character == '-' or character.isdigit() or character == 's':
            pass
        else:
            return False

    troops_patten = 'u([\d+x-]+)'
    check_link_troops = re.split(troops_patten, link)
    if len(check_link_troops) > 1 and check_link_troops[1] != '':
        troops_str = check_link_troops[1].split('-')
        for troop in troops_str:
            strings = troop.split('x')
            if int(strings[0]) > MAX_ARMY_CAMP:  # check for a valid count of the unit
                # print('wrong count')
                return False
            if not troop_ids(int(strings[1])):  # check if it actually exists in dicts
                # print('wrong id')
                return False

    spells_patten = 's([\d+x-]+)'
    check_link_spells = re.split(spells_patten, link)
    if len(check_link_spells) > 1 and check_link_spells[1] != '':
        spells_str = check_link_spells[1].split('-')
        for spell in spells_str:
            string = spell.split('x')
            if int(string[0]) > MAX_NUM_SPELLS:  # check for a valid count of the unit
                return False
            if not spell_ids(int(string[1])):  # check if it actually exists in dicts
                return False

    return True


async def super_troop_embed(
    bot: CustomClient,
    clans: List[coc.Clan],
    super_troop: str,
    embed_color: disnake.Color = EMBED_COLOR_CLASS,
) -> List[disnake.Embed]:
    player_tags = [m.tag for clan in clans for m in clan.members]
    players = await bot.get_players(tags=player_tags, custom=False)
    players = [p for p in players if p.get_troop(name=super_troop) is not None and p.get_troop(name=super_troop).is_active]
    base_embed = disnake.Embed(title=f'Players with {super_troop}', color=embed_color)
    embeds = iter_embed_creation(
        base_embed=base_embed,
        iter=players,
        scheme='{x.clan.name} - {x.name} [{x.tag}]\n',
        brk=50,
    )
    return embeds


async def clan_boost_embeds(
    bot: CustomClient,
    clans: List[coc.Clan],
    embed_color: disnake.Color = EMBED_COLOR_CLASS,
) -> List[disnake.Embed]:
    player_tags = [m.tag for clan in clans for m in clan.members]
    players = await bot.get_players(tags=player_tags, custom=False)
    player_dict: Dict[coc.Clan, List[coc.Player]] = {}
    for clan in clans:
        player_dict[clan] = []
        for player in players.copy():
            if player.clan is not None and player.clan.tag == clan.tag:
                player_dict[clan].append(player)

    embeds = []
    for clan, players in player_dict.items():
        clan_boosted = defaultdict(list)
        for player in players:
            for troop in [t for t in player.troops if t.is_active and t.is_super_troop]:
                clan_boosted[troop.name].append(player.name)

        if bool(clan_boosted):
            embed = disnake.Embed(title=f'Boosted Troops', color=embed_color)
            for troop, members in clan_boosted.items():
                text = ''.join([f'- {member}\n' for member in members])
                embed.add_field(
                    name=f'{bot.fetch_emoji(troop)} {troop}',
                    value=text,
                    inline=False,
                )
                embed.timestamp = pd.now(pd.UTC)
                embed.set_footer(icon_url=clan.badge.url, text=clan.name)
            embeds.append(embed)

    if not embeds:
        raise MessageException('No Super Troops Boosted')
    return embeds
