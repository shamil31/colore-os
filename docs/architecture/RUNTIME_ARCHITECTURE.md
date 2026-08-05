# Runtime Architecture v1

**Проект:** Coloré OS
**Sprint:** #4 — Research + Design
**Тип документа:** архитектура потока данных, без реализации
**Статус:** рабочий MVP (Research phase)

---

## Единственный вопрос, на который отвечает этот документ

Как информация проходит через Coloré OS от момента поступления до выдачи результата и обучения системы.

Это **не про реализацию**, **не про технологии**, **не про код**. Это про логику движения данных через слои и системы.

---

## Карта внешних источников данных

Информация поступает в Coloré OS из нескольких независимых источников:

### Коммуникационные каналы (первичный источник контактов)
1. **WhatsApp** — текстовые сообщения, медиа
2. **Telegram** — текстовые сообщения, медиа
3. **Телефон** — голосовые вызовы (требует транскрипции → текст)
4. **Сайт** — веб-формы, онлайн-чат
5. **Instagram DM** — прямые сообщения
6. **Email** — письма

### Операционная система (контекст клиента)
7. **Altegio API** (система записей и CRM) — читать:
   - История визитов клиента
   - Данные клиента (контакт, предпочтения)
   - История услуг и расходов
   - Текущее состояние записей
   - Доступность мастеров
   - График работы салона

### Система доставки (результаты выполненных действий)
8. **Integrilla API** (система доставки сообщений) — читать:
   - Статусы доставки сообщений
   - Подтверждения открытия
   - Метаданные доставки

### Бизнес-контекст (конфигурация)
9. **Конфигурация салона** (внутренний источник):
   - Доступные услуги
   - Расписание работы
   - Доступные мастера
   - Специальные условия и акции
   - Текущие ограничения (отпуск, техническое обслуживание)

---

## Цикл обработки одного контакта: полный поток данных

### Вход в систему (Entry Point)

**Триггер:** Новое сообщение или событие от клиента через любой канал

**Данные входа:**
```
{
  channel: "WhatsApp" | "Telegram" | "Phone" | "Website" | ...
  raw_message: <текст, голос, медиа>
  sender_id: <идентификатор в системе источника>
  timestamp: <время поступления>
  contact_info: <телефон, email, username>
}
```

**Точка входа:** Интеграционный слой (тех. описание: преобразование различных форматов в единый внутренний формат)

---

### Слой 1: Lead Intelligence Model (Понимание)

**Входы:**
- Сырое сообщение (текст, транскрибированная речь)
- История этого клиента из Altegio (если есть):
  - Прошлые визиты
  - Услуги
  - Потраченные суммы
  - Дата последнего визита
  - Отметки о доверии/проблемах

**Обработка:**
1. Экстракция Intent из текста (что хочет клиент: booking, info, comparison, consultation, price check)
2. Классификация Emotional State (уверен, растерян, раздражен, любопытен)
3. Оценка Decision Readiness (готов ли сейчас записаться, нужна ли информация, еще рано)
4. Загрузка Trust Score из истории (если клиент вернувшийся — история влияет)

**Выходы (передаются на следующий слой):**
```
{
  intent: <BOOKING | INFO | COMPARISON | CONSULTATION | PRICE_CHECK | ...>
  emotional_state: <CONFIDENT | HESITANT | ANXIOUS | CURIOUS | ...>
  decision_readiness: <READY_NOW | READY_SOON | NEEDS_INFO | NOT_READY | REJECTED>
  historical_trust: <SCORE from 0-100 or NULL if first-time>
  confidence: <HIGH | MEDIUM | LOW>
  reason: "customer is comparing services, showing medium trust"
}
```

**Данные, которые СОЗДАЁТ слой и должны СОХРАНЯТЬСЯ:**
- `intent_classification` (для обучения: помогли ли классификации точно)
- `emotion_assessment` (для обучения: попадали ли эмоции)
- `readiness_evaluation` (для обучения: была ли оценка корректна)

---

### Слой 2: Lead State Machine (Позиционирование)

**Входы:**
- Intent (из Lead Intelligence)
- Emotional State (из Lead Intelligence)
- Decision Readiness (из Lead Intelligence)
- Lead ID (из Altegio или новая учетная запись)
- История диалога этого лида (если есть)

