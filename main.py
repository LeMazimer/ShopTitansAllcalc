#!/bin/bash python
# -*- coding: utf-8 -*-
import json
import re
import sys
import traceback
from argparse import ArgumentParser
from typing import List, Any, Callable, Union

import excel2json

from additional_data import *
from class_definitions import *


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


class ShopTitansCalculator:
    class DataNotGeneratedError(Exception):
        pass

    def __init__(self, config_file: str):
        # prep result file
        self.result_file = open("result.txt", "w")
        # self.result_json = open("result.json", "w")
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

    def _write(self, msg: str):
        print(msg)
        self.result_file.write(f"{msg}\n")
        return None

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

            self._write(DIVIDER_STRING)
            result.player_craft_times = WorkerCraftTimes()
            for worker, worker_level in self.player_config.workers.items():
                craft_time = translation_dict[worker_level] * self.player_config.guild_boosts.craft_speed
                result.player_craft_times.set_attribute(worker, craft_time)
                self._write(f"Worker: {worker}, "
                            f"level: {worker_level}, "
                            f"craft time coefficient: {round(result.player_craft_times[worker], 2)}")
            self._write(DIVIDER_STRING)

            regen_dict_data = {
                "iron": ResourceProductionDict["t1"][self.player_config.buildings.IronMine] *
                self.player_config.guild_boosts.resource_generation,
                "wood": ResourceProductionDict["t1"][self.player_config.buildings.Lumberyard] *
                self.player_config.guild_boosts.resource_generation,
                "leather": ResourceProductionDict["t1"][self.player_config.buildings.Tannery] *
                self.player_config.guild_boosts.resource_generation,
                "herbs": ResourceProductionDict["t1"][self.player_config.buildings.Garden] *
                self.player_config.guild_boosts.resource_generation,
                "steel": ResourceProductionDict["t2"][self.player_config.buildings.Smelter] *
                self.player_config.guild_boosts.resource_generation,
                "ironwood": ResourceProductionDict["t2"][self.player_config.buildings.Sawmill] *
                self.player_config.guild_boosts.resource_generation,
                "fabric": ResourceProductionDict["t2"][self.player_config.buildings.WeaverMill] *
                self.player_config.guild_boosts.resource_generation,
                "oils": ResourceProductionDict["t2"][self.player_config.buildings.OilPress] *
                self.player_config.guild_boosts.resource_generation,
                "ether": ResourceProductionDict["t3"][self.player_config.buildings.EtherWell] *
                self.player_config.guild_boosts.resource_generation,
                "jewels": ResourceProductionDict["t3"][self.player_config.buildings.JewelStorehouse] *
                self.player_config.guild_boosts.resource_generation,
            }
            regen_values = PlayerRegenerationValues(**regen_dict_data)
            result.set_attribute("player_regen_values", regen_values)
            for building, building_level in self.player_config.buildings.items():
                self._write(
                    f"Building {building}, "
                    f"level: {building_level}, "
                    f"regen rate: {round(result.player_regen_values[ResourceBuildingsTranslationDict[building]], 2)}"
                )
            self._write(DIVIDER_STRING)

            return result
        except ValueError:
            traceback.print_exc()
            self.result_file.close()
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
            "ether",
            "jewels"
        ]
        # make sure these are all lowercase
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

        # apply upgrades to blueprints (mastery, ascensions)
        transformed_bps = list()
        for blueprint in bp_json:
            transformed_bp = TransformedBP(
                workers=list(),
                components=list()
            )
            # transformed_bp.workers = list()
            # get base values
            for key, value in blueprint.items():
                if key.lower() in base_keys:
                    # skip empty keys
                    if value == "---":
                        continue
                    try:
                        transformed_bp.set_attribute(key.lower(), value)
                    except ValueError:
                        pass
                elif key.lower() in special_base_keys:
                    if key.lower() == "crafting time (seconds)":
                        transformed_bp.set_attribute("crafting_time", value)
                    elif key.lower() in ["required worker", "required worker "]:
                        if value in self.worker_translation_dict:
                            transformed_bp.workers.append(self.worker_translation_dict[value])
            component_1 = blueprint.get("Component1", str()) if blueprint.get("Component1", str()) != "---" else str()
            quality_1 = blueprint.get("Component Quality1", str()) if blueprint.get("Component Quality1", str()) != "---" else str()
            amount_1 = blueprint.get("Amount Needed1", str())
            component_2 = blueprint.get("Component2", str())
            quality_2 = blueprint.get("Component Quality2", str())
            amount_2 = blueprint.get("Amount Needed2", str())
            transformed_bp.components.append(
                ComponentRequirement(
                    name=component_1,
                    amount=amount_1,
                    value=0
                )
            )
            transformed_bp.components.append(
                ComponentRequirement(
                    name=component_2,
                    amount=amount_2,
                    value=0
                )
            )

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
            profit = value
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
        spacings = OutputSpacings(
            # general
            name=30,
            value_per_minute_per_slot=40,
            profit_per_minute_per_slot=40,
            # t1
            iron_per_minute_per_slot=40,
            wood_per_minute_per_slot=40,
            leather_per_minute_per_slot=40,
            herbs_per_minute_per_slot=40,
            # t2
            steel_per_minute_per_slot=40,
            ironwood_per_minute_per_slot=40,
            fabric_per_minute_per_slot=40,
            oils_per_minute_per_slot=40,
            # t3
            ether_per_minute_per_slot=40,
            jewels_per_minute_per_slot=40,
            # t1
            value_per_iron=40,
            value_per_wood=40,
            value_per_leather=40,
            value_per_herbs=40,
            # t2
            value_per_steel=40,
            value_per_ironwood=40,
            value_per_fabric=40,
            value_per_oils=40,
            # t3
            value_per_ether=40,
            value_per_jewels=40
        )
        header = str()
        for key, spacing in spacings.items():
            key = key.replace("_per_", "/")
            header += key.center(spacing) + "|"
        self._write(
            msg=header
        )
        for bp in final_data_list:
            write_line = str()
            for key, spacing in spacings.items():
                current_key_value = bp.calculated_values.get(key)
                if isinstance(current_key_value, float):
                    current_key_value = round(current_key_value, 3)
                write_line += str(current_key_value).center(spacing) + "|"
            # input(json.dumps(final_data_list, indent=4))
            self._write(msg=write_line)

        self.result_file.close()

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
