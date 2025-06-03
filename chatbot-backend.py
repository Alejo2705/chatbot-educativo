from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from flask_session import Session
from pymongo import MongoClient
from datetime import datetime, timedelta
import google.generativeai as genai
from googleapiclient import discovery
import os
import re
import random
from dotenv import load_dotenv
import json

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuración de sesiones
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'tu-clave-secreta-aqui')
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Configuración de MongoDB Atlas
MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://usuario:password@cluster.mongodb.net/chatbot_escolar?retryWrites=true&w=majority')
client = MongoClient(MONGO_URI)
db = client['chatbot_escolar']
users_collection = db['usuarios']
conversations_collection = db['conversaciones']
queries_collection = db['consultas']
feedback_collection = db['feedback']
resources_collection = db['recursos']
topics_collection = db['temas']

# Configuración de Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Configuración de Perspective API
PERSPECTIVE_API_KEY = os.getenv('PERSPECTIVE_API_KEY')
perspective_client = discovery.build(
    "commentanalyzer",
    "v1alpha1",
    developerKey=PERSPECTIVE_API_KEY,
    discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
    static_discovery=False,
)

# Frases motivadoras
FRASES_MOTIVADORAS = [
    "¡Tú puedes lograrlo! 💪 Cada paso cuenta en tu camino al éxito.",
    "El esfuerzo de hoy es el éxito de mañana. ¡Sigue adelante! 🌟",
    "Los grandes logros requieren tiempo. ¡No te rindas! 🚀",
    "Cada error es una oportunidad de aprendizaje. ¡Adelante! 📚",
    "Tu dedicación te llevará lejos. ¡Confía en ti! 🎯",
    "El conocimiento es poder. ¡Sigue aprendiendo! 🧠",
    "Paso a paso se llega lejos. ¡Continúa! 👣",
    "Tu esfuerzo vale la pena. ¡No pares! 🏆"
]

# Límites de intentos de DNI
dni_attempts = {}
MAX_DNI_ATTEMPTS = 3
LOCKOUT_TIME = 30  # segundos

def validate_dni(dni):
    """Valida que el DNI tenga 8 dígitos numéricos"""
    return bool(re.match(r'^\d{8}$', dni))

def check_message_toxicity(text):
    """Verifica si el mensaje es tóxico usando Perspective API"""
    try:
        analyze_request = {
            'comment': {'text': text},
            'requestedAttributes': {
                'TOXICITY': {},
                'SEVERE_TOXICITY': {},
                'INSULT': {},
                'THREAT': {}
            }
        }
        
        response = perspective_client.comments().analyze(body=analyze_request).execute()
        scores = response['attributeScores']
        
        # Si alguna puntuación es mayor a 0.7, consideramos el mensaje como inapropiado
        for attribute in scores:
            if scores[attribute]['summaryScore']['value'] > 0.7:
                return True, attribute
        
        return False, None
    except Exception as e:
        print(f"Error en Perspective API: {e}")
        return False, None

def get_user_info(dni):
    """Obtiene información del usuario desde MongoDB"""
    user = users_collection.find_one({'dni': dni})
    return user

def save_query(user_dni, message, response, topic=None):
    """Guarda la consulta en la base de datos"""
    query = {
        'dni': user_dni,
        'timestamp': datetime.now(),
        'message': message,
        'response': response,
        'topic': topic
    }
    queries_collection.insert_one(query)

def get_ai_response(message, context=None):
    """Obtiene respuesta de Gemini API"""
    try:
        # Primero verificar si es un comando especial
        if message.startswith('/'):
            return handle_command(message)
        
        # Construir el prompt con contexto educativo
        prompt = f"""Eres un asistente educativo amigable para estudiantes de secundaria. 
        Tu objetivo es ayudar con dudas académicas, explicar conceptos de manera clara y motivar el aprendizaje.
        
        Contexto del estudiante: {context if context else 'Estudiante de secundaria'}
        
        Pregunta del estudiante: {message}
        
        Por favor, responde de manera clara, educativa y motivadora. Si es una pregunta académica, 
        proporciona una explicación paso a paso cuando sea apropiado."""
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error con Gemini API: {e}")
        return "Lo siento, hubo un error al procesar tu pregunta. Por favor, intenta de nuevo."

