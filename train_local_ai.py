"""
Script para entrenar la IA local con datasets educativos
"""

from local_ai import LocalEducationalAI
import json
import os

# Datasets de ejemplo - REEMPLAZAR CON TUS DATASETS REALES
SAMPLE_DATASETS = {
    'matematicas': [
        {
            'pregunta': '¿Qué es una ecuación de primer grado?',
            'respuesta': 'Una ecuación de primer grado es una igualdad algebraica donde la incógnita (generalmente x) aparece elevada a la potencia 1. Su forma general es ax + b = c, donde a, b y c son números conocidos y x es la incógnita que debemos encontrar.'
        },
        {
            'pregunta': '¿Cómo se resuelve una ecuación de primer grado?',
            'respuesta': 'Para resolver una ecuación de primer grado:\n1. Agrupa los términos con x de un lado y los números del otro\n2. Simplifica cada lado\n3. Despeja x dividiendo por su coeficiente\n\nEjemplo: 2x + 5 = 13\n- Resta 5: 2x = 8\n- Divide entre 2: x = 4'
        },
        {
            'pregunta': '¿Qué es el área de un triángulo?',
            'respuesta': 'El área de un triángulo es la medida de la superficie que ocupa. Se calcula con la fórmula: Área = (base × altura) / 2. La base es cualquier lado del triángulo y la altura es la distancia perpendicular desde ese lado hasta el vértice opuesto.'
        },
        {
            'pregunta': '¿Cómo se calcula el perímetro?',
            'respuesta': 'El perímetro es la suma de todos los lados de una figura. Para calcularlo:\n- Rectángulo: P = 2(largo + ancho)\n- Cuadrado: P = 4 × lado\n- Triángulo: P = lado1 + lado2 + lado3\n- Círculo: P = 2πr (llamado circunferencia)'
        },
        {
            'pregunta': '¿Qué son las fracciones equivalentes?',
            'respuesta': 'Las fracciones equivalentes son fracciones que representan la misma cantidad pero están escritas de forma diferente. Por ejemplo, 1/2 = 2/4 = 3/6. Para obtener fracciones equivalentes, multiplica o divide el numerador y denominador por el mismo número.'
        }
    ],
    
    'comunicacion': [
        {
            'pregunta': '¿Qué es un sustantivo?',
            'respuesta': 'El sustantivo es una palabra que nombra personas, animales, cosas, lugares o ideas. Ejemplos:\n- Personas: Juan, profesora\n- Animales: perro, águila\n- Cosas: mesa, computadora\n- Lugares: Perú, escuela\n- Ideas: amor, libertad'
        },
        {
            'pregunta': '¿Cuáles son los tipos de sustantivos?',
            'respuesta': 'Los sustantivos se clasifican en:\n1. **Propios**: nombres únicos (María, Lima)\n2. **Comunes**: nombres generales (niña, ciudad)\n3. **Concretos**: se pueden percibir (árbol, libro)\n4. **Abstractos**: ideas o sentimientos (paz, alegría)\n5. **Individuales**: un solo ser (soldado)\n6. **Colectivos**: conjunto de seres (ejército)'
        },
        {
            'pregunta': '¿Qué es el verbo?',
            'respuesta': 'El verbo es la palabra que expresa acciones, estados o procesos. Es el núcleo del predicado. Ejemplos:\n- Acciones: correr, saltar, estudiar\n- Estados: ser, estar, permanecer\n- Procesos: crecer, envejecer, madurar\n\nLos verbos se conjugan según persona, número y tiempo.'
        },
        {
            'pregunta': '¿Qué es un párrafo?',
            'respuesta': 'Un párrafo es un conjunto de oraciones que desarrollan una idea principal. Características:\n- Comienza con mayúscula\n- Termina con punto aparte\n- Tiene unidad temática\n- Se separa visualmente del siguiente\n\nUn buen párrafo tiene entre 4 y 8 oraciones relacionadas.'
        }
    ],
    
    'ciencias': [
        {
            'pregunta': '¿Qué es la célula?',
            'respuesta': 'La célula es la unidad básica de la vida. Todos los seres vivos están formados por células. Hay dos tipos principales:\n1. **Procariotas**: sin núcleo definido (bacterias)\n2. **Eucariotas**: con núcleo definido (animales, plantas, hongos)\n\nPartes básicas: membrana celular, citoplasma y material genético.'
        },
        {
            'pregunta': '¿Cuáles son las partes de la célula?',
            'respuesta': 'Las partes principales de una célula eucariota son:\n1. **Membrana celular**: controla entrada y salida\n2. **Núcleo**: contiene el ADN\n3. **Citoplasma**: líquido donde flotan los organelos\n4. **Mitocondrias**: producen energía\n5. **Ribosomas**: fabrican proteínas\n6. **Retículo endoplasmático**: transporte interno\n7. **Aparato de Golgi**: empaqueta sustancias'
        },
        {
            'pregunta': '¿Qué son las leyes de Newton?',
            'respuesta': 'Las tres leyes de Newton explican el movimiento:\n\n1. **Ley de inercia**: Un cuerpo permanece en reposo o movimiento uniforme a menos que actúe una fuerza\n2. **F = ma**: La fuerza es igual a masa por aceleración\n3. **Acción-reacción**: A toda acción corresponde una reacción igual y opuesta'
        },
        {
            'pregunta': '¿Qué es un ecosistema?',
            'respuesta': 'Un ecosistema es el conjunto de seres vivos (factores bióticos) y el medio físico (factores abióticos) donde viven, más las relaciones entre ellos. Componentes:\n- **Bióticos**: plantas, animales, microorganismos\n- **Abióticos**: agua, suelo, luz, temperatura\n- **Relaciones**: cadenas alimenticias, ciclos de nutrientes'
        }
    ],
    
    'historia': [
        {
            'pregunta': '¿Quiénes fueron los incas?',
            'respuesta': 'Los incas fueron una civilización que dominó gran parte de Sudamérica entre los siglos XIII y XVI. Su imperio, el Tahuantinsuyo, abarcó Perú, Ecuador, Bolivia, parte de Chile, Argentina y Colombia. Su capital fue Cusco y su último emperador fue Atahualpa.'
        },
        {
            'pregunta': '¿Qué fue el Tahuantinsuyo?',
            'respuesta': 'El Tahuantinsuyo fue el imperio incaico, que significa "las cuatro regiones unidas":\n1. **Chinchaysuyo**: norte\n2. **Antisuyo**: este\n3. **Collasuyo**: sur\n4. **Contisuyo**: oeste\n\nFue el imperio más grande de América precolombina, unido por el Qhapaq Ñan (camino inca).'
        },
        {
            'pregunta': '¿Cuándo fue la independencia del Perú?',
            'respuesta': 'La independencia del Perú fue proclamada el 28 de julio de 1821 por Don José de San Martín en Lima. Sin embargo, la independencia real se consolidó tras la Batalla de Ayacucho el 9 de diciembre de 1824, donde Antonio José de Sucre derrotó al ejército realista.'
        },
        {
            'pregunta': '¿Quiénes fueron los libertadores del Perú?',
            'respuesta': 'Los principales libertadores del Perú fueron:\n1. **José de San Martín**: Proclamó la independencia (1821)\n2. **Simón Bolívar**: Completó la independencia\n3. **Antonio José de Sucre**: Venció en Ayacucho\n\nTambién destacaron peruanos como José Olaya, María Parado de Bellido y los montoneros.'
        }
    ]
}

