import csv
import json

from dotenv import load_dotenv
from pydantic_ai import Agent

from agent_eval.schemas import BearingInfo

agent = Agent()
load_dotenv()


@agent.tool_plain(docstring_format="google", require_parameter_descriptions=True)
async def find_bearing(prompt: str) -> str:
    """This function takes a text prompt describing the requirements for a bearing and returns a list of bearings that match those requirements from a CSV file.
    The function first extracts the bearing information from the prompt using an LLM, and then searches for bearings in the CSV file that meet the specified criteria.

    Args:
        prompt (str): A prommpt containing the requirements for the bearing, such as dimensions, load ratings, speed ratings, mass, and type.

    Returns:
        str: A list of bearings that match the specified criteria.
    """

    def extract_bearing_info(text: str, model: str = "ollama:qwen3.5:latest") -> BearingInfo:
        system_message = """
        Your task is to extract bearing information from the given text. The information you need to extract includes:
        1. min_srednica_wewn_d: The minimum inner diameter of the bearing in mm.
        2. max_srednica_wewn_d: The maximum inner diameter of the bearing in mm.
        3. min_srednica_zewn_D: The minimum outer diameter of the bearing in mm.
        4. max_srednica_zewn_D: The maximum outer diameter of the bearing in mm.
        5. min_szerokosc_B: The minimum width of the bearing in mm.
        6. max_szerokosc_B: The maximum width of the bearing in mm.
        7. min_nosnosc_dyn_C: The minimum dynamic load rating of the bearing in kN.
        8. max_nosnosc_dyn_C: The maximum dynamic load rating of the bearing in kN.
        9. min_nosnosc_stat_C0: The minimum static load rating of the bearing in kN.
        10. max_nosnosc_stat_C0: The maximum static load rating of the bearing in kN.
        11. min_obc_zmecz_Pu: The minimum fatigue load of the bearing in kN.
        12. max_obc_zmecz_Pu: The maximum fatigue load of the bearing in kN.
        13. min_v: The minimum operating speed of the bearing, typically measured in revolutions per minute (RPM).
        14. max_v: The maximum operating speed of the bearing, typically measured in revolutions per minute (RPM).
        15. min_v_max: The minimum maximum operating speed of the bearing, typically measured in revolutions per minute (RPM).
        16. max_v_max: The maximum maximum operating speed of the bearing, typically measured in revolutions per minute (RPM).
        17. min_mass: The minimum mass of the bearing, typically measured in kilograms (kg).
        18. max_mass: The maximum mass of the bearing, typically measured in kilograms (kg).
        19. typ: The type of the bearing, which can be one of the following: "Ball", "Angular Contact Ball", "Self-Aligning Ball", or "Spherical Roller".
        <rules>
        - when you return always respond with min_srednica, max_srednica, min_srednica_zewn_D, max_srednica_zewn_D, min_szerokosc_B, max_szerokosc_B, min_nosnosc_dyn_C, max_nosnosc_dyn_C, min_nosnosc_stat_C0, max_nosnosc_stat_C0, min_obc_zmecz_Pu, max_obc_zmecz_Pu, min_v, max_v, min_v_max, max_v_max, min_mass, max_mass, and typ and nothing else.
        - if any of the information is not available in the text, return null for that field.
        - if the type of the bearing is not specified in the text, return Ball for the typ field.
        # </rules>

        <examples>
        Text: "Potrzebuję łożyska o średnicy wewnętrznej minimum 20 mm, nośności dynamicznej minimum 20 kN i nośności statycznej minimum 10 kN."
        Output: {
            "min_srednica_wewn_d": 20,
            "max_srednica_wewn_d": null,
            "min_srednica_zewn_D": null,
            "max_srednica_zewn_D": null,
            "min_szerokosc_B": null,
            "max_szerokosc_B": null,
            "min_nosnosc_dyn_C": 20,
            "max_nosnosc_dyn_C": null,
            "min_nosnosc_stat_C0": 10,
            "max_nosnosc_stat_C0": null,
            "min_obc_zmecz_Pu": null,
            "max_obc_zmecz_Pu": null,
            "min_v": null,
            "max_v": null,
            "min_v_max": null,
            "max_v_max": null,
            "min_mass": null,
            "max_mass": null,
            "typ": "Ball"
        }
        Text: "Szukam łożyska kulkowego o średnicy zewnętrznej maksymalnie 50 mm, szerokości między 10 a 20 mm, nośności dynamicznej minimum 15 kN, nośności statycznej minimum 5 kN, prędkości maksymalnej 5000 RPM i masie do 0.5 kg."
        Output: {
            "min_srednica_wewn_d": null,
            "max_srednica_wewn_d": null,
            "min_srednica_zewn_D": null,
            "max_srednica_zewn_D": 50,
            "min_szerokosc_B": 10,
            "max_szerokosc_B": 20,
            "min_nosnosc_dyn_C": 15,
            "max_nosnosc_dyn_C": null,
            "min_nosnosc_stat_C0": 5,
            "max_nosnosc_stat_C0": null,
            "min_obc_zmecz_Pu": null,
            "max_obc_zmecz_Pu": null,
            "min_v": null,
            "max_v": null,
            "min_v_max": null,
            "max_v_max": 5000,
            "min_mass": null,
            "max_mass": 0.5,
            "typ": "Ball"
        }
        </examples>
        """
        agent = Agent(model=model, instructions=system_message, output_type=BearingInfo)

        result = agent.run_sync(text)
        return result.output

    def search_bearings(bearing_info: BearingInfo, sciezka_do_pliku="data\\bearings.csv"):
        """
        Narzędzie dla agenta AI do wyszukiwania łożysk w pliku CSV.
        """
        znalezione_lozyska = []

        try:
            # Otwieramy plik w trybie odczytu ('r')
            with open(sciezka_do_pliku, mode="r", encoding="utf-8") as plik:
                # DictReader automatycznie traktuje pierwszy wiersz jako klucze słownika
                czytnik = csv.DictReader(plik)

                # Przechodzimy przez każde łożysko w pliku
                for wiersz in czytnik:
                    pasuje = True

                    def safe_float(value, field_name):
                        """Safely convert value to float, return None if conversion fails"""
                        try:
                            if value is None or value.strip() == "":
                                return None
                            return float(value)
                        except (ValueError, AttributeError):
                            return None

                    # Sprawdzamy warunek minimalnej średnicy wewnętrznej
                    if bearing_info.min_srednica_wewn_d is not None:
                        val = safe_float(wiersz.get("d[mm]"), "d[mm]")
                        if val is not None and val < bearing_info.min_srednica_wewn_d:
                            pasuje = False
                    # Sprawdzamy warunek maksymalnej średnicy wewnętrznej
                    if bearing_info.max_srednica_wewn_d is not None:
                        val = safe_float(wiersz.get("d[mm]"), "d[mm]")
                        if val is not None and val > bearing_info.max_srednica_wewn_d:
                            pasuje = False
                    # Sprawdzamy warunek maksymalnej średnicy zewnętrznej
                    if bearing_info.max_srednica_zewn_D is not None:
                        val = safe_float(wiersz.get("D[mm]"), "D[mm]")
                        if val is not None and val > bearing_info.max_srednica_zewn_D:
                            pasuje = False
                    # Sprawdzamy warunek minimalnej średnicy zewnętrznej
                    if bearing_info.min_srednica_zewn_D is not None:
                        val = safe_float(wiersz.get("D[mm]"), "D[mm]")
                        if val is not None and val < bearing_info.min_srednica_zewn_D:
                            pasuje = False
                    # Sprawdzamy warunek minimalnej szerokości
                    if bearing_info.min_szerokosc_B is not None:
                        val = safe_float(wiersz.get("B[mm]"), "B[mm]")
                        if val is not None and val < bearing_info.min_szerokosc_B:
                            pasuje = False

                    # Sprawdzamy warunek maksymalnej szerokości
                    if bearing_info.max_szerokosc_B is not None:
                        val = safe_float(wiersz.get("B[mm]"), "B[mm]")
                        if val is not None and val > bearing_info.max_szerokosc_B:
                            pasuje = False

                    # Sprawdzamy warunek nosności dynamicznej
                    if bearing_info.min_nosnosc_dyn_C is not None:
                        val = safe_float(wiersz.get("C[kN]"), "C[kN]")
                        if val is not None and val < bearing_info.min_nosnosc_dyn_C:
                            pasuje = False
                    if bearing_info.max_nosnosc_dyn_C is not None:
                        val = safe_float(wiersz.get("C[kN]"), "C[kN]")
                        if val is not None and val > bearing_info.max_nosnosc_dyn_C:
                            pasuje = False
                    # Sprawdzamy warunek nosności statycznej
                    if bearing_info.min_nosnosc_stat_C0 is not None:
                        val = safe_float(wiersz.get("C0[kN]"), "C0[kN]")
                        if val is not None and val < bearing_info.min_nosnosc_stat_C0:
                            pasuje = False
                    if bearing_info.max_nosnosc_stat_C0 is not None:
                        val = safe_float(wiersz.get("C0[kN]"), "C0[kN]")
                        if val is not None and val > bearing_info.max_nosnosc_stat_C0:
                            pasuje = False
                    # Sprawdzamy warunek obciążenia zmęczeniowego
                    if bearing_info.min_obc_zmecz_Pu is not None:
                        val = safe_float(wiersz.get("Pu[kN]"), "Pu[kN]")
                        if val is not None and val < bearing_info.min_obc_zmecz_Pu:
                            pasuje = False
                    if bearing_info.max_obc_zmecz_Pu is not None:
                        val = safe_float(wiersz.get("Pu[kN]"), "Pu[kN]")
                        if val is not None and val > bearing_info.max_obc_zmecz_Pu:
                            pasuje = False
                    # Sprawdzamy warunek minimalnej prędkości
                    if bearing_info.min_v is not None:
                        val = safe_float(wiersz.get("v[RPM]"), "v[RPM]")
                        if val is not None and val < bearing_info.min_v:
                            pasuje = False
                    # Sprawdzamy warunek maksymalnej prędkości
                    if bearing_info.max_v is not None:
                        val = safe_float(wiersz.get("v[RPM]"), "v[RPM]")
                        if val is not None and val > bearing_info.max_v:
                            pasuje = False
                    # Sprawdzamy warunek minimalnej maksymalnej prędkości
                    if bearing_info.min_v_max is not None:
                        val = safe_float(wiersz.get(" v_max[RPM]"), " v_max[RPM]")
                        if val is not None and val < bearing_info.min_v_max:
                            pasuje = False
                    # Sprawdzamy warunek maksymalnej maksymalnej prędkości
                    if bearing_info.max_v_max is not None:
                        val = safe_float(wiersz.get(" v_max[RPM]"), " v_max[RPM]")
                        if val is not None and val > bearing_info.max_v_max:
                            pasuje = False
                    # Sprawdzamy warunek minimalnej masy
                    if bearing_info.min_mass is not None:
                        val = safe_float(wiersz.get("m[kg]"), "m[kg]")
                        if val is not None and val < bearing_info.min_mass:
                            pasuje = False
                    # Sprawdzamy warunek maksymalnej masy
                    if bearing_info.max_mass is not None:
                        val = safe_float(wiersz.get("m[kg]"), "m[kg]")
                        if val is not None and val > bearing_info.max_mass:
                            pasuje = False
                    if bearing_info.typ is not None:
                        if str(wiersz.get("Type", "")).strip() != bearing_info.typ:
                            pasuje = False

                    # Jeśli łożysko przeszło wszystkie filtry, dodajemy je do listy
                    if pasuje:
                        znalezione_lozyska.append(wiersz)

            # String sformatowany jako JSON z wcięciami
            return json.dumps(znalezione_lozyska, indent=4, ensure_ascii=False)

        except FileNotFoundError:
            return json.dumps({"blad": f"Nie znaleziono pliku: {sciezka_do_pliku}"})
        except Exception as e:
            return json.dumps({"blad": f"Wystapil nieoczekiwany blad: {str(e)}"})

    return f"Parametry łożyska: {extract_bearing_info(prompt)}. \nZnalezione łożyska: {search_bearings(extract_bearing_info(prompt))}"


