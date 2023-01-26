"""
Разработайте программный модуль фитнес-трекера, который обрабатывает данные для
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

❗ В ТЗ указаны формулы, которые нужно использовать для расчёта результатов
тренировок. Хороший разработчик чётко следует всем требованиям ТЗ. Не меняйте
формулы, используйте их в точно таком же виде, как они указаны в задании.
"""

M_IN_KM = 1000


class InfoMessage:
    """Информационное сообщение о тренировке."""

    """
    ревьюер написал использовать dataclasses и метод asdict() в классе
    InfoMessage. Он советует вынести строку, которую возвращает метод
    get_message() в константы в сам класс, а потом использовать на ней метод
    format, передав в качестве параметра распакованный словарь (**asdict).
    Логика заключается в том, чтобы метод get_message() был максимально
    универсальным (т.е. мы можем менять строку сообщения, а метод при этом
    переписывать не придется). Если я создаю переменную message внутри метода
    get_message(), то все работает. Но если выношу ее в класс
    (MESSAGE на скрине), то программа не распознает переменные
    training_type, duration и т.д. (с self то же самое).
    Я правильно поняла ревьюера, что константу нужно вынести в класс?
    А метод format уже использовать в get_message()?
    """

    def __init__(self,
                 training_type: str,
                 training_obj):
        self.training_type = training_type  # Name your training
        self.duration = training_obj.duration  # hours
        self.distance = training_obj.get_distance()
        self.speed = training_obj.get_mean_speed()
        self.calories = training_obj.get_spent_calories()

    def get_message(self) -> str:
        """Return a string of the given type."""
        return (f'Тип тренировки: {self.training_type};'
                f' Длительность: {"{:.3f}".format(self.duration)} ч.;'
                f' Дистанция: {"{:.3f}".format(self.distance)} км;'
                f' Ср. скорость: {"{:.3f}".format(self.speed)} км/ч;'
                f' Потрачено ккал: {"{:.3f}".format(self.calories)}.')


class Training:
    """Базовый класс тренировки."""
    LEN_STEP = 0.65  # metres, for both walking & running except swimming

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
        return self.action * self.LEN_STEP / M_IN_KM

    def get_mean_speed(self) -> float:
        """Получить среднюю скорость движения."""
        return self.get_distance() / self.duration

    def get_spent_calories(self) -> float:  # type: ignore[empty-body, return]
        """Получить количество затраченных калорий."""
        pass

    def show_training_info(self) -> InfoMessage:
        """Вернуть информационное сообщение о выполненной тренировке."""
        return InfoMessage('My training', self)


class Running(Training):
    """Тренировка: бег."""

    CALORIES_MEAN_SPEED_MULTIPLIER = 18
    CALORIES_MEAN_SPEED_SHIFT = 1.79

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
            * self.weight / M_IN_KM
            * self.duration * 60
        )


class SportsWalking(Training):
    """Тренировка: спортивная ходьба.

    Конструктор этого класса принимает дополнительный параметр height — рост
    спортсмена.
    Расчёт калорий для этого класса должен проводиться по такой формуле:

    (0.035 * вес + (средняя_скорость_в_метрах_в_секунду**2 / рост_в_метрах)
    * 0.029 * вес) * время_тренировки_в_минутах
    m/s = km/h ÷ 3.6
    """

    WEIGHT_MULTIPLIER_ONE = 0.035
    WEIGHT_MULTIPLIER_TWO = 0.029
    MEAN_SPEED_DIV = 3.6

    def __init__(self,
                 action: int,
                 duration: float,  # hours
                 weight: float,  # kilos
                 height) -> None:
        super().__init__(action, duration, weight)
        self.height = height  # The athlete's height in metres

    def get_spent_calories(self) -> float:
        """Получить количество затраченных калорий."""
        return (
            (self.WEIGHT_MULTIPLIER_ONE * self.weight
             + ((self.get_mean_speed() / self.MEAN_SPEED_DIV)**2 / self.height)
             * self.WEIGHT_MULTIPLIER_TWO * self.weight) * self.duration * 60
        )


class Swimming(Training):
    """Тренировка: плавание."""
    LEN_STEP = 1.38  # metres, overridden for swimming vs walking & running
    SWIM_CALORIES_ADD = 1.1
    SWIM_CALORIES_MULTIPLIER = 2

    def __init__(self,
                 action: int,
                 duration: float,  # hours
                 weight: float,  # kilos
                 *args) -> None:
        super().__init__(action, duration, weight)
        self.length_pool = args[0]  # metres
        self.count_pool = args[1]  # int

    def get_mean_speed(self) -> float:
        """Получить среднюю скорость движения."""
        return (self.length_pool * self.count_pool / M_IN_KM
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
    return Swimming(*data)


def main(training: Training) -> None:
    """Главная функция."""

    """
    Функция main() должна принимать на вход экземпляр класса Training.

    При выполнении функции main() для этого экземпляра должен быть вызван
    метод show_training_info(); результатом выполнения метода должен быть
    объект класса InfoMessage, его нужно сохранить в переменную info.
    Для объекта InfoMessage, сохранённого в переменной info, должен быть
    вызван метод, который вернёт строку сообщения с данными о тренировке;
    эту строку нужно передать в функцию print().

    Задача описана, можно приступать к её выполнению. Удачи!
    """


if __name__ == '__main__':
    """
    Прежде чем отдавать модуль в релиз, его работоспособность нужно проверить
    на реальном фитнес-трекере. Но у разработчиков не всегда есть такая
    возможность, поэтому можно имитировать работу датчиков и передать в
    программу заранее подготовленные тестовые данные.
    В исходном коде эти данные уже подготовлены:

    packages = [
        ('SWM', [720, 1, 80, 25, 40]),
        ('RUN', [15000, 1, 75]),
        ('WLK', [9000, 1, 75, 180]),
    ]

    for workout_type, data in packages:
        training = read_package(workout_type, data)
        main(training)

    Данные для тестов
    Блок датчиков фитнес-трекера передаёт пакеты данных в виде кортежа,
    первый элемент которого — кодовое обозначение прошедшей тренировки,
    второй — список показателей, полученных от датчиков устройства. Для
    проверки были смоделированы пакеты для каждого вида тренировки и добавлены
    в список packages:

     packages = [
         ('SWM', [720, 1, 80, 25, 40]),
         ('RUN', [15000, 1, 75]),
         ('WLK', [9000, 1, 75, 180]),
     ]

    Последовательность данных в принимаемых пакетах:
    Плавание

        Код тренировки: 'SWM'.
        Элементы списка: количество гребков, время в часах, вес пользователя,
        длина бассейна, сколько раз пользователь переплыл бассейн.

    Бег

        Код тренировки: 'RUN'.
        Элементы списка: количество шагов, время тренировки в часах, вес
        пользователя.

    Спортивная ходьба

        Код тренировки: 'WLK'.
        Элементы списка: количество шагов, время тренировки в часах, вес
        пользователя, рост пользователя.

    Программа должна перебирать в цикле список пакетов, распаковывает каждый
    кортеж и передаёт данные в функцию read_package().

    """

    packages = [
        ('SWM', [720, 1, 80, 25, 40]),
        ('RUN', [15000, 1, 75]),
        ('WLK', [9000, 1, 75, 180]),
    ]

    for workout_type, data in packages:
        training = read_package(workout_type, data)
        # main(training)
    # swimming = Swimming(720, 1, 80, 25, 40)