**Обработка:**
1. Определение текущего состояния лида из 10 возможных
   - Initial Contact
   - Information Gathering
   - Price Conversation
   - Competitor Comparison
   - Consultation-Only Request
   - In Consultation
   - Interested in Booking
   - Lead Gone Cold
   - Lead Returned
   - Lead Gone (Final)

2. Выбор стартового или следующего состояния на основе Intent + Readiness + истории

**Выходы (передаются на следующий слой):**
```
{
  lead_state: <одно из 10 состояний>
  state_entry_reason: "intent is BOOKING, readiness is READY_NOW"
  allowed_actions: <набор действий, разрешённых в этом состоянии>
  constraints: <ограничения этого состояния (что запрещено)>
}
```

**Данные, которые СОЗДАЁТ слой и должны СОХРАНЯТЬСЯ:**
- `state_transition_history` (какое состояние было, какое стало, почему)
- `state_duration` (как долго лид находился в каждом состоянии)

---

### Слой 3: Next Best Action Engine (Решение)

**Входы:**
- Lead State (из Lead State Machine)
- Intent, Emotional State, Decision Readiness, Trust (из Lead Intelligence)
- Business Context (из Altegio):
  - Доступные мастера и слоты
  - Текущие акции и специальные предложения
  - Конкретные услуги, которые невозможны (закрыты, отпуск, техническое обслуживание)
  - Ограничения по времени
- Conversation History (последние обмены в этом диалоге)
- `Reason` из предыдущего выбора действия (если был)

**Обработка:**
1. Определение наибольшего барьера для буксирования (Trust? Understanding? Readiness?)
2. Выбор одного действия из каталога 8:
   - `AskQuestion` — задать уточняющий вопрос
   - `ShowProof` — показать работы и отзывы
   - `Differentiate` — объяснить отличия
   - `GivePrice` — назвать цену
   - `OfferConsultation` — предложить консультацию
   - `OfferBooking` — предложить запись
   - `HandOffToHuman` — передать человеку
   - `DoNothing` — выждать паузу

3. Проверка Business Context: может ли это действие быть выполнено?
   - Если `OfferBooking` выбрано, но нет свободных слотов → fallback на `AskQuestion`

4. Оценка уверенности в решении (Confidence)
   - Если Confidence < порог → `HandOffToHuman`

**Выходы (передаются на следующий слой):**
```
{
  action: <одно из 8 действий>
  action_reason: "biggest barrier is low trust, showing proof addresses it"
  confidence: <HIGH | MEDIUM | LOW>
  action_parameters: {
    if action == GivePrice: { price: <value>, service: <service_id> }
    if action == OfferBooking: { available_slots: <list>, master_id: <id> }
    if action == AskQuestion: { question_topic: <CLARIFICATION | CONCERN | ...> }
    ...
  }
}
```

**Данные, которые СОЗДАЁТ слой и должны СОХРАНЯТЬСЯ:**
- `action_selection_reasoning` (для обучения: какой барьер определен, почему это действие)
- `confidence_assessment` (для обучения: была ли уверенность оправдана)
- `barrier_identification` (какой барьер был определен как наибольший)

---

### Слой 4: Conversation Engine (Речь)

**Входы:**
- Action (из Next Best Action Engine)
- `Reason` (из Next Best Action Engine) — подсказка для акцентирования
- Emotional State (из Lead Intelligence) — как подавать информацию
- Trust Score (из Lead Intelligence) — сколько обоснования нужно
- Conversation History (последние обмены) — контекст
- Tone of Brand (конфигурация) — голос бренда Coloré
- Action Parameters (цена, доступные слоты, вопрос, и т.д.)

**Обработка:**
1. Трансформация Action в сообщение:
   - `AskQuestion` → "Можно узнать, какой результат вам нужен?"
   - `ShowProof` → (ссылка на галерею работ + короткий текст)
   - `GivePrice` → "Стандартная стрижка стоит 1500 р. Вас интересует?"
   - `OfferBooking` → "Есть свободное окно завтра в 15:00 с Мариной. Подходит?"

2. Адаптация тона под Emotion:
   - Если Emotional State = ANXIOUS → мягче, спокойнее, больше заверений
   - Если Emotional State = CONFIDENT → прямо и коротко

3. Адаптация обоснования под Trust:
   - Если Trust LOW → "Вот ссылка на отзывы других клиентов. Они помогут?"
   - Если Trust HIGH → "Записать вас?"

4. Контроль за историей:
   - Не переспрашивать то, что клиент уже сказал
   - Не повторять предыдущие сообщения
   - Продолжать установленный контакт

