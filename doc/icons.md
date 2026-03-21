# icons/ — Zasoby ikon (Tango)

Zestaw ikon w stylu Tango dla interfejsu graficznego Qt.

---

## Struktura

```
icons/
├── index.theme       # Plik definiujący temat ikon
├── tango.qrc         # Plik zasobów Qt (do kompilacji pyrcc5)
├── 16x16/            # Ikony 16×16 pikseli
│   ├── actions/
│   ├── animations/
│   ├── apps/
│   ├── categories/
│   ├── devices/
│   ├── emblems/
│   ├── emotes/
│   ├── mimetypes/
│   ├── places/
│   └── status/
├── 22x22/            # Ikony 22×22 pikseli
│   ├── actions/
│   ├── ...
│   └── status/
└── 32x32/            # Ikony 32×32 pikseli
    └── ...
```

---

## Zastosowanie

Ikony Tango to otwarty zestaw ikon (public domain) używany przez aplikację w toolbarach, menu i przyciskach.

### Kompilacja zasobów

Plik `tango.qrc` definiuje mapowanie ikon na zasoby Qt. Skompilowany do `tango_rc.py` w katalogu głównym:

```bash
pyrcc5 icons/tango.qrc -o tango_rc.py
```

Plik `tango_rc.py` jest importowany przez UI — ikony są wbudowane w aplikację i nie wymagają instalacji osobnych plików.

### Kategorie ikon

| Katalog | Zastosowanie |
|---|---|
| `actions/` | Akcje (save, open, delete, undo, redo, ...) |
| `apps/` | Ikony aplikacji |
| `categories/` | Kategorie preferencji |
| `devices/` | Urządzenia (kamera, dysk, ...) |
| `emblems/` | Emblematy (ważne, ulubione, ...) |
| `emotes/` | Emotikony |
| `mimetypes/` | Typy plików |
| `places/` | Miejsca (folder, home, ...) |
| `status/` | Statusy (błąd, info, ...) |
| `animations/` | Animacje (loading, ...) |
