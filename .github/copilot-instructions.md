## 0. Środowisko docelowe i CI/CD

### Środowisko deweloperskie
- Projekt jest rozwijany i uruchamiany na **Linux** (deweloperzy pracują na Linuksie)
- Testy lokalne i CI uruchamiane są na Ubuntu (`ubuntu-22.04`)

### Pakowanie i dystrybucja (Windows)
- Produkcyjna aplikacja jest **pakowana na Windows** w ramach pipeline'u CI/CD
- Do budowania pliku wykonywalnego używany jest **PyInstaller** (plik spec: `AitrackerGuiPyInstaller.spec`)
- Gotowy plik wykonywalny jest następnie pakowany w **instalator przy użyciu Inno Setup** (plik: `innosetup_github.iss`)
- Instalator jest opcjonalnie podpisywany cyfrowo przy użyciu DigiCert Software Trust Manager

### Plik workflow CI/CD
- Plik GitHub Actions workflow znajduje się w: **`.github/workflows/main.yml`**
- Pipeline składa się z trzech głównych jobów:
  1. **`build-test`** – testy na Ubuntu (uruchamiane przy każdym pushu/PR do `main`)
  2. **`tests-windows-build-app`** – testy + build PyInstaller + Inno Setup na Windows (przy każdym pushu/PR, instalator budowany tylko przy tagach `v*`)
  3. **`upload-ftps`** – upload instalatora przez FTPS na serwer (tylko przy tagach `v*`)

## 0a. Analiza kodu – zasady ogólne

Zawsze używaj analizy semantycznej, drzewa AST i serwera językowego (LSP) do rozwiązywania symboli i referencji. Kategorycznie unikaj prostego wyszukiwania tekstowego (stylu "grep").

Kiedy analizujesz kod, generujesz odpowiedzi lub proponujesz refaktoryzację, stosuj następujące zasady:

1. **Rozwiązywanie symboli:** Opieraj się na definicjach typów i konfiguracji statycznej analizy (Pyright). Śledź jawne typowanie zmiennych oraz argumentów, aby precyzyjnie określić, jakiego obiektu dotyczy zapytanie.
2. **Narzędzia obszaru roboczego:** Używając agenta @workspace, priorytetyzuj zapytania "Find All References" oraz "Go to Implementation" nad wyszukiwaniem ciągów znaków.

## 1. Szybki start (Python 3.11+)

Zakładamy standardową strukturę:
- `aitracker_gui/` – główny pakiet Pythona
- `pyproject.toml` – konfiguracja projektu, zależności i narzędzi (formatowanie, lint, typy itp.)
- `uv.lock` – plik lockfile z dokładnymi wersjami zależności (generowany przez `uv`)
- `tests/` – testy jednostkowe i integracyjne

Rekomendowane kroki (Linux/macOS):
```bash
# Instalacja zależności i synchronizacja środowiska
uv sync

# Dodawanie nowej zależności runtime
uv add <nazwa-pakietu>

# Dodawanie zależności deweloperskiej
uv add --dev <nazwa-pakietu>
```

## 2. Walidacja podstawowa

```bash
# Formatowanie (ruff)
ruff format --check
# Lint (ruff)
ruff check
# Typy (pyright – jeśli zainstalowany globalnie przez npm)
npx pyright aitracker_gui
# lub jeśli pyright w środowisku Pythona:
pyright aitracker_gui
# Testy (bez testów oznaczonych markerami manual/gpu/benchmark)
uv run pytest -m "not manual and not gpu and not benchmark" --cov=aitracker_gui --cov-fail-under=55 -v
```

## 3. Zasady kodowania

### Typowanie (type hints)
- **ZAWSZE** dodawaj typowanie do wszystkich funkcji i metod (argumenty + typ zwracany)
- Dla metod bez argumentów (poza `self`/`cls`) i bez zwracanej wartości dodawaj `-> None`
- Dla metod `__init__` zawsze dodawaj `-> None`
- Używaj nowoczesnej składni typów (Python 3.10+): `list[str]`, `dict[str, int]`, `str | None` zamiast `List[str]`, `Dict[str, int]`, `Optional[str]`
- Dla kolekcji używaj wbudowanych typów generycznych: `list`, `dict`, `set`, `tuple`
- Dla tablic NumPy używaj aliasu `NumpyArray` z `aitracker_gui.helpers.aisp_typing` zamiast `np.ndarray`
- Dotyczy również testów – wszystkie funkcje testowe i fixtury muszą mieć typowanie

