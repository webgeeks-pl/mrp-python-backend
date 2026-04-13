from __future__ import annotations

from dataclasses import dataclass

from input import (
    GHP_LEVEL0_INPUT,
    MRP_LEVEL1_KIJ_INPUT,
    MRP_LEVEL1_OSTRZE_INPUT,
    MRP_LEVEL2_DESKA_INPUT,
)




@dataclass
class GHPResult:
    tygodnie: int
    popyt: list[int]
    produkcja: list[int]
    dostepne: list[int]
    stan_poczatkowy: int


@dataclass
class MRPResult:
    tygodnie: int
    calkowite_zapotrzebowanie: list[int]
    planowane_przyjecia: list[int]
    przewidywane_na_stanie: list[int]
    zapotrzebowanie_netto: list[int]
    planowane_zamowienia: list[int]
    planowane_przyjecie_zamowien: list[int]
    czas_realizacji: int
    wielkosc_partii: int
    poziom_bom: int
    stan_poczatkowy: int
    nazwa_elementu: str

def waliduj_wejscie(
    tygodnie: int,
    calkowite_zamowienie: int,
    partie: list[tuple[int, int]],
    stan_poczatkowy: int,
    czas_realizacji: int,
) -> None:
    if tygodnie <= 0:
        raise ValueError("Liczba tygodni planowania musi byc > 0.")
    if calkowite_zamowienie <= 0:
        raise ValueError("Wielkosc zamowienia musi byc > 0.")
    if stan_poczatkowy < 0:
        raise ValueError("Liczba wyrobow gotowych na stanie musi byc >= 0.")
    if czas_realizacji < 1:
        raise ValueError("Czas realizacji musi byc >= 1.")
    if not partie:
        raise ValueError("Lista partii nie moze byc pusta.")

    for tydzien, ilosc in partie:
        if tydzien < 1 or tydzien > tygodnie:
            raise ValueError(f"Tydzien partii {tydzien} musi byc z zakresu 1..{tygodnie}.")
        if ilosc <= 0:
            raise ValueError("Ilosc partii musi byc > 0.")

    suma_partii = sum(ilosc for _, ilosc in partie)
    if suma_partii != calkowite_zamowienie:
        raise ValueError(
            "Suma partii musi byc rowna wielkosci zamowienia. "
            f"Podano {suma_partii}, oczekiwano {calkowite_zamowienie}."
        )


def oblicz_ghp_poziom0(
    tygodnie: int,
    stan_poczatkowy: int,
    popyt_po_tygodniach: list[int],
) -> GHPResult:
    popyt = list(popyt_po_tygodniach)
    produkcja = [0] * tygodnie
    dostepne = [0] * tygodnie

    poprzednie_dostepne = stan_poczatkowy
    for i in range(tygodnie):
        # Planowane przyjecie w tygodniu i pokrywa niedobor po uwzglednieniu zapasu.
        niedobor = popyt[i] - poprzednie_dostepne
        planowane_przyjecie = niedobor if niedobor > 0 else 0

        produkcja[i] = planowane_przyjecie

        dostepne_na_koniec = poprzednie_dostepne + planowane_przyjecie - popyt[i]

        dostepne[i] = dostepne_na_koniec
        poprzednie_dostepne = dostepne_na_koniec

    return GHPResult(
        tygodnie=tygodnie,
        popyt=popyt,
        produkcja=produkcja,
        dostepne=dostepne,
        stan_poczatkowy=stan_poczatkowy,
    )


def formatuj_wiersz(etykieta: str, wartosci: list[str], szerokosc_komorki: int, szerokosc_etykiety: int) -> str:
    komorki = " | ".join(f"{wartosc:>{szerokosc_komorki}}" for wartosc in wartosci)
    return f"| {etykieta:<{szerokosc_etykiety}} | {komorki} |"


