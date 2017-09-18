from enum import Enum, unique


@unique
class CFR(Enum):
    PART = 'part'
    SUBPART = 'subpart'
    SUBJGRP = 'subjgrp'
    SEC = 'sec'
    APP = 'app'
    APPSEC = 'appsec'
    PAR = 'par'
    DEFPAR = 'defpar'
    LVL1 = 'lvl1'
    LVL2 = 'lvl2'
    LVL3 = 'lvl3'
    LVL4 = 'lvl4'
    LVL5 = 'lvl5'
    LVL6 = 'lvl6'
