#!/bin/bash python
# -*- coding: utf-8 -*-
from typing import List

from prodict import Prodict


class ComponentRequirement(Prodict):
    name: str
    amount: int
    value: int


class TransformedBP(Prodict):
    """
    This class is what the name, tier, costs and value look like for
    a Shop Titans blueprint when all crafting and ascension upgrades
    have been applied.
    """
    # general
    name: str
    tier: int
    value: int
    crafting_time: float
    workers: List[str]
    components: List[ComponentRequirement]
    # t1
    iron: int
    wood: int
    leather: int
    herbs: int
    # t2
    steel: int
    ironwood: int
    fabric: int
    oils: int
    # t3
    ether: int
    jewels: int


class TransformedBPData(Prodict):
    # general
    name: str
    value_per_minute_per_slot: float
    # t1
    iron_per_minute_per_slot: float
    wood_per_minute_per_slot: float
    leather_per_minute_per_slot: float
    herbs_per_minute_per_slot: float
    # t2
    steel_per_minute_per_slot: float
    ironwood_per_minute_per_slot: float
    fabric_per_minute_per_slot: float
    oils_per_minute_per_slot: float
    # t3
    ether_per_minute_per_slot: float
    jewels_per_minute_per_slot: float

    # t1
    value_per_iron: float
    value_per_wood: float
    value_per_leather: float
    value_per_herbs: float
    # t2
    value_per_steel: float
    value_per_ironwood: float
    value_per_fabric: float
    value_per_oils: float
    # t3
    value_per_ether: float
    value_per_jewels: float


class OutputSpacings(Prodict):
    # how many chars should each key take up in the txt output
    # general
    name: int
    value_per_minute_per_slot: int
    # t1
    iron_per_minute_per_slot: int
    wood_per_minute_per_slot: int
    leather_per_minute_per_slot: int
    herbs_per_minute_per_slot: int
    # t2
    steel_per_minute_per_slot: int
    ironwood_per_minute_per_slot: int
    fabric_per_minute_per_slot: int
    oils_per_minute_per_slot: int
    # t3
    ether_per_minute_per_slot: int
    jewels_per_minute_per_slot: int

    # t1
    value_per_iron: int
    value_per_wood: int
    value_per_leather: int
    value_per_herbs: int
    # t2
    value_per_steel: int
    value_per_ironwood: int
    value_per_fabric: int
    value_per_oils: int
    # t3
    value_per_ether: int
    value_per_jewels: int


# this has to be true for calculations to work
assert OutputSpacings().keys() == TransformedBPData().keys()


class FinalBPData(Prodict):
    transformed_data: TransformedBP
    calculated_values: TransformedBPData


class PlayerRegenerationValues(Prodict):
    # t1
    iron: float
    wood: float
    leather: float
    herbs: float
    # t2
    steel: float
    ironwood: float
    fabric: float
    oils: float
    # t3
    ether: float
    jewels: float


class WorkerLevels(Prodict):
    Wallace: int
    Julia: int
    Allan: int
    Maribel: int
    Grimar: int
    Katarina: int
    Freyja: int
    Theodore: int
    Evelyn: int
    Roxanne: int


class WorkerCraftTimes(Prodict):
    Wallace: float
    Julia: float
    Allan: float
    Maribel: float
    Grimar: float
    Katarina: float
    Freyja: float
    Theodore: float
    Evelyn: float
    Roxanne: float


class WorkerTranslationDict(Prodict):
    Blacksmith: str
    Tailor: str
    Carpenter: str
    Herbalist: str
    Wizard: str
    Jeweler: str
    Priestess: str
    Master: str
    Scholar: str
    Engineer: str


class GuildBoosts(Prodict):
    # add of these are additive
    craft_speed: float
    resource_generation: float
    quest_rest_speed: float
    xp_earned: float


class BuildingLevels(Prodict):
    IronMine: int
    Lumberyard: int
    Tannery: int
    Garden: int

    Smelter: int
    Sawmill: int
    WeaverMill: int
    OilPress: int

    EtherWell: int
    JewelStorehouse: int


class Ascensions(Prodict):
    Sword: int
    Axe: int
    Dagger: int
    Mace: int
    Spear: int
    Bow: int
    Staff: int
    Wand: int
    Crossbow: int
    Gun: int
    Herbal_Medicine: int
    Potion: int
    Spell: int
    Heavy_Armor: int
    Light_Armor: int
    Clothes: int
    Helmet: int
    Rogue_Hat: int
    Magician_Hat: int
    Gauntlets: int
    Gloves: int
    Heavy_Footwear: int
    Light_Footwear: int
    Shield: int
    Ring: int
    Amulet: int
    Element: int
    Spirit: int


class ShopTitansPlayerConfig(Prodict):
    workers: WorkerLevels
    buildings: BuildingLevels
    guild_boosts: GuildBoosts
    ascensions: Ascensions


class ShopTitansCalculatorConfig(Prodict):
    player_regen_values: PlayerRegenerationValues
    player_craft_times: WorkerCraftTimes