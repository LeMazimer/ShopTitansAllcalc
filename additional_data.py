#!/bin/bash python
# -*- coding: utf-8 -*-
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
    "EtherWell": "ether",
    "JewelStorehouse": "jewels"
}
