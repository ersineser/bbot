import asyncio
from abc import abstractmethod, ABCMeta
from typing import Any, Dict, List, FrozenSet


from ..data.candle     import Candle
from ..data.database   import Database
from ..data.user_event import UserEvent
from ..options         import Interval, Options

class BaseClient(metaclass=ABCMeta):
    """Abstract interface for all exchange clients.
    Only for Binance a client is implemented.
    """


    def __init__(self, options: Options):
        """All bootstrapping logic of client is defined here.
        Client is spawned in a separate process.
        1) Initialize Database
        2) Create event loop
        3) Initialize client object
        4) Discover all pairs on the exchange and make a selection
        5) Start all downloads and streams
        """

        # 1
        self.options = options
        self.db = self._create_database(self.options)
        # 2
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        # 3
        self.client = self._create_async_client(self.options)
        # 4
        raw = self._download_all_symbols(self.client)

        parsed = self._parse_all_symbols(raw)
        self.db.all_symbols = parsed

        filtered = self.db._filter_symbols(parsed)
        self.db.selected_symbols = filtered
        # 5
        self._start_coroutines(filtered, self.client)
        


    def _create_database(self, options: Options) -> Database:
        """Returns a Database object that contains all data.
        It needs to be initialized in the separate process where
        the API client lives. Not in the main process.
        """

        return Database(options)

    
    @abstractmethod
    def _shutdown():
        """Shutdown client."""
        
        raise NotImplementedError


    @abstractmethod
    async def _create_async_client(options: Options) -> Any:
        """Returns some client object. In the case of Binance this
        is the python-binance.AsyncClient object. This object is
        passed as an argument in all functions that do API calls.
        """

        raise NotImplementedError
    

    @abstractmethod
    async def _download_all_symbols(self, client: Any) -> Any:
        """Downloads *some data* that contains all symbols of the 
        pairs being traded at the exchange. An example of a symbol 
        is 'BTCUSDT'. Return this data as provided by the API.
        """

        raise NotImplementedError


    @abstractmethod
    def _parse_all_symbols(raw: Any) -> FrozenSet[str]:
        """Filters and returns all symbols of pairs being traded
        at the exchange from raw data and returns them as a set.
        """

        raise NotImplementedError
    

    async def _start_coroutines(self, symbols: FrozenSet[str], client: Any, db: Database) -> None:
        _hist = asyncio.create_task(self._download_history(symbols, client, db))
        _cs   = asyncio.create_task(self._start_candle_sockets(symbols, client))
        _us   = asyncio.create_task(self._start_user_socket(client))
        await _cs, _hist, _us


    @abstractmethod
    async def _download_history(symbols: FrozenSet[str], client: Any, db: Database) -> None:
        """Downloads all windows of historical candlestick data, 
        as raw data in the format provided by the API. Then iterates through
        each window and passes a single candle to _parse_historical_candle().
        """
    
        raise NotImplementedError


    @abstractmethod
    def _parse_historical_candle(raw: Any, symbol: str, interval: Interval, db: Database) -> None:
        """Takes single candle from raw historical candlestick data coming 
        from _download_history() and transforms it to a Candle object.
        Then passes this candle object to the corresponding Window instance in 
        db.<Pair>.<Window>._add_historical_candle().
        """

        raise NotImplementedError


    @abstractmethod
    async def _start_candle_sockets(symbols: FrozenSet[str], client: Any, db: Database) -> None:
        """Starts one or multiple websockets that stream candlestick data.
        Each socket streams data related to one pair. Only time interval 
        1 minute is streamed. Other intervals are calculated on the fly later.
        Passes parsed candle to db.<Pair>._calc_window_rolls().
        """
              
        raise NotImplementedError


    @abstractmethod
    def _parse_candle(raw: Any) -> Candle:
        """Takes raw data of a single candle and returns a Candle object."""
        
        raise NotImplementedError


    @abstractmethod
    async def _start_user_socket(client: Any) -> None:
        """Starts a websocket that listens to user events."""
        
        raise NotImplementedError


    @abstractmethod
    def _parse_user_event(event: Any) -> UserEvent:
        """Parses a message from a user socket. This message is one of
        the following events:
        1) Account update
        2) Order update
        3) Trade update
        """
        
        raise NotImplementedError