from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
import time
from playsound import playsound

# Configuración del WebDriver para Microsoft Edge
edge_options = Options()
edge_options.add_argument("--disable-gpu")

service = Service('C:/Users/JRRR/Desktop/QA/Selenium web/msedgedriver.exe')  # Especifica la ruta al msedgedriver

# Crear dos instancias del WebDriver para abrir dos ventanas
driver1 = webdriver.Edge(service=service, options=edge_options)
driver2 = webdriver.Edge(service=service, options=edge_options)

# URLs de los partidos
url_partido1 = "https://www.flashscore.es/partido/OQqSjnv9/#/resumen-del-partido/resumen-del-partido"
url_partido2 = "https://www.flashscore.es/partido/YcAFQVSP/#/resumen-del-partido/resumen-del-partido"

# Abre las URLs en las dos instancias del WebDriver
driver1.get(url_partido1)
driver2.get(url_partido2)

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

# Variables para almacenar el número de goles detectados en el ciclo anterior
prev_goals_1 = 0
prev_goals_2 = 0

# Bucle para revisar si se marca un nuevo gol en ambos partidos
try:
    while True:
        # Contar los goles actuales en ambos partidos
        current_goals_1 = count_goals(driver1)
        current_goals_2 = count_goals(driver2)

        # Comparar con el número de goles en el ciclo anterior
        if current_goals_1 > prev_goals_1:
            print(f"¡Nuevo gol en el partido 1! Reproduciendo sonido...")
            playsound('C:/Users/JRRR/Desktop/QA/Selenium web/Flashcore goal/sonido.mp3')
        
        if current_goals_2 > prev_goals_2:
            print(f"¡Nuevo gol en el partido 2! Reproduciendo sonido...")
            playsound('C:/Users/JRRR/Desktop/QA/Selenium web/Flashcore goal/sonido.mp3')

        # Actualizar el número de goles previos
        prev_goals_1 = current_goals_1
        prev_goals_2 = current_goals_2

        # Esperar 10 segundos antes de volver a verificar
        time.sleep(10)
except KeyboardInterrupt:
    print("Script terminado por el usuario.")
finally:
    driver1.quit()
    driver2.quit()