**Przykłady poprawnego typowania:**
```python
# Funkcja z argumentami i wartością zwracaną
def calculate_total(items: list[int], multiplier: float) -> float:
    return sum(items) * multiplier

# Metoda bez wartości zwracanej
def update_state(self, new_value: str) -> None:
    self.value = new_value

# Metoda bez argumentów
def reset(self) -> None:
    self.value = ""

# __init__ zawsze z -> None
def __init__(self, name: str, count: int = 0) -> None:
    self.name = name
    self.count = count

# Opcjonalne wartości
def find_item(self, key: str) -> Item | None:
    return self.items.get(key)

# Callbacki i funkcje wyższego rzędu
def process(self, callback: Callable[[str], bool]) -> None:
    callback(self.data)
```

**Przykład typowania w testach:**
```python
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_service() -> MagicMock:
    return MagicMock()

@pytest.fixture
def sample_data() -> list[dict[str, int]]:
    return [{"a": 1}, {"b": 2}]

def test_calculation(sample_data: list[dict[str, int]]) -> None:
    result = calculate(sample_data)
    assert result == 3
```

### Importy
1. Najpierw standardowa biblioteka
2. Potem zależności zewnętrzne
3. Na końcu moduły lokalne `aitracker_gui.*`
Używaj importów absolutnych.

### Zakaz używania TYPE_CHECKING
- **NIGDY** nie używaj `TYPE_CHECKING` z modułu `typing`
- Dobra architektura kodu broni się sama – jeśli pojawia się potrzeba `TYPE_CHECKING`, to znak na cykliczną zależność, którą należy rozwiązać przez refaktoryzację (np. wydzielenie interfejsu, odwrócenie zależności)
- Importy muszą być bezwarunkowe – typ musi być dostępny w czasie wykonania, nie tylko przy statycznej analizie

**Zamiast:**
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aitracker_gui.data.models.tracklet_trajectory import TrackletTrajectory
```

**Użyj:**
```python
from aitracker_gui.data.models.tracklet_trajectory import TrackletTrajectory
```

Jeśli import powoduje cykliczną zależność – to jest sygnał do refaktoryzacji architektury, nie do obejścia problemu przez `TYPE_CHECKING`.

### Guard clauses
Preferuj wczesne wyjścia (`return`, `continue`, `break`) zamiast zagnieżdżania wielu `if`/`elif`.

**Dlaczego guard clauses są lepsze:**
- Redukują zagnieżdżenie kodu (mniej indentacji)
- Eliminują potrzebę zmiennych tymczasowych (np. `result = None` ... `if result is not None`)
- Każdy warunek jest niezależny i łatwiejszy do zrozumienia
- Ułatwiają dodawanie nowych przypadków bez modyfikacji istniejącej logiki
- Kod czyta się "od góry do dołu" - najpierw warunki brzegowe, potem główna logika

**Przykład - zamiast:**
```python
def validate(value: int, limit: int) -> str:
    result = None
    if value > 0:
        if value < limit:
            result = "ok"
        else:
            result = "too_high"
    else:
        result = "invalid"
    return result
```

**Użyj:**
```python
def validate(value: int, limit: int) -> str:
    # Check: value must be positive
    if value <= 0:
        return "invalid"

    # Check: value must be below limit
    if value >= limit:
        return "too_high"

    return "ok"
```

### Formatowanie guard clauses
- **Zawsze** dodawaj pustą linię po bloku guard clause (po `return`, `continue`, `break`)
- **Zawsze** dodawaj pustą linię **po zamknięciu pętli** (`for`/`while`) przed kolejnym kodem
- Opcjonalnie: przed guard clause możesz dodać komentarz opisujący co sprawdzamy, w formacie `# Check: <opis>`

**Przykład - poprawne formatowanie:**
```python
def process(self, data: list[int], limit: int) -> str:
    # Check: input list must not be empty
    if not data:
        return "empty"

    # Check: limit must be positive
    if limit <= 0:
        return "invalid_limit"

    # Main logic starts here
    total = sum(data)
    return str(total)
```

**Przykład - puste linie w pętlach z `continue` i po zakończeniu pętli:**
```python
# ❌ ZŁE – brak pustej linii po continue i po zamknięciu pętli
result: dict[str, Foo] = {}
for item in items:
    value = mapping.get(item.id)
    if value is None:
        continue
    result[item.id] = value
do_something(result)

# ✅ DOBRE – puste linie po continue i po zamknięciu pętli
result: dict[str, Foo] = {}
for item in items:
    value = mapping.get(item.id)
    if value is None:
        continue

    result[item.id] = value

do_something(result)
```

### Wartości sentinel
Tam gdzie to upraszcza logikę – używaj wartości specjalnych (np. -1) zamiast `None` przy prostych typach.

