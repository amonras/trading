import random
from typing import List, Dict
import copy

from strategies.strategy import Strategy
from strategies.native_strategy import NativeStrategy
from utils import STRAT_PARAMS, resample_timeframe

from storage.database import Hdf5Client
from models import BacktestResult

from strategies import *


class Nsga2:
    def __init__(self, exchange: str, symbol: str, strategy: str, tf: str, from_time: int, to_time: int,
                 population_size: int):
        self.exchange = exchange
        self.symbol = symbol
        self.strategy = strategy
        self.tf = tf
        self.from_time = from_time
        self.to_time = to_time
        self.population_size = population_size

        self.params_data = STRAT_PARAMS[strategy]

        self.population_params = []

        if self.strategy == 'obv':
            self.strategy_class = Obv
        elif self.strategy == 'ichimoku':
            self.strategy_class = Ichimoku
        elif self.strategy == 'sup_res':
            self.strategy_class = SupportResistance
        elif self.strategy == 'sma':
            self.strategy_class = Sma
        elif self.strategy == 'psar':
            self.strategy_class = Psar
        else:
            print('unknown strategy name')

        if issubclass(self.strategy_class, NativeStrategy):
            # In this case we can factor out data collection
            h5_db = Hdf5Client(exchange)
            self.data = h5_db.get_data(symbol, from_time, to_time)
            self.data = resample_timeframe(self.data, tf)

    def create_initial_population(self) -> List[BacktestResult]:
        """
        Creates population of BacktestResults, ensuring no repeated instances.
        Backtest results are unevaluated
        :return:
        """
        population = []

        while len(population) < self.population_size:
            backtest = BacktestResult()
            for p_code, p in self.params_data.items():
                if p['type'] == int:
                    backtest.parameters[p_code] = random.randint(p['min'], p['max'])
                if p['type'] == float:
                    backtest.parameters[p_code] = round(random.uniform(p['min'], p['max']), p['decimals'])

            if backtest not in population:
                population.append(backtest)
                self.population_params.append(backtest.parameters)

        return population

    def create_new_population(self, fronts: List[List[BacktestResult]]) -> List[BacktestResult]:
        """
        Return as many backtest results from a list of lists (dominated sorting fronts) as determined
        in self.population_size.
        :param fronts:
        :return:
        """

        new_pop = []

        for front in fronts:
            if len(new_pop) + len(front) > self.population_size:
                max_individuals = self.population_size - len(new_pop)
                if max_individuals > 0:
                    new_pop += sorted(front, key=lambda x: x.crowding_distance)[-max_individuals:]
            else:
                new_pop += front

        return new_pop

    def crowding_distance(self, population: List[BacktestResult]) -> List[BacktestResult]:

        for objective in ['pnl', 'max_dd']:
            population = sorted(population, key=lambda x: getattr(x, objective))
            min_value = getattr(min(population, key=lambda x: getattr(x, objective)), objective)
            max_value = getattr(max(population, key=lambda x: getattr(x, objective)), objective)

            population[0].crowding_distance = float('inf')
            population[-1].crowding_distance = float('inf')

            for i in range(1, len(population) - 1):
                distance = getattr(population[i + 1], objective) - getattr(population[i - 1], objective)
                if max_value - min_value != 0:
                    distance = distance / (max_value - min_value)
                population[i].crowding_distance += distance

        return population

    def create_offspring_population(self, population: List[BacktestResult]) -> List[BacktestResult]:

        offspring_pop = []

        while len(offspring_pop) != self.population_size:
            parents: List[BacktestResult] = []

            for i in range(2):
                random_parents = random.sample(population, k=2)
                if random_parents[0].rank != random_parents[1].rank:
                    best_parent = min(random_parents, key=lambda x: x.rank)
                else:
                    best_parent = min(random_parents, key=lambda x: x.crowding_distance)

                parents.append(best_parent)

            new_child = BacktestResult()
            new_child.parameters = copy.copy(parents[0].parameters)

            # Crossover

            number_of_crossover = random.randint(1, len(self.params_data))
            params_to_cross = random.sample(list(self.params_data.keys()), k=number_of_crossover)

            for p in params_to_cross:
                new_child.parameters[p] = copy.copy(parents[1].parameters[p])

            # Mutation

            number_of_mutations = random.randint(0, len(self.params_data))
            params_to_change = random.sample(list(self.params_data.keys()), k=number_of_mutations)

            for p in params_to_change:
                mutations_strength = random.uniform(-2, 2)
                new_child.parameters[p] = self.params_data[p]['type'](  # Make sure it is cast to the right type
                    new_child.parameters[p] * (1 + mutations_strength)
                )
                new_child.parameters[p] = max(new_child.parameters[p], self.params_data[p]['min'])
                new_child.parameters[p] = min(new_child.parameters[p], self.params_data[p]['max'])

                if self.params_data[p]['type'] == float:
                    new_child.parameters[p] = round(new_child.parameters[p], self.params_data[p]['decimals'])

            new_child.parameters = self._params_constraints(new_child.parameters)

            if new_child.parameters not in self.population_params:
                offspring_pop.append(new_child)
                self.population_params.append(new_child.parameters)

        return offspring_pop

    def _params_constraints(self, params: Dict) -> Dict:
        if self.strategy == 'obv':
            pass
        elif self.strategy == 'sup_res':
            pass
        elif self.strategy == 'ichimoku':
            params['kijun'] = max(params['kijun'], params['tenkan'])
        elif self.strategy == 'sma':
            params['slow_ma'] = max(params['slow_ma'], params['fast_ma'])
        elif self.strategy == 'psar':
            params['initial_acc'] = min(params['initial_acc'], params['max_acc'])
            params['acc_increment'] = min(params['acc_increment'], params['max_acc'] - params['initial_acc'])

        return params

    def non_dominated_sorting(self, population: Dict[int, BacktestResult]) -> List[List[BacktestResult]]:

        fronts = []

        for id_1, indiv_1 in population.items():
            for id_2, indiv_2 in population.items():
                if indiv_1.pnl >= indiv_2.pnl and indiv_1.max_dd <= indiv_2.max_dd \
                        and (indiv_1.pnl > indiv_2.pnl or indiv_1.max_dd < indiv_2.max_dd):
                    indiv_1.dominates.append(id_2)
                elif indiv_2.pnl >= indiv_1.pnl and indiv_2.max_dd <= indiv_1.max_dd \
                        and (indiv_2.pnl > indiv_1.pnl or indiv_2.max_dd < indiv_1.max_dd):
                    indiv_1.dominated_by += 1

            if indiv_1.dominated_by == 0:
                if len(fronts) == 0:
                    fronts.append([])
                fronts[0].append(indiv_1)
                indiv_1.rank = 0

        i = 0

        while True:
            fronts.append([])

            for indiv_1 in fronts[i]:
                for indiv_2_id in indiv_1.dominates:
                    population[indiv_2_id].dominated_by -= 1
                    if population[indiv_2_id].dominated_by == 0:
                        fronts[i + 1].append(population[indiv_2_id])
                        population[indiv_2_id].rank = i + 1

            if len(fronts[i + 1]) > 0:
                i += 1
            else:
                del fronts[-1]
                break

        return fronts

    def evaluate_population(self, population: List[BacktestResult]) -> List[BacktestResult]:
        for bt in population:
            obj: Strategy = self.strategy_class(**bt.parameters)

            if isinstance(obj, NativeStrategy):
                # Bypass data collection if possible
                bt.pnl, bt.max_dd = obj.backtest(self.data)
            else:
                obj.set_target(
                    exchange=self.exchange,
                    symbol=self.symbol,
                    tf=self.tf,
                    from_time=self.from_time,
                    to_time=self.to_time
                )
                bt.pnl, bt.max_dd = obj.backtest()

            # Avoid conservative strategy to not trade
            if bt.pnl == 0:
                bt.pnl = -float("inf")
                bt.max_dd = float("inf")

        return population