5. Применение Tone of Brand:
   - Единый стиль, узнаваемый голос
   - Премиальный регистр, без канцеляризма

**Выходы (отправляются клиенту через Integrilla):**
```
{
  message_text: <готовое сообщение для клиента>
  message_format: "text" | "image" | "carousel" | "link"
  channel: <тот же канал, откуда пришло исходное сообщение>
  
  internal_metadata: {
    generated_from_action: <какое действие привело к этому сообщению>
    tone_applied: "brand_voice"
    emotion_adaptation: <какая эмоция учитывалась>
    trust_adaptation: <какой уровень доверия учитывался>
    reason_accentuation: <где сделан упор на основе Reason>
  }
}
```

**Данные, которые СОЗДАЁТ слой и должны СОХРАНЯТЬСЯ:**
- `generated_message` (само сообщение — для аудита)
- `generation_parameters` (какие параметры привели к этому тексту)
- `adaptation_log` (какие адаптации были применены)

---

## Отправка сообщения клиенту

**Выход из Conversation Engine:**
```
→ Integrilla API (система доставки сообщений)
```

**Integrilla:**
- Получает сообщение
- Выбирает канал доставки
- Доставляет сообщение
- Возвращает статусы: `delivered`, `read`, `failed`, `timeout`

**Данные, которые запрашиваются из Integrilla:**
- Статус доставки (для Learning Loop)
- Время доставки
- Время прочитания (если доступно)

---

## Ожидание ответа клиента

**Состояние:** Ожидание (Waiting state)

**Триггеры выхода из ожидания:**
1. Клиент отправил сообщение → новый цикл обработки (начало с Lead Intelligence Model)
2. Истекло время ожидания (timeout) → Lead Gone Cold (переход в State Machine)
3. Клиент явно закрыл чат / отклонил предложение → Lead Gone (Final)

---

## Фаза Learning Loop: Обратная связь

**Триггеры Learning Loop:**
1. Клиент ответил или не ответил (не ответил тоже сигнал)
2. Клиент совершил действие (записался или не записался)
3. Прошло время и статус лида изменился

**Сбор данных для обучения:**
```
{
  cycle_id: <уникальный идентификатор цикла обработки>
  
  input_data: {
    raw_message: <исходное сообщение>
    channel: <источник>
  }
  
  predictions_and_decisions: {
    predicted_intent: <что сказала Lead Intelligence>
    predicted_emotion: <предсказанное эмоциональное состояние>
    predicted_readiness: <готовность к записи>
    selected_action: <какое действие выбрал NBA Engine>
    confidence: <уверенность>
  }
  
  actual_outcome: {
    client_response: <что сделал клиент>
    response_time: <за сколько ответил>
    booking_result: <записался или нет>
  }
  
  validation: {
    was_intent_correct: <true | false>
    was_emotion_assessment_accurate: <true | false>
    was_action_effective: <true | false>
    what_barrier_was_actually_blocking: <данные из диалога>
  }
}
```

**Куда сохраняется:**
- База данных (Learning Dataset) — для переобучения моделей
- Метрики системы — для мониторинга качества
- Аудит диалогов — для анализа ошибок

---

## События, запускающие новый цикл

**Внешние события (инициированы клиентом):**
1. Новое сообщение от клиента (любой канал)
2. Клиент заявил о себе через веб-форму (сайт)
3. Клиент перезвонил по телефону

**Внутренние события (инициированы системой):**
4. Истекло время ожидания ответа (timeout) → переход в "Lead Gone Cold"
5. Получено уведомление из Integrilla о неудачной доставке → action: `HandOffToHuman`
6. Клиент вернулся после длительного отсутствия (сигнал из истории Altegio)

**События из Altegio:**
7. Изменилась доступность мастеров → пересчет Business Context → возможно новый Action
8. Клиент записался в салон через Altegio напрямую (система должна узнать об этом для завершения цикла)

---

## События, завершающие цикл

**Явное завершение (цель достигнута):**
1. Клиент записался на услугу → запись в Altegio → цикл завершен
2. Клиент отказался от записи → состояние "Lead Gone (Final)" → цикл завершен

**Неявное завершение (ожидание):**
3. Клиент перешел в "Lead Gone Cold" → система ждет возобновления контакта
4. Клиент передан человеку (HandOffToHuman) → цикл ждет результата действия человека

**Завершение с ошибкой:**
5. Сообщение не доставлено несколько раз → Lead Gone → цикл завершен (неудачно)

