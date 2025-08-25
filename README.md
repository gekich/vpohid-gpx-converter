# vpohid-gpx-converter

![Main screenshot](assets/screenshots/Screenshot_1.png)

Конвертер об'єктів з https://vpohid.com.ua у GPX або OsmAnd.

## Можливості
- Конвертація з JSON або напряму з сайту (URL: https://vpohid.com.ua/json/map/v/items/...).
- Результат: GPX-файл (з тегами OsmAnd або стандартний).
- Групування точок: в одну групу або за типом (`kind`).

## Приклади
- Імпорт напряму:
    - `python convert.py -u "https://vpohid.com.ua/json/map/v/items/..."`
- Імпорт з json:
  - `python convert.py -i path/to/my_places.json`
- Без тегів OsmAnd:
  - `python convert.py --no-osmand-extensions`
- Групувати точки за типом (`kind`) замість однієї групи:
  - `python convert.py --by-kind`
- Задати власну назву єдиної групи:
  - `python convert.py --single-group --group-name "Мої точки"`

> Усі опції: `python convert.py -h`

## Налаштування через .env (опціонально)
`mv .env.example .env`

> CLI-параметри мають пріоритет над .env

## Імпортувати в OsmAnd
- OsmAnd → Мої місця → Імпортувати закладки.
- Оберіть створений GPX-файл.

## Ліцензія
MIT — див. файл LICENSE.

## Посилання
- Репозиторій: https://github.com/gekich/vpohid-gpx-converter
- Issues: https://github.com/gekich/vpohid-gpx-converter/issues
- Pull Requests: https://github.com/gekich/vpohid-gpx-converter/pulls
