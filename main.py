#!/bin/bash python
# -*- coding: utf-8 -*-
import json
import re
import sys
import traceback
from argparse import ArgumentParser
from typing import List, Any, Callable, Union

import excel2json
from prodict import Prodict

DIVIDER_STRING = "-" * 20

ROUNDING_THRESHOLDS: dict = {
    10: 5,
    50: 10,
    1000: 50,
    10000: 500,
    100000: 5000,
    1000000: 50000
}

ResourceProductionDict: dict = {
    "t1": {
        1: 6,
        2: 6.5,
        3: 7,
        4: 7.5,
        5: 8,
        6: 8.5,
        7: 9,
        8: 9.5,
        9: 10,
        10: 10.75,
        11: 11.5,
        12: 12.25,
        13: 13,
        14: 13.75,
        15: 14.5,
        16: 15.25,
        17: 16,
        18: 17,
        19: 19,
        20: 22
    },
    "t2": {
        1: 0.7,
        2: 0.9,
        3: 1.1,
        4: 1.2,
        5: 1.5,
        6: 1.7,
        7: 1.9,
        8: 2.1,
        9: 2.3,
        10: 2.6,
        11: 2.9,
        12: 3.2,
        13: 3.5,
        14: 3.8,
        15: 4.1,
        16: 4.4,
        17: 4.7,
        18: 5.2,
        19: 6,
        20: 7
    },
    "t3": {
        1: 0.1,
        2: 0.15,
        3: 0.2,
        4: 0.25,
        5: 0.3,
        6: 0.35,
        7: 0.4,
        8: 0.45,
        9: 0.5,
        10: 0.55,
        11: 0.6,
        12: 0.65,
        13: 0.7,
        14: 0.75,
        15: 0.8,
        16: 0.85,
        17: 0.9,
        18: 1,
        19: 1.1,
        20: 1.25
    }
}

ResourceBuildingsTranslationDict: dict = {
    "IronMine": "iron",
    "Lumberyard": "wood",
    "Tannery": "leather",
    "Garden": "herbs",
    "Smelter": "steel",
    "Sawmill": "ironwood",
    "WeaverMill": "fabric",
    "OilPress": "oils",
    # TODO: fix to ether
    "EtherWell": "aether",
    "JewelStorehouse": "jewels"
}


def generate_args():
    """
    argparse is used to create CLI arguments. --help helps.
    :return: ArgumentParser object
    """
    args = ArgumentParser(
        description="Shop titans CLI arguments parser"
    )
    args.add_argument(
        "--spreadsheet", "-s",
        type=str,
        default="spreadsheet.xlsx"
    )
    args.add_argument(
        "--generate-data", "-g",
        action="store_true"
    )
    args.add_argument(
        "--config", "-c",
        type=str,
        default="config.json"
    )
    return args.parse_args()


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


class ShopTitansPlayerConfig(Prodict):
    workers: WorkerLevels
    buildings: BuildingLevels
    guild_boosts: GuildBoosts


class ShopTitansCalculatorConfig(Prodict):
    player_regen_values: PlayerRegenerationValues
    player_craft_times: WorkerCraftTimes


