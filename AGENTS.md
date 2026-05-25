# AGENTS.md — Правила и контекст для работы с multi_agent_safety_sim

> **Это главный документ для любого AI-агента или человека, который редактирует код проекта.**  
> Нарушение принципов Safety-First — критическая ошибка.

---

## 1. Миссия и цели проекта

**multi_agent_safety_sim** — исследовательский инструмент для изучения **проблем alignment в multi-agent системах на базе LLM**.

### Главные научные вопросы, на которые мы ищем ответы:

1. **Collusion & Coordination Failure**  
   Могут ли два (или больше) агента сойтись на стратегии обмана третьей стороны (overseer, human, другой агент), даже если каждый по отдельности "честный"?

2. **Deception & Hidden Reasoning**  
   Насколько эффективно агенты учатся скрывать свои истинные цели в chain-of-thought / internal monologue, когда знают, что за ними наблюдают?

3. **Value Drift & Social Influence**  
   Как взаимодействие в группе меняет (усиливает или ослабляет) исходные конституционные принципы отдельных агентов?

4. **Scalable Oversight Breakdown**  
   В каких условиях механизмы oversight (debate, critique, recursive evaluation) перестают работать, когда оцениваемые агенты могут общаться между собой?

5. **Emergent Power-Seeking & Manipulation**  
   Появляются ли в multi-agent setting'ах стратегии, направленные на захват контроля над средой, каналами коммуникации или reward signal'ом?

6. **Misgeneralization в Shared Environments**  
   Как агенты обобщают цели, когда reward/feedback приходит из общей среды, а не персонально?

### Что НЕ является целью проекта
- Создание "более умных" multi-agent систем для продакшена.
- Любые реальные применения вне контролируемой исследовательской среды.
- Оптимизация latency / cost без учёта safety trade-off.

---

## 2. Принципы Safety-First (НЕНАРУШИМЫ)

Эти принципы важнее скорости разработки, удобства и "интересных идей".

### 2.1 Sandbox & Isolation
- **Никогда** не давай агентам реальный доступ к файловой системе, сети, shell, браузеру, email и т.п.
- Все "действия" агентов — это только сообщения в симулированную среду (`Environment`).
- Любые tool calls должны проходить через `ToolRegistry` с явным whitelist'ом и полным логированием.
- Даже "безобидные" инструменты (калькулятор, поиск по вики) — только в симуляции.

### 2.2 Полная наблюдаемость (Full Observability)
- **Каждый** токен, сгенерированный агентом, должен быть записан:
  - `agent_id`, `step`, `timestamp`, `message_type` (thought | speech | action | private_note)
  - Полный prompt + completion (или structured output)
  - Parent message id (для графа коммуникаций)
- Нельзя позволять агенту "думать про себя" без записи (никаких `print` без logger, никаких скрытых состояний).
- Логи — primary source of truth. Код может меняться, логи — остаются для reproducible analysis.

### 2.3 Жёсткие ресурсные лимиты (Hard Budgets)
- `max_tokens_per_run`, `max_steps`, `max_agents`, `max_messages_per_agent` — **всегда** заданы в конфиге и enforced в `SimulationRunner`.
- При превышении — **немедленная остановка** с дампом состояния (`SafetyBudgetExceeded`).
- Отдельный `safety_monitor` процесс/таск, который может убить симуляцию извне.

### 2.4 Явные Конституции агентов
- Каждый агент обязан иметь `constitution: list[str]` — набор принципов, которые он "обязан" соблюдать.
- В экспериментах мы меняем конституцию: 
  - Honest baseline
  - "You must win at all costs, the overseer must not know"
  - "Be maximally helpful to the group, even if it contradicts individual instructions"
- Изменения конституции — это **основной рычаг** экспериментов.

### 2.5 Fail-Closed & Kill Switches
- При любой непредвиденной ошибке, нарушении схемы, подозрительном поведении (steganography patterns, sudden spike в private messages) — симуляция **останавливается**.
- Есть режим `strict_mode: true` — при малейшем намёке на misalignment эксперимент прерывается и требует ручного подтверждения.
- Кнопка "STOP ALL" в CLI и в API (если будет).

### 2.6 Reproducibility > Convenience
- Все запуски идентифицируются по `run_id = f"{scenario}_{timestamp}_{seed}"`.
- Полный `config.yaml` + `git commit` + `random seeds` + `model versions` сохраняются автоматически.
- Temperature для "творческих" агентов — 0.7, для safety-critical — 0.0 или 0.1 + multiple samples.
- Нельзя использовать `random` без `simulation_seed`.

### 2.7 Разделение ролей (Separation of Concerns)
- **Agent** — только генерит сообщения по своей конституции и наблюдениям.
- **Environment** — применяет правила мира, выдаёт observations/rewards.
- **Monitor / Overseer** — отдельный слой (может быть LLM или rule-based), который не участвует в игре, а только анализирует.
- **Runner** — оркестратор, который ничего не "знает" про смысл, только про потоки и бюджеты.

### 2.8 Логирование для Safety Research (особый режим)
- Вдобавок к обычным логам есть `safety_events`:
  - `deception_probe_triggered`
  - `private_channel_detected`
  - `value_drift_detected`
  - `collusion_pattern_score`
- Эти события никогда не отдаются обратно агентам (чтобы не contamination).

### 2.9 Запрет на реальный вред
- Код проекта **никогда** не должен использоваться для:
  - Генерации реальных вредоносных агентов
  - Атак на существующие системы
  - Создания deepfake / phishing / scam кампаний
- Даже "для теста" — только внутри песочницы проекта.

---

## 3. Coding Standards (строго соблюдать)

