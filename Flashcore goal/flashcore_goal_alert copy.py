from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from playsound import playsound
import re

# Configuración del WebDriver para Microsoft Edge
edge_options = Options()
edge_options.add_argument("--disable-gpu")

service = Service('C:/Users/JRRR/Desktop/QA/Selenium web/msedgedriver.exe')

# Crear una instancia del WebDriver
driver = webdriver.Edge(service=service, options=edge_options)

# URL de la página principal de Flashscore
url_flashscore = "https://www.flashscore.es/"
driver.get(url_flashscore)

# Esperar a que se carguen los partidos
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.event__match")))

# Selectores para los partidos de la Bundesliga y la Premier League
bundesliga_selector = "div.event__match.event__match--live.event__match--withRowLink.event__match--twoLine"
premier_league_selector = "div.event__match.event__match--live.event__match--withRowLink.event__match--twoLine"

# Filtrar partidos por liga
def get_partidos(liga_selector, nombre_liga):
    partidos = driver.find_elements(By.CSS_SELECTOR, liga_selector)
    partidos_disponibles = []

    for partido in partidos:
        try:
            hora = partido.find_element(By.CSS_SELECTOR, "div.event__stage").text.strip()
            equipo_local = partido.find_element(By.CSS_SELECTOR, "div.event__homeParticipant span").text.strip()
            equipo_visitante = partido.find_element(By.CSS_SELECTOR, "div.event__awayParticipant span").text.strip()
            nombre_partido = f"{equipo_local} vs {equipo_visitante} - {hora}"
            partidos_disponibles.append((nombre_partido, hora, equipo_local, equipo_visitante))
        except Exception as e:
            print(f"Error al extraer información del partido: {e}")
    
    return partidos_disponibles

# Extraer partidos de la Bundesliga
print("Partidos de la Bundesliga:")
partidos_bundesliga = get_partidos(bundesliga_selector, "Bundesliga")
for idx, (nombre_partido, hora, equipo_local, equipo_visitante) in enumerate(partidos_bundesliga):
    print(f"{idx + 1}: {nombre_partido}")

# Extraer partidos de la Premier League
print("\nPartidos de la Premier League:")
partidos_premier_league = get_partidos(premier_league_selector, "Premier League")
for idx, (nombre_partido, hora, equipo_local, equipo_visitante) in enumerate(partidos_premier_league):
    print(f"{idx + 1}: {nombre_partido}")

# Permitir al usuario seleccionar los partidos a analizar
elecciones = input("Selecciona los números de los partidos a analizar (Bundesliga y Premier League), separados por coma (o ingresa un enlace de partido para agregarlo manualmente): ")
indices_seleccionados = []

if elecciones.lower().startswith("https://"):
    # El usuario ingresó un enlace del partido
    enlace_partido = elecciones.strip()
    
    # Extraer el ID del partido del enlace
    partido_id_match = re.search(r"/partido/([a-zA-Z0-9]+)/", enlace_partido)
    if partido_id_match:
        partido_id = partido_id_match.group(1)
        
        # Buscar el partido en las listas de partidos disponibles
        encontrado = False
        all_partidos = partidos_bundesliga + partidos_premier_league
        for idx, (nombre, _, _, _) in enumerate(all_partidos):
            if partido_id in nombre:
                indices_seleccionados.append(idx)
                encontrado = True
                break
        
        if not encontrado:
            print(f"No se encontró el partido con ID '{partido_id}' en la lista de partidos disponibles.")
            exit()
    else:
        print("Enlace no válido.")
        exit()
else:
    # Procesar la entrada de selección de partidos
    try:
        indices_seleccionados = [int(i.strip()) - 1 for i in elecciones.split(',')]
    except ValueError:
        print("Entrada no válida. Debes ingresar números separados por comas o un enlace de partido válido.")
        exit()

# Filtrar los partidos seleccionados
partidos_seleccionados = [partidos_bundesliga[i] if i < len(partidos_bundesliga) else partidos_premier_league[i - len(partidos_bundesliga)] for i in indices_seleccionados]

# Crear instancias del WebDriver para cada partido seleccionado
drivers = []
prev_goals = []

for index in indices_seleccionados:
    liga_partidos = partidos_bundesliga if index < len(partidos_bundesliga) else partidos_premier_league
    partido_element = driver.find_elements(By.CSS_SELECTOR, bundesliga_selector + ", " + premier_league_selector)[index]
    link_partido = partido_element.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
    
    driver_partido = webdriver.Edge(service=service, options=edge_options)
    driver_partido.get(link_partido)
    drivers.append(driver_partido)
    prev_goals.append(0)

# Selector CSS para el icono de gol
goal_icon_selector = "svg[data-testid='wcl-icon-soccer']"

# Función para contar los goles
def count_goals(driver):
    try:
        goals = driver.find_elements(By.CSS_SELECTOR, goal_icon_selector)
        return len(goals)
    except Exception as e:
        print(f"Error al contar los goles: {e}")
        return 0

# Bucle para revisar si se marca un nuevo gol en los partidos seleccionados
try:
    while True:
        for i, driver in enumerate(drivers):
            current_goals = count_goals(driver)

            if current_goals > prev_goals[i]:
                print(f"¡Nuevo gol en el partido {i + 1} ({partidos_seleccionados[i][0]})! Reproduciendo sonido...")
                playsound('C:/Users/JRRR/Desktop/QA/Selenium web/Flashcore goal/sonido.mp3')

            prev_goals[i] = current_goals

        time.sleep(10)
except KeyboardInterrupt:
    print("Script terminado por el usuario.")
finally:
    for driver in drivers:
        driver.quit()
