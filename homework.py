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
from dataclasses import dataclass, asdict


@dataclass
class InfoMessage:
    """Информационное сообщение о тренировке."""

    training_type: str  # имя класса тренировки;
    duration: float  # длительность тренировки в часах;
    distance: float  # дистанция в км за время тренировки;
    speed: float  # средняя скорость, с которой двигался пользователь;
    calories: float  # кол-во ккалорий, израсходованное за время тренировки.
    template_str: str = ('Тип тренировки: {training_type}; '
                         'Длительность: {duration:.3f} ч.; '
                         'Дистанция: {distance:.3f} км; '
                         'Ср. скорость: {speed:.3f} км/ч; '
                         'Потрачено ккал: {calories:.3f}.'
                         )

    def get_message(self) -> str:
        """Return a string of the given type."""
        return self.template_str.format(**asdict(self))


class Training:
    """Базовый класс тренировки."""
    M_IN_KM: int = 1000
    HRS_TO_MIN: int = 60
    LEN_STEP: float = 0.65  # metres (walking & running), swimming differs

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

    def get_spent_calories(self) -> float:  # type: ignore[empty-body, return]
        """Получить количество затраченных калорий."""
        pass

    def show_training_info(self) -> InfoMessage:
        """Вернуть информационное сообщение о выполненной тренировке."""
        return InfoMessage(self.__class__.__name__,
                           self.duration,
                           self.get_distance(),
                           self.get_mean_speed(),
                           self.get_spent_calories())


class Running(Training):
    """Тренировка: бег."""

    CALORIES_MEAN_SPEED_MULTIPLIER: int = 18
    CALORIES_MEAN_SPEED_SHIFT: float = 1.79

    def __init__(self,
                 action: int,
                 duration: float,  # hours
                 weight: float,  # kilos
                 ) -> None:
        super().__init__(action, duration, weight)
    """
    Все свойства и методы этого класса без изменений наследуются от базового
    класса. Исключение составляет только метод расчёта калорий, его нужно
    переопределить.
    Расход калорий для бега рассчитывается по такой формуле:

    (18 * средняя_скорость + 1.79) * вес_спортсмена / M_IN_KM *
    время_тренировки_в_минутах  # Yet the inherited duration is hours!
    """

    def get_spent_calories(self) -> float:
        """Получить количество затраченных калорий."""
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
                 duration: float,  # hours
                 weight: float,  # kilos
                 height: float) -> None:
        super().__init__(action, duration, weight)
        self.height = height / self.CM_TO_M  # The athlete's height in metres

    def get_spent_calories(self) -> float:
        """Получить количество затраченных калорий."""
        inter = ((self.get_mean_speed() * self.KMH_TO_MPS)**2 / self.height)

        return (
            (self.WEIGHT_MULTIPLIER_ONE * self.weight
                + inter * self.WEIGHT_MULTIPLIER_TWO * self.weight)
            * self.duration * self.HRS_TO_MIN)


class Swimming(Training):
    """Тренировка: плавание."""
    LEN_STEP: float = 1.38  # metres, unlike in walking & running
    SWIM_CALORIES_ADD: float = 1.1
    SWIM_CALORIES_MULTIPLIER: int = 2

    def __init__(self,
                 action: int,
                 duration: float,  # hours
                 weight: float,  # kilos
                 length_pool: int,
                 count_pool: int) -> None:
        super().__init__(action, duration, weight)
        self.length_pool = length_pool  # metres, int?
        self.count_pool = count_pool  # int

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


def read_package(workout_type: str, data: list) -> Training:
    """Прочитать данные, полученные от датчиков."""

    # Add a helper dictionary.
    # (, 'WLK', 'SWM'
    trainings_dict = {
        'RUN': Running,
        'WLK': SportsWalking,
        'SWM': Swimming
    }

    if workout_type in trainings_dict:
        return trainings_dict[workout_type](*data)
    print(f'Выбран неподдерживаемый режим тренировки {workout_type}.'
          ' По умолчанию выводятся дежурные данные.')
    return Training(0, 1 / 3600, 0)  # To negotialte the division by zero error


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