def handle_command(command):
    """Maneja comandos especiales del chatbot"""
    parts = command.split(' ', 1)
    cmd = parts[0].lower()
    
    if cmd == '/motivar':
        return random.choice(FRASES_MOTIVADORAS)
    
    elif cmd == '/temas':
        if len(parts) < 2:
            return "Usa el comando así: /temas <curso>\nCursos disponibles: Matemáticas, Ciencias, Historia, Comunicación"
        
        curso = parts[1].title()
        temas = topics_collection.find_one({'curso': curso})
        
        if not temas:
            return f"Curso no reconocido. Cursos disponibles: Matemáticas, Ciencias, Historia, Comunicación"
        
        temas_list = "\n".join([f"{i+1}. {tema}" for i, tema in enumerate(temas.get('temas', []))])
        return f"Temas de {curso}:\n{temas_list}"
    
    elif cmd == '/definir':
        if len(parts) < 2:
            return "Usa el comando así: /definir <palabra>"
        
        palabra = parts[1]
        # Aquí usaremos Gemini para obtener la definición
        prompt = f"Define la palabra '{palabra}' de manera simple para un estudiante de secundaria y proporciona un ejemplo de uso."
        response = model.generate_content(prompt)
        return response.text
    
    elif cmd == '/reset':
        # Limpiar el contexto de la sesión
        if 'conversation_context' in session:
            session.pop('conversation_context')
        return "Contexto reiniciado. ¿En qué te ayudo ahora?"
    
    else:
        return "Comando no reconocido. Comandos disponibles: /motivar, /temas <curso>, /definir <palabra>, /reset"

@app.route('/')
def index():
    """Página principal del aula virtual con el chatbot"""
    return render_template('index.html')