### Nie twórz metod pomocniczych wywoływanych tylko raz
Nie wyodrębniaj logiki do osobnej metody, jeśli jest wywoływana tylko w jednym miejscu. Długie funkcje są czytelniejsze niż skakanie po metodach i szukanie, gdzie flow kodu przeskoczył dalej.

Metodę warto tworzyć dopiero gdy:
- ten sam fragment logiki jest wywoływany w **co najmniej 2 miejscach** (DRY)
- metoda ma jasno wydzielony, testowalny kontrakt (np. parsowanie, walidacja zewnętrznego wejścia)

**Zamiast:**
```python
def process(self, tracklet: TrackletV2) -> None:
    self._run_pipeline(tracklet)
    self._validate(tracklet)   # wywołane tylko tutaj

def _validate(self, tracklet: TrackletV2) -> None:
    # 20 linii logiki...
```

**Użyj:**
```python
def process(self, tracklet: TrackletV2) -> None:
    self._run_pipeline(tracklet)

    # Validation : ...
    # 20 linii logiki bezpośrednio tu
```

### Brak bloków separatorów komentarzy
Nie twórz wizualnych sekcji z separatorami poziomymi, np.:
```python
# ------------------------------------------------------------------
# Private
# ------------------------------------------------------------------
```
Takie bloki zaśmiecają kod i są zbędne szczególnie w małych klasach. Jeśli plik jest duży i podział jest naprawdę potrzebny, użyj docstringa lub pogrupuj metody logicznie bez separatorów.

### Obsługa błędów – preferuj graceful degradation, nie wyjątki
Nie rzucaj wyjątków (`raise`) w metodach pomocniczych i wewnętrznych rejestratorach, gdy błąd można obsłużyć łagodnie.
Lepiej aby aplikacja działała w 80% poprawnie niż żeby się całkowicie wysypała z powodu jednego błędu konfiguracyjnego.

**Zamiast:**
```python
def _register(self, classifier: TrackerClassifier) -> None:
    if classifier.kind() in self._classifiers:
        raise ValueError(f"Classifier '{classifier.kind()}' already registered.")
    self._classifiers[classifier.kind()] = classifier
```

**Użyj:**
```python
def _register(self, classifier: TrackerClassifier) -> None:
    kind = classifier.kind()
    if kind in self._classifiers:
        logger.fatal("Classifier '%s' already registered, skipping.", kind)
        return
    self._classifiers[kind] = classifier
```

Zasada: loguj błąd na odpowiednim poziomie (`logger.fatal` / `logger.error`) i kontynuuj działanie.

### Pydantic BaseModel
- Dla mutowalnych wartości domyślnych (listy, słowniki, obiekty) używaj `Field(default_factory=...)`
- Nigdy nie używaj `= []`, `= {}` ani `= SomeModel()` jako domyślnych wartości pól
- Przykład poprawnej definicji:
```python
from pydantic import BaseModel, Field

class MyModel(BaseModel):
    # Listy - używaj default_factory=list
    items: list[str] = Field(default_factory=list)

    # Słowniki - używaj default_factory=dict
    mapping: dict[str, int] = Field(default_factory=dict)

    # Zagnieżdżone modele - używaj default_factory=ModelClass
    nested: NestedModel = Field(default_factory=NestedModel)

    # Typy niemutowalne (int, str, bool, None) - można używać bezpośrednio
    count: int = 0
    name: str = ""
    enabled: bool = True
```

### Pydantic - serializacja i metadane pól
- Używaj `model_dump()` zamiast ręcznego budowania słowników
- Dynamicznie generuj listy pól/nagłówków z `model_fields` zamiast twardego kodowania
- Dla warunkowego wykluczania pól (np. eksport CSV vs baza danych) używaj `json_schema_extra` z własnymi flagami
- Nigdy nie twórz osobnych list stringów z nazwami pól - wykorzystuj introspekcję modelu

**Przykład - metadane pól dla selektywnej serializacji:**
```python
from pydantic import BaseModel, Field

class FileEntry(BaseModel):
    name: str = Field(default="", alias="Name")
    index: int = Field(default=0, alias="Index")
    # Pole wykluczone z eksportu CSV, ale serializowane do bazy
    thumbnail: bytes | None = Field(default=None, json_schema_extra={"csv_exclude": True})

    def to_csv_row(self) -> dict[str, Any]:
        """Eksport wiersza z wykluczeniem pól oznaczonych csv_exclude."""
        excluded = {
            name for name, info in type(self).model_fields.items()
            if isinstance(info.json_schema_extra, dict) and info.json_schema_extra.get("csv_exclude")
        }
        return self.model_dump(mode="json", by_alias=True, exclude=excluded)

    @classmethod
    def csv_headers(cls) -> list[str]:
        """Dynamiczne generowanie nagłówków z definicji modelu."""
        headers = []
        for field_name, field_info in cls.model_fields.items():
            extra = field_info.json_schema_extra
            if isinstance(extra, dict) and extra.get("csv_exclude"):
                continue
            headers.append(field_info.alias or field_name)
        return headers
```