class ShopTitansCalculator:
    class DataNotGeneratedError(Exception):
        pass

    def __init__(self, config_file: str):
        # prep player config
        raw_data = json.load(open(config_file))
        try:
            self.player_config = ShopTitansPlayerConfig(**raw_data)
        except ValueError:
            print("Invalid JSON input file")
        # prep translation data for workers
        raw_worker_translation_data = json.load(open("spreadsheet_data/Workers.json"))
        worker_translation_data = dict()
        for worker in raw_worker_translation_data:
            worker_translation_data[worker["Worker"]] = worker["Name"]
        self.worker_translation_dict = WorkerTranslationDict(**worker_translation_data)
        # prep calc config
        self.calc_config = self.generate_calc_config()

    @staticmethod
    def generate_data(spreadsheet_file):
        excel2json.convert_from_file(spreadsheet_file, "spreadsheet_data")

    def data_not_generated(self):
        raise self.DataNotGeneratedError("Data is not generated")

    def generate_calc_config(self) -> ShopTitansCalculatorConfig:
        try:
            result = ShopTitansCalculatorConfig()
            levels_json = json.load(open("spreadsheet_data/Worker Levels.json"))
            translation_dict = dict()
            translation_dict[1] = 0
            for level in levels_json:
                try:
                    worker_level = int(level["Worker Level"])
                    # craft speed needs to be rounded to 2 decimals, because lulfloats
                    craft_speed = round(
                        1.0 - float(level["Crafting Speed Bonus"]), 2
                    )
                    translation_dict[worker_level] = craft_speed
                except ValueError:
                    pass

            print(DIVIDER_STRING)
            result.player_craft_times = WorkerCraftTimes()
            for worker, worker_level in self.player_config.workers.items():
                craft_time = translation_dict[worker_level] * self.player_config.guild_boosts.craft_speed
                result.player_craft_times.set_attribute(worker, craft_time)
                print(f"Worker: {worker}, "
                      f"level: {worker_level}, "
                      f"craft time coefficient: {round(result.player_craft_times[worker], 2)}")
            print(DIVIDER_STRING)

            regen_dict_data = {
                "iron": ResourceProductionDict["t1"][self.player_config.buildings.IronMine] *
                        self.player_config.guild_boosts.resource_generation,
                "wood": ResourceProductionDict["t1"][self.player_config.buildings.Lumberyard] *
                        self.player_config.guild_boosts.resource_generation,
                "leather": ResourceProductionDict["t1"][self.player_config.buildings.Tannery] *
                           self.player_config.guild_boosts.resource_generation,
                "herbs": ResourceProductionDict["t1"][self.player_config.buildings.Garden] *
                         self.player_config.guild_boosts.resource_generation,

                "steel": ResourceProductionDict["t1"][self.player_config.buildings.Smelter] *
                         self.player_config.guild_boosts.resource_generation,
                "ironwood": ResourceProductionDict["t1"][self.player_config.buildings.Sawmill] *
                            self.player_config.guild_boosts.resource_generation,
                "fabric": ResourceProductionDict["t1"][self.player_config.buildings.WeaverMill] *
                          self.player_config.guild_boosts.resource_generation,
                "oils": ResourceProductionDict["t1"][self.player_config.buildings.OilPress] *
                        self.player_config.guild_boosts.resource_generation,

                "aether": ResourceProductionDict["t1"][self.player_config.buildings.EtherWell] *
                          self.player_config.guild_boosts.resource_generation,
                "jewels": ResourceProductionDict["t1"][self.player_config.buildings.JewelStorehouse] *
                          self.player_config.guild_boosts.resource_generation,
            }
            regen_values = PlayerRegenerationValues(**regen_dict_data)
            result.set_attribute("player_regen_values", regen_values)
            for building, building_level in self.player_config.buildings.items():
                print(f"Building {building}, "
                      f"level: {building_level}, "
                      f"regen rate: {round(result.player_regen_values[ResourceBuildingsTranslationDict[building]], 2)}")
            print(DIVIDER_STRING)

            return result
        except ValueError:
            traceback.print_exc(

            )
            self.data_not_generated()

    def calculate(self):
        # make sure base_keys are lowercase
        special_base_keys = [
            "crafting time (seconds)",
            "required worker",
            "required worker "
        ]
        base_keys = [
            "name",
            "value",
            "tier",
            "iron",
            "wood",
            "leather",
            "herbs",
            "steel",
            "ironwood",
            "oils",
            "fabric",
            # TODO: fix to ether
            "aether",
            "jewels"
        ]
        assert False not in [x.lower() == x for x in special_base_keys]
        assert False not in [x.lower() == x for x in base_keys]
        upgrade_keys = [
            "Crafting Upgrade 1",
            "Crafting Upgrade 2",
            "Crafting Upgrade 3",
            "Crafting Upgrade 4",
            "Crafting Upgrade 5",
            "Ascension Upgrade 1",
            "Ascension Upgrade 2",
            "Ascension Upgrade 3"
        ]
        bp_json: List[dict] = json.load(open("spreadsheet_data/Blueprints.json"))
        components_json = json.load(open("spreadsheet_data/Quest Components.json"))

        # apply upgrades to blueprints (mastery, ascensions)
        transformed_bps = list()
        for blueprint in bp_json:
            transformed_bp = TransformedBP(
                workers=list()
            )
            # transformed_bp.workers = list()
            # get base values
            for key, value in blueprint.items():
                if key.lower() in base_keys:
                    # skip empty keys
                    if value == "---":
                        continue
                    try:
                        if key.lower() == "aether":
                            transformed_bp.set_attribute("ether", value)
                        else:
                            transformed_bp.set_attribute(key.lower(), value)
                    except ValueError:
                        pass
                elif key.lower() in special_base_keys:
                    if key.lower() == "crafting time (seconds)":
                        transformed_bp.set_attribute("crafting_time", value)
                    elif key.lower() in ["required worker", "required worker "]:
                        if value in self.worker_translation_dict:
                            transformed_bp.workers.append(self.worker_translation_dict[value])

            # fix value, resource costs
            resource_regex = r"-(\d+) (\w+) Spent"
            for key, value in blueprint.items():
                adjusted_value_coeffient = 1
                adjusted_time_coefficient = 1
                if key in upgrade_keys:
                    # extract value increase
                    if "Value Increase" in value:
                        adjusted_value_coeffient *= float(value.split()[0][1:])
                    elif "Craft Time Reduction" in value:
                        extracted_coefficient = float(1 - (float(value.split()[0][1:-1]) / 100))
                        adjusted_time_coefficient *= extracted_coefficient
                    elif re.match(resource_regex, value):
                        amount, resource = re.findall(resource_regex, value)[0]
                        amount = int(amount)
                        if resource.lower() in transformed_bp:
                            transformed_bp.set_attribute(
                                resource.lower(),
                                transformed_bp[resource.lower()] - amount
                            )
                transformed_bp.value *= adjusted_value_coeffient
                transformed_bp.crafting_time *= adjusted_time_coefficient
            # apply player values
            for worker in transformed_bp.workers:
                transformed_bp.crafting_time *= self.calc_config.player_craft_times[worker]
            # round value
            transformed_bp.value = self._round(transformed_bp.value)
            transformed_bps.append(transformed_bp)

        # now prep the data from transformed BPs
        final_data_list: List[FinalBPData] = list()
        no_resource_found = -1
        # noinspection PyUnusedLocal
        resource_gone_fix: Callable[[Any], Union[int, Any]] = lambda x: no_resource_found if x == 0 else x
        for transformed_bp in transformed_bps:
            # get value, calculate profit
            value = transformed_bp.value

            # in mins
            craft_time = transformed_bp.crafting_time / 60
            # resources
            # if upgrades make a resource go to 0, choose -1
            # t1
            iron: int = max(resource_gone_fix(transformed_bp.get("iron", no_resource_found)), no_resource_found)
            wood: int = max(resource_gone_fix(transformed_bp.get("wood", no_resource_found)), no_resource_found)
            leather: int = max(resource_gone_fix(transformed_bp.get("leather", no_resource_found)), no_resource_found)
            herbs: int = max(resource_gone_fix(transformed_bp.get("herbs", no_resource_found)), no_resource_found)
            # t2
            steel: int = max(resource_gone_fix(transformed_bp.get("steel", no_resource_found)), no_resource_found)
            ironwood: int = max(resource_gone_fix(transformed_bp.get("ironwood", no_resource_found)), no_resource_found)
            fabric: int = max(resource_gone_fix(transformed_bp.get("fabric", no_resource_found)), no_resource_found)
            oils: int = max(resource_gone_fix(transformed_bp.get("oils", no_resource_found)), no_resource_found)
            # t3
            ether: int = max(resource_gone_fix(transformed_bp.get("ether", no_resource_found)), no_resource_found)
            jewels: int = max(resource_gone_fix(transformed_bp.get("jewels", no_resource_found)), no_resource_found)
            calculated_data = TransformedBPData(
                # general
                name=transformed_bp.name,
                value_per_minute_per_slot=value / craft_time,
                profit_per_minute_per_slot=profit / craft_time,
                # if iron < 0 due to point above, choose 0
                # t1
                iron_per_minute_per_slot=max(iron / craft_time, 0),
                wood_per_minute_per_slot=max(wood / craft_time, 0),
                leather_per_minute_per_slot=max(leather / craft_time, 0),
                herbs_per_minute_per_slot=max(herbs / craft_time, 0),
                # t2
                steel_per_minute_per_slot=max(steel / craft_time, 0),
                ironwood_per_minute_per_slot=max(ironwood / craft_time, 0),
                fabric_per_minute_per_slot=max(fabric / craft_time, 0),
                oils_per_minute_per_slot=max(oils / craft_time, 0),
                # t3
                ether_per_minute_per_slot=max(ether / craft_time, 0),
                jewels_per_minute_per_slot=max(jewels / craft_time, 0),
                # t1
                value_per_iron=max(value / iron, 0),
                value_per_wood=max(value / wood, 0),
                value_per_leather=max(value / leather, 0),
                value_per_herbs=max(value / herbs, 0),
                # t2
                value_per_steel=max(value / steel, 0),
                value_per_ironwood=max(value / ironwood, 0),
                value_per_fabric=max(value / fabric, 0),
                value_per_oils=max(value / oils, 0),
                # t3
                value_per_ether=max(value / ether, 0),
                value_per_jewels=max(value / jewels, 0)
            )
            final_data_list.append(
                FinalBPData(
                    transformed_data=transformed_bp,
                    calculated_values=calculated_data
                )
            )

        input(json.dumps(final_data_list, indent=4))

    @staticmethod
    def _round(value):
        def based_round(x: float, rounding_base: int):
            return int(rounding_base * round(x / rounding_base))

        for threshold, base in ROUNDING_THRESHOLDS.items():
            if value >= threshold:
                return based_round(value, base)
        # if somehow this fails, just return value
        return int(value)


def main():
    args = generate_args()
    if args.generate_data:
        ShopTitansCalculator.generate_data(args.spreadsheet)
        print("Data has been generated")
        sys.exit(0)
    calc = ShopTitansCalculator(
        config_file=args.config
    )
    calc.calculate()
    sys.exit(0)


if __name__ == '__main__':
    main()