def wydrukuj_tabele_ghp(wynik: GHPResult, czas_realizacji: int) -> None:
    etykiety = ["tydzien", "przewidywany popyt", "produkcja", "dostepne"]
    etykiety_tygodni = [str(i) for i in range(1, wynik.tygodnie + 1)]
    etykiety_popytu = [str(v) if v != 0 else "" for v in wynik.popyt]
    etykiety_produkcji = [str(v) if v != 0 else "" for v in wynik.produkcja]
    etykiety_dostepnych = [str(v) for v in wynik.dostepne]

    wszystkie_komorki = etykiety_tygodni + etykiety_popytu + etykiety_produkcji + etykiety_dostepnych
    szerokosc_komorki = max(2, max(len(komorka) for komorka in wszystkie_komorki))
    szerokosc_etykiety = max(len(etykieta) for etykieta in etykiety)
    separator = " | ".join("-" * szerokosc_komorki for _ in range(wynik.tygodnie))

    print("\nGHP dla poziomu 0 (wyrob finalny)")
    print(formatuj_wiersz("tydzien", etykiety_tygodni, szerokosc_komorki, szerokosc_etykiety))
    print(f"| {'-' * szerokosc_etykiety} | {separator} |")
    print(formatuj_wiersz("przewidywany popyt", etykiety_popytu, szerokosc_komorki, szerokosc_etykiety))
    print(formatuj_wiersz("produkcja", etykiety_produkcji, szerokosc_komorki, szerokosc_etykiety))
    print(formatuj_wiersz("dostepne", etykiety_dostepnych, szerokosc_komorki, szerokosc_etykiety))
    print(f"na stanie = {wynik.stan_poczatkowy}")
    print(f"czas realizacji = {czas_realizacji}")


def waliduj_wejscie_mrp(
    tygodnie: int,
    zuzycie_na_wyrob: int,
    stan_poczatkowy: int,
    czas_realizacji: int,
    wielkosc_partii: int,
    planowane_przyjecia_surowe: list[tuple[int, int]],
) -> None:
    if zuzycie_na_wyrob <= 0:
        raise ValueError("Zuzycie komponentu na wyrob nadrzedny musi byc > 0.")
    if stan_poczatkowy < 0:
        raise ValueError("Stan poczatkowy komponentu musi byc >= 0.")
    if czas_realizacji < 1:
        raise ValueError("Czas realizacji komponentu musi byc >= 1.")
    if wielkosc_partii <= 0:
        raise ValueError("Wielkosc partii komponentu musi byc > 0.")

    for tydzien, ilosc in planowane_przyjecia_surowe:
        if tydzien < 1 or tydzien > tygodnie:
            raise ValueError(f"Tydzien planowanego przyjecia {tydzien} musi byc z zakresu 1..{tygodnie}.")
        if ilosc < 0:
            raise ValueError("Planowane przyjecia nie moga miec ujemnej ilosci.")


def zagreguj_planowane_przyjecia(tygodnie: int, przyjecia_surowe: list[tuple[int, int]]) -> list[int]:
    przyjecia = [0] * tygodnie
    for tydzien, ilosc in przyjecia_surowe:
        przyjecia[tydzien - 1] += ilosc
    return przyjecia