# if __name__ == "__main__":
#     # query = input("Enter the text containing engine information: ")
#     result = extract_bearing_info(
#         "Potrzebuję łożyska baryłkowego o średnicy wewnętrznej minimum 20 mm nośności dynamicznej minimum 20 kN i nośności statycznej minimum 10 kN."
#     )

#     print("Wymagane parametry łożyska:")
#     print(f"Średnica wewnętrzna: {result.min_srednica_wewn_d} mm - {result.max_srednica_wewn_d} mm")
#     print(f"Średnica zewnętrzna: {result.min_srednica_zewn_D} mm - {result.max_srednica_zewn_D} mm")
#     print(f"Szerokość: {result.min_szerokosc_B} mm - {result.max_szerokosc_B} mm")
#     print(f"Nosność dynamiczna: {result.min_nosnosc_dyn_C} kN - {result.max_nosnosc_dyn_C} kN")
#     print(f"Nosność statyczna: {result.min_nosnosc_stat_C0} kN - {result.max_nosnosc_stat_C0} kN")
#     print(f"Obciążenie zmęczeniowe: {result.min_obc_zmecz_Pu} kN - {result.max_obc_zmecz_Pu} kN")
#     print(f"Prędkość: {result.min_v} RPM - {result.max_v} RPM")
#     print(f"Masa: {result.min_mass} kg - {result.max_mass} kg")
#     print(f"Typ łożyska: {result.typ}")

#     # Use the extracted bearing info as the search filter
#     wynik_od_agenta = search_bearings(bearing_info=result)

#     if wynik_od_agenta == "[]":
#         print("\nNie znaleziono łożysk spełniających kryteria." + "\n" + "Spróbuj zmienić kryteria wyszukiwania.\n")
#     else:
#         print("\nWynik wyszukiwania:" + "\n" + wynik_od_agenta + "\n")
