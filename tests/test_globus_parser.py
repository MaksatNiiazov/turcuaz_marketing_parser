from decimal import Decimal

from app.modules.market_parser.models.entities import ParserCategory, ParserSource
from app.modules.market_parser.services.globus_parser import GlobusParser


def test_normalize_product_and_discount_percent() -> None:
    parser = GlobusParser()
    source = ParserSource(name="Globus", code="globus", base_url="https://globus-online.kg/ru-kg")
    category = ParserCategory(
        source=source,
        source_id=1,
        external_id="cat1",
        name="Конфеты",
        url="https://globus-online.kg/ru-kg/catalog/grocery/category/cat1",
    )
    parsed = parser.normalize_product(
        {
            "type": "good",
            "id": "sku-1",
            "title": "Шоколад тестовый 100г",
            "amount": "за 1 шт.",
            "currentPrice": 80,
            "oldPrice": 100,
            "available": True,
            "snippetImage": {"url": "https://img/{w}x{h}"},
        },
        category,
    )

    assert parsed is not None
    assert parsed.external_sku == "sku-1"
    assert parsed.name == "Шоколад тестовый 100г"
    assert parsed.unit == "шт."
    assert parsed.price == Decimal("100.00")
    assert parsed.discount_price == Decimal("80.00")
    assert parsed.discount_percent == Decimal("20.00")
    assert parsed.image_url == "https://img/800x800"


def test_discount_percent_empty_when_no_discount() -> None:
    assert GlobusParser.calculate_discount_percent(Decimal("100"), Decimal("100")) is None
    assert GlobusParser.calculate_discount_percent(None, Decimal("90")) is None


def test_extract_category_tree_with_parent_and_child() -> None:
    parser = GlobusParser()
    categories = parser._extract_category_tree(
        """
        <div data-testid="catalog-menu-item-collapse" data-item-id="parent-1">
          <button><img alt="Стирка и уборка" /></button>
          <ul>
            <li data-item-id="child-1">
              <a href="/ru-kg/catalog/grocery/category/child-1">Средства для стирки</a>
            </li>
          </ul>
        </div>
        """
    )

    parent = next(category for category in categories if category.external_id == "parent-1")
    child = next(category for category in categories if category.external_id == "child-1")

    assert parent.name == "Стирка и уборка"
    assert parent.is_group is True
    assert child.name == "Средства для стирки"
    assert child.parent_external_id == "parent-1"
