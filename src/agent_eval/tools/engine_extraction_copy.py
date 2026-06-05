import asyncio
import csv
import json

from dotenv import load_dotenv
from pydantic_ai import Agent

agent = Agent()
load_dotenv()


async def find_engine(
    min_moc_kw: float | None = None,
    max_moc_kw: float | None = None,
    min_moment_nm: float | None = None,
    max_moment_nm: float | None = None,
    min_obroty: int | None = None,
    max_obroty: int | None = None,
) -> str:
    """
    Your task is to extract engine information from the given text and return a list of matching engines. The information you need to extract includes:
    1. minimal_engine_power: The minimum power output of the engine, in kilowatts (kW).
    2. maximal_engine_power: The maximum power output of the engine, in kilowatts (kW).
    3. minimal_engine_RPM: The minimum revolutions per minute (RPM) at which the engine operates.
    4. maximal_engine_RPM: The maximum revolutions per minute (RPM) at which the engine operates.
    5. minimal_engine_torque: The minimum torque produced by the engine, usually measured in Newton-meters (Nm).
    6. maximal_engine_torque: The maximum torque produced by the engine, usually measured in Newton-meters (Nm).
    <rules>
    - when you return always respond with minimal_engine_power, maximal_engine_power, minimal_engine_RPM, maximal_engine_RPM, minimal_engine_torque, and maximal_engine_torque and nothing else.
    - if any of the information is not available in the text, return None for that field.
    </rules>
    <examples>
    Text: "I need an engine with a power output of at least 20 kW and a maximum torque of 100 Nm."
    Output: {
        "minimal_engine_power": 20,
        "maximal_engine_power": None,
        "minimal_engine_RPM": None,
        "maximal_engine_RPM": None,
        "minimal_engine_torque": None,
        "maximal_engine_torque": 100
    }
    Text: "I am looking for an engine with a power output between 50 and 100 kW, operating at RPM between 1500 and 3000, and with a minimum rated torque of 200 Nm."
    Output: {
        "minimal_engine_power": 50,
        "maximal_engine_power": 100,
        "minimal_engine_RPM": 1500,
        "maximal_engine_RPM": 3000,
        "minimal_engine_torque": 200,
        "maximal_engine_torque": None
    }
    Text: "I want an engine with a power output of 75 kW, operating at up to 2500 RPM, and with a rated torque of up to 150 Nm."
    Output: {
        "minimal_engine_power": 75,
        "maximal_engine_power": 75,
        "minimal_engine_RPM": None,
        "maximal_engine_RPM": 2500,
        "minimal_engine_torque": None,
        "maximal_engine_torque": 150
    }
    </examples>
    """

    znalezione_silniki = []

    try:
        # Otwieramy plik w trybie odczytu ('r')
        with open("data\\engines.csv", mode="r", encoding="utf-8") as plik:
            # DictReader automatycznie traktuje pierwszy wiersz jako klucze słownika
            czytnik = csv.DictReader(plik)

            # Przechodzimy przez każdy silnik w pliku
            for wiersz in czytnik:
                pasuje = True

                # Sprawdzamy warunek minimalnej mocy
                if min_moc_kw is not None:
                    if float(wiersz["Moc[kW]"]) < min_moc_kw:
                        pasuje = False

                # Sprawdzamy warunek maksymalnej mocy
                if max_moc_kw is not None:
                    if float(wiersz["Moc[kW]"]) > max_moc_kw:
                        pasuje = False

                # Sprawdzamy warunek minimalnego momentu
                if min_moment_nm is not None:
                    if float(wiersz["Moment_znamionowy[Nm]"]) < min_moment_nm:
                        pasuje = False

                # Sprawdzamy warunek maksymalnego momentu
                if max_moment_nm is not None:
                    if float(wiersz["Moment_znamionowy[Nm]"]) > max_moment_nm:
                        pasuje = False
                # Sprawdzamy warunek minimalnego obrotu
                if min_obroty is not None:
                    if int(wiersz["Obroty[1/min]"]) < min_obroty:
                        pasuje = False

                # Sprawdzamy warunek maksymalnego obrotu
                if max_obroty is not None:
                    if int(wiersz["Obroty[1/min]"]) > max_obroty:
                        pasuje = False

                # Jeśli silnik przeszedł wszystkie filtry, dodajemy go do listy
                if pasuje:
                    znalezione_silniki.append(wiersz)

        # Zwracamy wyniki w formacie JSON
        if znalezione_silniki == []:
            return "\nNie znaleziono silników spełniających kryteria.\nSpróbuj zmienić kryteria wyszukiwania.\n"
        else:
            return json.dumps(znalezione_silniki, indent=4, ensure_ascii=False)

    except FileNotFoundError:
        return "\nError: Could not find file: data\\engines.csv\n"
    except Exception as e:
        return f"\nError: An unexpected error occurred: {str(e)}\n"


if __name__ == "__main__":
    # run the async function properly
    result = asyncio.run(
        find_engine(
            min_moc_kw=20, min_moment_nm=100, max_moc_kw=None, max_moment_nm=None, min_obroty=None, max_obroty=None
        )
    )
    print(result)