### Nazewnictwo metod serializacji i deserializacji

#### Serializacja (obiekt → dane)
- Metody serializujące obiekt do innej postaci nazywaj z prefiksem `to_`:
  - `to_dict()` – serializacja do słownika
  - `to_json()` – serializacja do stringa JSON
  - `to_csv()` – serializacja do stringa/pliku CSV
  - `to_csv_row()` – serializacja do wiersza CSV (słownik z wartościami)
  - `to_dataframe()` – konwersja do `pd.DataFrame`
- Są to **metody instancji** (przyjmują `self`)

#### Deserializacja (dane → obiekt)
- Metody tworzące obiekt na podstawie danych zewnętrznych nazywaj z prefiksem `from_`:
  - `from_dict()` – tworzenie obiektu ze słownika
  - `from_json()` – tworzenie obiektu z JSON
  - `from_csv_row()` – tworzenie obiektu z wiersza CSV
- Są to zawsze **metody statyczne** (`@staticmethod`) lub **metody klasowe** (`@classmethod`)

**Przykład:**
```python
from __future__ import annotations
import json
from pydantic import BaseModel, Field

class MeasurementEntry(BaseModel):
    name: str = Field(default="")
    value: float = Field(default=0.0)

    # Serializacja – metody instancji z prefiksem to_
    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()

    def to_json(self) -> str:
        return self.model_dump_json()

    def to_csv_row(self) -> dict[str, Any]:
        return {"Name": self.name, "Value": self.value}

    # Deserializacja – metody statyczne z prefiksem from_
    @staticmethod
    def from_dict(data: dict[str, Any]) -> MeasurementEntry:
        return MeasurementEntry(**data)

    @staticmethod
    def from_json(raw: str) -> MeasurementEntry:
        return MeasurementEntry(**json.loads(raw))

    @staticmethod
    def from_csv_row(row: dict[str, Any]) -> MeasurementEntry:
        return MeasurementEntry(name=row["Name"], value=float(row["Value"]))
```

#### Transformacja do nowego obiektu tego samego typu (obiekt → obiekt)
- Metody zwracające **nowy obiekt tego samego typu** (kopiowanie z modyfikacją) nazywaj z prefiksem `as_`:
  - `as_offseted(offset)` – nowy obiekt z przesuniętymi ramkami
  - `as_trimmed(start, end)` – nowy obiekt przycięty do zakresu
  - `as_scaled(factor)` – nowy obiekt przeskalowany
  - `as_filtered(condition)` – nowy obiekt po filtracji
- Są to **metody instancji** (przyjmują `self`), zawsze zwracają nową instancję – oryginał pozostaje niezmieniony
- Wzorzec ten jest typowy dla niemutowalnych lub quasi-niemutowalnych struktur danych (np. dataclass z `@cached_property`)

**Przykład:**
```python
@dataclass
class TrackletTrajectory:
    frames: NumpyArray
    boxes: NumpyArray

    def as_offseted(self, offset: int) -> TrackletTrajectory:
        """Return a new trajectory with frames shifted by *-offset*."""
        mask = self.frames >= offset
        return TrackletTrajectory(
            frames=(self.frames[mask] - offset).astype(np.int32),
            boxes=self.boxes[mask].copy(),
        )

    def as_trimmed(self, start: int, end: int) -> TrackletTrajectory:
        """Return a new trajectory trimmed to [start, end] frame range."""
        mask = (self.frames >= start) & (self.frames <= end)
        return TrackletTrajectory(
            frames=self.frames[mask].copy(),
            boxes=self.boxes[mask].copy(),
        )
```

### Separacja odpowiedzialności w modelach
- Model danych powinien wiedzieć jak się serializować (`to_csv_row()`, `to_dict()`)
- Kolekcja modeli (np. `LocationModel.files`) powinna tylko agregować dane i delegować serializację do modelu
- Zewnętrzne klasy (np. dialogi UI) nie muszą znać struktury pól modelu