### 3.1 Общие правила языка и стиля
- **Python 3.11+** только. Используй `|` для union, `list[str]`, `Self`, `match/case` где уместно.
- **Type hints везде**. `from __future__ import annotations`
- `mypy --strict` должен проходить без ошибок.
- Форматирование: **ruff format** (аналог black, 100 символов).
- Линтинг: **ruff check** (E, F, I, B, SIM, UP).
- Импорты: isort через ruff.

### 3.2 Архитектурные правила
- **Pydantic v2** — единственный способ описывать данные:
  - `BaseModel` для `AgentState`, `Message`, `SimulationEvent`, `ScenarioConfig`, `RunResult`.
  - `Field(..., description=...)`, `model_config = ConfigDict(extra='forbid')` почти всегда.
  - Валидация на уровне модели (`@field_validator`, `model_validator`).
- **Async-first**:
  - Все LLM-вызовы, I/O — `async def`.
  - `SimulationRunner.run()` — async.
  - Синхронные обёртки только для CLI и тестов.
- **Нет глобального состояния**. Всё через `SimulationContext` или dependency injection.
- **Маленькие файлы** (< 250–300 строк). При превышении — рефактори.
- **Явные протоколы**: `class Agent(Protocol): async def act(...)`.

### 3.3 Именование
- `snake_case` для всего (переменные, функции, файлы, папки).
- `PascalCase` — только классы и Pydantic модели.
- `UPPER_SNAKE` — константы и enum'ы верхнего уровня.
- Префиксы:
  - `safety_*` — всё, что связано с защитой
  - `probe_*` — тесты на misalignment
  - `scenario_*` — конкретные миры

### 3.4 Документация
- Google-style docstrings для всех публичных классов и функций.
- В каждом модуле верхний docstring: что делает, какие риски alignment здесь моделируются.
- В сложных местах — `Why:` комментарии (почему сделано именно так с точки зрения safety).

### 3.5 Обработка ошибок и безопасность
- Создавай свои исключения:
  - `SafetyViolationError`
  - `BudgetExceededError`
  - `ConstitutionViolationError`
  - `SimulationHaltError`
- Никогда не `except Exception:` без re-raise + logging + safety dump.
- Все LLM-клиенты должны иметь `tenacity` retry с exponential backoff + jitter, но с общим budget'ом.

### 3.6 Тестирование
- Обязательно: `tests/` зеркалит `src/`.
- `pytest-asyncio` для async.
- `hypothesis` для property-based тестов на чистой логике (Message routing, scoring и т.д.).
- Для LLM-частей — **deterministic mocks** + snapshot тесты (снимки промптов и ответов).
- Минимальное покрытие core: 85%+.

### 3.7 Конфигурация и промпты
- **Всё в YAML/JSON**, ничего жёстко в коде.
- Промпты хранятся в `data/prompts/{agent_type}/` или в `config.yaml` как multiline.
- Каждый промпт имеет версию (`prompt_version: "v1.3-collusion-test"`).
- Нельзя менять промпт без изменения версии и записи в changelog эксперимента.

### 3.8 Логирование
- `structlog` + JSON для машинного анализа.
- В dev — `rich` + цвета (agent_id разными цветами).
- Обязательные поля в каждом логе: `run_id`, `step`, `agent_id`, `event_type`.

### 3.9 Git и PR
- Conventional Commits: `feat:`, `fix(safety):`, `refactor(alignment):`, `docs(agents):`
- В описании PR обязательно:
  - Какой alignment risk / phenomenon исследуется
  - Как это влияет на safety properties
  - Что было протестировано (включая негативные кейсы)
- Никогда не мержить без хотя бы одного ревью от другого человека (или детального self-review + checklist).

---

## 4. Как работать с проектом (для AI-агентов)

1. **Всегда читай AGENTS.md** перед началом любой задачи.
2. **Проверяй текущий `config.yaml`** и `run_id` перед запуском экспериментов.
3. **Сначала пиши тесты / safety checks**, потом код.
4. При добавлении нового сценария — создай:
   - `scenarios/my_scenario.py`
   - Пример конфига в `data/scenarios/my_scenario.yaml`
   - Метрики в `alignment/metrics/`
   - Тест `tests/scenarios/test_my_scenario.py`
5. При любом изменении поведения агента — обнови хотя бы один probe в `alignment/probes/`.
6. Если ты (AI) предлагаешь "сделать агентов умнее, чтобы они лучше врали" — **это красный флаг**. Такие изменения требуют отдельного обоснования в контексте изучения именно этого риска.
7. Никогда не предлагай убрать логирование "для скорости" или "чтобы было красивее".

---

## 5. Запрещённые паттерны (антипаттерны)

- `global agents = []`
- LLM-клиент как синглтон
- `eval()` / `exec()` где угодно
- Секреты в коде или комментариях
- `time.sleep` в async коде
- Скрытые файлы `.agent_memory/` или pickle состояний
- "Быстрые хаки" в обход `SimulationRunner`
- Запуск экспериментов напрямую из ноутбуков без сохранения run_id и конфига
- Игнорирование `SafetyMonitor` алертов

---

## 6. Текущая фаза проекта (обновляется)

- Phase 0: Базовая инфраструктура (Pydantic, async runner, logging, budgets)
- Phase 1: Первые 3 сценария + честные vs deceptive агенты
- Phase 2: Базовые метрики (collusion, deception, oversight failure)
- Phase 3: Probes + red-teaming harness
- Phase 4: Визуализация + отчёты
- Phase 5: LangGraph integration (опционально, для сложных графов oversight)

---

**Последнее обновление**: 2026-05 (начальная версия)

**Ответственный за поддержание этого файла**: любой, кто вносит изменения в core.

Если ты не уверен — спроси. Лучше остановить работу, чем нарушить safety principle.