def oblicz_mrp_poziom1(
    produkcja_rodzica: list[int],
    zuzycie_na_wyrob: int,
    stan_poczatkowy: int,
    czas_realizacji: int,
    wielkosc_partii: int,
    planowane_przyjecia: list[int],
    nazwa_elementu: str,
    poziom_bom: int,
    czas_realizacji_ghp: int = 1,
) -> MRPResult:
    tygodnie = len(produkcja_rodzica)
    
    # Przesuniecie produkcji rodzica w lewo o tylko czas_realizacji_ghp aby uzyskac calkowite zapotrzebowanie
    przesunieta_produkcja = [0] * tygodnie
    for idx in range(tygodnie):
        zrodlo_idx = idx + czas_realizacji_ghp
        if zrodlo_idx < tygodnie:
            przesunieta_produkcja[idx] = produkcja_rodzica[zrodlo_idx]
    
    calkowite_zapotrzebowanie = [ilosc * zuzycie_na_wyrob for ilosc in przesunieta_produkcja]
    przewidywane_na_stanie = [0] * tygodnie
    zapotrzebowanie_netto = [0] * tygodnie
    planowane_zamowienia = [0] * tygodnie
    planowane_przyjecie_zamowien = [0] * tygodnie

    poprzednie_dostepne = stan_poczatkowy
    for i in range(tygodnie):
        dostepne_przed_popytem = poprzednie_dostepne + planowane_przyjecia[i] + planowane_przyjecie_zamowien[i]

        if calkowite_zapotrzebowanie[i] == 0:
            zapot_netto = 0
            przyjecie = 0
        elif dostepne_przed_popytem >= calkowite_zapotrzebowanie[i]:
            zapot_netto = 0
            przyjecie = 0
        else:
            zapot_netto = calkowite_zapotrzebowanie[i] - dostepne_przed_popytem
            # Stala wielkosc partii: przy niedoborze uruchamiamy jedna partie.
            przyjecie = wielkosc_partii

            tydzien_uruchomienia = i - czas_realizacji
            if tydzien_uruchomienia < 0:
                raise ValueError(
                    f"MRP dla {nazwa_elementu}: brak czasu na realizacje zamowienia dla tygodnia {i + 1}."
                )
            planowane_zamowienia[tydzien_uruchomienia] += przyjecie
            planowane_przyjecie_zamowien[i] += przyjecie

        dostepne_na_koniec = dostepne_przed_popytem + przyjecie - calkowite_zapotrzebowanie[i]

        zapotrzebowanie_netto[i] = zapot_netto
        przewidywane_na_stanie[i] = dostepne_na_koniec
        poprzednie_dostepne = dostepne_na_koniec

    return MRPResult(
        tygodnie=tygodnie,
        calkowite_zapotrzebowanie=calkowite_zapotrzebowanie,
        planowane_przyjecia=planowane_przyjecia,
        przewidywane_na_stanie=przewidywane_na_stanie,
        zapotrzebowanie_netto=zapotrzebowanie_netto,
        planowane_zamowienia=planowane_zamowienia,
        planowane_przyjecie_zamowien=planowane_przyjecie_zamowien,
        czas_realizacji=czas_realizacji,
        wielkosc_partii=wielkosc_partii,
        poziom_bom=poziom_bom,
        stan_poczatkowy=stan_poczatkowy,
        nazwa_elementu=nazwa_elementu,
    )


def wydrukuj_tabele_mrp(wynik: MRPResult) -> None:
    etykiety = [
        "okres",
        "calk. zapotrz.",
        "planowane przyjecia",
        "przewidywane na stanie",
        "zapotrzebowanie netto",
        "planowane zamowienia",
        "plan. przyj. zamowien",
    ]
    etykiety_tygodni = [str(i) for i in range(1, wynik.tygodnie + 1)]
    etykiety_zapotrzebowania = [str(v) if v != 0 else "" for v in wynik.calkowite_zapotrzebowanie]
    etykiety_przyjec = [str(v) if v != 0 else "" for v in wynik.planowane_przyjecia]
    etykiety_dostepnych = [str(v) for v in wynik.przewidywane_na_stanie]
    etykiety_netto = [str(v) if v != 0 else "" for v in wynik.zapotrzebowanie_netto]
    etykiety_zamowien = [str(v) if v != 0 else "" for v in wynik.planowane_zamowienia]
    etykiety_przyjecia_zamowien = [str(v) if v != 0 else "" for v in wynik.planowane_przyjecie_zamowien]

    wszystkie_komorki = (
        etykiety_tygodni
        + etykiety_zapotrzebowania
        + etykiety_przyjec
        + etykiety_dostepnych
        + etykiety_netto
        + etykiety_zamowien
        + etykiety_przyjecia_zamowien
    )
    szerokosc_komorki = max(2, max(len(komorka) for komorka in wszystkie_komorki))
    szerokosc_etykiety = max(len(etykieta) for etykieta in etykiety)
    separator = " | ".join("-" * szerokosc_komorki for _ in range(wynik.tygodnie))

    print(f"\nMRP poziom {wynik.poziom_bom}: {wynik.nazwa_elementu}")
    print(formatuj_wiersz("okres", etykiety_tygodni, szerokosc_komorki, szerokosc_etykiety))
    print(f"| {'-' * szerokosc_etykiety} | {separator} |")
    print(formatuj_wiersz("calk. zapotrz.", etykiety_zapotrzebowania, szerokosc_komorki, szerokosc_etykiety))
    print(formatuj_wiersz("planowane przyjecia", etykiety_przyjec, szerokosc_komorki, szerokosc_etykiety))
    print(formatuj_wiersz("przewidywane na stanie", etykiety_dostepnych, szerokosc_komorki, szerokosc_etykiety))
    print(formatuj_wiersz("zapotrzebowanie netto", etykiety_netto, szerokosc_komorki, szerokosc_etykiety))
    print(formatuj_wiersz("planowane zamowienia", etykiety_zamowien, szerokosc_komorki, szerokosc_etykiety))
    print(formatuj_wiersz("plan. przyj. zamowien", etykiety_przyjecia_zamowien, szerokosc_komorki, szerokosc_etykiety))
    print(f"czas realizacji = {wynik.czas_realizacji}")
    print(f"wielkosc partii = {wynik.wielkosc_partii}")
    print(f"poziom BOM = {wynik.poziom_bom}")
    print(f"na stanie = {wynik.stan_poczatkowy}")


