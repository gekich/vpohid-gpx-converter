# vpohid-gpx-converter

![Main screenshot](assets/screenshots/Screenshot_1.png)

Конвертер об'єктів з https://vpohid.com.ua у GPX або OsmAnd.

## Можливості
- Конвертація з JSON або напряму з сайту (URL: https://vpohid.com.ua/json/map/v/items/...).
- Результат: GPX-файл (з тегами OsmAnd або стандартний). Зберігає таку інформацію:
  - широта/довгота, висота над рівнем моря
  - назва/дата додавання
  - опис з посиланням на оригінальний об'єкт на сайті
  - тип/категорія, з відповідною іконкою (для OsmAnd).
- Групування точок: в одну групу або за типом (`kind`).

## Вимоги
- Python 3.7

## Параметри
- -u, --url: URL з об'єктами (очікується response.items). https://vpohid.com.ua/json/map/v/items/...
- -i, --input: Вхідний JSON-файл. Якщо не вказано і не задано URL, використовується my_places.json.
- -o, --output: Шлях до вихідного GPX-файлу. За замовчуванням converted_places_osmand.gpx або converted_places_standard.gpx.
- --no-osmand-tags: Вимкнути теги OsmAnd.
- --group-name: Назва єдиної групи точок; якщо не вказано — групування відбувається за типом (kind).

## Приклади
Мінімальний запуск з URL:

`python convert.py -u "https://vpohid.com.ua/json/map/v/items/..."`

## Імпорт в OsmAnd
- OsmAnd → Мої місця → Імпортувати закладки.
- Оберіть створений GPX-файл.

## Ліцензія
MIT — див. файл LICENSE.

## Посилання
- Репозиторій: https://github.com/gekich/vpohid-gpx-converter
- Issues: https://github.com/gekich/vpohid-gpx-converter/issues
- Pull Requests: https://github.com/gekich/vpohid-gpx-converter/pulls
