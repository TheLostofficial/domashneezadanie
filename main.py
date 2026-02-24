from __future__ import annotations
from typing import Tuple, Optional


class CoffeeOrder:
    """
    Неизменяемый value object заказа кофе.
    """

    __slots__ = ("base", "size", "milk", "syrups", "sugar", "iced", "price", "description")

    def __init__(
        self,
        base: str,
        size: str,
        milk: str = "none",
        syrups: Tuple[str, ...] = (),
        sugar: int = 0,
        iced: bool = False,
        price: float = 0.0,
        description: Optional[str] = None,
    ) -> None:
        self.base: str = base
        self.size: str = size
        self.milk: str = milk
        self.syrups: Tuple[str, ...] = syrups
        self.sugar: int = sugar
        self.iced: bool = iced
        self.price: float = price
        if description is not None:
            self.description = description
        else:
            self.description = self._gen_description()

    def _gen_description(self) -> str:
        parts = [self.size, self.base]

        # добавляем milk, если не 'none'
        if self.milk != "none":
            parts.append(f"with {self.milk} milk")

        # сиропы, если есть
        if self.syrups:
            parts.append("+" + ", ".join(self.syrups))

        # лед
        if self.iced:
            parts.append("(iced)")

        # сахар, если > 0
        if self.sugar > 0:
            parts.append(f"{self.sugar} tsp sugar")

        return " ".join(parts)

    def __str__(self) -> str:
        if self.description:
            return self.description
        return f"Coffee order: {self.price:.2f} ₽"


class CoffeeOrderBuilder:
    """
    Fluent builder для заказа кофе.

    Правила:
    - Обязательные поля: base, size.
    - Макс 4 сиропа без дубликатов.
    - Лимит сахара 0..5.
    - Множители цены и доплаты учитываются согласно константам.
    - Методы возвращают self для цепочек.
    - Состояние билдера не протекает наружу и создаёт новый неизменяемый CoffeeOrder.
    """

    BASE_PRICES = {
        "espresso": 200,
        "americano": 250,
        "latte": 300,
        "cappuccino": 320,
    }

    SIZE_MULTIPLIERS = {
        "small": 1.0,
        "medium": 1.2,
        "large": 1.4,
    }

    MILK_PRICES = {
        "none": 0.0,
        "whole": 30.0,
        "skim": 30.0,
        "oat": 60.0,
        "soy": 50.0,
    }

    SYRUP_PRICE = 40.0
    ICED_EXTRA = 0.2
    MAX_SYRUPS = 4
    MAX_SUGAR = 5
    MIN_SUGAR = 0

    VALID_BASES = set(BASE_PRICES)
    VALID_SIZES = set(SIZE_MULTIPLIERS)
    VALID_MILKS = set(MILK_PRICES)

    def __init__(self) -> None:
        self._base: Optional[str] = None
        self._size: Optional[str] = None
        self._milk: str = "none"
        self._syrups: list[str] = []
        self._sugar: int = 0
        self._iced: bool = False

    def set_base(self, base: str) -> CoffeeOrderBuilder:
        if base not in self.VALID_BASES:
            raise ValueError(f"Invalid base '{base}', must be one of {self.VALID_BASES}")
        self._base = base
        return self

    def set_size(self, size: str) -> CoffeeOrderBuilder:
        if size not in self.VALID_SIZES:
            raise ValueError(f"Invalid size '{size}', must be one of {self.VALID_SIZES}")
        self._size = size
        return self

    def set_milk(self, milk: str) -> CoffeeOrderBuilder:
        if milk not in self.VALID_MILKS:
            raise ValueError(f"Invalid milk '{milk}', must be one of {self.VALID_MILKS}")
        self._milk = milk
        return self

    def add_syrup(self, name: str) -> CoffeeOrderBuilder:
        if name not in self._syrups:
            if len(self._syrups) >= self.MAX_SYRUPS:
                raise ValueError(f"Cannot add more than {self.MAX_SYRUPS} syrups")
            self._syrups.append(name)
        # игнорируем дубликаты
        return self

    def set_sugar(self, teaspoons: int) -> CoffeeOrderBuilder:
        if not isinstance(teaspoons, int):
            raise TypeError("Sugar must be an int")
        if teaspoons < self.MIN_SUGAR or teaspoons > self.MAX_SUGAR:
            raise ValueError(f"Sugar must be between {self.MIN_SUGAR} and {self.MAX_SUGAR}")
        self._sugar = teaspoons
        return self

    def set_iced(self, iced: bool = True) -> CoffeeOrderBuilder:
        if not isinstance(iced, bool):
            raise TypeError("Iced must be a bool")
        self._iced = iced
        return self

    def clear_extras(self) -> CoffeeOrderBuilder:
        """
        Сбросить добавки: молоко, сиропы, сахар, лед
        """
        self._milk = "none"
        self._syrups.clear()
        self._sugar = 0
        self._iced = False
        return self

    def build(self) -> CoffeeOrder:
        # валидация обязательных полей
        if self._base is None:
            raise ValueError("Base is required")
        if self._size is None:
            raise ValueError("Size is required")

        # пересчёт цены
        base_price = self.BASE_PRICES[self._base]
        size_mul = self.SIZE_MULTIPLIERS[self._size]
        milk_price = self.MILK_PRICES[self._milk]
        syrups_price = len(self._syrups) * self.SYRUP_PRICE
        iced_price = self.ICED_EXTRA if self._iced else 0.0

        total_price = (base_price * size_mul) + milk_price + syrups_price + iced_price

        # Формируем неизменяемый заказ
        order = CoffeeOrder(
            base=self._base,
            size=self._size,
            milk=self._milk,
            syrups=tuple(self._syrups),
            sugar=self._sugar,
            iced=self._iced,
            price=total_price,
        )

        return order


