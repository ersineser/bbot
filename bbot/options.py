'''

All options go inside Options class

'''
from enum import Enum
from typing import Optional, Union, Dict, List

class Interval(Enum):
    # name = interval, value = time in ms
    s2:  2000
    m1:  60000
    m3:  180000
    m5:  300000
    m15: 900000
    m30: 1800000
    h1:  3600000
    h2:  7200000
    h4:  14400000
    h6:  21600000
    h8:  28800000
    h12: 43200000
    d1:  86400000
    d3:  259200000
    w1:  604800000
    M1:  2419200000 # TODO: varies
class Mode(Enum):
    DEBUG:   0
    HISTORY: 1
    STREAM:  2
    PAPER:   3
    TESTNET: 4
    TRADE:   5
class Options:
    
    def __init__(self, 
                 mode:         Optional[str]                   = 'DEBUG',
                 base_assets:  Optional[Union[str, List[str]]] = 'BTC',
                 quote_assets: Optional[Union[str, List[str]]] = 'USDT',
                 windows:      Optional[Dict[str, int]]        = {
                     '1m'   : 500, 
                     '15m'  : 200
                    }
                 ):

        self.mode         = self._verify_clean_mode(mode)
        self.base_assets  = self._verify_clean_base_assets(base_assets)
        self.quote_assets = self._verify_clean_quote_assets(quote_assets)
        self.windows      = self._verify_clean_windows(windows)


    def _verify_clean_mode(mode: str) -> Mode:
        #TODO
        return Mode.DEBUG

    def _verify_clean_base_assets(base_assets: Union[str, List[str]]) -> List[str]:
        #TODO
        return ['BTC',]

    def _verify_clean_quote_assets(quote_assets: Union[str, List[str]]) -> List[str]:
        #TODO
        return ['USDT']

    def _verify_clean_windows(windows: Dict[str, int]) -> Dict[Interval, int]:
        #TODO
        return {'1m': 500, '15m': 200}