**Przykład - poprawna architektura:**
```python
# Model wie jak się serializować
class FileEntry(BaseModel):
    def to_csv_row(self) -> dict[str, Any]: ...

# Kolekcja deleguje do modelu i używa istniejących helperów
class LocationModel(BaseModel):
    files: list[FileEntry] = Field(default_factory=list)

    def files_to_dataframe(self) -> pd.DataFrame:
        rows = [f.to_csv_row() for f in self.files]
        return pd.DataFrame(rows)

    def files_to_csv(self, filepath: str) -> bool:
        df = self.files_to_dataframe()
        return DataframeToCsv(filepath, df, isIndexStored=False)
```

### Wykorzystuj istniejącą infrastrukturę
- Przed napisaniem nowego kodu sprawdź czy istnieją helpery w projekcie (np. `helpers/pandas.py`)
- Używaj sprawdzonych bibliotek (pandas, csv) zamiast pisać własne rozwiązania
- Dla operacji na DataFrame używaj `DataframeToCsv()` i `CsvToDataframe()` z `helpers/pandas.py`
- Przy zapisie CSV używaj `isIndexStored=False` (domyślnie), wyjątek: gdy indeks DataFrame jest znaczący (np. macierz O-D z nazwami wlotów jako indeksem) – wtedy `isIndexStored=True`
- **Nigdy** nie używaj `df.to_csv()` bezpośrednio – zawsze przez `DataframeToCsv()`

### Ścieżki systemowe
- **ZAWSZE** używaj `os.path.join()` do łączenia ścieżek - NIGDY nie używaj f-stringów z `/` lub `\`
- Projekt działa zarówno na Windows (używa `\`) jak i Linux (używa `/`)
- Używanie literalnych separatorów (`/` lub `\`) w kodzie prowadzi do błędów cross-platformowych

**Przykład - zamiast:**
```python
# ❌ ZŁE - hardcoded separator
path = f"{base_path}/{subdir}"
path = base_path + "/" + filename
path = f"{root}\\{folder}\\{file}"

# ❌ ZŁE - również w testach!
expected = f"{location.ConfigurationPath}/{custom_name}"
```

**Użyj:**
```python
# ✅ DOBRE - os.path.join działa na wszystkich platformach
import os

path = os.path.join(base_path, subdir)
path = os.path.join(base_path, filename)
path = os.path.join(root, folder, file)

# ✅ DOBRE - również w testach
expected = os.path.join(location.ConfigurationPath, custom_name)
```

**Dlaczego to ważne:**
- `os.path.join()` automatycznie używa właściwego separatora dla systemu (Windows: `\`, Linux/macOS: `/`)
- Testy muszą działać na różnych platformach (CI/CD)

### PyQt5 – pełne ścieżki enum (fully-qualified enums)
- **ZAWSZE** używaj pełnych ścieżek enum z podklasą, np. `Qt.GlobalColor.black` zamiast `Qt.black`
- Pyright / mypy nie rozpoznają skróconych ścieżek (np. `Qt.LeftButton`) – wymagana jest pełna specyfikacja przez podklasę enum
- Dotyczy to **wszystkich** stałych z `Qt`, m.in.:
  - Kolory: `Qt.GlobalColor.black`, `Qt.GlobalColor.white`, `Qt.GlobalColor.red`, `Qt.GlobalColor.gray`, ...
  - Przyciski myszy: `Qt.MouseButton.LeftButton`, `Qt.MouseButton.RightButton`, `Qt.MouseButton.MiddleButton`
  - Modyfikatory klawiatury: `Qt.KeyboardModifier.ShiftModifier`, `Qt.KeyboardModifier.ControlModifier`, `Qt.KeyboardModifier.AltModifier`
  - Style pędzla: `Qt.BrushStyle.NoBrush`, `Qt.BrushStyle.SolidPattern`
  - Style pióra: `Qt.PenStyle.DashLine`, `Qt.PenStyle.SolidLine`, `Qt.PenStyle.NoPen`
  - Kursory: `Qt.CursorShape.PointingHandCursor`, `Qt.CursorShape.ArrowCursor`, `Qt.CursorShape.CrossCursor`
  - Wyrównanie: `Qt.AlignmentFlag.AlignCenter`, `Qt.AlignmentFlag.AlignLeft`
  - Orientacja: `Qt.Orientation.Horizontal`, `Qt.Orientation.Vertical`
  - Flagi elementów: `Qt.ItemFlag.ItemIsSelectable`, `Qt.ItemFlag.ItemIsEnabled`

**Przykład - zamiast:**
```python
# ❌ ZŁE - skrócone ścieżki enum (pyright error)
painter.setPen(QPen(Qt.black, 2))
painter.setBrush(Qt.NoBrush)
if event.button() == Qt.LeftButton:
if event.modifiers() & Qt.ShiftModifier:
widget.setCursor(Qt.PointingHandCursor)
```

**Użyj:**
```python
# ✅ DOBRE - pełne ścieżki enum z podklasą
painter.setPen(QPen(Qt.GlobalColor.black, 2))
painter.setBrush(Qt.BrushStyle.NoBrush)
if event.button() == Qt.MouseButton.LeftButton:
if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
widget.setCursor(Qt.CursorShape.PointingHandCursor)
```

**Dlaczego to ważne:**
- Dotyczy to całego PyQt5 – nie tylko `Qt`, ale też np. `QGraphicsItem.GraphicsItemFlag`, `QPainter.RenderHint` itp.

### PyQt5 – kursor dla QPushButton
- **ZAWSZE** ustawiaj kursor `Qt.CursorShape.PointingHandCursor` dla każdego tworzonego `QPushButton`
- Dzięki temu użytkownik widzi wskaźnik „rączki" przy najechaniu na przycisk, co poprawia UX
- Kursor należy ustawić bezpośrednio po utworzeniu przycisku

**Przykład:**
```python
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt

# ✅ DOBRE – kursor ustawiony zaraz po stworzeniu przycisku
button = QPushButton(self.tr("Delete"))
button.setCursor(Qt.CursorShape.PointingHandCursor)

# ❌ ZŁE – brak ustawienia kursora
button = QPushButton(self.tr("Delete"))
```

### Logowanie
- Zawsze twórz logger na poziomie modułu: `logger = logging.getLogger(__name__)`
- Używaj `logger.debug()`, `logger.info()`, `logger.warning()`, `logger.error()`, `logger.critical()` zamiast `logging.debug()`, `logging.info()`, itd.
- Przykład:
```python
import logging

logger = logging.getLogger(__name__)

def my_function() -> None:
    logger.info("Starting function")
    try:
        # ...
    except Exception as e:
        logger.error("Error occurred: %s", e)
```

### Komentarze
- Nie usuwaj istniejących komentarzy – są tam z ważnych powodów
- Dodawaj komentarze wyjaśniające „dlaczego” (nie „co” – to powinno być jasne z kodu)
- Unikaj komentarzy opisujących oczywiste rzeczy (np. `# Increment counter` dla `counter += 1`)
- Komentarze powinny dodawać wartość informacyjną, np. wyjaśniać kontekst biznesowy, powód istnienia danej logiki, lub wskazywać na potencjalne pułapki- **Komentarz opisujący zawartość bloku `if`/`else` umieszczaj PRZED instrukcją `if`/`else`, nie wewnątrz bloku** – komentarz należy do warunku, a nie do jego ciała

**Przykład - zamiast:**
```python
# ❌ ZŁE – komentarz wewnątrz bloku if
if is_complete:
    # Complete trajectory - immediate classification
    return MovementResult(...)
```

**Użyj:**
```python
# ✅ DOBRE – komentarz przed ifem
# Complete trajectory - immediate classification
if is_complete:
    return MovementResult(...)
```
### Nazewnictwo zmiennych
- **NIGDY** nie używaj jednoliterowych nazw zmiennych (np. `m`, `i`, `x`, `v`, `f`)
- Każda zmienna musi mieć co najmniej jedno słowo lub skrót, który jednoznacznie opisuje jej znaczenie
- Wyjątek: indeksy w pętlach gdzie kontekst jest absolutnie oczywisty matematycznie (`i`, `j` w operacjach na macierzach) – i tak preferuj `idx`, `row_idx`, itp.
- Przykłady poprawnych nazw: `movement` zamiast `m`, `frame_idx` zamiast `i`, `gate` zamiast `g`, `value` zamiast `v`

**Przykład - zamiast:**
```python
# ❌ ZŁE – jednoliterowe zmienne
for m in movements:
    f = m.entry_gate_id
    v = crossings.get(f)

for i, x in enumerate(points):
    d = x[0] - x[1]
```

**Użyj:**
```python
# ✅ DOBRE – opisowe nazwy
for movement in movements:
    gate_id = movement.entry_gate_id
    crossing = crossings.get(gate_id)

for idx, point in enumerate(points):
    delta = point[0] - point[1]
```

### dict
- Nie używaj `dict()` jeżeli nie jest to konieczne, twórz dataclass albo Pydantic BaseModel
- dict używaj tylko do algorytmów i operacji na danych, ale nie jako struktury danych reprezentującej obiekt biznesowy