if __name__ == "__main__":
    # Примеры проверок assert

    # 1) Базовый заказ - должен корректно застраиваться
    builder = CoffeeOrderBuilder()
    order1 = (
        builder
        .set_base("latte")
        .set_size("medium")
        .set_milk("oat")
        .add_syrup("vanilla")
        .add_syrup("caramel")
        .set_sugar(2)
        .set_iced(True)
        .build()
    )

    assert isinstance(order1, CoffeeOrder)
    assert order1.price > 0
    assert order1.base == "latte"
    assert order1.size == "medium"
    assert order1.milk == "oat"
    assert order1.syrups == ("vanilla", "caramel")
    assert order1.sugar == 2
    assert order1.iced is True
    assert "vanilla" in order1.description
    assert "oat milk" in order1.description
    assert "iced" in order1.description
    assert "2 tsp sugar" in order1.description

    # 2) Переиспользование билдера - меняем пару опций, order1 не меняется
    order2 = builder.set_base("espresso").set_size("small").clear_extras().build()
    assert order2.base == "espresso"
    assert order2.size == "small"
    assert order2.milk == "none"
    assert order2.syrups == ()
    assert order2.sugar == 0
    assert order2.iced is False
    assert order2.price > 0
    assert order2.price != order1.price
    assert str(order2) == order2.description

    # 3) Валидация - отсутствие base
    builder3 = CoffeeOrderBuilder()
    builder3.set_size("small")
    try:
        builder3.build()
        assert False, "Должен быть ValueError из-за отсутствия base"
    except ValueError as e:
        assert str(e) == "Base is required"

    # 4) Валидация - отсутствие size
    builder4 = CoffeeOrderBuilder()
    builder4.set_base("americano")
    try:
        builder4.build()
        assert False, "Должен быть ValueError из-за отсутствия size"
    except ValueError as e:
        assert str(e) == "Size is required"

    # 5) Валидация - сахар > 5
    builder5 = CoffeeOrderBuilder()
    builder5.set_base("latte").set_size("large")
    try:
        builder5.set_sugar(6)
        assert False, "Должен быть ValueError из-за сахара > 5"
    except ValueError:
        pass

    # 6) Валидация - максимальное количество сиропов
    builder6 = CoffeeOrderBuilder()
    builder6.set_base("latte").set_size("medium")
    builder6.add_syrup("vanilla")
    builder6.add_syrup("caramel")
    builder6.add_syrup("hazelnut")
    builder6.add_syrup("pumpkin spice")
    try:
        builder6.add_syrup("extra syrup")
        assert False, "Должен быть ValueError из-за количества сиропов больше 4"
    except ValueError:
        pass

    # 7) Дубликаты сиропов игнорятся и не влияют на цену
    builder7 = CoffeeOrderBuilder()
    builder7.set_base("latte").set_size("medium").clear_extras()
    builder7.add_syrup("vanilla").add_syrup("vanilla").add_syrup("caramel")
    order7 = builder7.build()
    assert order7.syrups.count("vanilla") == 1
    price_with_2_syrups = CoffeeOrderBuilder.SYRUP_PRICE * 2 + \
                          CoffeeOrderBuilder.BASE_PRICES["latte"] * CoffeeOrderBuilder.SIZE_MULTIPLIERS["medium"] + \
                          CoffeeOrderBuilder.MILK_PRICES["none"] + \
                          0.0
    # цена должна совпадать с расчетной вручную
    assert abs(order7.price - price_with_2_syrups) < 0.0001

    # 8) iced добавляет доплату
    builder8 = CoffeeOrderBuilder()
    builder8.set_base("espresso").set_size("small").set_iced(True)
    order8 = builder8.build()
    base_price = CoffeeOrderBuilder.BASE_PRICES["espresso"] * CoffeeOrderBuilder.SIZE_MULTIPLIERS["small"]
    expected_price = base_price + CoffeeOrderBuilder.MILK_PRICES["none"] + CoffeeOrderBuilder.ICED_EXTRA
    assert abs(order8.price - expected_price) < 0.0001

    print("Все тесты пройдены ✅")
    