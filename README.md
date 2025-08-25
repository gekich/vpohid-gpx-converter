# vpohid-gpx-converter

![Main screenshot](assets/screenshots/Screenshot_1.png)

Конвертер об'єктів з https://vpohid.com.ua у GPX або OsmAnd (іконки, кольори), щоб точки гарно відображались у застосунку.

## Що вміє
- Вхід: локальний JSON-файл або URL з JSON-відповіддю.
- Підтримувані форми JSON: масив; об'єкт з `items`; об'єкт з `response.items`.
- Вихід: GPX-файл (стандартний або з підтримкою полів OsmAnd).
- Групування точок: в одну групу або за типом (`kind`).

## Приклади використання
- Імпорт з файлу:
  - `python convert.py -i path/to/export.json`
- Імпорт з напряму з URL:
  - `python convert.py -u "https://vpohid.com.ua/json/map/v/items/..."`
- Змінити вихідний файл:
  - `python convert.py -o places.gpx`
- Вимкнути розширення OsmAnd (чистий GPX):
  - `python convert.py --no-osmand-extensions`
- Групувати точки за типом (`kind`) замість однієї групи:
  - `python convert.py --by-kind`
- Задати власну назву єдиної групи:
  - `python convert.py --single-group --group-name "Мої точки"`

> Підказка: запустіть `python convert.py -h`, щоб побачити всі опції.

## Налаштування через .env (необов'язково)
`mv .env.example .env`

> CLI-параметри мають пріоритет над .env

## Імпортуват в OsmAnd
- OsmAnd → Мої місця → Імпортувати закладки.
- Оберіть створений GPX-файл.

## Ліцензія
MIT — див. файл LICENSE.

## Посилання
- Репозиторій: https://github.com/gekich/vpohid-gpx-converter
- Issues: https://github.com/gekich/vpohid-gpx-converter/issues
- Pull Requests: https://github.com/gekich/vpohid-gpx-converter/pulls