def uruchom() -> None:
    print("=== Symulacja GHP + MRP (poziom 1 Ostrze + Kij, poziom 2 Deska) ===")

    tygodnie = int(GHP_LEVEL0_INPUT.weeks)
    calkowite_zamowienie = int(GHP_LEVEL0_INPUT.total_order)
    stan_poczatkowy = int(GHP_LEVEL0_INPUT.initial_stock)
    czas_realizacji = int(GHP_LEVEL0_INPUT.lead_time)
    partie = [(int(tydzien), int(ilosc)) for tydzien, ilosc in GHP_LEVEL0_INPUT.batches]

    waliduj_wejscie(
        tygodnie=tygodnie,
        calkowite_zamowienie=calkowite_zamowienie,
        partie=partie,
        stan_poczatkowy=stan_poczatkowy,
        czas_realizacji=czas_realizacji,
    )

    popyt_po_tygodniach = [0] * tygodnie
    for tydzien, ilosc in partie:
        popyt_po_tygodniach[tydzien - 1] += ilosc

    wynik = oblicz_ghp_poziom0(
        tygodnie=tygodnie,
        stan_poczatkowy=stan_poczatkowy,
        popyt_po_tygodniach=popyt_po_tygodniach,
    )

    wydrukuj_tabele_ghp(wynik, czas_realizacji=czas_realizacji)

    nazwa_elementu = str(MRP_LEVEL1_OSTRZE_INPUT.name)
    poziom_bom = int(MRP_LEVEL1_OSTRZE_INPUT.bom_level)
    zuzycie_na_wyrob = int(MRP_LEVEL1_OSTRZE_INPUT.usage_per_parent)
    stan_poczatkowy_mrp = int(MRP_LEVEL1_OSTRZE_INPUT.initial_stock)
    czas_realizacji_mrp = int(MRP_LEVEL1_OSTRZE_INPUT.lead_time)
    wielkosc_partii = int(MRP_LEVEL1_OSTRZE_INPUT.lot_size)
    planowane_przyjecia_surowe = [
        (int(tydzien), int(ilosc)) for tydzien, ilosc in MRP_LEVEL1_OSTRZE_INPUT.scheduled_receipts
    ]

    waliduj_wejscie_mrp(
        tygodnie=tygodnie,
        zuzycie_na_wyrob=zuzycie_na_wyrob,
        stan_poczatkowy=stan_poczatkowy_mrp,
        czas_realizacji=czas_realizacji_mrp,
        wielkosc_partii=wielkosc_partii,
        planowane_przyjecia_surowe=planowane_przyjecia_surowe,
    )

    planowane_przyjecia = zagreguj_planowane_przyjecia(tygodnie=tygodnie, przyjecia_surowe=planowane_przyjecia_surowe)

    wynik_mrp = oblicz_mrp_poziom1(
        produkcja_rodzica=wynik.produkcja,
        zuzycie_na_wyrob=zuzycie_na_wyrob,
        stan_poczatkowy=stan_poczatkowy_mrp,
        czas_realizacji=czas_realizacji_mrp,
        wielkosc_partii=wielkosc_partii,
        planowane_przyjecia=planowane_przyjecia,
        nazwa_elementu=nazwa_elementu,
        poziom_bom=poziom_bom,
        czas_realizacji_ghp=czas_realizacji,
    )

    wydrukuj_tabele_mrp(wynik_mrp)

    nazwa_elementu_kij = str(MRP_LEVEL1_KIJ_INPUT.name)
    poziom_bom_kij = int(MRP_LEVEL1_KIJ_INPUT.bom_level)
    zuzycie_na_wyrob_kij = int(MRP_LEVEL1_KIJ_INPUT.usage_per_parent)
    stan_poczatkowy_kij = int(MRP_LEVEL1_KIJ_INPUT.initial_stock)
    czas_realizacji_kij = int(MRP_LEVEL1_KIJ_INPUT.lead_time)
    wielkosc_partii_kij = int(MRP_LEVEL1_KIJ_INPUT.lot_size)
    planowane_przyjecia_surowe_kij = [
        (int(tydzien), int(ilosc)) for tydzien, ilosc in MRP_LEVEL1_KIJ_INPUT.scheduled_receipts
    ]

    waliduj_wejscie_mrp(
        tygodnie=tygodnie,
        zuzycie_na_wyrob=zuzycie_na_wyrob_kij,
        stan_poczatkowy=stan_poczatkowy_kij,
        czas_realizacji=czas_realizacji_kij,
        wielkosc_partii=wielkosc_partii_kij,
        planowane_przyjecia_surowe=planowane_przyjecia_surowe_kij,
    )

    planowane_przyjecia_kij = zagreguj_planowane_przyjecia(
        tygodnie=tygodnie,
        przyjecia_surowe=planowane_przyjecia_surowe_kij,
    )

    wynik_mrp_kij = oblicz_mrp_poziom1(
        produkcja_rodzica=wynik.produkcja,
        zuzycie_na_wyrob=zuzycie_na_wyrob_kij,
        stan_poczatkowy=stan_poczatkowy_kij,
        czas_realizacji=czas_realizacji_kij,
        wielkosc_partii=wielkosc_partii_kij,
        planowane_przyjecia=planowane_przyjecia_kij,
        nazwa_elementu=nazwa_elementu_kij,
        poziom_bom=poziom_bom_kij,
        czas_realizacji_ghp=czas_realizacji,
    )

    wydrukuj_tabele_mrp(wynik_mrp_kij)

    nazwa_elementu_deska = str(MRP_LEVEL2_DESKA_INPUT.name)
    poziom_bom_deska = int(MRP_LEVEL2_DESKA_INPUT.bom_level)
    zuzycie_na_wyrob_deska = int(MRP_LEVEL2_DESKA_INPUT.usage_per_parent)
    stan_poczatkowy_deska = int(MRP_LEVEL2_DESKA_INPUT.initial_stock)
    czas_realizacji_deska = int(MRP_LEVEL2_DESKA_INPUT.lead_time)
    wielkosc_partii_deska = int(MRP_LEVEL2_DESKA_INPUT.lot_size)
    planowane_przyjecia_surowe_deska = [
        (int(tydzien), int(ilosc)) for tydzien, ilosc in MRP_LEVEL2_DESKA_INPUT.scheduled_receipts
    ]

    waliduj_wejscie_mrp(
        tygodnie=tygodnie,
        zuzycie_na_wyrob=zuzycie_na_wyrob_deska,
        stan_poczatkowy=stan_poczatkowy_deska,
        czas_realizacji=czas_realizacji_deska,
        wielkosc_partii=wielkosc_partii_deska,
        planowane_przyjecia_surowe=planowane_przyjecia_surowe_deska,
    )

    planowane_przyjecia_deska = zagreguj_planowane_przyjecia(
        tygodnie=tygodnie,
        przyjecia_surowe=planowane_przyjecia_surowe_deska,
    )

    wynik_mrp_deska = oblicz_mrp_poziom1(
        produkcja_rodzica=wynik_mrp_kij.planowane_zamowienia,
        zuzycie_na_wyrob=zuzycie_na_wyrob_deska,
        stan_poczatkowy=stan_poczatkowy_deska,
        czas_realizacji=czas_realizacji_deska,
        wielkosc_partii=wielkosc_partii_deska,
        planowane_przyjecia=planowane_przyjecia_deska,
        nazwa_elementu=nazwa_elementu_deska,
        poziom_bom=poziom_bom_deska,
        czas_realizacji_ghp=0,
    )

    wydrukuj_tabele_mrp(wynik_mrp_deska)


if __name__ == "__main__":
    try:
        uruchom()
    except ValueError as exc:
        print(f"Blad danych wejsciowych: {exc}")