---

## Сохранение vs. Временные данные

### СОХРАНЯЮТСЯ (в базе данных):
- **Lead Profile** (клиент и его история)
  - История контактов
  - Все состояния, в которых был лид
  - Все выбранные действия и причины
  - История доверия (Trust Score)
  - История попыток записи

- **Dialogue Transcript**
  - Все сообщения (входящие и исходящие)
  - Временные метки
  - Каналы
  - Внутренние метаданные (какое действие привело к сообщению)

- **System Decisions**
  - Intent классификация → результат (правильно/неправильно)
  - Emotion assessment → результат
  - Action selection → результат
  - Confidence assessment → результат

- **Learning Dataset**
  - Все пары (входные данные → выходные решения → результат)
  - Используется для переобучения моделей

- **Business Context Snapshots**
  - На момент каждого решения: какие мастера были свободны, какие акции действовали
  - Нужна для анализа: почему выбран был fallback?

### ВРЕМЕННЫЕ (не сохраняются после цикла):
- Raw text сообщения (в сыром виде) — только финальная версия с метаданными
- Промежуточные черновики сообщений (Conversation Engine может генерировать варианты)
- Пересчеты Business Context в процессе (сохраняется только финальное состояние на момент решения)
- Internal reasoning traces (как система думала) — упоминается только в Reason field

---

## Полный цикл в деталях: Пример

**Сценарий:** Новый клиент пишет в WhatsApp: "Привет! Можно ли сделать балаяж?"

### Цикл 1

**Вход:**
```
Channel: WhatsApp
Message: "Привет! Можно ли сделать балаяж?"
Sender: +7-999-123-45-67
History: нет (первый контакт)
```

**Lead Intelligence Model:**
```
intent: CONSULTATION (спрашивает про возможность услуги)
emotional_state: CURIOUS (тон позитивный)
decision_readiness: NEEDS_INFO (нужна информация перед решением)
trust: NULL (новый клиент)
confidence: HIGH
```

**Lead State Machine:**
```
lead_state: INITIAL_CONTACT → INFORMATION_GATHERING
allowed_actions: [AskQuestion, ShowProof, Differentiate, OfferConsultation, HandOffToHuman]
forbidden_actions: [OfferBooking, OfferPrice]
```

**Next Best Action Engine:**
```
barrier: LACKS_UNDERSTANDING (не знает, как выглядит балаяж, что входит)
action: SHOW_PROOF (показать портфолио балаяжей салона)
confidence: HIGH
reason: "Client is curious about specific service, portfolio will build confidence"
```

**Conversation Engine:**
```
message_text: "Да, балаяж — одна из наших фирменных техник! 
Вот несколько примеров работ нашего мастера Анны: [ссылка на галерею]
Подходит ли вам такой результат?"

generated_from_action: SHOW_PROOF
emotion_adaptation: friendly, engaged tone (CURIOUS is positive)
trust_adaptation: minimal explanation (new client, needs proof more than reassurance)
```

**Отправка:** → Integrilla → WhatsApp

**Ожидание:** Цикл 1 завершен, система ждет ответа

---

### Цикл 2 (если клиент ответит через 30 минут)

**Вход:**
```
Channel: WhatsApp
Message: "Красиво! А сколько стоит и сколько времени?"
Sender: +7-999-123-45-67
History: диалог из Цикла 1 + история портфолио, которое было показано
```

**Lead Intelligence Model:**
```
intent: PRICE_CHECK + INFO (просит цену и время)
emotional_state: INTERESTED (фраза "Красиво!")
decision_readiness: READY_SOON (может записаться, но нужна цена)
trust: LOW (новый клиент, но уже проявил интерес)
confidence: HIGH
```

**Lead State Machine:**
```
lead_state: INFORMATION_GATHERING → PRICE_CONVERSATION
(он спросил про цену, это переход в ценовую зону)
```

**Next Best Action Engine:**
```
barrier: MISSING_FACTUAL_INFO (цена и время)
action: GIVE_PRICE
confidence: HIGH
action_parameters: {
  service: "balayage",
  price: "4500 руб",
  duration: "180 minutes",
  available_masters: ["Anna"],
  next_available: "tomorrow 15:00"
}
```

**Conversation Engine:**
```
message_text: "Балаяж у Анны стоит 4500 руб и занимает около 3 часов. 
У неё есть свободное окно завтра в 15:00, если интересует?"

emotion_adaptation: Direct, confident tone (client showed clear interest)
trust_adaptation: Simple facts, no excessive justification (increasing trust already)
```