@app.route('/validate_dni', methods=['POST'])
def validate_dni_endpoint():
    """Endpoint para validar DNI"""
    data = request.json
    dni = data.get('dni', '')
    client_ip = request.remote_addr
    
    # Verificar intentos de DNI
    current_time = datetime.now()
    if client_ip in dni_attempts:
        attempts_info = dni_attempts[client_ip]
        if attempts_info['locked_until'] and current_time < attempts_info['locked_until']:
            remaining_time = (attempts_info['locked_until'] - current_time).seconds
            return jsonify({
                'success': False,
                'error': f'Demasiados intentos, espera {remaining_time} segundos e inténtalo otra vez'
            }), 429
    
    # Validar formato DNI
    if not validate_dni(dni):
        # Incrementar contador de intentos
        if client_ip not in dni_attempts:
            dni_attempts[client_ip] = {'attempts': 0, 'locked_until': None}
        
        dni_attempts[client_ip]['attempts'] += 1
        
        if dni_attempts[client_ip]['attempts'] >= MAX_DNI_ATTEMPTS:
            dni_attempts[client_ip]['locked_until'] = current_time + timedelta(seconds=LOCKOUT_TIME)
            return jsonify({
                'success': False,
                'error': 'Demasiados intentos, espera 30 segundos e inténtalo otra vez'
            }), 429
        
        return jsonify({
            'success': False,
            'error': 'DNI no válido, inténtalo de nuevo'
        }), 400
    
    # Buscar usuario en la base de datos
    user = get_user_info(dni)
    if not user:
        return jsonify({
            'success': False,
            'error': 'Usuario no encontrado'
        }), 404
    
    # Guardar información del usuario en la sesión
    session['user_dni'] = dni
    session['user_name'] = user.get('nombre', 'Usuario')
    session['user_role'] = user.get('rol', 'estudiante')
    
    # Resetear intentos
    if client_ip in dni_attempts:
        del dni_attempts[client_ip]
    
    return jsonify({
        'success': True,
        'user': {
            'nombre': user.get('nombre'),
            'rol': user.get('rol')
        }
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint principal del chat"""
    if 'user_dni' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    data = request.json
    message = data.get('message', '')
    
    # Verificar toxicidad del mensaje
    is_toxic, toxic_type = check_message_toxicity(message)
    if is_toxic:
        return jsonify({
            'response': 'Por favor, mantén un lenguaje respetuoso y apropiado.',
            'warning': True
        })
    
    # Obtener contexto del usuario
    user_context = {
        'nombre': session.get('user_name'),
        'rol': session.get('user_role')
    }
    
    # Obtener respuesta de la IA
    response = get_ai_response(message, user_context)
    
    # Guardar la consulta
    save_query(session['user_dni'], message, response)
    
    return jsonify({
        'response': response,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/feedback', methods=['POST'])
def feedback():
    """Endpoint para recibir feedback de las respuestas"""
    if 'user_dni' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    data = request.json
    feedback_data = {
        'dni': session['user_dni'],
        'timestamp': datetime.now(),
        'message_id': data.get('message_id'),
        'rating': data.get('rating'),  # 'positive' o 'negative'
    }
    
    feedback_collection.insert_one(feedback_data)
    
    if data.get('rating') == 'positive':
        return jsonify({'message': '¡Gracias por tu feedback positivo!'})
    else:
        return jsonify({'message': 'Lamentamos la experiencia; indicaré esto al equipo.'})

@app.route('/resources/<topic>', methods=['GET'])
def get_resources(topic):
    """Endpoint para obtener recursos adicionales de un tema"""
    if 'user_dni' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    resources = resources_collection.find({'topic': topic}).limit(3)
    resources_list = []
    
    for resource in resources:
        resources_list.append({
            'tipo': resource.get('tipo'),
            'titulo': resource.get('titulo'),
            'url': resource.get('url'),
            'descripcion': resource.get('descripcion')
        })
    
    if not resources_list:
        return jsonify({'message': 'No tengo recursos disponibles para este tema, inténtalo con otro'})
    
    return jsonify({'resources': resources_list})

@app.route('/stats', methods=['GET'])
def get_stats():
    """Endpoint para obtener estadísticas (solo admin y docentes)"""
    if 'user_dni' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    if session.get('user_role') not in ['admin', 'docente']:
        return jsonify({'error': 'Sin permisos'}), 403
    
    # Estadísticas básicas
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    stats = {
        'sesiones_hoy': queries_collection.count_documents({
            'timestamp': {'$gte': today}
        }),
        'total_usuarios': users_collection.count_documents({}),
        'consultas_semana': queries_collection.count_documents({
            'timestamp': {'$gte': today - timedelta(days=7)}
        })
    }
    
    # Top temas consultados
    pipeline = [
        {'$match': {'timestamp': {'$gte': today - timedelta(days=7)}}},
        {'$group': {'_id': '$topic', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': 5}
    ]
    
    top_topics = list(queries_collection.aggregate(pipeline))
    stats['top_topics'] = top_topics
    
    return jsonify(stats)

@app.route('/grades', methods=['GET'])
def get_grades():
    """Endpoint para obtener notas del estudiante"""
    if 'user_dni' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    if session.get('user_role') != 'estudiante':
        return jsonify({'error': 'Solo para estudiantes'}), 403
    
    # Simular obtención de notas (en producción vendría de otro sistema)
    grades = {
        'Matemáticas': {'nota': 16, 'promedio': 15},
        'Comunicación': {'nota': 17, 'promedio': 16},
        'Ciencias': {'nota': 15, 'promedio': 14},
        'Historia': {'nota': 18, 'promedio': 17}
    }
    
    return jsonify({'grades': grades})

@app.route('/schedule', methods=['GET'])
def get_schedule():
    """Endpoint para obtener cronograma escolar"""
    if 'user_dni' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    # Cronograma de ejemplo
    schedule = [
        {'fecha': '2025-06-15', 'evento': 'Día del Padre - Actuación'},
        {'fecha': '2025-07-06', 'evento': 'Día del Maestro'},
        {'fecha': '2025-07-28', 'evento': 'Fiestas Patrias - Desfile'},
        {'fecha': '2025-08-30', 'evento': 'Día de Santa Rosa de Lima'},
        {'fecha': '2025-10-31', 'evento': 'Día de la Canción Criolla'}
    ]
    
    return jsonify({'schedule': schedule})

@app.route('/weekly_summary', methods=['GET'])
def get_weekly_summary():
    """Endpoint para obtener resumen semanal de consultas"""
    if 'user_dni' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    week_ago = datetime.now() - timedelta(days=7)
    
    queries = list(queries_collection.find({
        'dni': session['user_dni'],
        'timestamp': {'$gte': week_ago}
    }).sort('timestamp', -1))
    
    if not queries:
        return jsonify({'message': 'No tienes consultas esta semana'})
    
    summary = []
    for query in queries:
        summary.append({
            'fecha': query['timestamp'].strftime('%d/%m/%Y %H:%M'),
            'pregunta': query['message'][:50] + '...' if len(query['message']) > 50 else query['message'],
            'tema': query.get('topic', 'General')
        })
    
    return jsonify({'summary': summary})

@app.route('/extra_problem', methods=['POST'])
def get_extra_problem():
    """Endpoint para generar problemas extra"""
    if 'user_dni' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    data = request.json
    topic = data.get('topic', 'matemáticas')
    difficulty = session.get('difficulty', 'intermedio')
    
    # Verificar límite diario
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    problems_today = queries_collection.count_documents({
        'dni': session['user_dni'],
        'timestamp': {'$gte': today},
        'message': {'$regex': 'problema extra'}
    })
    
    if problems_today >= 15:
        return jsonify({'error': 'Límite diario alcanzado, vuelve mañana'})
    
    # Generar problema con Gemini
    prompt = f"""Genera un problema de {topic} de nivel {difficulty} para un estudiante de secundaria. 
    Incluye:
    1. El enunciado del problema
    2. Espacio para que el estudiante trabaje
    3. NO incluyas la solución todavía
    
    Formato:
    PROBLEMA:
    [enunciado]
    
    DATOS:
    [datos relevantes]
    
    PREGUNTA:
    [qué se debe encontrar]"""
    
    response = model.generate_content(prompt)
    problem = response.text
    
    # Guardar consulta
    save_query(session['user_dni'], f"Problema extra de {topic}", problem, topic)
    
    return jsonify({
        'problem': problem,
        'topic': topic,
        'difficulty': difficulty
    })

@app.route('/set_difficulty', methods=['POST'])
def set_difficulty():
    """Endpoint para ajustar dificultad de ejercicios"""
    if 'user_dni' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    data = request.json
    difficulty = data.get('difficulty', '').lower()
    
    valid_difficulties = ['básico', 'intermedio', 'avanzado']
    
    if difficulty not in valid_difficulties:
        return jsonify({
            'error': 'Nivel no válido: básico, intermedio o avanzado'
        })
    
    session['difficulty'] = difficulty
    
    # Actualizar en la base de datos
    users_collection.update_one(
        {'dni': session['user_dni']},
        {'$set': {'difficulty_preference': difficulty}}
    )
    
    return jsonify({
        'message': f'Nivel configurado: {difficulty}'
    })

# Inicializar datos de ejemplo
def init_sample_data():
    """Inicializa datos de ejemplo en MongoDB"""
    # Usuarios de ejemplo
    sample_users = [
        {'dni': '12345678', 'nombre': 'Juan Pérez', 'rol': 'estudiante'},
        {'dni': '87654321', 'nombre': 'María García', 'rol': 'estudiante'},
        {'dni': '11111111', 'nombre': 'Prof. Carlos López', 'rol': 'docente'},
        {'dni': '99999999', 'nombre': 'Admin Sistema', 'rol': 'admin'}
    ]
    
    for user in sample_users:
        if not users_collection.find_one({'dni': user['dni']}):
            users_collection.insert_one(user)
    
    # Temas por curso
    sample_topics = [
        {
            'curso': 'Matemáticas',
            'temas': ['Álgebra', 'Geometría', 'Trigonometría', 'Estadística', 'Aritmética']
        },
        {
            'curso': 'Ciencias',
            'temas': ['Física', 'Química', 'Biología', 'Ecología', 'Anatomía']
        },
        {
            'curso': 'Historia',
            'temas': ['Historia del Perú', 'Historia Universal', 'Geografía', 'Economía', 'Civismo']
        },
        {
            'curso': 'Comunicación',
            'temas': ['Gramática', 'Literatura', 'Comprensión Lectora', 'Redacción', 'Oratoria']
        }
    ]
    
    for topic_group in sample_topics:
        if not topics_collection.find_one({'curso': topic_group['curso']}):
            topics_collection.insert_one(topic_group)
    
    # Recursos de ejemplo
    sample_resources = [
        {
            'topic': 'Álgebra',
            'tipo': 'video',
            'titulo': 'Introducción al Álgebra',
            'url': 'https://example.com/algebra-intro',
            'descripcion': 'Video explicativo sobre conceptos básicos de álgebra'
        },
        {
            'topic': 'Álgebra',
            'tipo': 'artículo',
            'titulo': 'Ecuaciones de primer grado',
            'url': 'https://example.com/ecuaciones-primer-grado',
            'descripcion': 'Artículo detallado sobre resolución de ecuaciones'
        },
        {
            'topic': 'Álgebra',
            'tipo': 'ejercicio',
            'titulo': 'Práctica de ecuaciones',
            'url': 'https://example.com/practica-ecuaciones',
            'descripcion': 'Set de ejercicios para practicar ecuaciones'
        }
    ]
    
    for resource in sample_resources:
        if not resources_collection.find_one({'titulo': resource['titulo']}):
            resources_collection.insert_one(resource)

if __name__ == '__main__':
    init_sample_data()
    app.run(debug=True, port=5000)