### Architektura
- Oddziel logikę biznesową od warstwy prezentacji (UI)
- Logika powinna być testowalna bez konieczności uruchamiania interfejsu graficznego
- UI powinno być „głupie” – tylko wyświetlać dane i przekazywać interakcje do logiki
- wykorzystuj MVC/MVP – modele danych, prezenter/serwis z logiką, i widoki (Qt5) tylko do prezentacji
- Pamiętaj o wykorzystywaniu wzorców projektowych (np. fabryki, strategii) tam gdzie to upraszcza kod i redukuje duplikację
- Pamiętaj o wykorzystywaniu SOLID – pojedyncza odpowiedzialność, otwarte/zamknięte, Liskov, segregacja interfejsów, odwrócenie zależności
- Pamiętaj o wykorzystywaniu istniejących bibliotek i helperów – nie pisz własnych rozwiązań tam gdzie można użyć sprawdzonych narzędzi (np. pandas, csv, pydantic)
- Stosuj zasady czystego kodu – czytelność, prostota, unikanie duplikacji, jasne nazwy, itp.

## 4. Testowanie
- Framework: `pytest`
- Nie używaj klas `unittest`
- Preferuj `pytest.mark` do kategoryzacji (`manual`, `gpu`, `benchmark`)
- Wielokrotne warianty danych: `@pytest.mark.parametrize`
- Testy jednostkowe w `tests/` (jeśli katalog istnieje); integracyjne w `tests/integration/`
- (UI) Testy logiki warstwy Qt5 traktuj jak zwykłe testy jednostkowe (oddziel logikę od warstwy prezentacji)

### Mockowanie
- Używaj `MagicMock` z `unittest.mock` zamiast ręcznych klas Dummy
- Definiuj mocki jako fixtury pytest (`@pytest.fixture`)
- Dla złożonych obiektów twórz fixtury fabrykujące (factory fixtures) zwracające funkcję `_create()`
- Konfiguruj zachowanie mocków przez `mock.method.return_value = ...`
- Weryfikuj wywołania przez `mock.method.assert_called_once()`, `assert_called_once_with(...)`, `assert_not_called()`
- Pobieraj argumenty wywołań przez `mock.method.call_args[0][0]`

### Przykład struktury fixtur
```python
@pytest.fixture
def mock_presenter() -> MagicMock:
    presenter = MagicMock()
    presenter.GetData.return_value = None
    return presenter

@pytest.fixture
def callback_values() -> list[str]:
    return []

@pytest.fixture
def widget_factory(mock_presenter: MagicMock, callback_values: list[str]) -> Callable[[], MyWidget]:
    def _create() -> MyWidget:
        return MyWidget(presenter=mock_presenter, callback=callback_values.append)
    return _create
```

## 5. Konfiguracja przez TOML
- `config_gui.e.toml` – ustawienia bazowe


## 7. Scenariusze walidacji (manualne)
1. Podstawowa funkcjonalność:
   - Import pakietu: `python -c "import aitracker_gui; print('OK')"`
2. Jakość kodu:
   - `ruff check` → brak błędów krytycznych
   - `pyright aitracker_gui` → brak błędów typów (lub zaakceptowane ostrzeżenia)
3. Uruchomienie aplikacji Qt5 (przykład – dopasuj do faktycznego entrypointu):
   - `python -m aitracker_gui.main` – okno powinno się otworzyć bez błędów

(Dostosuj nazwy entrypointów do faktycznych modułów – jeśli różnią się, zaktualizuj ten dokument.)


## 10. Częste zadania
```bash
# Formatowanie kodu
ruff format
# Automatyczna korekta wybranych lintów
ruff check --fix
# Test pojedynczego pliku
uv run pytest tests/test_example.py -v
```


## 12. Dalsze uwagi
- Przed commitem: format + lint + szybkie testy
- Zmiany w zależnościach: używaj `uv add <pakiet>` (runtime) lub `uv add --dev <pakiet>` (deweloperskie), co automatycznie aktualizuje `pyproject.toml` i `uv.lock`
- Rozszerzenia GPU / specyficzne moduły – oznacz testy markerem `gpu`

## 12a. Dokumentacja

### Wiki użytkownika (`wiki/en/`)
- Katalog `wiki/en/` zawiera dokumentację dla użytkownika końcowego w formacie Markdown
- Po zakończeniu prac, które wprowadzają zmiany widoczne dla użytkownika (nowe funkcje, zmiany UI, itp.), zaktualizuj odpowiednie pliki wiki
- Wiki dotyczy tylko instrukcji obsługi i informacji dla użytkownika – nie dokumentacji technicznej/developerskiej

### Opisy issues dla developerów (`docs/issues/`)
- Katalog `docs/issues/` zawiera szczegółowe opisy zadań i problemów do rozwiązania dla developerów
- Przed rozpoczęciem pracy nad issue, sprawdź czy istnieje plik z opisem w tym katalogu

