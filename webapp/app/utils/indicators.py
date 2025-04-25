from decimal import Decimal
from typing import List, Dict, Any
from ..models.quote import Quote

def calculate_sma(quotes: List[Quote], period: int) -> List[Decimal]:
    """Calculate Simple Moving Average"""
    if len(quotes) < period:
        return [None] * len(quotes)
    
    sma_values = []
    for i in range(len(quotes)):
        if i < period - 1:
            sma_values.append(None)
        else:
            sum_close = sum(quote.close for quote in quotes[i-period+1:i+1])
            sma_values.append(sum_close / Decimal(period))
    
    return sma_values

def calculate_bollinger_bands(quotes: List[Quote], period: int, std_dev: int) -> Dict[str, List[Decimal]]:
    """Calculate Bollinger Bands"""
    sma = calculate_sma(quotes, period)
    std_values = []
    
    for i in range(len(quotes)):
        if i < period - 1:
            std_values.append(None)
        else:
            prices = [quote.close for quote in quotes[i-period+1:i+1]]
            mean = sum(prices) / Decimal(len(prices))
            squared_diff_sum = sum((price - mean) ** 2 for price in prices)
            std = (squared_diff_sum / Decimal(len(prices))) ** Decimal('0.5')
            std_values.append(std)
    
    upper_band = []
    lower_band = []
    
    for i in range(len(quotes)):
        if sma[i] is None:
            upper_band.append(None)
            lower_band.append(None)
        else:
            upper_band.append(sma[i] + Decimal(std_dev) * std_values[i])
            lower_band.append(sma[i] - Decimal(std_dev) * std_values[i])
    
    return {
        'sma': sma,
        'upper_band': upper_band,
        'lower_band': lower_band
    }

def calculate_supertrend(quotes: List[Quote], period: int, multiplier: int) -> Dict[str, List[Any]]:
    """Calculate SuperTrend indicator"""
    atr = calculate_atr(quotes, period)
    supertrend = []
    direction = []
    
    for i in range(len(quotes)):
        if i < period:
            supertrend.append(None)
            direction.append(0)
        else:
            close = quotes[i].close
            high = quotes[i].high
            low = quotes[i].low
            
            if supertrend[i-1] is None:
                supertrend.append(close)
                direction.append(1)
            else:
                basic_upper = (high + low) / Decimal('2') + multiplier * atr[i]
                basic_lower = (high + low) / Decimal('2') - multiplier * atr[i]
                
                if direction[i-1] == 1:
                    if close < supertrend[i-1]:
                        supertrend.append(basic_lower)
                        direction.append(-1)
                    else:
                        supertrend.append(max(basic_lower, supertrend[i-1]))
                        direction.append(1)
                else:
                    if close > supertrend[i-1]:
                        supertrend.append(basic_upper)
                        direction.append(1)
                    else:
                        supertrend.append(min(basic_upper, supertrend[i-1]))
                        direction.append(-1)
    
    return {
        'supertrend': supertrend,
        'direction': direction
    }

def calculate_macd(quotes: List[Quote], fast_period: int, slow_period: int, signal_period: int) -> Dict[str, List[Decimal]]:
    """Calculate MACD indicator"""
    fast_ema = calculate_ema(quotes, fast_period)
    slow_ema = calculate_ema(quotes, slow_period)
    
    macd_line = []
    for i in range(len(quotes)):
        if fast_ema[i] is None or slow_ema[i] is None:
            macd_line.append(None)
        else:
            macd_line.append(fast_ema[i] - slow_ema[i])
    
    signal_line = calculate_ema([Quote(quotes[i].date, Decimal('0'), Decimal('0'), Decimal('0'), macd_line[i], Decimal('0')) 
                               for i in range(len(quotes)) if macd_line[i] is not None], signal_period)
    
    histogram = []
    for i in range(len(quotes)):
        if macd_line[i] is None or signal_line[i] is None:
            histogram.append(None)
        else:
            histogram.append(macd_line[i] - signal_line[i])
    
    return {
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram
    }

def calculate_rsi(quotes: List[Quote], period: int) -> List[Decimal]:
    """Calculate Relative Strength Index"""
    if len(quotes) < period + 1:
        return [None] * len(quotes)
    
    gains = []
    losses = []
    
    for i in range(1, len(quotes)):
        change = quotes[i].close - quotes[i-1].close
        gains.append(max(change, Decimal('0')))
        losses.append(max(-change, Decimal('0')))
    
    avg_gain = sum(gains[:period]) / Decimal(period)
    avg_loss = sum(losses[:period]) / Decimal(period)
    
    rsi_values = []
    for i in range(len(quotes)):
        if i < period:
            rsi_values.append(None)
        else:
            if avg_loss == Decimal('0'):
                rsi_values.append(Decimal('100'))
            else:
                rs = avg_gain / avg_loss
                rsi = Decimal('100') - (Decimal('100') / (Decimal('1') + rs))
                rsi_values.append(rsi)
            
            if i < len(quotes) - 1:
                avg_gain = (avg_gain * Decimal(period - 1) + gains[i]) / Decimal(period)
                avg_loss = (avg_loss * Decimal(period - 1) + losses[i]) / Decimal(period)
    
    return rsi_values

def calculate_atr(quotes: List[Quote], period: int) -> List[Decimal]:
    """Calculate Average True Range"""
    if len(quotes) < 2:
        return [None] * len(quotes)
    
    tr_values = []
    for i in range(1, len(quotes)):
        high = quotes[i].high
        low = quotes[i].low
        prev_close = quotes[i-1].close
        
        tr1 = high - low
        tr2 = abs(high - prev_close)
        tr3 = abs(low - prev_close)
        
        tr_values.append(max(tr1, tr2, tr3))
    
    atr_values = []
    for i in range(len(quotes)):
        if i < period:
            atr_values.append(None)
        else:
            atr = sum(tr_values[i-period:i]) / Decimal(period)
            atr_values.append(atr)
    
    return atr_values

def calculate_ema(quotes: List[Quote], period: int) -> List[Decimal]:
    """Calculate Exponential Moving Average"""
    if len(quotes) < period:
        return [None] * len(quotes)
    
    multiplier = Decimal('2') / Decimal(period + 1)
    ema_values = []
    
    # Calculate first EMA using SMA
    sma = sum(quote.close for quote in quotes[:period]) / Decimal(period)
    ema_values.append(sma)
    
    for i in range(1, len(quotes)):
        if i < period:
            ema_values.append(None)
        else:
            ema = (quotes[i].close - ema_values[-1]) * multiplier + ema_values[-1]
            ema_values.append(ema)
    
    return ema_values

def calculate_indicators(quotes: List[Quote]) -> Dict[str, Any]:
    """Calculate all technical indicators"""
    return {
        'sma_20': calculate_sma(quotes, 20),
        'sma_50': calculate_sma(quotes, 50),
        'sma_200': calculate_sma(quotes, 200),
        'bb': calculate_bollinger_bands(quotes, 20, 2),
        'supertrend': calculate_supertrend(quotes, 10, 3),
        'macd': calculate_macd(quotes, 12, 26, 9),
        'rsi': calculate_rsi(quotes, 14),
        'atr': calculate_atr(quotes, 14)
    } 