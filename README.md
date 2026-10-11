# todo-scan

Находит маркеры `TODO`, `FIXME`, `XXX` и `HACK` в репозитории и может провалить CI, если найден блокирующий маркер или маркер без владельца. Работает офлайн, только читает файлы, без зависимостей, Python 3.10+.

## Быстрый старт

```bash
python -m todo_scan                          # отчёт по текущей папке
python -m todo_scan . --block FIXME          # FIXME валит запуск (код 1)
python -m todo_scan . --require-owner        # каждый маркер нужен с владельцем: TODO(alice)
python -m todo_scan . --json
```

Пример вывода для [examples](examples):

```text
sample.py:2: TODO(alice) cache the result
sample.py:5: FIXME crash on empty input
sample.py:6: HACK temporary workaround
markers: 3 (FIXME=1, HACK=1, TODO=1); violations: 0
```

## Что сканируется

- Все текстовые файлы в папке, кроме `.git`, `node_modules`, `.venv`, `venv`, `__pycache__`, `dist`, `build`.
- Бинарные файлы (изображения, архивы, шрифты) и файлы больше 1 МБ пропускаются.
- Маркер ищется по целому слову: `TODOS` и `mytodo` не считаются.

## Коды возврата

`0` — нарушений нет, `1` — есть блокирующие маркеры или маркеры без владельца, `2` — путь не папка.

## Ограничения

- Простой поиск по словам, без разбора языка: строка с `TODO` в строковом литерале тоже считается маркером.
- Не отслеживает, когда маркер появился (нужна git-история; это отдельная задача).

## Использование в CI

```yaml
- uses: actions/checkout@v4
- uses: actions/setup-python@v5
  with:
    python-version: "3.12"
- name: todo-scan
  run: python -m todo_scan . --block FIXME
```

## Разработка

```bash
python -m unittest discover -s tests -t .
```

## Лицензия

MIT — см. [LICENSE](LICENSE).
