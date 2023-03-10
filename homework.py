"""
Программный модуль фитнес-трекера, который обрабатывает данные для
трёх видов тренировок: бега, спортивной ходьбы и плавания.
Этот модуль должен выполнять следующие функции:
    принимать от блока датчиков информацию о прошедшей тренировке,
    определять вид тренировки,
    рассчитывать результаты тренировки,
    выводить информационное сообщение о результатах тренировки.

Информационное сообщение должно включать такие данные:
    тип тренировки (бег, ходьба или плавание);
    длительность тренировки в мин?;
    дистанция, которую преодолел пользователь, в километрах;
    среднюю скорость на дистанции в км/ч;
    расход энергии в килокалориях.
"""
from dataclasses import asdict, dataclass
from typing import Dict, List, Type


@dataclass
class InfoMessage:
    """Информационное сообщение о тренировке."""

    training_type: str
    duration: float
    distance: float
    speed: float
    calories: float
    MESSAGE: str = ('Тип тренировки: {training_type}; '
                    'Длительность: {duration:.3f} ч.; '
                    'Дистанция: {distance:.3f} км; '
                    'Ср. скорость: {speed:.3f} км/ч; '
                    'Потрачено ккал: {calories:.3f}.'
                    )

    def get_message(self) -> str:
        """Return a string of the given type."""
        return self.MESSAGE.format(**asdict(self))


class Training:
    """Базовый класс тренировки."""
    M_IN_KM: int = 1000
    HRS_TO_MIN: int = 60
    LEN_STEP: float = 0.65

    def __init__(self,
                 action: int,
                 duration: float,  # hours
                 weight: float,  # kilos
                 ) -> None:
        self.action = action
        self.duration = duration
        self.weight = weight

    def get_distance(self) -> float:
        """Получить дистанцию в км."""
        return self.action * self.LEN_STEP / self.M_IN_KM

    def get_mean_speed(self) -> float:
        """Получить среднюю скорость движения."""
        return self.get_distance() / self.duration

    def get_spent_calories(self) -> float:
        """Получить количество затраченных калорий."""
        raise NotImplementedError('Базовый метод Training; см. реализацию у'
                                  ' "детей".')

    def show_training_info(self) -> InfoMessage:
        """Вернуть информационное сообщение о выполненной тренировке."""
        return InfoMessage(self.__class__.__name__,
                           self.duration,
                           self.get_distance(),
                           self.get_mean_speed(),
                           self.get_spent_calories())


class Running(Training):
    """Тренировка: бег.
    Все свойства и методы этого класса без изменений наследуются от базового
    класса. Поэтому не нужно дублировать конструктор.
    Исключение составляет только метод расчёта калорий, его нужно
    переопределить.
    """

    CALORIES_MEAN_SPEED_MULTIPLIER: int = 18
    CALORIES_MEAN_SPEED_SHIFT: float = 1.79

    def get_spent_calories(self) -> float:
        """Получить количество затраченных калорий.
        Расход калорий для бега рассчитывается по такой формуле:

        (18 * средняя_скорость + 1.79) * вес_спортсмена / M_IN_KM *
        время_тренировки_в_минутах  # Yet the inherited duration is hours!
        """
        return (
            (self.CALORIES_MEAN_SPEED_MULTIPLIER
             * self.get_mean_speed() + self.CALORIES_MEAN_SPEED_SHIFT)
            * self.weight / self.M_IN_KM
            * self.duration * self.HRS_TO_MIN
        )


class SportsWalking(Training):
    """Тренировка: спортивная ходьба.

    Конструктор этого класса принимает дополнительный параметр height — рост
    спортсмена.
    Расчёт калорий для этого класса должен проводиться по такой формуле:

    ((0.035 * вес + (средняя_скорость_в_метрах_в_секунду**2 / рост_в_метрах)
    * 0.029 * вес) * время_тренировки_в_минутах)

    """

    WEIGHT_MULTIPLIER_ONE: float = 0.035
    WEIGHT_MULTIPLIER_TWO: float = 0.029
    KMH_TO_MPS: float = 0.278
    CM_TO_M: int = 100

    def __init__(self,
                 action: int,
                 duration: float,
                 weight: float,
                 height: float) -> None:
        super().__init__(action, duration, weight)
        self.height = height / self.CM_TO_M

    def get_spent_calories(self) -> float:
        """Получить количество затраченных калорий."""
        return (
            (self.WEIGHT_MULTIPLIER_ONE * self.weight
                + ((self.get_mean_speed() * self.KMH_TO_MPS)**2 / self.height)
                * self.WEIGHT_MULTIPLIER_TWO * self.weight)
            * self.duration * self.HRS_TO_MIN)


class Swimming(Training):
    """Тренировка: плавание."""
    LEN_STEP: float = 1.38
    SWIM_CALORIES_ADD: float = 1.1
    SWIM_CALORIES_MULTIPLIER: int = 2

    def __init__(self,
                 action: int,
                 duration: float,
                 weight: float,
                 length_pool: int,
                 count_pool: int) -> None:
        super().__init__(action, duration, weight)
        self.length_pool = length_pool
        self.count_pool = count_pool

    def get_mean_speed(self) -> float:
        """Получить среднюю скорость движения."""
        return (self.length_pool * self.count_pool / self.M_IN_KM
                / self.duration)

    def get_spent_calories(self) -> float:
        """Получить количество затраченных калорий."""
        return (
            (self.get_mean_speed() + self.SWIM_CALORIES_ADD)
            * self.SWIM_CALORIES_MULTIPLIER * self.weight * self.duration
        )


def read_package(workout_type: str, data: List[int]) -> Training:
    """Прочитать данные, полученные от датчиков."""

    available_workout_types: Dict[str, Type[Training]] = {
        'RUN': Running,
        'WLK': SportsWalking,
        'SWM': Swimming,
    }

    if workout_type in available_workout_types:
        return available_workout_types[workout_type](*data)
    else:
        raise KeyError('Выбран неподдерживаемый режим тренировки –'
                       f' {workout_type}')


def main(training: Training) -> None:
    """Главная функция."""
    info = training.show_training_info()
    print(info.get_message())


if __name__ == '__main__':
    packages = [
        ('SWM', [720, 1, 80, 25, 40]),
        ('RUN', [15000, 1, 75]),
        ('WLK', [9000, 1, 75, 180]),
    ]

    for workout_type, data in packages:
        training = read_package(workout_type, data)
        main(training)
