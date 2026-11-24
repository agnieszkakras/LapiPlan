# LapiPlan — instrukcja instalacji i obsługi

## 1. Wymagania
- Komputer z Windows 10/11, macOS lub Linux.
- Python 3.11 lub 3.12. Podczas instalacji Pythona na Windows zaznacz „Add Python to PATH”.
- Dostęp do internetu podczas pierwszej instalacji bibliotek.

## 2. Instalacja Windows — najprościej
1. Rozpakuj ZIP do folderu `LapiPlan`.
2. Otwórz folder i kliknij dwukrotnie `START_WINDOWS.bat`.
3. Przy pierwszym uruchomieniu skrypt utworzy środowisko `.venv` i zainstaluje biblioteki.
4. W przeglądarce otwórz `http://localhost:8501`, jeśli strona nie otworzy się automatycznie.
5. Aby zakończyć, zamknij okno konsoli lub naciśnij `Ctrl+C`.

Jeżeli Windows blokuje plik BAT, skorzystaj z ręcznej instalacji niżej. Uruchamiaj tylko kod, któremu ufasz.

## 3. Ręczne uruchomienie
Otwórz terminal w rozpakowanym folderze:

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

macOS / Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

## 4. Pierwsze kroki
1. Wybierz język `PL` lub `EN` w panelu bocznym.
2. Dodaj profil dziecka. Na potrzeby portfolio wpisz fikcyjne dane.
3. Otwórz `Plan tygodnia` i wybierz `Załaduj przykładowy plan` albo wprowadzaj zajęcia ręcznie.
4. Do harmonogramu dodawaj: szkołę, zajęcia dodatkowe, naukę własną, czas rodzinny i czas wolny.
5. W zakładce `Nauka` zapisuj czas i przedmiot sesji nauki.
6. W zakładce `Zadania` wprowadzaj sprawdziany, prace domowe i inne terminy.
7. W `Pulpicie` zobaczysz cotygodniowe podsumowanie i wykresy.
8. W `Dane i prywatność` możesz pobrać pliki CSV i usunąć profil.

## 5. Możliwości dostosowania
- Zmiana wieku: ustaw datę urodzenia podczas dodawania profilu; wiek liczony jest automatycznie.
- Długość nauki: pole `Sugerowana długość bloku nauki`; wpisz indywidualną wartość.
- Harmonogram: jeden plan dla każdego dziecka; zajęcia mogą być różne w poszczególne dni.
- Kategorie: szkoła, zajęcia dodatkowe, nauka, rodzina, czas wolny, inne.
- Nie ma wbudowanych ocen, progów czy oceniania dziecka — aplikacja służy do organizacji.

## 6. Przechowywanie danych
Baza danych znajduje się w `data/lapiplan.sqlite3` i powstaje lokalnie przy pierwszym uruchomieniu. Aby wykonać kopię zapasową, zamknij aplikację i skopiuj folder `data` w bezpieczne miejsce. Nie umieszczaj go w publicznym repozytorium.

## 7. GitHub
Utwórz repozytorium `lapiplan-family-planner`. Dodaj pliki projektu, **bez** folderów `data/` i `.venv/` (są ignorowane przez `.gitignore`). Do portfolio możesz dołączyć zrzut ekranu wyłącznie z danymi fikcyjnymi. Uruchom `python -m pytest -q` po zainstalowaniu `requirements-dev.txt`.

## 8. Ograniczenia MVP
- Harmonogram dotyczy powtarzającego się tygodnia, bez wyjątków świątecznych i kalendarza szkolnego.
- Brak kont użytkowników, powiadomień i synchronizacji między urządzeniami.
- Brak integracji z e-dziennikiem.
- Konflikty sprawdzane są przy dodawaniu bloków harmonogramu, nie między dziennikiem nauki a kalendarzem.
- To wersja lokalna: nie publikuj jej jako otwartego serwisu z prawdziwymi danymi dzieci bez odpowiednich zabezpieczeń.

## NOWOŚĆ: kalendarz i sprawdziany — wersja 2

1. Otwórz `START_WINDOWS.bat` albo uruchom `streamlit run app.py`.
2. W pasku bocznym ustaw `Język / Language` na PL lub EN.
3. W polu `Kraj / region świąt` wybierz Polskę, Anglię i Walię, Szkocję, Irlandię Północną albo USA (święta federalne).
4. Wybierz paletę: błękitno-żółtą, turkusowo-beżową lub jasnozielono-liliową.
5. Dodaj profil dziecka, następnie przejdź do **Terminarza szkolnego** i wpisuj zapowiedziane kartkówki, sprawdziany, prace klasowe, projekty grupowe, olimpiady i prezentacje.
6. W zakładce **Kalendarz 10-letni** wybierz miesiąc/rok, kliknij dzień, aby zobaczyć święta, tygodniowe bloki zajęć i zapisane terminy.
7. W terminarzu zaznaczysz zrealizowane wydarzenia i pobierzesz raport CSV.

**Kalendarz** działa w ruchomym zakresie 10 lat od bieżącego dnia, nie tylko 2026–2036. Angielski interfejs nie narzuca świąt USA — region wybierasz osobno. Nie obejmuje automatycznie ferii, wakacji szkolnych ani jednorazowych zmian wprowadzanych przez rządy po publikacji tej wersji. Plik bazy danych nie powinien być publikowany w repozytorium.


## Nowa nazwa LapiPlan i subskrypcja
Aplikacja działa w **przeglądarce** przez Streamlit (nie jest instalowana jako APK). Ikona została dodana do `assets/`, nagłówka oraz karty przeglądarki.

**30 dni bezpłatnie:** od pierwszego uruchomienia na danej lokalnej bazie. Po tym okresie aplikacja prezentuje ekran subskrypcji 14,99 zł / miesiąc i umożliwia eksport danych.

**Ważne:** jest to demonstracja modelu subskrypcyjnego. Opłaty NIE są pobierane, a system nie weryfikuje zakupu. Aby wdrożyć płatności dla klientów, trzeba dodać konta, bezpieczny serwer i webhooki potwierdzające płatności. Sam link `LAPIPLAN_PAYMENT_URL` nie daje automatycznego dostępu.

### Zachowanie wcześniejszych danych
Przed aktualizacją wykonaj kopię zapasową pliku `data/studypulse.sqlite3` ze starej aplikacji. Skopiuj go do nowego folderu jako `data/lapiplan.sqlite3` przed pierwszym uruchomieniem LapiPlan. Nie udostępniaj pliku bazy na GitHubie.
