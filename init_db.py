"""
Script de inicialización de base de datos para el Chatbot Educativo
Este script crea las colecciones necesarias y carga datos de ejemplo
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import random

# Cargar variables de entorno
load_dotenv()

# Conexión a MongoDB
MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['chatbot_escolar']

def clear_collections():
    """Limpia las colecciones existentes"""
    print("Limpiando colecciones existentes...")
    collections = ['usuarios', 'conversaciones', 'consultas', 'feedback', 'recursos', 'temas', 'cronograma', 'notas']
    for collection in collections:
        db[collection].delete_many({})
    print("✓ Colecciones limpiadas")

def create_users():
    """Crea usuarios de ejemplo"""
    print("\nCreando usuarios...")
    users = [
        # Estudiantes
        {'dni': '12345678', 'nombre': 'Juan Pérez', 'rol': 'estudiante', 'grado': '4to', 'seccion': 'A'},
        {'dni': '87654321', 'nombre': 'María García', 'rol': 'estudiante', 'grado': '4to', 'seccion': 'B'},
        {'dni': '23456789', 'nombre': 'Carlos Rodríguez', 'rol': 'estudiante', 'grado': '5to', 'seccion': 'A'},
        {'dni': '34567890', 'nombre': 'Ana López', 'rol': 'estudiante', 'grado': '3ro', 'seccion': 'A'},
        {'dni': '45678901', 'nombre': 'Luis Martínez', 'rol': 'estudiante', 'grado': '5to', 'seccion': 'B'},
        
        # Docentes
        {'dni': '11111111', 'nombre': 'Prof. Carlos López', 'rol': 'docente', 'cursos': ['Matemáticas', 'Física']},
        {'dni': '22222222', 'nombre': 'Prof. Sandra Ruiz', 'rol': 'docente', 'cursos': ['Comunicación', 'Literatura']},
        {'dni': '33333333', 'nombre': 'Prof. Roberto Díaz', 'rol': 'docente', 'cursos': ['Historia', 'Geografía']},
        
        # Administrador
        {'dni': '99999999', 'nombre': 'Admin Sistema', 'rol': 'admin', 'permisos': ['all']}
    ]
    
    db.usuarios.insert_many(users)
    print(f"✓ {len(users)} usuarios creados")

def create_topics():
    """Crea los temas por curso"""
    print("\nCreando temas por curso...")
    topics = [
        {
            'curso': 'Matemáticas',
            'temas': [
                'Álgebra: Ecuaciones de primer grado',
                'Álgebra: Ecuaciones de segundo grado',
                'Geometría: Triángulos y sus propiedades',
                'Geometría: Círculos y circunferencias',
                'Trigonometría: Razones trigonométricas',
                'Estadística: Media, mediana y moda',
                'Aritmética: Fracciones y decimales'
            ]
        },
        {
            'curso': 'Ciencias',
            'temas': [
                'Física: Movimiento rectilíneo uniforme',
                'Física: Leyes de Newton',
                'Química: Tabla periódica',
                'Química: Enlaces químicos',
                'Biología: La célula',
                'Biología: Sistemas del cuerpo humano',
                'Ecología: Ecosistemas'
            ]
        },
        {
            'curso': 'Historia',
            'temas': [
                'Historia del Perú: Culturas preincaicas',
                'Historia del Perú: Imperio Incaico',
                'Historia del Perú: Conquista y Virreinato',
                'Historia del Perú: Independencia',
                'Historia Universal: Edad Media',
                'Historia Universal: Revolución Industrial',
                'Geografía: Regiones del Perú'
            ]
        },
        {
            'curso': 'Comunicación',
            'temas': [
                'Gramática: Partes de la oración',
                'Gramática: Análisis sintáctico',
                'Literatura: Géneros literarios',
                'Literatura: Literatura peruana',
                'Comprensión Lectora: Técnicas de lectura',
                'Redacción: Tipos de texto',
                'Oratoria: Técnicas de expresión oral'
            ]
        }
    ]
    
    db.temas.insert_many(topics)
    print(f"✓ Temas creados para {len(topics)} cursos")

def create_resources():
    """Crea recursos educativos de ejemplo"""
    print("\nCreando recursos educativos...")
    resources = [
        # Recursos de Álgebra
        {
            'topic': 'Álgebra',
            'tipo': 'video',
            'titulo': 'Introducción al Álgebra - Khan Academy',
            'url': 'https://es.khanacademy.org/math/algebra',
            'descripcion': 'Video explicativo sobre conceptos básicos de álgebra'
        },
        {
            'topic': 'Álgebra',
            'tipo': 'artículo',
            'titulo': 'Ecuaciones de primer grado paso a paso',
            'url': 'https://www.superprof.es/apuntes/escolar/matematicas/algebra/ecuaciones',
            'descripcion': 'Guía completa para resolver ecuaciones lineales'
        },
        {
            'topic': 'Álgebra',
            'tipo': 'ejercicio',
            'titulo': 'Práctica interactiva de ecuaciones',
            'url': 'https://www.geogebra.org/m/BQ9WRcJZ',
            'descripcion': 'Ejercicios interactivos para practicar ecuaciones'
        },
        
        # Recursos de Geometría
        {
            'topic': 'Geometría',
            'tipo': 'video',
            'titulo': 'Propiedades de los triángulos',
            'url': 'https://www.youtube.com/watch?v=example',
            'descripcion': 'Video sobre tipos y propiedades de triángulos'
        },
        {
            'topic': 'Geometría',
            'tipo': 'simulador',
            'titulo': 'GeoGebra - Geometría Dinámica',
            'url': 'https://www.geogebra.org/geometry',
            'descripcion': 'Herramienta interactiva para explorar geometría'
        },
        
        # Recursos de Física
        {
            'topic': 'Física',
            'tipo': 'video',
            'titulo': 'Leyes de Newton explicadas',
            'url': 'https://www.youtube.com/watch?v=example2',
            'descripcion': 'Explicación visual de las tres leyes de Newton'
        },
        {
            'topic': 'Física',
            'tipo': 'simulador',
            'titulo': 'PhET - Simulaciones de Física',
            'url': 'https://phet.colorado.edu/es/simulations/filter?subjects=physics',
            'descripcion': 'Simulaciones interactivas de fenómenos físicos'
        }
    ]
    
    db.recursos.insert_many(resources)
    print(f"✓ {len(resources)} recursos educativos creados")

def create_schedule():
    """Crea el cronograma escolar"""
    print("\nCreando cronograma escolar...")
    current_year = datetime.now().year
    
    schedule = [
        {'fecha': f'{current_year}-03-01', 'evento': 'Inicio del año escolar', 'tipo': 'académico'},
        {'fecha': f'{current_year}-05-01', 'evento': 'Día del Trabajo - Feriado', 'tipo': 'feriado'},
        {'fecha': f'{current_year}-05-10', 'evento': 'Día de la Madre - Actuación', 'tipo': 'cultural'},
        {'fecha': f'{current_year}-06-15', 'evento': 'Día del Padre - Actuación', 'tipo': 'cultural'},
        {'fecha': f'{current_year}-06-29', 'evento': 'San Pedro y San Pablo - Feriado', 'tipo': 'feriado'},
        {'fecha': f'{current_year}-07-06', 'evento': 'Día del Maestro', 'tipo': 'especial'},
        {'fecha': f'{current_year}-07-15', 'evento': 'Entrega de libretas - Primer bimestre', 'tipo': 'académico'},
        {'fecha': f'{current_year}-07-28', 'evento': 'Fiestas Patrias - Desfile escolar', 'tipo': 'cívico'},
        {'fecha': f'{current_year}-08-30', 'evento': 'Santa Rosa de Lima - Feriado', 'tipo': 'feriado'},
        {'fecha': f'{current_year}-09-23', 'evento': 'Día de la Primavera y la Juventud', 'tipo': 'cultural'},
        {'fecha': f'{current_year}-10-08', 'evento': 'Combate de Angamos - Feriado', 'tipo': 'feriado'},
        {'fecha': f'{current_year}-10-15', 'evento': 'Entrega de libretas - Segundo bimestre', 'tipo': 'académico'},
        {'fecha': f'{current_year}-10-31', 'evento': 'Día de la Canción Criolla', 'tipo': 'cultural'},
        {'fecha': f'{current_year}-11-01', 'evento': 'Todos los Santos - Feriado', 'tipo': 'feriado'},
        {'fecha': f'{current_year}-12-08', 'evento': 'Inmaculada Concepción - Feriado', 'tipo': 'feriado'},
        {'fecha': f'{current_year}-12-15', 'evento': 'Clausura del año escolar', 'tipo': 'académico'}
    ]
    
    db.cronograma.insert_many(schedule)
    print(f"✓ {len(schedule)} eventos agregados al cronograma")

def create_sample_grades():
    """Crea notas de ejemplo para los estudiantes"""
    print("\nCreando notas de ejemplo...")
    
    estudiantes = db.usuarios.find({'rol': 'estudiante'})
    cursos = ['Matemáticas', 'Comunicación', 'Ciencias', 'Historia', 'Inglés', 'Arte', 'Educación Física']
    
    notas_creadas = 0
    for estudiante in estudiantes:
        for curso in cursos:
            # Generar notas aleatorias pero realistas
            nota_base = random.randint(11, 18)
            notas = {
                'dni': estudiante['dni'],
                'curso': curso,
                'bimestre1': {
                    'parcial1': nota_base + random.randint(-2, 2),
                    'parcial2': nota_base + random.randint(-2, 2),
                    'examen': nota_base + random.randint(-1, 1),
                    'promedio': nota_base
                },
                'bimestre2': {
                    'parcial1': nota_base + random.randint(-2, 2),
                    'parcial2': nota_base + random.randint(-2, 2),
                    'examen': nota_base + random.randint(-1, 1),
                    'promedio': nota_base + 1
                },
                'promedio_general': nota_base + 0.5
            }
            db.notas.insert_one(notas)
            notas_creadas += 1
    
    print(f"✓ {notas_creadas} registros de notas creados")

def create_sample_queries():
    """Crea consultas de ejemplo para las estadísticas"""
    print("\nCreando consultas de ejemplo...")
    
    estudiantes = list(db.usuarios.find({'rol': 'estudiante'}))
    temas_consulta = [
        'ecuaciones de primer grado',
        'triángulos',
        'leyes de Newton',
        'célula eucariota',
        'Imperio Incaico',
        'análisis sintáctico',
        'tabla periódica',
        'fracciones'
    ]
    
    queries = []
    for i in range(50):  # Crear 50 consultas de ejemplo
        estudiante = random.choice(estudiantes)
        fecha = datetime.now() - timedelta(days=random.randint(0, 30))
        
        query = {
            'dni': estudiante['dni'],
            'timestamp': fecha,
            'message': f"¿Cómo resuelvo problemas de {random.choice(temas_consulta)}?",
            'response': "Aquí está la explicación paso a paso...",
            'topic': random.choice(['Matemáticas', 'Ciencias', 'Historia', 'Comunicación'])
        }
        queries.append(query)
    
    db.consultas.insert_many(queries)
    print(f"✓ {len(queries)} consultas de ejemplo creadas")

def create_indexes():
    """Crea índices para optimizar las consultas"""
    print("\nCreando índices...")
    
    # Índices para usuarios
    db.usuarios.create_index('dni', unique=True)
    
    # Índices para consultas
    db.consultas.create_index([('dni', 1), ('timestamp', -1)])
    db.consultas.create_index('timestamp')
    db.consultas.create_index('topic')
    
    # Índices para notas
    db.notas.create_index([('dni', 1), ('curso', 1)])
    
    print("✓ Índices creados")

def main():
    """Función principal"""
    print("=== INICIALIZACIÓN DE BASE DE DATOS ===")
    print(f"Conectando a: {MONGO_URI.split('@')[1].split('/')[0]}...")  # Mostrar solo el host
    
    try:
        # Verificar conexión
        client.server_info()
        print("✓ Conexión exitosa a MongoDB")
        
        # Ejecutar inicialización
        clear_collections()
        create_users()
        create_topics()
        create_resources()
        create_schedule()
        create_sample_grades()
        create_sample_queries()
        create_indexes()
        
        print("\n✅ Base de datos inicializada correctamente")
        print("\nUsuarios de prueba creados:")
        print("- Estudiante: DNI 12345678 (Juan Pérez)")
        print("- Estudiante: DNI 87654321 (María García)")
        print("- Docente: DNI 11111111 (Prof. Carlos López)")
        print("- Admin: DNI 99999999 (Admin Sistema)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Verifica tu conexión a MongoDB Atlas y las credenciales en el archivo .env")
    
    finally:
        client.close()

if __name__ == "__main__":
    main()