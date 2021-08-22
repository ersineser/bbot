from typing import Deque, Optional, Union
from datetime import time

from pydantic import BaseModel
from pydantic.class_validators import validator
from pydantic.error_wrappers import ValidationError

from .candle import Candle
from .ticker import MiniTicker, Ticker
from .depth import Depth5, Depth10, Depth20
from .orderbook import OrderBook
from .trade import AggTrade, Trade


class TimeFrame(BaseModel):
    """Holds all data related to market events between two points in time.
    A window is a sequence of timeframes. If only candle data is
    selected, then `timeframe` is equivalent to `candle`.
    Depth is the depthchart at close time of this timeframe.
    """
    _candle_prev_2s: Candle
    _miniticker_prev_2s: MiniTicker

    open_time:  time
    close_time: time

    candle:     Optional[Candle]
    miniticker: Optional[MiniTicker]
    ticker:     Optional[Ticker]
    depth:      Optional[Union[Depth5, Depth10, Depth20]]
    orderbook:  Optional[OrderBook]
    aggtrade:   Optional[Deque[AggTrade]]
    trade:      Optional[Deque[Trade]]



    @validator("candle")
    def update_candle(self, v):
        if self.candle == None:
            self._candle_prev_2s = v
            return v
        if v.open_time < self.open_time:
            raise ValidationError("Attempted to add candle to the wrong timeframe. Needs to be in a previous timeframe.")
        if v.close_time > self.close_time:
            raise ValidationError("Attempted to add candle to the wrong timeframe. Needs to be in the next timeframe.")

        # Update candle
        new = self.candle
        new.close_price = v.close_price
        new.high_price = v.high_price if v.high_price > new.high_price else new.high_price
        new.low_price = v.low_price if v.low_price < new.low_price else new.low_price

        is_new_1m = v.open_time != self._candle_prev_2s.open_time and v.closetime != self._candle_prev_2s.close_time
        if is_new_1m:
            new.base_volume += v.base_volume
            new.quote_volume += v.quote_volume
            new.base_volume_taker += v.base_volume_taker
            new.quote_volume_taker += v.quote_volume_taker
            new.n_trades += v.n_trades
        else:
            new.base_volume += v.base_volume - self._candle_prev_2s.base_volume
            new.quote_volume += v.quote_volume - self._candle_prev_2s.quote_volume
            new.base_volume_taker += v.base_volume_taker - self._candle_prev_2s.base_volume_taker
            new.quote_volume_taker += v.quote_volume_taker - self._candle_prev_2s.quote_volume_taker
            new.n_trades += v.n_trades - self._candle_prev_2s.n_trades

        self._candle_prev_2s = v
        return new