# Systemy zintegrowane w zarządzaniu

## Temat 2. Algorytm MRP

- Prezentacja i dyskusja materiału dotyczącego algorytmu MRP (ppt).
- Wykonanie zadania z prezentowanego materiału.
- Zdefiniowanie i omówienie zadania do wykonania / projektu (10 pkt)

## Projekt: Implementacja algorytmu MRP

## Założenia:

- Projekt grupowy, maksymalna liczebność grupy: 4 osób.
- Podział na grupy według zamieszczonej listy na platformie e-learningowej.
- Wraz z projektem należy złożyć zestawienie dotyczące wkładu każdego z uczestników grupy i pełnionych ról podczas wykonywania projektu.
- W każdej grupie powinien zostać wybrany kierownik projektu, który pełni także funkcję osoby kontaktowej.
- Kierownik projektu ustala z prowadzącym modelowany produkt (na zajęciach lub zdalnie).
- Wykonanie projektu polega na opracowaniu rozwiązania, przedstawieniu modelu na zajęciach oraz wyjaśnieniu rozwiązania (w tym odpowiedzi na pytania).
- Platforma do implementacji rozwiązania wybierana przez zespoły projektowe i ustalana z prowadzącym.
- Plik z rozwiązaniem powinien być przesłany na platformę e-learningową przed ustalonym terminem. Należy przesłać archiwum, w skład którego wchodzi kod źródłowy rozwiązania, program w wersji wykonywalnej oraz dokument MS Word opisujący role w projekcie. Brak pliku na platformie skutkuje brakiem punktów za zadanie.
- Do uzyskania jest maksymalnie 10 punktów, zespół projektowy traktowany jest jako całość w punktacji. Ocena zadania według kryteriów zawartych w definicji projektu (zawartość merytoryczna rozwiązania, poziom prezentacji rozwiązania podczas zajęć, odpowiedzi na pytania)

## Zadanie:

Należy opracować rozwiązanie pozwalające na symulację GHP oraz MRP. Rozwiązanie ma
dotyczyć prostej struktury produktu z trzema poziomami (poziom 0, 1, 2). Rozwiązanie
powinno umożliwiać wprowadzenie wszystkich parametrów z rekordu MRP i GHP oraz
umożliwiać zmiany tych parametrów w celach symulacyjnych.

Przykładowy BOM to:    łopata (ostrze, kij(deska))


<1 deska to ile kijów ????>

Sam algorytm ma być zaimplementowany w języku python


Na wejściu podaje się:
- wielkość zamówienia: 120 łopat
- w których tygodniach mają być dostarczone partie, np: w 2 tygodniu 20, a w 4 tygodniu 100 (reszta). Ważne jest sprawdzanie czy użytkownik nie popełnia błędów przy wprowadzaniu.
- aktualna liczba łopat, ostrz, kijów oraz desek na stanie.
- czas oczekiwania na dostawe ostrz, kijów oraz desek (łopat nie, oczywiście), w tygodniach

Wprowadź BOM (Poziom 0): Łopata  
Wprowadź BOM (Poziom 1, po przecinku): Ostrze, Kij  
Wprowadź BOM (Poziom 2, rodzic: Ostrze, po przecinku): <enter>  
Wprowadź BOM (Poziom 2, rodzic: Kij, po przecinku): Deska  
  
Wielkość zamówienia: 120  
Partie (2 liczby, pierwsza oznacza tydzień, druga ilość): 2 20  
Partie (2 liczby, pierwsza oznacza tydzień, druga ilość): 4 100  

Liczba Łopat na stanie: 5  
Liczba Ostrz na stanie: 10  
Liczba Kijów na stanie: 0  
Liczba Desek na stanie: 1  

Czas oczekiwania na Ostrza (w tygodniacj): 1  
Czas oczekiwania na Kije (w tygodniacj): 1  
Czas oczekiwania na deski (w tygodniacj): 1  

Na wyjściu:

taka tabelka GHP dla Łopaty (poziom 0):


| tydzień            | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
| ------------------ | - | - | - | - | - | - | - | - | - | -  |
| przewidywany popyt |   |   |   |   |   |   |   |   |   |    |
| produkcja          |   |   |   |   |   |   |   |   |   |    |
| dostępne           |   |   |   |   |   |   |   |   |   |    |
| na stanie =   ??   |

A dla reszty taka tabela:

| \\/ Dane produkcyjne  Okres => |  1 |  2 |  3 |  4 |  5 |  6 |
| ------------------------------ | -- | -- | -- | -- | -- | -- |
| Całkowite zapotrzebowanie      |    |    |    |    |    |    |
| Planowane przyjęcia            |    |    |    |    |    |    |
| Przewidywane na stanie         |    |    |    |    |    |    |
| Zapotrzebowanie netto          |    |    |    |    |    |    |
| Planowane zamówienia           |    |    |    |    |    |    |
| Planowane przyjęcie zamówień   |    |    |    |    |    |    |
| &nbsp;
| Czas realizacji =  ??
| Wielkość partii =  ??
| Poziom BOM = ??
| Na stanie =  ??