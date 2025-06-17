"""
Módulo de IA Local para el Chatbot Educativo
Primera capa de respuesta basada en datasets entrenados
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
import json
from typing import Tuple, Optional, List, Dict
import re
from unidecode import unidecode

class LocalEducationalAI:
    """
    IA local entrenada con datasets educativos
    Sirve como primera capa antes de usar Gemini
    """
    
    def __init__(self, models_path='models/'):
        self.models_path = models_path
        self.vectorizers = {}
        self.knowledge_bases = {}
        self.confidence_threshold = 0.65  # Umbral de confianza para usar respuesta local
        self.subjects = ['matematicas', 'comunicacion', 'ciencias', 'historia']
        
        # Crear directorio de modelos si no existe
        os.makedirs(models_path, exist_ok=True)
        
        # Cargar modelos si existen
        self.load_models()
    
    def preprocess_text(self, text: str) -> str:
        """Preprocesa el texto para mejorar la búsqueda"""
        # Convertir a minúsculas
        text = text.lower()
        
        # Remover acentos
        text = unidecode(text)
        
        # Remover caracteres especiales pero mantener espacios
        text = re.sub(r'[^a-z0-9\s]', '', text)
        
        # Remover espacios múltiples
        text = ' '.join(text.split())
        
        return text
    
    def identify_subject(self, question: str) -> Optional[str]:
        """Identifica el curso/materia de la pregunta"""
        question_lower = question.lower()
        
        # Palabras clave por materia
        keywords = {
            'matematicas': ['matematica', 'algebra', 'geometria', 'ecuacion', 'numero', 
                           'fraccion', 'porcentaje', 'triangulo', 'area', 'perimetro',
                           'suma', 'resta', 'multiplicacion', 'division', 'calculo'],
            'comunicacion': ['comunicacion', 'lenguaje', 'gramatica', 'oracion', 
                            'sustantivo', 'verbo', 'adjetivo', 'texto', 'redaccion',
                            'literatura', 'cuento', 'poema', 'parrafo', 'palabra'],
            'ciencias': ['ciencia', 'fisica', 'quimica', 'biologia', 'celula', 
                        'atomo', 'molecula', 'energia', 'fuerza', 'newton',
                        'ecosistema', 'ser vivo', 'planta', 'animal', 'elemento'],
            'historia': ['historia', 'peru', 'inca', 'colonia', 'independencia',
                        'cultura', 'civilizacion', 'virrey', 'conquista', 'batalla',
                        'heroe', 'procer', 'fecha', 'epoca', 'siglo']
        }
        
        # Contar coincidencias por materia
        subject_scores = {}
        for subject, words in keywords.items():
            score = sum(1 for word in words if word in question_lower)
            if score > 0:
                subject_scores[subject] = score
        
        # Retornar la materia con más coincidencias
        if subject_scores:
            return max(subject_scores, key=subject_scores.get)
        
        return None
    
    def train_from_dataset(self, subject: str, dataset: List[Dict[str, str]]):
        """
        Entrena el modelo con un dataset específico
        dataset: Lista de diccionarios con 'pregunta' y 'respuesta'
        """
        if subject not in self.subjects:
            raise ValueError(f"Materia no válida: {subject}")
        
        # Preprocesar preguntas
        questions = [self.preprocess_text(item['pregunta']) for item in dataset]
        
        # Crear y entrenar vectorizador TF-IDF
        vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 3),  # Unigramas, bigramas y trigramas
            stop_words=None,  # No usar stop words para mantener contexto
            min_df=1
        )
        
        # Ajustar vectorizador
        question_vectors = vectorizer.fit_transform(questions)
        
        # Guardar vectorizador y knowledge base
        self.vectorizers[subject] = vectorizer
        self.knowledge_bases[subject] = {
            'questions': questions,
            'answers': [item['respuesta'] for item in dataset],
            'vectors': question_vectors,
            'original_questions': [item['pregunta'] for item in dataset]
        }
        
        # Guardar modelo
        self.save_model(subject)
        
        print(f"✓ Modelo de {subject} entrenado con {len(dataset)} ejemplos")
    
    def get_response(self, question: str) -> Tuple[Optional[str], float, Optional[str]]:
        """
        Obtiene respuesta de la IA local
        Retorna: (respuesta, confianza, materia)
        """
        # Identificar materia
        subject = self.identify_subject(question)
        
        if not subject or subject not in self.knowledge_bases:
            return None, 0.0, None
        
        # Preprocesar pregunta
        processed_question = self.preprocess_text(question)
        
        # Vectorizar pregunta
        vectorizer = self.vectorizers[subject]
        question_vector = vectorizer.transform([processed_question])
        
        # Calcular similitud con todas las preguntas en la base
        kb = self.knowledge_bases[subject]
        similarities = cosine_similarity(question_vector, kb['vectors'])[0]
        
        # Encontrar la pregunta más similar
        best_match_idx = np.argmax(similarities)
        best_similarity = similarities[best_match_idx]
        
        # Si la similitud supera el umbral, devolver respuesta
        if best_similarity >= self.confidence_threshold:
            answer = kb['answers'][best_match_idx]
            original_question = kb['original_questions'][best_match_idx]
            
            # Agregar contexto a la respuesta
            enriched_answer = self._enrich_answer(answer, subject, best_similarity)
            
            return enriched_answer, best_similarity, subject
        
        return None, best_similarity, subject
    
    def _enrich_answer(self, answer: str, subject: str, confidence: float) -> str:
        """Enriquece la respuesta con formato y contexto"""
        # Agregar emoji según la materia
        emojis = {
            'matematicas': '📐',
            'comunicacion': '📝',
            'ciencias': '🔬',
            'historia': '📜'
        }
        
        emoji = emojis.get(subject, '📚')
        
        # Formatear respuesta
        formatted_answer = f"{emoji} **{subject.capitalize()}**\n\n{answer}"
        
        # Si la confianza es media, agregar sugerencia
        if confidence < 0.8:
            formatted_answer += "\n\n💡 *Si necesitas más detalles o una explicación diferente, no dudes en preguntar.*"
        
        return formatted_answer
    
    def save_model(self, subject: str):
        """Guarda el modelo entrenado"""
        if subject not in self.vectorizers:
            return
        
        model_file = os.path.join(self.models_path, f'{subject}_model.pkl')
        kb_file = os.path.join(self.models_path, f'{subject}_kb.pkl')
        
        # Guardar vectorizador
        with open(model_file, 'wb') as f:
            pickle.dump(self.vectorizers[subject], f)
        
        # Guardar knowledge base (sin los vectores que son grandes)
        kb_data = {
            'questions': self.knowledge_bases[subject]['questions'],
            'answers': self.knowledge_bases[subject]['answers'],
            'original_questions': self.knowledge_bases[subject]['original_questions']
        }
        
        with open(kb_file, 'wb') as f:
            pickle.dump(kb_data, f)
    
    def load_models(self):
        """Carga todos los modelos disponibles"""
        for subject in self.subjects:
            model_file = os.path.join(self.models_path, f'{subject}_model.pkl')
            kb_file = os.path.join(self.models_path, f'{subject}_kb.pkl')
            
            if os.path.exists(model_file) and os.path.exists(kb_file):
                try:
                    # Cargar vectorizador
                    with open(model_file, 'rb') as f:
                        self.vectorizers[subject] = pickle.load(f)
                    
                    # Cargar knowledge base
                    with open(kb_file, 'rb') as f:
                        kb_data = pickle.load(f)
                    
                    # Recrear vectores
                    vectors = self.vectorizers[subject].transform(kb_data['questions'])
                    
                    self.knowledge_bases[subject] = {
                        'questions': kb_data['questions'],
                        'answers': kb_data['answers'],
                        'original_questions': kb_data['original_questions'],
                        'vectors': vectors
                    }
                    
                    print(f"✓ Modelo de {subject} cargado")
                except Exception as e:
                    print(f"✗ Error cargando modelo de {subject}: {e}")
    
    def add_qa_pair(self, subject: str, question: str, answer: str):
        """Agrega un nuevo par pregunta-respuesta al dataset"""
        if subject not in self.knowledge_bases:
            # Inicializar con un dataset vacío
            self.train_from_dataset(subject, [{'pregunta': question, 'respuesta': answer}])
            return
        
        # Agregar al dataset existente
        kb = self.knowledge_bases[subject]
        processed_question = self.preprocess_text(question)
        
        # Actualizar listas
        kb['questions'].append(processed_question)
        kb['answers'].append(answer)
        kb['original_questions'].append(question)
        
        # Re-entrenar vectorizador con todas las preguntas
        all_questions = kb['questions']
        vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 3),
            min_df=1
        )
        
        kb['vectors'] = vectorizer.fit_transform(all_questions)
        self.vectorizers[subject] = vectorizer
        
        # Guardar modelo actualizado
        self.save_model(subject)
    
    def get_statistics(self) -> Dict[str, int]:
        """Obtiene estadísticas de los modelos cargados"""
        stats = {}
        for subject, kb in self.knowledge_bases.items():
            stats[subject] = len(kb['questions'])
        return stats


# Función auxiliar para integrar con el chatbot existente
def get_ai_response_with_fallback(local_ai: LocalEducationalAI, message: str, 
                                 gemini_model, context: dict = None) -> Tuple[str, str]:
    """
    Intenta responder con IA local, si no puede, usa Gemini
    Retorna: (respuesta, fuente)
    """
    # Intentar con IA local primero
    local_response, confidence, subject = local_ai.get_response(message)
    
    if local_response and confidence >= local_ai.confidence_threshold:
        print(f"✓ Respuesta local con confianza {confidence:.2f}")
        return local_response, "local"
    
    # Si no hay respuesta local suficiente, usar Gemini
    print(f"→ Usando Gemini (confianza local: {confidence:.2f})")
    
    prompt = f"""Eres un asistente educativo amigable para estudiantes de secundaria. 
    Tu objetivo es ayudar con dudas académicas, explicar conceptos de manera clara y motivar el aprendizaje.
    
    Contexto del estudiante: {context if context else 'Estudiante de secundaria'}
    {'Materia detectada: ' + subject if subject else ''}
    
    Pregunta del estudiante: {message}
    
    Por favor, responde de manera clara, educativa y motivadora. Si es una pregunta académica, 
    proporciona una explicación paso a paso cuando sea apropiado.
    
    Usa formato markdown para resaltar información importante con **negritas**."""
    
    try:
        response = gemini_model.generate_content(prompt)
        return response.text, "gemini"
    except Exception as e:
        print(f"Error con Gemini: {e}")
        return "Lo siento, hubo un error al procesar tu pregunta. Por favor, intenta de nuevo.", "error"