import faiss
import numpy as np
import json
import os

import requests

from instructions import full_instructions
from jina import interact_stream


# Функция поиска по вопросу
def find_instruction(question):
    print(f'Вопрос: {question}')
    print('')
    # Проверка размерности эмбеддингов инструкций
    print("Размерность эмбеддингов инструкций:", embeddings_array.shape)

    # Генерация эмбеддинга для вопроса
    question_embedding = generate_embedding(question)
    question_embedding = np.array(question_embedding).astype('float32').reshape(1, -1)

    # Нормализация эмбеддинга вопроса
    faiss.normalize_L2(question_embedding)

    # Проверка размерности эмбеддинга вопроса
    print("Размерность эмбеддинга вопроса:", question_embedding.shape)

    # Убедитесь, что размеры совпадают
    if embeddings_array.shape[1] != question_embedding.shape[1]:
        raise ValueError("Размерности эмбеддингов инструкций и вопроса не совпадают!")

    # Поиск ближайших соседей
    D, I = index.search(question_embedding, k=1)  # k - количество ближайших соседей

    print("Индексы похожих инструкций:", I[0])

    instructions_array = []

    # Извлечение текстов инструкций по найденным индексам
    for idx in I[0]:
        if idx in instructions_dict:
            print("idx:", idx)
            instruction = instructions_dict[idx]
            print("instruction:", instruction)
            instructions_array.append(instruction['content'])
            print(f"Инструкция: {instruction['title']}\nСодержание: {instruction['content']}\n")

    return instructions_array


def interact_stream_voiceflow(text):
    data_launch = {
        "action": {
            "type": "launch"
        }
    }

    data_text = {
        "action": {
            "type": "text",
            'payload': f'{text}'
        }
    }

    user_id = "your_user_id_here"
    voiceflow_api_key = "VF.DM.67499102b357d4928b4ac58b.ZQrIJbkjPUwhCr2I"
    project_id = "672caaaf565396bb1012956f"
    url = f"https://general-runtime.voiceflow.com/v2/project/{project_id}/user/{user_id}/interact/stream"

    headers = {
        'Accept': 'text/event-stream',
        'Authorization': voiceflow_api_key,
        'Content-Type': 'application/json'
    }

    # Запуск взаимодействия
    requests.post(url, headers=headers, json=data_launch)
    response = requests.post(url, headers=headers, json=data_text)

    if response.status_code == 200:
        # Обработка данных ответа
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("data:"):
                    try:
                        # Удаляем префикс "data:" и разбираем JSON
                        json_data = decoded_line[5:]
                        parsed_data = json.loads(json_data)

                        # Логируем всю структуру parsed_data
                        # print("Parsed Data:", json.dumps(parsed_data, indent=4))

                        # Проверяем наличие нужных данных
                        if 'paths' in parsed_data and len(parsed_data['paths']) > 0:
                            for path in parsed_data['paths']:
                                event_type = path.get('event', {}).get('type')
                                event_payload = path.get('event', {}).get('payload', {})
                                # print(f"Event Type: {event_type}")
                                # print(f"Event Payload: {json.dumps(event_payload, indent=4)}")

                                # Извлечение message и output из payload
                                message = event_payload.get('message')
                                output = event_payload.get('output')

                                if message:
                                    # print("Message Found:", message)
                                    # Попробуем разобрать message как JSON
                                    try:
                                        resp = json.loads(message)
                                        print("resp:", resp)
                                        return resp
                                    except json.JSONDecodeError:
                                        print("Failed to decode message as JSON:", message)

                                # if output:
                                #     # print("Output Found:", output)
                                #     # Попробуем разобрать output как JSON
                                #     try:
                                #         embedding_list = json.loads(output)
                                #         # print("Embedding List from Output:", embedding_list)
                                #         return embedding_list
                                #     except json.JSONDecodeError:
                                #         print("Failed to decode output as JSON:", output)

                    except json.JSONDecodeError:
                        print(f"Не удалось разобрать: {decoded_line}")
                    except KeyError as e:
                        print(f"Ошибка ключа: {e}, данные: {decoded_line}")
    else:
        print(f"Error: {response.status_code}")


def generate_embedding(text):
    # Здесь должен быть код для отправки текста на API модели генерации эмбеддингов
    response = interact_stream(text)
    return response


def generate_data_for_final_response(user_question):
    instructions_data = find_instruction(user_question)
    text = f"Вопрос: {user_question} \n Инструкции: {instructions_data}"
    print("")
    print(text)
    data_for_final_response = interact_stream_voiceflow(text)
    print("data_for_final_response:", data_for_final_response)
    return data_for_final_response



# Путь к файлам для сохранения
index_file = 'vector_index.bin'
instructions_file = 'instructions.json'
embeddings_file = 'embeddings.npy'

# Проверка на существование файлов
if os.path.exists(index_file) and os.path.exists(instructions_file) and os.path.exists(embeddings_file):
    # Загрузка индекса
    index = faiss.read_index(index_file)

    # Загрузка инструкций
    with open(instructions_file, 'r', encoding='utf-8') as f:
        instructions_dict = json.load(f)

    # Загрузка эмбеддингов
    embeddings_array = np.load(embeddings_file).astype('float32')
else:
    instructions = full_instructions

    # Генерация эмбеддингов для инструкций
    embeddings = []
    for instruction in instructions:
        full_text = f"{instruction['title']} {instruction['content']}"
        embedding = generate_embedding(full_text)  # Вызов функции для получения эмбеддинга через API
        if embedding is not None:  # Проверяем, что длина равна 20
            embeddings.append(embedding)

    # Преобразование списка эмбеддингов в numpy массив
    embeddings_array = np.array(embeddings).astype('float32')

    # Нормализация эмбеддингов для использования с косинусным сходством
    faiss.normalize_L2(embeddings_array)

    # Создание индекса
    index = faiss.IndexFlatL2(embeddings_array.shape[1])  # L2 метрика
    index.add(embeddings_array)  # Добавление эмбеддингов в индекс

    # Сохранение индекса на диск
    faiss.write_index(index, index_file)

    # Сохранение инструкций для дальнейшего использования
    instructions_dict = {i: instruction for i, instruction in enumerate(instructions)}

    # Сохранение инструкций в файл (например, JSON)
    with open(instructions_file, 'w', encoding='utf-8') as f:
        json.dump(instructions_dict, f, ensure_ascii=False, indent=4)

    # Сохранение эмбеддингов в файл (например, NumPy)
    np.save(embeddings_file, embeddings_array)

    print("Эмбеддинги и инструкции успешно загружены или созданы.")