def load_dataset_from_file(filepath):
    """Carga un dataset desde un archivo JSON"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error cargando {filepath}: {e}")
        return None

def train_all_models():
    """Entrena todos los modelos con los datasets disponibles"""
    # Crear instancia de IA local
    local_ai = LocalEducationalAI()
    
    print("=== ENTRENAMIENTO DE IA LOCAL ===\n")
    
    # Verificar si hay archivos de datasets personalizados
    datasets_dir = 'datasets/'
    if os.path.exists(datasets_dir):
        print("Buscando datasets personalizados...")
        for subject in ['matematicas', 'comunicacion', 'ciencias', 'historia']:
            dataset_file = os.path.join(datasets_dir, f'{subject}.json')
            if os.path.exists(dataset_file):
                dataset = load_dataset_from_file(dataset_file)
                if dataset:
                    print(f"\n✓ Dataset personalizado encontrado para {subject}")
                    local_ai.train_from_dataset(subject, dataset)
                    continue
            
            # Si no hay dataset personalizado, usar el de ejemplo
            print(f"\n→ Usando dataset de ejemplo para {subject}")
            local_ai.train_from_dataset(subject, SAMPLE_DATASETS[subject])
    else:
        # Usar solo datasets de ejemplo
        print("Usando datasets de ejemplo...\n")
        for subject, dataset in SAMPLE_DATASETS.items():
            local_ai.train_from_dataset(subject, dataset)
    
    # Mostrar estadísticas
    print("\n=== ESTADÍSTICAS DE ENTRENAMIENTO ===")
    stats = local_ai.get_statistics()
    for subject, count in stats.items():
        print(f"{subject.capitalize()}: {count} preguntas")
    
    print("\n✅ Entrenamiento completado!")
    print("\nPara usar datasets personalizados:")
    print("1. Crea una carpeta 'datasets/'")
    print("2. Agrega archivos JSON: matematicas.json, comunicacion.json, etc.")
    print("3. Formato: [{\"pregunta\": \"...\", \"respuesta\": \"...\"}, ...]")

def test_local_ai():
    """Prueba la IA local con algunas preguntas"""
    local_ai = LocalEducationalAI()
    
    print("\n=== PRUEBAS DE IA LOCAL ===\n")
    
    test_questions = [
        "¿Qué es una ecuación?",
        "¿Cómo se calcula el área de un triángulo?",
        "¿Qué es un sustantivo?",
        "¿Qué es la célula?",
        "¿Quiénes fueron los incas?",
        "¿Cómo se hace una pizza?"  # Pregunta fuera de dominio
    ]
    
    for question in test_questions:
        print(f"\n❓ Pregunta: {question}")
        response, confidence, subject = local_ai.get_response(question)
        
        if response:
            print(f"✓ Respuesta (confianza: {confidence:.2f}, materia: {subject}):")
            print(response)
        else:
            print(f"✗ Sin respuesta local (confianza: {confidence:.2f})")

if __name__ == "__main__":
    # Entrenar modelos
    train_all_models()
    
    # Realizar pruebas
    test_local_ai()