**Отправка:** → Integrilla → WhatsApp

**Ожидание:** Цикл 2 завершен, система ждет ответа

---

### Цикл 3 (если клиент согласится)

**Вход:**
```
Channel: WhatsApp
Message: "Отлично! Записываю себя на завтра в 15:00"
Sender: +7-999-123-45-67
```

**Lead Intelligence Model:**
```
intent: BOOKING_CONFIRMATION (явное согласие)
emotional_state: CONFIDENT (решение принято)
decision_readiness: READY_NOW (готов к записи)
trust: MEDIUM (перешел от LOW, система показала надежность)
confidence: HIGH
```

**Lead State Machine:**
```
lead_state: PRICE_CONVERSATION → INTERESTED_IN_BOOKING → [передача человеку]
```

**Next Best Action Engine:**
```
barrier: none (барьер устранен)
action: HANDOFF_TO_HUMAN (запись должна быть создана в Altegio)
confidence: HIGH
reason: "All information provided, ready to create booking in Altegio"
```

**Conversation Engine:**
```
message_text: "Отлично! Подтверждаю запись на завтра в 15:00. 
Мы пришлём вам напоминание. До встречи! 💇‍♀️"
```

**Отправка:** → Integrilla → WhatsApp

**Параллельно:** Запись создается в Altegio, статус клиента обновляется

**Цикл завершен:** УСПЕШНО (клиент записался)

---

### Learning Loop для всех трех циклов

**Сбор:**
```
Цикл 1:
  - Predicted: CONSULTATION, CURIOUS, NEEDS_INFO
  - Actual: Клиент ответил через 30 мин, проявил интерес
  - Validation: ✓ Все предсказания были верны

Цикл 2:
  - Predicted: PRICE_CHECK, INTERESTED, READY_SOON
  - Actual: Клиент согласился
  - Validation: ✓ Действие SHOW_PROOF помогло переходу на PRICE_CONVERSATION

Цикл 3:
  - Predicted: BOOKING_CONFIRMATION, CONFIDENT, READY_NOW
  - Actual: Клиент записался
  - Validation: ✓ Система корректно предсказала готовность
```

**Обучение:**
- Для Intent Classifier: "Балаяж + тон позитивный = CONSULTATION (не BOOKING, не PRICE_CHECK)"
- Для Emotion Classifier: "Слово 'красиво' = INTERESTED (повышает доверие)"
- Для Action Selection: "SHOW_PROOF эффективна для CONSULTATION intent"
- Для Readiness Predictor: "После SHOW_PROOF + вопрос о цене = переход в READY_SOON"

---

## События в хронологическом порядке

| Время | Событие | Триггер | Результат |
|-------|---------|---------|-----------|
| T0 | Сообщение пришло в систему | Клиент написал в WhatsApp | Начало Цикла 1 |
| T0+1s | Полная обработка (все 4 слоя) | Автоматическое | Action выбран |
| T0+2s | Сообщение отправлено | Action = SHOW_PROOF | Клиент получит ссылку |
| T0+3s | Сообщение доставлено | Integrilla подтвердил | Статус "delivered" |
| T0+30m | Новое сообщение от клиента | Клиент ответил | Начало Цикла 2 |
| T0+30m+2s | Полная переобработка | Новый контекст | Action = GIVE_PRICE |
| T0+1h | Третье сообщение от клиента | Клиент согласился | Начало Цикла 3 |
| T0+1h+2s | Запись создается в Altegio | Action = HANDOFF_TO_HUMAN | Клиент в системе |
| T0+1h+3s | Learning Loop | Все циклы завершены | Данные собраны |
| T0+1h+4s | Метрики обновлены | Learning Loop завершен | System Quality Metrics |

---

## Данные, требующиеся от каждого источника на каждый момент

### Altegio (читается для каждого цикла)
- История клиента (если есть)
- Доступность мастеров в реальном времени
- Расписание работы салона
- Текущие акции и спецпредложения
- Статус услуг (какие доступны, какие закрыты)

### Integrilla (читается для каждой отправки)
- Статусы доставки предыдущих сообщений
- Доступные каналы для этого клиента
- Ограничения по частоте отправки
- История неудачных доставок

