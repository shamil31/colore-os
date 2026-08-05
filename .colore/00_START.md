# Coloré OS — START

## First Runtime Rule

Before any work, every AI must read .colore/bootstrap.md, .colore/09_UAOP.md, and .colore/01_CONTRACT.md.

## Workspace Check

Перед началом любой работы обязательно проверить:

- VS Code открыт в корне репозитория.
- Репозиторий содержит каталог `.git`.
- Рабочая папка — `/root/colore-os`.
- Все изменения выполняются только внутри этого репозитория.

Если хотя бы один пункт не выполнен — работу не начинать.

---

## Runtime Entry

1. Открыть проект /root/colore-os.
2. Прочитать .colore/bootstrap.md как авторитетный runtime contract.
3. Восстановить runtime context и выполнить Runtime Entry Procedure из bootstrap.
4. Подтвердить текущий sprint и KPI.
5. Выбрать только одну активную задачу и зафиксировать ее в .colore/00_Master/TODAY.md.
6. Перевести задачу в DOING.

---

## Во время работы

Работаем только над одной задачей.

Статусы задач:

BACKLOG → TODO → DOING → REVIEW → DONE

Каждая задача обязательно проходит полный цикл:

BACKLOG → TODO → DOING → REVIEW → DONE

Переход к следующей задаче запрещён, пока текущая задача не получила статус DONE после успешного REVIEW.

Новые идеи не прерывают текущую работу и сначала помещаются в BACKLOG.

Новые идеи не выполняются сразу.

Они добавляются в Backlog.

---

## Close Day

1. Зафиксировать только подтвержденные результаты.
2. Обновить .colore/bootstrap.md, .colore/06_SESSION.md и .colore/07_DECISIONS.md.
3. Обновить текущий phase, sprint, completed work, next task и blocked items.
4. Выполнить Sync Project по правилам контракта.
5. Определить первую задачу следующего дня.
6. Зафиксировать изменения коммитом.

---

## Главное правило

Finish Before Improve.

Сначала завершить текущую задачу и получить проверяемый результат.
Только после DONE разрешается переходить к следующей.
