import pandas as pd
import plotly.graph_objects as go


class Plot:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.supports = None
        self.resistances = None

    def get_sup_res(self):
        pass

    def get_trades_lines(self, trades):
        lines = []

        for i, trade in trades.iterrows():
            x = [trade['enter_at'], trade['exit_at']]
            y = [trade['open'], trade['close']]
            if (trade['close'] - trade['open'])*trade['position'] > 0:
                color = 'green'
            else:
                color = 'red'

            lines.append(
                go.Scatter(x=x, y=y, marker=dict(color=color), name=f'trade {i}')
            )

        return lines

    def plot(self, levels=None, trades=None):
        df = self.df

        time_range = [df.index.min(), df.index.max()]
        if levels is not None:
            supports = [
                [(pd.Timestamp(from_pt[0]), from_pt[1]), (pd.Timestamp(to_pt[0]), to_pt[1])]
                for from_pt, to_pt in levels['supports']
                if from_pt[0] > time_range[0] and to_pt[0] < time_range[1]
            ]

            resistances = [
                [(pd.Timestamp(from_pt[0]), from_pt[1]), (pd.Timestamp(to_pt[0]), to_pt[1])]
                for from_pt, to_pt in levels['resistances']
                if from_pt[0] > time_range[0] and to_pt[0] < time_range[1]
            ]
        else:
            supports = []
            resistances = []

        r_df = df

        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=r_df.index,
                    open=r_df['open'],
                    high=r_df['high'],
                    low=r_df['low'],
                    close=r_df['close']
                )
            ],
            layout=dict(
                yaxis=dict(
                    fixedrange=False
                )
            )
        )

        for i, (from_pt, to_pt) in enumerate(supports):
            fig.add_trace(
                go.Line(
                    x=[from_pt[0], to_pt[0]],
                    y=[from_pt[1], to_pt[1]],
                    marker=dict(color='green'),
                    legendgroup='supports',
                    name='supports',
                    showlegend=i == 0
                )
            )

        for i, (from_pt, to_pt) in enumerate(resistances):
            fig.add_trace(
                go.Line(
                    x=[from_pt[0], to_pt[0]],
                    y=[from_pt[1], to_pt[1]],
                    marker=dict(color='red'),
                    legendgroup='resistances',
                    name='resistances',
                    showlegend=i == 0
                )
            )

        fig.update_layout(height=600)

        return fig
