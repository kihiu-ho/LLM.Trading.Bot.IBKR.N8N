import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import io
from decimal import Decimal
from ..models.quote import Quote
from ..utils.indicators import calculate_indicators
import logging

logger = logging.getLogger(__name__)

class TechnicalChartService:
    @staticmethod
    def generate_chart(df, symbol, width=1920, height=2048):
        """Generate technical analysis chart with improved visualization"""
        try:
            # Convert DataFrame to Quote objects
            quotes = [
                Quote(
                    date=row['Date'].to_pydatetime(),
                    open=Decimal(str(row['Open'])),
                    high=Decimal(str(row['High'])),
                    low=Decimal(str(row['Low'])),
                    close=Decimal(str(row['Close'])),
                    volume=Decimal(str(row['Volume']))
                )
                for _, row in df.iterrows()
            ]

            # Calculate indicators
            indicators_dict = calculate_indicators(quotes)
            processed_indicators = TechnicalChartService.process_indicators(indicators_dict, df)

            # Create figure with subplots
            fig = make_subplots(
                rows=7, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                subplot_titles=(
                    f"{symbol} Price",
                    "SuperTrend",
                    "Volume (M)",
                    "MACD",
                    "RSI",
                    f"OBV ({processed_indicators['obv_unit']})",
                    "ATR"
                ),
                row_heights=[0.35, 0.15, 0.1, 0.15, 0.15, 0.1, 0.1],
                specs=[[{"secondary_y": True}]] * 7
            )

            # Add price chart
            TechnicalChartService.add_price_chart(fig, df, processed_indicators, symbol)
            
            # Add SuperTrend
            TechnicalChartService.add_supertrend(fig, df, processed_indicators)
            
            # Add Volume
            TechnicalChartService.add_volume(fig, df, processed_indicators)
            
            # Add MACD
            TechnicalChartService.add_macd(fig, df, processed_indicators)
            
            # Add RSI
            TechnicalChartService.add_rsi(fig, df, processed_indicators)
            
            # Add OBV
            TechnicalChartService.add_obv(fig, df, processed_indicators)
            
            # Add ATR
            TechnicalChartService.add_atr(fig, df, processed_indicators)

            # Update layout
            TechnicalChartService.update_layout(fig, symbol, df)

            # Convert to image
            buf = io.BytesIO()
            pio.write_image(fig, buf, format='jpeg', width=width, height=height)
            buf.seek(0)
            return buf

        except Exception as e:
            logger.error(f"Error generating technical chart: {str(e)}")
            raise

    @staticmethod
    def add_price_chart(fig, df, indicators, symbol):
        """Add price chart with moving averages and Bollinger Bands"""
        dates = df['Date']
        latest = df.iloc[-1]

        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=dates,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name=f'{symbol} Price',
                increasing_line_color='green',
                decreasing_line_color='red'
            ),
            row=1, col=1
        )

        # Moving averages
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=indicators['sma_20'],
                mode='lines',
                name='SMA 20',
                line=dict(color='blue')
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=indicators['sma_50'],
                mode='lines',
                name='SMA 50',
                line=dict(color='rgb(47,203,13)', width=2)
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=indicators['sma_200'],
                mode='lines',
                name='SMA 200',
                line=dict(color='rgb(240,130,21)', width=1)
            ),
            row=1, col=1
        )

        # Bollinger Bands
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=indicators['bb_upper'],
                mode='lines',
                name='BB Upper',
                line=dict(color='rgb(33,150,243)', width=1)
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=indicators['bb_lower'],
                mode='lines',
                name='BB Lower',
                line=dict(color='rgb(33,150,243)', width=1),
                fill='tonexty',
                fillcolor='rgba(33,150,243,0.1)'
            ),
            row=1, col=1
        )

    @staticmethod
    def add_supertrend(fig, df, indicators):
        """Add SuperTrend indicator"""
        dates = df['Date']
        st_up = [v if d == 1 else None for v, d in zip(indicators['st_values'], indicators['st_direction'])]
        st_down = [v if d == -1 else None for v, d in zip(indicators['st_values'], indicators['st_direction'])]

        fig.add_trace(
            go.Scatter(
                x=dates,
                y=st_up,
                mode='lines',
                name='SuperTrend Up',
                line=dict(color='rgb(0,128,0)')
            ),
            row=2, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=st_down,
                mode='lines',
                name='SuperTrend Down',
                line=dict(color='rgb(128,0,0)')
            ),
            row=2, col=1
        )

    @staticmethod
    def add_volume(fig, df, indicators):
        """Add volume chart"""
        dates = df['Date']
        colors = ['green' if df['Close'][i] >= df['Open'][i] else 'red' for i in range(len(df))]

        fig.add_trace(
            go.Bar(
                x=dates,
                y=indicators['volume'],
                name='Volume',
                marker_color=colors
            ),
            row=3, col=1
        )

    @staticmethod
    def add_macd(fig, df, indicators):
        """Add MACD indicator"""
        dates = df['Date']

        fig.add_trace(
            go.Bar(
                x=dates,
                y=indicators['histogram'],
                name='MACD Histogram',
                marker_color=[
                    'rgb(34,171,148)' if h > 0 else 'rgb(255,82,82)'
                    for h in indicators['histogram']
                ]
            ),
            row=4, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=indicators['macd_line'],
                mode='lines',
                name='MACD',
                line=dict(color='rgb(33,150,243)', width=1)
            ),
            row=4, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=indicators['signal_line'],
                mode='lines',
                name='Signal',
                line=dict(color='rgb(255,109,0)', width=1)
            ),
            row=4, col=1
        )

    @staticmethod
    def add_rsi(fig, df, indicators):
        """Add RSI indicator"""
        dates = df['Date']

        fig.add_trace(
            go.Scatter(
                x=dates,
                y=indicators['rsi'],
                mode='lines',
                name='RSI',
                line=dict(color='rgb(126,87,194)', width=1)
            ),
            row=5, col=1
        )
        fig.add_hline(y=70, line_dash="dash", line_color="rgb(120,123,134)", line_width=1, row=5, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="rgb(120,123,134)", line_width=1, row=5, col=1)
        fig.add_hrect(y0=30, y1=70, fillcolor="rgba(126,87,194,0.1)", line_width=0, row=5, col=1)

    @staticmethod
    def add_obv(fig, df, indicators):
        """Add OBV indicator"""
        dates = df['Date']

        fig.add_trace(
            go.Scatter(
                x=dates,
                y=indicators['obv_normalized'],
                mode='lines',
                name='OBV',
                line=dict(color='rgb(33,150,243)', width=1)
            ),
            row=6, col=1
        )

    @staticmethod
    def add_atr(fig, df, indicators):
        """Add ATR indicator"""
        dates = df['Date']

        fig.add_trace(
            go.Scatter(
                x=dates,
                y=indicators['atr'],
                mode='lines',
                name='ATR',
                line=dict(color='rgb(128,25,34)', width=1)
            ),
            row=7, col=1
        )

    @staticmethod
    def update_layout(fig, symbol, df):
        """Update chart layout"""
        latest = df.iloc[-1]
        latest_ohlc = f"Open: {latest['Open']:.2f} | High: {latest['High']:.2f} | Low: {latest['Low']:.2f} | Close: {latest['Close']:.2f}"

        fig.update_layout(
            title=dict(
                text=f'{symbol} <br><sup>{latest_ohlc}</sup>',
                x=0.5,
                xanchor='center',
                font=dict(size=20)
            ),
            xaxis_rangeslider_visible=False,
            hovermode="x unified",
            template='plotly_white',
            height=1400,
            font=dict(size=16),
            legend=dict(x=0.01, y=-0.05, xanchor="left", yanchor="top", orientation="h"),
            xaxis7_title="Date"
        )

        # Update y-axis titles
        fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
        fig.update_yaxes(title_text="SuperTrend", row=2, col=1)
        fig.update_yaxes(title_text="Volume (M)", row=3, col=1)
        fig.update_yaxes(title_text="MACD", row=4, col=1)
        fig.update_yaxes(title_text="RSI", row=5, col=1)
        fig.update_yaxes(title_text="OBV", row=6, col=1)
        fig.update_yaxes(title_text="ATR", row=7, col=1)

        # Hide secondary y-axis titles
        for i in range(1, 8):
            fig.update_yaxes(showgrid=False, title_text="", row=i, col=1, secondary_y=True) 