### Business Context (актуализируется каждый цикл)
- `current_available_masters`: ["Anna", "Maria"]
- `booked_slots_today`: [(13:00-15:30), (16:00-18:00)]
- `active_promos`: ["Summer haircut 15% off", "First visit 500 rub discount"]
- `service_status`: {"balayage": "available", "straightening": "closed", ...}

### Lead Intelligence State (сохраняется)
- `last_intent_classification`
- `last_emotion_assessment`
- `last_readiness_score`
- `trust_score_history`
- `conversation_history`

---

## Граница ответственности каждого компонента

| Компонент | Что ДЕЛАЕТ | Что НЕ ДЕЛАЕТ |
|-----------|-----------|-------------|
| **Lead Intelligence Model** | Читает сообщение, оценивает Intent/Emotion/Readiness | Не выбирает действие, не пишет сообщения |
| **Lead State Machine** | Определяет состояние, разрешенные действия | Не выбирает конкретное действие |
| **Next Best Action Engine** | Выбирает КАКОЕ действие, не КОГДА и не КАК | Не пишет сообщения, не меняет действие |
| **Conversation Engine** | Превращает действие в сообщение | Не решает, какое действие, не создает запись |
| **Integrilla** | Доставляет сообщение | Не выбирает, что писать |
| **Altegio** | Хранит реальное состояние (записи, клиенты) | Не решает, что делать, когда клиент свяжется |

---

## Места, где система может сломаться (ошибки в потоке)

1. **Intent Misclassification** → выбран неправильный Action → неэффективное сообщение
2. **Missing Business Context** → обещана недоступная услуга → конфликт
3. **Confidence Too High** → неверное действие не эскалировано → клиент потерян
4. **Emotion Misread** → неправильный тон сообщения → потеря доверия
5. **Historical Context Lost** → повтор вопроса, уже заданного → раздражение
6. **Integrilla Failure** → сообщение не доставлено → молчание вместо ответа
7. **Altegio Out of Sync** → система предлагает несуществующие слоты → ошибка

---

## Итоговая архитектура потока данных

```
ИСТОЧНИКИ ДАННЫХ
    ↓
    ├─ WhatsApp / Telegram / Phone / Web / Email
    ├─ Altegio (история, контекст, доступность)
    └─ Integrilla (статусы доставки)
    
    ↓ [преобразование в единый формат]
    
LEAD INTELLIGENCE MODEL (Понимание)
    Intent, Emotion, Readiness, Trust
    
    ↓
    
LEAD STATE MACHINE (Позиционирование)
    10 состояний, разрешенные действия
    
    ↓
    
NEXT BEST ACTION ENGINE (Решение)
    1 действие из 8 + Reason
    
    ↓
    
CONVERSATION ENGINE (Речь)
    1 сообщение в Tone of Brand
    
    ↓ [доставка]
    
INTEGRILLA
    Клиент получает сообщение
    
    ↓ [ожидание ответа]
    
[ТРИ ВОЗМОЖНЫХ ПУТИ]
├─ Клиент ответил → новый цикл
├─ Timeout → Lead Gone Cold
└─ Явный отказ → Lead Gone Final

    ↓
    
LEARNING LOOP
    Сбор: predictions → actual outcomes
    Сохранение: в database для обучения
    Использование: для улучшения моделей в будущих циклах
```

---

## Вопросы, на которые отвечает эта архитектура

1. **Все ли внешние источники определены?** ✅ Да (6 каналов + Altegio + Integrilla + конфиг)

2. **Как данные попадают в систему?** ✅ Через интеграционный слой (преобразование в единый формат)

3. **Какие слои используют какие данные?** ✅ Каждый слой описан с входами

4. **Какие данные создает каждый слой?** ✅ Документировано в выходах каждого слоя

5. **Что передается между слоями?** ✅ Структурированные объекты (Intent, State, Action, Message)

6. **Какие данные сохраняются?** ✅ Профиль лида, диалог, решения, dataset обучения

7. **Какие данные временные?** ✅ Промежуточные вычисления, черновики

8. **Какие события запускают цикл?** ✅ Сообщение клиента, события из Altegio, timeout

9. **Какие события завершают цикл?** ✅ Запись, отказ, передача человеку, многократный timeout

10. **Где начинается Learning Loop?** ✅ После завершения цикла (во всех вариантах)

---

**Этот документ описывает АРХИТЕКТУРУ потока, не реализацию. Техническое решение (сервисы, БД, API, инструменты) — это следующий этап (Sprint #5+).**