## 13. Tłumaczenia (i18n) w PyQt5

### Podstawowe zasady
- **NIGDY** nie wpisuj tekstów UI bezpośrednio w kodzie (np. `"Zarządzaj"`, `"Usuń"`)
- Wszystkie teksty widoczne dla użytkownika muszą być opakowane w funkcję tłumaczącą
- Teksty źródłowe pisz po angielsku - tłumaczenia na inne języki będą w plikach `.ts`

### W klasach dziedziczących po QWidget/QDialog
Używaj metody `self.tr()`:
```python
class MyDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(self.tr("Manage configurations"))

        button = QPushButton(self.tr("Delete"))
        button.setToolTip(self.tr("Cannot delete the last item"))

        label = QLabel(self.tr("Enter your name:"))
```

### W klasach NIE dziedziczących po QWidget (np. MainWindowGui)
Używaj `QtCore.QCoreApplication.translate()`:
```python
from PyQt5 import QtCore

class MainWindowGui:
    def some_method(self) -> None:
        _translate = QtCore.QCoreApplication.translate
        self.ui.myButton.setText(_translate("MainWindowGui", "Save"))
        self.ui.myLabel.setText(_translate("MainWindowGui", "Status: Ready"))
```

### Teksty z parametrami
Używaj `.format()` po tłumaczeniu:
```python
# Poprawnie:
_translate = QtCore.QCoreApplication.translate
text = _translate("MainWindowGui", "{current}/{total} Manage").format(current=1, total=3)

# W QDialog:
text = self.tr("{count} items selected").format(count=5)
```


### Plik .pro dla Qt Linguist
Każdy nowy plik z tłumaczeniami musi być dodany do `AITrackerConfig.pro` w sekcji `SOURCES`:
```pro
SOURCES = aitracker_gui/Gui/MainWindowGui.py \
          aitracker_gui/Gui/dialogs/DialogConfigurations.py \
          ...
```


### Konteksty tłumaczeń
- Używaj nazwy klasy jako kontekstu (pierwszy argument `_translate`)
- Dla usług/chmury używaj dedykowanych kontekstów: `"Services"`, `"Cloud"`
- Przykład:
```python
_translate("Cloud", "Cloud is online!")
_translate("Services", "Traffic counting")
_translate("MainWindowGui", "Open file")
```

## 14. Git Workflow – model branchowania

Projekt stosuje model pracy z gałęziami oparty na **Gitflow**, z `main` jako branchem ciągłego rozwoju. Szczegółowa dokumentacja: `docs/GitGraph.md`.

### Struktura branchy

| Branch | Cel | Tworzone z | Mergowane do |
|--------|-----|------------|--------------|
| `main` | Ciągły rozwój – wszystkie nowe funkcje i poprawki | — | — |
| `feature/nazwa` | Nowa funkcjonalność | `main` | `main` (przez PR) |
| `fixes/nazwa` | Poprawka błędu | `main` lub `release/vX.Y` | `main` lub `release/vX.Y` (przez PR) |
| `release/vX.Y` | Stabilna linia wydania (LTS) | `main` | — (tylko przyjmuje hotfixy) |

### Zasady pracy z branchami

- **Nowe funkcjonalności** (`feature/`) zawsze wychodzą z `main` i wracają do `main` przez PR
- **Poprawki bieżące** (`fixes/`) wychodzą z `main` i wracają do `main` przez PR
- **Release** (`release/vX.Y`) – odcinany od `main` w momencie decyzji o wydaniu; na tym branchu **nie** lądują nowe ficzery – tylko hotfixy
- **Hotfixy produkcyjne** (`fixes/`) wychodzą z `release/vX.Y`, są mergowane do `release/vX.Y` przez PR, a następnie **backportowane** (merge `release/vX.Y` → `main`)
- **Tagi** (`vX.Y.Z`) oznaczają konkretne wydania na branchu release

### Konwencja nazewnictwa branchy

```
feature/krotki-opis       # nowa funkcja
fixes/krotki-opis         # poprawka błędu
release/vX.Y              # linia wydania (np. release/v2.5)
```

### Backporting

Po każdym hotfixie na branchu release'owym **obowiązkowo** merguj `release/vX.Y` z powrotem do `main`, aby poprawka nie „zaginęła" w przyszłych wersjach.

### Wersjonowanie (SemVer)

Tagi stosują format `vX.Y.Z`:
- `X` – major (breaking changes)
- `Y` – minor (nowe funkcje, kompatybilne wstecz)
- `Z` – patch (poprawki błędów na branchu release)
