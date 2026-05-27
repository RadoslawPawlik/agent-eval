import csv
import json

from dotenv import load_dotenv
from pydantic_ai import Agent

from agent_eval.schemas import EngineInfo

agent = Agent()
load_dotenv()


@agent.tool_plain(docstring_format="google", require_parameter_descriptions=True)
async def find_engine(prompt: str) -> str:
    """_summary_

    Args:
        prompt (str): _description_

    Returns:
        str: _description_
    """

    def extract_engine_info(text: str, model: str = "ollama:qwen3.5:latest") -> EngineInfo:
        system_message = """
        Your task is to extract engine information from the given text. The information you need to extract includes:
        1. minimal_engine_power: The minimum power output of the engine, in kilowatts (kW).
        2. maximal_engine_power: The maximum power output of the engine, in kilowatts (kW).
        3. minimal_engine_RPM: The minimum revolutions per minute (RPM) at which the engine operates.
        4. maximal_engine_RPM: The maximum revolutions per minute (RPM) at which the engine operates.
        5. minimal_engine_torque: The minimum torque produced by the engine, usually measured in Newton-meters (Nm).
        6. maximal_engine_torque: The maximum torque produced by the engine, usually measured in Newton-meters (Nm).
        <rules>
        - when you return always respond with minimal_engine_power, maximal_engine_power, minimal_engine_RPM, maximal_engine_RPM, minimal_engine_torque, and maximal_engine_torque and nothing else.
        - if any of the information is not available in the text, return null for that field.
        </rules>
        <examples>
        Text: "Potrzebuję silnika o minimalnej mocy 20 kW i maksymalnym momencie znamionowym 100 Nm."
        Output: {
            "minimal_engine_power": 20,
            "maximal_engine_power": null,
            "minimal_engine_RPM": null,
            "maximal_engine_RPM": null,
            "minimal_engine_torque": null,
            "maximal_engine_torque": 100
        }
        Text: "Szukam silnika o mocy od 50 do 100 kW, obrotach między 1500 a 3000 RPM i momencie znamionowym minimum 200 Nm."
        Output: {
            "minimal_engine_power": 50,
            "maximal_engine_power": 100,
            "minimal_engine_RPM": 1500,
            "maximal_engine_RPM": 3000,
            "minimal_engine_torque": 200,
            "maximal_engine_torque": null
        }
        Text: "Chcę silnik o mocy 75 kW, obrotach do 2500 RPM i momencie znamionowym do 150 Nm."
        Output: {
            "minimal_engine_power": 75,
            "maximal_engine_power": 75,
            "minimal_engine_RPM": null,
            "maximal_engine_RPM": 2500,
            "minimal_engine_torque": null,
            "maximal_engine_torque": 150
        }
        </examples>
        """

        agent = Agent(model=model, instructions=system_message, output_type=EngineInfo)

        result = agent.run_sync(text)
        return result.output

    def search_engines(
        sciezka_do_pliku="data\\engines.csv",
        min_moc_kw=None,
        max_moc_kw=None,
        min_moment_nm=None,
        max_moment_nm=None,
        min_obroty=None,
        max_obroty=None,
    ):
        """
        Narzędzie dla agenta AI do wyszukiwania silników w pliku CSV.
        """
        znalezione_silniki = []

        try:
            # Otwieramy plik w trybie odczytu ('r')
            with open(sciezka_do_pliku, mode="r", encoding="utf-8") as plik:
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
            return json.dumps({"blad": f"Nie znaleziono pliku: {sciezka_do_pliku}"})
        except Exception as e:
            return json.dumps({"blad": f"Wystąpił nieoczekiwany błąd: {str(e)}"})

    return f"Parametry silnika: {extract_engine_info(prompt)} \nZnalezione silniki: {search_engines(min_moc_kw=extract_engine_info(prompt).minimal_engine_power, max_moc_kw=extract_engine_info(prompt).maximal_engine_power, min_moment_nm=extract_engine_info(prompt).minimal_engine_torque, max_moment_nm=extract_engine_info(prompt).maximal_engine_torque, min_obroty=extract_engine_info(prompt).minimal_engine_RPM, max_obroty=extract_engine_info(prompt).maximal_engine_RPM)}"


# if __name__ == "__main__":
#     #query = input("Enter the text containing engine information: ")


#     result = extract_engine_info("Potrzebuję silnika o minimalnej mocy 20 kW i maksymalnym momencie znamionowym 100 Nm.")
#     #print(result)
#     print("Wymagane parametry silnika:")
#     print(f"Moc silnika: {result.minimal_engine_power} kW - {result.maximal_engine_power} kW")
#     print(f"Obroty silnika: {result.minimal_engine_RPM} RPM - {result.maximal_engine_RPM} RPM")
#     print(f"Moment silnika: {result.minimal_engine_torque} Nm - {result.maximal_engine_torque} Nm")

#     wynik_od_agenta = search_engines(
#         min_moc_kw=result.minimal_engine_power,
#         max_moc_kw=result.maximal_engine_power,
#         min_moment_nm=result.minimal_engine_torque,
#         max_moment_nm=result.maximal_engine_torque,
#         min_obroty=result.minimal_engine_RPM,
#         max_obroty=result.maximal_engine_RPM
#     )
#     print("\nWynik wyszukiwania:"
#         + "\n" + wynik_od_agenta + "\n")
